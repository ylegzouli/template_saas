#%%
import requests
from core.lib.score.openai_api import score_complete, get_lead_insight
# from score.openai_api import score_complete, get_lead_insight, sort_by_stars, scrape_website_content
import json
from urllib.parse import urlparse
import re
import os


STORELEAD_APIKEY=os.getenv('STORELEADS_APIKEY')
SCRAPIT_APIKEY=os.getenv('SCRAPIT_APIKEY')
GOOGLE_APIKEY=os.getenv('GOOGLE_APIKEY')


query = 'jewelry'
location = 'fr'
city="Paris"
url_lead_example='https://eclatparis.com/'
revenue=None

def calculate_revenue(revenue):
    if revenue == "0-50k":
        return 0, 5000000
    elif revenue == "50k-2M":
        return 5000000, 200000000
    elif revenue == "2M-10M":
        return 200000000, 1000000000
    elif revenue == "10M-50M":
        return 1000000000, 5000000000
    elif revenue == "+50M":
        return 5000000000, None

def get_company_list(query=query, location=location, city=city, revenue=revenue):
    print("Function: get_company_list()")
    url = "https://storeleads.app/json/api/v1/all/domain"
    headers = {'Authorization': f'Bearer {STORELEAD_APIKEY}'}
    cunjunct = []

    if len(location) > 0:
        cunjunct.append({"field": "cc", "operator": "or", "analyzer": "advanced", "match": location})
    if len(city) > 0:
        cunjunct.append({"field": "city", "operator": "or", "analyzer": "advanced", "match": city})
    
    if len(revenue) > 0:
        min_revenue, max_revenue = calculate_revenue(revenue)
        print(min_revenue, max_revenue)
        er = {"field": "er"}
        if min_revenue is not None:
            er['min'] = min_revenue
            er['inclusive_min'] = True
        if max_revenue is not None:
            er['max'] = max_revenue
            er['inclusive_max'] = True
        cunjunct.append(er)
    
    params = {
        'bq': json.dumps({
            "must": {
            "conjuncts": cunjunct
        },
        "should": {
            "disjuncts": [
                    {"field": "desc", "operator": "or", "analyzer": "stemmer", "match": query}
                ],
                "min": 1
            }
        }),
        'fields': 'street_address,name,merchant_name,categories, contact_info, employee_count, estimated_sales',
        'page_size': 100,

     }    
    
    response = requests.get(url, headers=headers, params=params)
    # print(response.json())
    if response.status_code == 200:
        return response.json()  # Returns the JSON response with specified fields
    else:
        return {'error': 'Failed to retrieve data', 'status_code': response.status_code, 'domains': {}}


def get_domain_info(domain: str):
    print("Function: get_domain_info()")
    url = f"https://storeleads.app/json/api/v1/all/domain/{domain}"
    headers = {'Authorization': f'Bearer {STORELEAD_APIKEY}'}
    params = {
    'fields': 'street_address,name,merchant_name,categories, contact_info, employee_count, estimated_sales',
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()  # Returns the JSON response with specified fields
    else:
        return {'error': 'Failed to retrieve data', 'status_code': response.status_code}


def get_domain_from_url(url):
    print("Function: get_domain_from_url()")
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain


def add_score_list_data(list_data, url_lead_example, product):
    print("Function: add_score_list_data()")
    result = []

    lead_base = get_lead_insight(url_lead_example)

    for data in list_data:
        try: 
            url = data['url']
            print(url)
            stars, categorie = score_complete(lead_base, url, product)
            data['stars'] = stars
            data['categories'] = categorie
            result.append(data)
        except Exception as e:
            print(e)
            pass

    return result


def extract_infos(info):
    print("Function: extract_infos()")
    email = []
    list_instagram = []
    list_linkedin = []
    list_facebook = []
    list_phone = []
    try:
        for contact in info['contact_info']:
            try:
                if contact['type'] == 'instagram':
                    list_instagram.append(contact['value'])
                elif contact['type'] == 'email':
                    email.append(contact['value'])
                elif contact['type'] == 'linkedin':
                    list_linkedin.append(contact['value'])
                elif contact['type'] == 'facebook':
                    list_facebook.append(contact['value'])
                elif contact['type'] == 'phone':
                    list_phone.append(contact['value'])

            except Exception as e:
                print(e)
                pass
    except Exception as e:
        print(e)
        pass
    instagram = list_instagram[0] if len(list_instagram) > 0 else None
    linkedin = list_linkedin[0] if len(list_linkedin) > 0 else None
    facebook = list_facebook[0] if len(list_facebook) > 0 else None
    
    return email, instagram, linkedin, facebook, list_phone 


def format_json_response(json_response):
    print("Function: format_json_response()")
    formatted_data = []
    for item in json_response["domains"]:
        email, insta, linkedin, facebook, phones = extract_infos(item)
        ca = str(int(int(item.get('estimated_sales', 0)) / 100)) if item.get('estimated_sales', "") else "" 
        formatted_item = {
            'name': item.get('merchant_name'),
            'url': f"https://{item.get('name')}",
            'categories': "",
            'email': email,
            'instagram': insta,
            'linkedin': linkedin,
            'facebook': facebook,
            'phone': phones,
            'nb_employee': item.get('employee_count', ""),
            'ca': ca,
            'adress': None,
            'source': "scorelead"
        }
        formatted_data.append(formatted_item)
    # result = add_score_list_data(formatted_data, url_lead_example, product)
    # return result
    return formatted_data


def get_googlem_data(query, country: str = "", location: str = ""):
    print("Function: get_googlem_data()")
    url = 'https://places.googleapis.com/v1/places:searchText'
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': GOOGLE_APIKEY,
        'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.types,places.websiteUri,places.internationalPhoneNumber'

    }
    data = {
        "textQuery": f"{query}, {country}, {city}"
    }

    response = requests.post(url, headers=headers, json=data)

    # print(response.json())
    return response.json()


