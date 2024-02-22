import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import string

client = OpenAI(api_key='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')

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
        return f"Error during requests to {url} : {str(e)}"

def get_product_description(url):
    try:
        content = scrape_website_content(url)
        result = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "User will give you some website content. you're job is identify the product which are sells by the website owner checking the information provide in the website content. you're answer have to contain only a list of product type separate by comma."},
                {"role": "user", "content": content}
            ]
        )
        print(url, "\n\n")
        print(result.choices[0].message.content)
        print("\n\n-----------------------------\n")
        return result.choices[0].message.content
    except:
        return ""

    
# A simple function to clean and split text into keywords
def extract_keywords(text):
    stopwords = set(["the", "and", "of", "in", "a", "to", "with", "for", "on", "as", "by", "is", "that", "they", "their", "such", "ensuring", "catering", "features", "offers", "offering", "including", "made"])  # Add more stopwords as needed
    text = text.lower()  # Convert to lowercase
    text = text.translate(str.maketrans("", "", string.punctuation))  # Remove punctuation
    words = text.split()  # Split into words
    keywords = [word for word in words if word not in stopwords]  # Remove stopwords
    return set(keywords)  # Return as a set to remove duplicates


# Function to score the potential match based on common keywords
def score_potential(client_desc, prospect_descs):
    client_keywords = extract_keywords(client_desc)
    prospect_keywords = extract_keywords(prospect_descs)
    common_keywords = client_keywords.intersection(prospect_keywords)
    score = len(common_keywords)
    return score

    
def score_prospect(prospect_desc):

    client_desc_en = "jewelry, rings, ear jewels, earrings, bracelets, brooches, ankle chains, waist chains, necklaces, jewelry sets, displays"
    
    score = score_potential(prospect_desc, client_desc_en) / len(prospect_desc.split(" "))
    return score