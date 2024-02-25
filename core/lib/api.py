#%%
import requests
from core.lib.score import score_func, stars_prospects
# from score import score_func, stars_prospects

api_key = "7fa615db-d3d3-44e8-71d9-39ea11ba"


query = 'jewelry'  # Replace with your actual query
location = 'FR'  # Replace with your actual location filter
city="Paris"

def get_company_list(query=query, location=location, city=city):
    url = "https://storeleads.app/json/api/v1/all/domain"
    headers = {'Authorization': f'Bearer {api_key}'}
    params = {
        'page_size': 10,
        'q': query, 
        'f:cc': location,
        'f:city': city,
        # 'fields': 'adresse,name,merchant_name,categories,contact_info'  # Fields you want to include in the response
        'fields': 'street_address,name,merchant_name,categories, contact_info'  # Fields you want to include in the response
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()  # Returns the JSON response with specified fields
    else:
        return {'error': 'Failed to retrieve data', 'status_code': response.status_code}
    

def add_score_list_data(list_data):
    result = []
    for data in list_data:
        url = data['url']
        print(url)
        stars = stars_prospects(score_func(url))
        data['stars'] = stars
        result.append(data)
    return result


def extract_infos(info):
    email = []
    instagram = []
    linkedin = []
    facebook = []
    for contact in info['contact_info']:
        try:
            if contact['type'] == 'instagram':
                instagram.append(contact['value'])
            elif contact['type'] == 'email':
                email.append(contact['value'])
            elif contact['type'] == 'linkedin':
                linkedin.append(contact['value'])
            elif contact['type'] == 'facebook':
                facebook.append(contact['value'])
        except Exception as e:
            print(e)
            pass
    return email, instagram, linkedin, facebook


def format_json_response(json_response):
    formatted_data = []
    for item in json_response["domains"]:
        email, insta, linkedin, facebook = extract_infos(item)
        formatted_item = {
            'name': item.get('merchant_name'),
            'url': f"https://{item.get('name')}",
            'categories': ", ".join(item.get('categories', [])),
            'email': "\n".join(email),
            'instagram': "\n".join(insta),
            'linkedin': "\n".join(linkedin),
            'facebook': "\n".join(facebook)
        }
        formatted_data.append(formatted_item)
    result = add_score_list_data(formatted_data)
    return result

#%%

# test = get_company_list()

#%%

# print(test['domains'][0]['contact_info'])


# def extract_infos(info):
#     email = []
#     instagram = []
#     linkedin = []
#     for contact in test['contact_info']:
#         try:
#             if contact['type'] == 'instagram':
#                 instagram.append(contact['value'])
#             elif contact['type'] == 'email':
#                 email.append(contact['value'])
#             elif contact['type'] == 'linkedin':
#                 linkedin.append(contact['value'])
#         except Exception as e:
#             print(e)
#             pass
#     return email, instagram, linkedin

    # print(email, instagram, linkedin)



#%%
# import requests

# url = "https://recherche-entreprises.api.gouv.fr/search"
# params = {
#     "q": "Eclat Paris",
#     "page": 1,
#     "per_page": 2
# }
# headers = {
    # "accept": "application/json"
# }

# response = requests.get(url, params=params, headers=headers)
# print(response)

# for res in response.json()['results']:
#     print(res)
    # print(response.json())

#%%
    


# test = get_company_list(query="Jewelry")
# print(test)

# for res in test['domains']:
    # print(res)


#%%

# add_score_list_data(test)

# print(test['domains'][0]['contact_info'])

# for contact in test['domains'][0]['contact_info']:
#     # print(contact)
#     if contact['type'] == "email":
#         email = contact['value'] 
#         print(email)


# %%


# import googlemaps

# client object
# client = googlemaps.Client(key = "AIzaSyA8sJE4G56oCkMckfsRo34CbmpzJeL-P90")

# area within 500 m of The White House
# lat =  38.897957, 
# lon = -77.036560, # lat lon of The White House
# radius = 500 # radius in meters
# token = None # page token for going to next page of search

# method 1
# desirable_places = client.places(query = 'jewelry paris')
# desirable_places = client.find_place('jewelry Paris', 'textquery')

# # or use way # method 2
# place_type = 'cafe'
# desirable_places = client.places(type = place_type)

# token for searching next page; to be used in a loop
# token = desirable_places['next_page_token'] 

# print(len(desirable_places))

# print(desirable_places)

# output
# Found 20 places
# %%
