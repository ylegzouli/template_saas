import requests

api_key = "7fa615db-d3d3-44e8-71d9-39ea11ba"


query = 'jewelry'  # Replace with your actual query
location = 'FR'  # Replace with your actual location filter
city=""

def get_company_list(query=query, location=location, city=city):
    url = "https://storeleads.app/json/api/v1/all/domain"
    headers = {'Authorization': f'Bearer {api_key}'}
    params = {
        'page_size': 2,
        'q': query, 
        'f:cc': location,
        'f:city': city,
        # 'fields': 'icon_url,description,name,app_store_url,vendor_url,vendor_website,categories,avg_price,brands_page,categories,city,contact_info,country_code,estimated_sales,financing_page,keywords,retailer_page'  # Fields you want to include in the response
        'fields': 'description,name,categories'  # Fields you want to include in the response
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()  # Returns the JSON response with specified fields
    else:
        return {'error': 'Failed to retrieve data', 'status_code': response.status_code}
    
def format_json_response(json_response):
    # Example transformation (adjust according to your needs)
    formatted_data = []
    for item in json_response["domains"]:
        formatted_item = {
            'name': item.get('name'),
            'description': item.get('description'),
            'categories': ", ".join(item.get('categories', []))  # Join categories list into a string
        }
        formatted_data.append(formatted_item)
    return formatted_data


