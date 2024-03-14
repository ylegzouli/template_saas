import time
from django.core.cache import cache
from core.lib.score.openai_api import sort_by_stars
from core.lib.api import add_score_list_data

def notify_user(data, url, prduct, lead_type):
    print("Background function: notify_user()")
    result = add_score_list_data(data['data'], url, prduct, lead_type)
    result = sort_by_stars(result)
    data['data'] = result

    return data
