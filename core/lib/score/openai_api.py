#%%

from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import os

API_KEY = os.getenv('OPENAI_APIKEY')

def sort_by_stars(data_list):
    print("Function: sort_by_stars()")
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
    print("Function: scrape_website_content()")
    try:
        # Send a GET request to the URL
        response = requests.get(url, timeout=10)
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

client = OpenAI(api_key=API_KEY)

def get_product_description(website_content):
    print("Function: get_product_description()")
    try:
        # content = scrape_website_content(url)
        result = client.chat.completions.create(
            timeout=30,
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


def clean_categorie(categorie):
    print("Function: get_product_description()")
    try:
        result = client.chat.completions.create(
            timeout=30,
            model="gpt-3.5-turbo",
            # model="gpt-4",
            messages=[
                # {"role": "system", "content": "User will give you some website content. you're job is identify the product which are sells by the website owner by checking the information provide in the website content. Alwais give me this list in english. you're answer have to contain only a list of product type separate by comma."},
                {"role": "system", "content": "User will give you a list of products/categories. I want you to resume it in one keyword categorie"},
                {"role": "user", "content": categorie}
            ]
        )
        return result.choices[0].message.content
    except Exception as e:
        print(e)
        return ""

def choose_categorie(product):
    print("Function: choose_categorie()")
    try:
        result = client.chat.completions.create(
            timeout=30,
            model="gpt-4",
            # model="gpt-4",
            messages=[
                # {"role": "system", "content": "User will give you some website content. you're job is identify the product which are sells by the website owner by checking the information provide in the website content. Alwais give me this list in english. you're answer have to contain only a list of product type separate by comma."},
                {"role": "system", "content": """
                 You are an AI assistant with the ability to understand and classify various products into specific categories based on their description, use, or target audience. Your goal is to analyze the product information provided by the user and accurately determine which of the following categories it belongs to: Home Decor, Food & Drink, Women, Beauty & Wellness, Jewellery, Paper & Novelty, Kids & Baby, Pets, Men or Other. Consider the product's features, purpose, and who it's primarily intended for while making your decision. Your classification will help organize products on a digital platform, enhancing the user experience by grouping similar items together. Please choose the most fitting category for each product presented to you, ensuring your selection aligns with the product's primary characteristics and intended use.
                  Only answer with a categorie."""},
                {"role": "user", "content": product}
            ]
        )
        return result.choices[0].message.content
    except Exception as e:
        print(e)
        return ""


def get_usertarget_description(website_content):
    print("Function: get_usertarget_description()")
    try:
        # content = scrape_website_content(url)
        result = client.chat.completions.create(
            timeout=30,
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "User will give you some website content. your job is identify the audience which are the target of the website by checking the information provide. Alwais give me this list in english describe the target by keyword. you're answer have to contain only a list of audience type separate by comma."},
                {"role": "user", "content": website_content}
            ]
        )
        return result.choices[0].message.content
    except Exception as e:
        print(e)
        return ""


def custom_filter(website_content, product):
    print("Function: custom_filter()")
    try:
        # content = scrape_website_content(url)
        result = client.chat.completions.create(
            timeout=30,
            model="gpt-3.5-turbo",
            messages=[
                #  {"role": "system", "content": "Based on the website content provided by the user, your job is to analyze and identify the target audience. Return all the target audience separate by comma. Provide your answer in English."},
                {"role": "system", "content": f"""
                 You are tasked with determining whether a specific product is sold by a brand based on the provided info content. Your response should be straightforward: answer "YES" if the brand sells the product in question, and "NO" if they do not. Ensure your analysis is based directly on the information provided about the brand and product. the product is: {product} only answer by YES or NO.
                 """},
                {"role": "user", "content": website_content}
            ]
        )
        return result.choices[0].message.content
    except Exception as e:
        print(e)
        return ""
    
def extract_website_info(website_content):
    print("Phase 1: extract_website_info()")
    try:
        result = client.chat.completions.create(
            timeout=30,
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """
Analyze the given website content and extract features that indicate whether the website is a BRAND, RETAILER, or OTHER. Look for keywords, phrases, product or service focus, and content type. Product is the key. Summarize your findings in a structured format.
                """},
                {"role": "user", "content": website_content}
            ]
        )
        # Extracting information and returning it
        return result.choices[0].message.content
    except Exception as e:
        print(e)
        return "" 