def format_json_response_google(json_response, url_lead_example, product):#, url_lead_example, product):
    print("Function: format_json_response_google()")
    formatted_data = []
    for item in json_response["places"]:
        url = item.get('websiteUri', None)
        if url is not None:
            try:
                name = item.get('displayName')['text']
            except:
                name = ""
            formatted_item = {
                'name': name,
                'url': url,
                'categories': ", ".join(item.get('types', [])),
                'email': None,
                'instagram': None,
                'linkedin': None,
                'facebook': None,
                'phone': item.get('internationalPhoneNumber', None),
                'nb_employee': None,
                'ca': None,
                'address': item.get('formattedAddress'),
                'source': 'googlemap'
            }
            formatted_data.append(formatted_item)
    # print(formatted_data)
    result = add_score_list_data(formatted_data, url_lead_example, product)
    return result

#%%


def get_data_scrapit(query, country, city, page=0):
    print("Function: get_data_scrapit()")
    query = query.replace(" ", "+")
    print(query)
    url = f'https://api.scrape-it.cloud/scrape/google-maps/search?q={query}+{country}+{city}'
    headers = {
        'x-api-key': SCRAPIT_APIKEY,
        'start': str(page)
    }

    response = requests.get(url, headers=headers)

    data = response.json()
    print(data)

    return data['localResults']



def get_data_scrapit_mpages(query, country, city):
    print("Function: get_data_scrapit_mpages()")
    data_p1 = get_data_scrapit(query, country, city, 0)
    # data_p2 = get_data_scrapit(query, country, city, 20)
    # data_p3 = get_data_scrapit(query, country, city, 40)
    # return data_p1 + data_p2 + data_p3
    return data_p1

def extract_social_and_email_urls(url):
    print("Function: extract_social_and_email_urls()")
    # Define regex patterns for matching URLs
    patterns = {
        'instagram': r'https?://www\.instagram\.com/[a-zA-Z0-9_.-]+(?!\.php|[a-zA-Z0-9_.-]+\.[a-zA-Z0-9]{2,})',
        'facebook': r'https?://www\.facebook\.com/[a-zA-Z0-9_.-]+(?!\.[a-zA-Z0-9_.-]+\.[a-zA-Z0-9]{2,})',
        'linkedin': r'https?://www\.linkedin\.com/in/[a-zA-Z0-9_.-]+(?!\.php|[a-zA-Z0-9_.-]+\.[a-zA-Z0-9]{2,})',
         'email': r'\b[a-zA-Z0-9_.+-]{1,25}@[a-zA-Z0-9-]+\.(?!png\b|jpg\b)[a-zA-Z]{2,}\b'
    }

    try:
        response = requests.get(url, timeout=30)
        html_content = response.text
    except requests.RequestException as e:
        print(f"Error fetching URL content: {e}")
        return {}

    found_urls = {}
    for platform, pattern in patterns.items():
        matches = re.findall(pattern, html_content)
        if matches:
            # For social links, keep only the first URL found
            if platform in ['instagram', 'facebook', 'linkedin']:
                found_urls[platform] = matches[0]  # Store as a single URL string
            else:  # For email, keeping it as a list assuming there might be multiple and unique emails
                found_urls[platform] = list(set(matches))[:1]  # Convert to set for uniqueness, then back to list

    return found_urls


def format_json_response_scrapit(json_response):
    print("Function: format_json_response_scrapit()")
    formatted_data = []
    for item in json_response:
        url = item.get('website', None)
        name = item.get('title')
        if url is not None:
            try:
                name = item.get('title')
            except:
                name = ""
            social = extract_social_and_email_urls(url)
            formatted_item = {
            'name': name,
            'url': url,
            'categories': item.get('type', []),
            'email': "\n".join(social.get('email', "")),
            'instagram': social.get('instagram', None),
            'linkedin': social.get('linkedin', None),
            'facebook': social.get('facebook', None),
            'phone': item.get('phone', None),
            'nb_employee': None,
            'ca': None,
            'address': item.get('address', None),
            'source': 'googlemap'
            }
            formatted_data.append(formatted_item)
    # result = add_score_list_data(formatted_data, url_lead_example, product)
    # return result 
    return formatted_data


# %%
