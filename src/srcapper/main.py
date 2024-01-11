from utils import get_links
from bs4 import BeautifulSoup
import pandas as pd
import requests

def preprocess(text):
    return text.replace('\n', '')

def get_soup(text):
    return BeautifulSoup(text, 'html.parser')

def scrape_websites(urls):
    data = {'website_link': [], 'text': [], 'website_name': [], 'soup': []}

    for link in urls:
        # Send a GET request to the URL
        response = requests.get(link, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko)'})

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all the text in the HTML document
        text = soup.get_text()

        # Add the website name and text to the data dictionary
        data['website_link'].append(link)
        data['text'].append(text)
        data['website_name'].append(link.replace("www.","").split("https://")[1].split("/")[0].replace(".com",""))
        data['soup'].append(soup)

    # Convert the data dictionary to a Pandas dataframe
    df = pd.DataFrame(data)

    # Preprocess the "text" column
    df['text'] = df['text'].apply(preprocess)

    df['links'] = df['website_link'].apply(get_links)

    return df