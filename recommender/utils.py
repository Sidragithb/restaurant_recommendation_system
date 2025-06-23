# recommender/utils.py
import itertools, random
from collections import Counter, defaultdict
from django.utils import timezone
from django.db.models import Count, Avg, Q
from menu.models  import MenuItem, Ingredient, Review
from order.models import Order, OrderItem

WEIGHTS = {
    "history": 0.30,
    "popular": 0.15,
    "time":    0.15,
    "content": 0.20,
    "cluster": 0.10,
    "basket":  0.10,
}

def history_scores(user):
    ids = OrderItem.objects.filter(order__customer=user)\
                           .values_list("menu_item_id", flat=True)
    return Counter(ids)

def popular_scores(top_k=20):
    qs = (OrderItem.objects.values("menu_item_id")
          .annotate(c=Count("id")).order_by("-c")[:top_k])
    return {row["menu_item_id"]: top_k-i for i, row in enumerate(qs)}

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

def content_scores(user):
    liked = Review.objects.filter(user=user, rating__gte=4)\
                          .values_list("menu_item_id", flat=True)
    ing   = Ingredient.objects.filter(
              recipeingredient__recipe__menu_item_id__in=liked)
    matches = MenuItem.objects.filter(recipe__ingredients__in=ing)\
                              .exclude(id__in=liked)
    return {m.id: 1 for m in matches}

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

# simple market-basket count kept in memory
PAIR_FREQ = defaultdict(int)
for order in Order.objects.prefetch_related("items"):
    ids = [i.menu_item_id for i in order.items.all()]
    for a, b in itertools.combinations(sorted(set(ids)), 2):
        PAIR_FREQ[(a, b)] += 1
def basket_scores():
    c = Counter()
    for (a, b), n in PAIR_FREQ.items():
        c[a] += n
        c[b] += n
    return c

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
    for fn, w in funcs:
        part = fn(user) if fn is not basket_scores else fn()
        for k, v in part.items():
            total[k] += w * v

    seen = set(OrderItem.objects.filter(order__customer=user)
                             .values_list("menu_item_id", flat=True))
    best = [i for i, _ in total.most_common() if i not in seen][:top_n]
    when = " ".join(f"WHEN id={i} THEN {p}" for p, i in enumerate(best))
    return list(MenuItem.objects.filter(id__in=best)
                .extra(select={'_o': f'CASE {when} END'}).order_by('_o'))