def classify_website(extracted_info):
    print("Phase 2: classify_website()")
    try:
        result = client.chat.completions.create(
            timeout=30,
            model="gpt-3.5-turbo",  # Update this to your GPT-4 model identifier if different
            messages=[
                {"role": "system", "content": """
Based on the extracted information, classify the website as BRAND, RETAILER, or OTHER. Use the provided insights to make an informed decision.
Only answer with: BRAND, RETAILER or OTHER.
                """},
                {"role": "user", "content": extracted_info}
            ]
        )
        return result.choices[0].message.content
    except Exception as e:
        print(e)
        return ""

    
def store_type_function(extracted_info):
    print("Function: store_type()")
    # print(extracted_info)
    classification = classify_website(extracted_info)
    print(classification)    
    return classification


def eval_product(product_1, product_2):
    print("Function: eval_product()")
    try:
        result = client.chat.completions.create(
            timeout=30,
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

def get_similar_query(query):
    print("Function: get_similar_query()")
    try:
        result = client.chat.completions.create(
            timeout=30,
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"""
                You're role will be to give me 5 exact synonyms in english of the query provide by the user, give only the list separate by comma.
                """},
                {"role": "user", "content": f"""
                    [QUERY]
                    {query}
                 """}
            ]
        )
        return result.choices[0].message.content
    except Exception as e:
        print(e)
        return ""

def eval_audience(audience_1, audience_2):
    print("Function: eval_audience()")
    try:
        result = client.chat.completions.create(
            model="gpt-4",
            timeout=30,
            messages=[
                {"role": "system", "content": f"""
                 user will provide you two list of users audiences, your job is to answer the question: is there similarity beetween the two audience taking care of the audience's revenu and audience's loves?
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
    extracted_info: str
    website_content: str
    products: str
    audiences: str
    store_type: str


    def __init__(self, website_content: str, products: str, audiences: str, store_type: str, categorie:str, extracted_info:str):
        self.extracted_info = extracted_info
        self.website_content = website_content
        self.products = products
        self.audiences = audiences
        self.store_type = store_type
        self.categorie= categorie



def get_lead_insight(url, lead_type="target"):
    print("Function: get_lead_insight()")
    content = scrape_website_content(url)
    extracted_info = extract_website_info(content)
    products = get_product_description(content)
    categorie = choose_categorie(products)
    audiences = get_usertarget_description(content)
    if lead_type == "target":
        store_type = store_type_function(extracted_info)
    else:
        store_type = ""
    return LeadInsight(
        extracted_info=extracted_info,
        website_content=content,
        products=products,
        audiences=audiences,
        store_type=store_type,
        categorie=categorie
    )

def score_lead(insight_base: LeadInsight, insight_target: LeadInsight, product: str):
    print("Function: score_lead()")
    # score_product = eval_product(insight_base.products, insight_target.products)
    # print(score_product)
    score_audience = eval_audience(insight_base.audiences, insight_target.audiences)
    print(score_audience)
    score_custom = custom_filter(insight_target.extracted_info, product)
    print(score_custom)


    score = 0
    # if score_product.lower().find("yes") == 0:
        # score += 1
    print("Fuction: check_categorie")
    if insight_base.categorie.lower().find(insight_target.categorie.lower()) == 0:
        print("YES")
        score += 1
    if score_audience.lower().find('yes') == 0:
        score += 2
    if score_custom.lower().find("yes") == 0:
        score += 1
    print("Fuction: check_type")
    if insight_base.store_type.lower().find(insight_target.store_type.lower()) == 0:
        print("YES")
        score += 1
    else:
        print("NO")


    print("⭐" * (score + 1))
    return "⭐" * (score + 1)

def score_complete(insight_base: LeadInsight, url_target: str, product: str):
    print("Function: score_complete()")
    insight_target = get_lead_insight(url_target)
    categorie = insight_target.categorie

    return score_lead(insight_base, insight_target, product), categorie, insight_target.store_type

# %%
