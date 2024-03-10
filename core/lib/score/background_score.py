import time
from django.core.cache import cache
from core.lib.score.openai_api import sort_by_stars
from core.lib.api import add_score_list_data

# @background(schedule=5)
def notify_user(data, url):
    print("Background function: notify_user()")
    result = add_score_list_data(data['data'], url, data['product'])
    result = sort_by_stars(result)
    data['data'] = result

    return data
