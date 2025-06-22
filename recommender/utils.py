from collections import Counter
from decimal import Decimal
from django.utils import timezone
from django.db.models import Count, Q
from order.models import OrderItem
from menu.models import MenuItem

# History‑based (most‑ordered by the user)

def recommend_items_for_user(user, top_n=5):
    ordered_items = OrderItem.objects.filter(order__customer=user)
    item_counts   = Counter(item.menu_item for item in ordered_items)

    return [item for item, _ in item_counts.most_common(top_n)]


# Globally popular items

def get_popular_items(top_n=5):
    top = (
        OrderItem.objects
        .values("menu_item")
        .annotate(cnt=Count("id"))
        .order_by("-cnt")[:top_n]
    )
    return [MenuItem.objects.get(id=row["menu_item"]) for row in top]


# Time‑aware suggestions (breakfast / lunch / dinner)

_MEAL_KEYWORDS = {
    "breakfast": ["tea", "egg", "paratha"],
    "lunch":     ["burger", "biryani", "rice"],
    "dinner":    ["karahi", "kebab", "naan"],
}

def current_meal_period():
    hour = timezone.localtime().hour
    if 6 <= hour < 11:
        return "breakfast"
    if 11 <= hour < 17:
        return "lunch"
    return "dinner"

def get_time_based_items(user=None, top_n=5):
    meal = current_meal_period()
    keywords = _MEAL_KEYWORDS.get(meal, [])
    q = Q()
    for kw in keywords:
        q |= Q(name__icontains=kw)
    items = MenuItem.objects.filter(q)[:top_n]
    return list(items)


# Content‑based (ingredient overlap)

def recommend_similar_items(menu_item, top_n=5):
    try:
        base_ing = set(menu_item.recipe.ingredients.all())
    except:
        return []

    similarities = []
    for item in MenuItem.objects.exclude(id=menu_item.id):
        try:
            other_ing = set(item.recipe.ingredients.all())
            score = len(base_ing & other_ing)
            if score:
                similarities.append((item, score))
        except:
            continue

    similarities.sort(key=lambda x: x[1], reverse=True)
    return [itm for itm, _ in similarities[:top_n]]


# Hybrid recommendation combining all strategies
from django.contrib.auth import get_user_model
def get_user_by_id(user_id):
    User = get_user_model()
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None
    
    
def hybrid_recommendation(user, top_n=5):
    items = (
        recommend_items_for_user(user, top_n)
        + get_popular_items(top_n)
        + get_time_based_items(user, top_n)
    )

    # uniqueness while preserving order
    seen, unique = set(), []
    for itm in items:
        if itm.id not in seen:
            unique.append(itm)
            seen.add(itm.id)
        if len(unique) >= top_n:
            break
    return unique
