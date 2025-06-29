import itertools, random
from collections import Counter, defaultdict
from django.utils import timezone
from django.db.models import Count, Avg, Q
from menu.models  import MenuItem, Ingredient, Review
from order.models import Order, OrderItem

# Define weights for each recommendation method
WEIGHTS = {
    "history": 0.30,
    "popular": 0.15,
    "time":    0.15,
    "content": 0.20,
    "cluster": 0.10,
    "basket":  0.10,
}

# Get menu item frequencies based on user's past orders
def history_scores(user):
    ids = OrderItem.objects.filter(order__customer=user)\
                           .values_list("menu_item_id", flat=True)
    return Counter(ids)

# Get globally popular menu items
def popular_scores(top_k=20):
    qs = (OrderItem.objects.values("menu_item_id")
          .annotate(c=Count("id")).order_by("-c")[:top_k])
    return {row["menu_item_id"]: top_k - i for i, row in enumerate(qs)}

# Get time-based menu recommendations based on current hour
def time_scores():
    now  = timezone.localtime()
    hour = now.hour
    q = Q()
    if hour < 12:
        q |= Q(name__icontains="tea") | Q(name__icontains="paratha")
    elif hour < 17:
        q |= Q(name__icontains="biryani")
    else:
        q |= Q(name__icontains="karahi") | Q(name__icontains="kebab")
    return {m.id: 1 for m in MenuItem.objects.filter(q)}

# Recommend items based on ingredients from user's high-rated reviews
def content_scores(user):
    liked = Review.objects.filter(user=user, rating__gte=4)\
                          .values_list("menu_item_id", flat=True)
    ing = Ingredient.objects.filter(
            recipeingredient__recipe__menu_item_id__in=liked)
    matches = MenuItem.objects.filter(recipe__ingredients__in=ing)\
                              .exclude(id__in=liked)
    return {m.id: 1 for m in matches}

# Recommend based on user's spending behavior
def cluster_scores(user):
    avg = Order.objects.filter(customer=user)\
                       .aggregate(a=Avg("total_price"))["a"] or 0
    if avg < 500:
        qs = MenuItem.objects.filter(price__lt=400)
    elif avg < 1000:
        qs = MenuItem.objects.filter(price__gte=400, price__lt=800)
    else:
        qs = MenuItem.objects.filter(price__gte=800)
    return {m.id: 1 for m in qs}

# Basket data stored in memory (market basket logic)
PAIR_FREQ = defaultdict(int)

# Initialize basket pair frequencies from historical orders
def init_basket_freq():
    global PAIR_FREQ
    PAIR_FREQ.clear()
    for order in Order.objects.prefetch_related("items"):
        ids = [i.menu_item_id for i in order.items.all()]
        for a, b in itertools.combinations(sorted(set(ids)), 2):
            PAIR_FREQ[(a, b)] += 1

# Calculate basket-based item scores using co-occurrence frequency
def basket_scores():
    if not PAIR_FREQ:  # only calculate once
        init_basket_freq()
    c = Counter()
    for (a, b), n in PAIR_FREQ.items():
        c[a] += n
        c[b] += n
    return c

# Combine all recommendation strategies into one hybrid method
def hybrid_recommendation(user, top_n=5):
    total = Counter()
    funcs = [
        (history_scores, WEIGHTS["history"]),
        (popular_scores, WEIGHTS["popular"]),
        (time_scores,    WEIGHTS["time"]),
        (content_scores, WEIGHTS["content"]),
        (cluster_scores, WEIGHTS["cluster"]),
        (basket_scores,  WEIGHTS["basket"]),
    ]
    
    # Apply each strategy and add weighted scores
    for fn, w in funcs:
        part = fn(user) if fn is not basket_scores else fn()
        for k, v in part.items():
            total[k] += w * v

    # Exclude items the user has already ordered
    seen = set(OrderItem.objects.filter(order__customer=user)
                             .values_list("menu_item_id", flat=True))
                             
    # Sort recommendations by score and maintain custom order
    best = [i for i, _ in total.most_common() if i not in seen][:top_n]
    when = " ".join(f"WHEN id={i} THEN {p}" for p, i in enumerate(best))
    
    # Return menu items in recommended order
    return list(MenuItem.objects.filter(id__in=best)
                .extra(select={'_o': f'CASE {when} END'}).order_by('_o'))
