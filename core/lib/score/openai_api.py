#%%

from openai import OpenAI
import requests
from bs4 import BeautifulSoup

def sort_by_stars(data_list):
    """
    Sorts a list of dictionaries based on the star rating in descending order.
    
    Parameters:
    - data_list: A list of dictionaries, where each dictionary contains a 'stars' key with a string of star symbols.
    
    Returns:
    - The sorted list in descending order of star ratings.
    """
    # Define a helper function to convert star symbols to numerical count
    def star_count(star_string):
        return star_string.count('⭐')
    
    # Sort the list using the star_count function to determine the order
    sorted_list = sorted(data_list, key=lambda x: star_count(x['stars']), reverse=True)
    
    return sorted_list

def scrape_website_content(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        # Raise an exception if the request was unsuccessful
        response.raise_for_status()
        
        # Parse the HTML content of the page with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract and return the text content
        # You might need to adjust the method of extraction based on the website's structure
        return soup.get_text(separator='\n', strip=True)
    except requests.RequestException as e:
        print(e)
        return f"Error during requests to {url} : {str(e)}"




def get_product_description(website_content):
    try:
        # content = scrape_website_content(url)
        result = client.chat.completions.create(
            timeout=50,
            model="gpt-3.5-turbo",
            # model="gpt-4",
            messages=[
                # {"role": "system", "content": "User will give you some website content. you're job is identify the product which are sells by the website owner by checking the information provide in the website content. Alwais give me this list in english. you're answer have to contain only a list of product type separate by comma."},
                {"role": "system", "content": "User will give you some website content. you're job is to create a detailed description of the website containing the product which are sells by the website owner by checking the information provide in the website content. Alwais answer in english. you're answer have to contain only a list of keywords separate by comma."},
                {"role": "user", "content": website_content}
            ]
        )
        return result.choices[0].message.content
    except Exception as e:
        print(e)
        return ""


def get_usertarget_description(website_content):
    try:
        # content = scrape_website_content(url)
        result = client.chat.completions.create(
            timeout=50,
            model="gpt-3.5-turbo",
            messages=[
                #  {"role": "system", "content": "Based on the website content provided by the user, your job is to analyze and identify the target audience. Return all the target audience separate by comma. Provide your answer in English."},
                {"role": "system", "content": "User will give you some website content. you're job is identify the audience which are the target of the website by checking the information provide. Alwais give me this list in english describe the target by keyword. you're answer have to contain only a list of audience type separate by comma."},
                {"role": "user", "content": website_content}
            ]
        )
        return result.choices[0].message.content
    except Exception as e:
        print(e)
        return ""


def custom_filter(website_content, product):
    try:
        # content = scrape_website_content(url)
        result = client.chat.completions.create(
            timeout=50,
            model="gpt-3.5-turbo",
            messages=[
                #  {"role": "system", "content": "Based on the website content provided by the user, your job is to analyze and identify the target audience. Return all the target audience separate by comma. Provide your answer in English."},
                {"role": "system", "content": f"""
                 User will give you some website content. you're job is answer by YES or NO to the question. Only answer YES if you are 100% sure of your answer. DID THEY SELL EXACTLY THIS PRODUCT: {product} ? If they don't sell EXACTLY THE SAME product, answer NO.
                 """},
                {"role": "user", "content": website_content}
            ]
        )
        return result.choices[0].message.content
    except Exception as e:
        print(e)
        return ""

def eval_product(product_1, product_2):
    try:
        result = client.chat.completions.create(
            timeout=50,
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"""
                 user will provide you two list of product, your job is to answer the question: is it the same type of products ?
                 Answer only by YES or NO, Only answer YES if you are 100% sure of your answer.
                 """},
                {"role": "user", "content": f"""
                    [PRODUCT 1]
                    {product_1}
                    [PRODUCT 2]
                    {product_2}
                 """}
            ]
        )
        return result.choices[0].message.content
    except Exception as e:
        print(e)
        return ""

def eval_audience(audience_1, audience_2):
    try:
        result = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"""
                 user will provide you two list of users audiences, your job is to answer the question: is there similitude beetween the two audience ?
                 Answer only by YES or NO, Only answer YES if you are 100% sure of your answer.
                 """},
                {"role": "user", "content": f"""
                    [USER AUDIENCE 1]
                    {audience_1}
                    [USER AUDIENCE 2]
                    {audience_2}
                 """}
            ]
        )
        return result.choices[0].message.content
    except Exception as e:
        print(e)
        return ""
    
def are_CA_similar(CA1, CA2, threshold_percentage=30):
    # Calculate the maximum difference allowed based on the threshold percentage
    max_difference = max(CA1, CA2) * threshold_percentage / 100
    
    # Calculate the actual difference
    actual_difference = abs(CA1 - CA2)
    
    # Determine if the actual difference is within the allowed threshold
    if actual_difference <= max_difference:
        return "YES"
    else:
        return "NO"



class LeadInsight():
    website_content: str
    products: str
    audiences: str

    def __init__(self, website_content: str, products: str, audiences: str):
        self.website_content = website_content
        self.products = products
        self.audiences = audiences



def get_lead_insight(url):
    content = scrape_website_content(url)
    products = get_product_description(content)
    audiences = get_usertarget_description(content)
    return LeadInsight(
        website_content=content,
        products=products,
        audiences=audiences,
    )

def score_lead(insight_base: LeadInsight, insight_target: LeadInsight, product: str):
    score_product = eval_product(insight_base.products, insight_target.products)
    print(score_product)
    score_audience = eval_audience(insight_base.audiences, insight_target.audiences)
    print(score_audience)
    score_custom = custom_filter(insight_target.website_content, product)
    print(score_custom)


    score = 0
    if score_product.lower().find("yes") == 0:
        score += 2
    if score_audience.lower().find('yes') == 0:
        score += 1
    if score_custom.lower().find("yes") == 0:
        score += 1

    print("⭐" * (score + 1))
    return "⭐" * (score + 1)

def score_complete(insight_base: LeadInsight, url_target: str, product: str):
    insight_target = get_lead_insight(url_target)

    return score_lead(insight_base, insight_target, product)


#%%

# insight_base = get_lead_insight(url_1)

# urls = [url_2, url_3, url_4, url_5, url_6, url_7]

# for url in urls:
#     print(url)
#     score = score_complete(insight_base, url, "Beauty Mirror")
#     print(score)
#     print("--------------------------------")


# %%
