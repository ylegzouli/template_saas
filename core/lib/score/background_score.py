import time
from django.core.cache import cache
from core.lib.score.openai_api import sort_by_stars
from core.lib.api import add_score_list_data

# @background(schedule=5)
def notify_user(task_id, email, url):
    print("Background function: notify_user()")
    cache_id = f"{email}_ecommerce"
    data = cache.get(cache_id)
    result = add_score_list_data(data['data'], url, data['product'])
    result = sort_by_stars(result)
    # result = []
    data['data'] = result
    cache.set(cache_id, data, timeout=3600)
    print("cache set")
    time.sleep(5)
    cache.set(task_id, {"status" :"Complete"}, timeout=3600)
    print("status set")
    return {"status" :"Complete"} 