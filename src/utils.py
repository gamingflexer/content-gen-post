from urllib.parse import urlparse
import requests
import PyPDF2
import os,re
import tiktoken
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime
from zipfile import ZipFile

def zip_folder(folder_path, zip_path):
    with ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname=arcname)


def add_timestamp_column(dataframe):
    dataframe['timestamp'] = datetime.now()
    return dataframe


def num_tokens_from_string(string: str) -> int:
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    """Returns the number of tokens in a text string."""
    num_tokens = len(encoding.encode(string))
    return num_tokens

def get_headlines(text):
  if text.endswith("/"):
      return text.split("/")[-2]
  else:
      return text.split("/")[-1]
skip_domains = ['news.ycombinator.com']
keywords = ['FB', 'Insta', 'Twitter', 'Youtube','pinterest','cloudflare', 'compliance', 'AutoDealerToday', 'news', 'search', 'blogs', 'login', 'issues', 'opinion' ,'awards', 'training', 'Reddit', 'tiktok','t.me', '#bc-favorites-modal', 'digitalmagazine', 'whitepapers', 'articles', 'videos', 'javascript', 'rss', 'digital' ,'Linkedin','legal','deals', 'free', 'press', 'coupons', 'offers', 'discounts', 'faq', 'about', 'contact', 'privacy', 'terms', 'conditions', 'policy', 'careers', 'help', 'support', 'subscribe']

def filter_links_by_domain_main(links, target_domain):
    filtered_links = []

    for link in links:
        parsed_url = urlparse(link)
        if parsed_url.netloc == target_domain:
            filtered_links.append(link)
    if filtered_links == []:
      return links
    return filtered_links

def indivual_news_scrapper(link):
    try:
        link = re.sub(r"[',\"]", "", link)
        response = requests.get(link, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko)'})
        soup = BeautifulSoup(response.content, 'html.parser')
        text_from_link = soup.get_text()
        text_from_link = text_from_link.replace('\n', '')
        return text_from_link[:-650]
    except:
        return ""

def filter_links_based_keywords(links,domain):
    filtered_links = []
    for link in links:
        if link is not None:
            if any(keyword.lower() in link.lower() for keyword in keywords):
                continue
            if "https://" not in str(link):
                link = "https://www."  + domain + str(link)
            filtered_links.append(link)
    return filtered_links

def filter_links(domain, links):
    domain = domain.replace(".com", "")
    filtered_links = []
    if domain is not None:
        filtered_links.extend(
            link for link in links if link is not None and domain in link or "story"
        )
    return filtered_links

def remove_unwanted_links(filtered_links):
    new_filtered_links = []
    for filtered_link in filtered_links:
        if "https://" in str(filtered_link):
            new_filtered_links.append(filtered_link)
    return new_filtered_links


def get_links(input_link):
    domain = input_link.replace("www.","").split("https://")[1].split("/")[0]
    re=requests.get(input_link, headers={'User-Agent': 'Mozilla/5.0'})
    data = re.text
    soup = BeautifulSoup(data)
    final_links = [link.get('href') for link in soup.find_all('a')]
    final_links = filter_links_by_domain_main(final_links,domain)
    if domain in skip_domains:
        print("Skipping domain: ", domain)
        return filter_links_based_keywords(remove_unwanted_links(list(set(final_links))),domain)
    return filter_links_based_keywords(filter_links(domain,list(set(final_links))),domain)

def regex_clean_links(link):
    pattern = r'(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})'

    links = re.findall(pattern, link)

    for link in links:
        if 'category/security' in link:
            links.remove(link)
    return links

def get_longest_one(text_list):
    max_id = 0
    for i in range(1, len(text_list)):
        if len(text_list[i].split(" ")) > len(text_list[max_id].split(" ")):
            max_id = i
    return text_list[max_id]

def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfFileReader(file)
            text = ""
            for page_num in range(pdf_reader.numPages):
                page = pdf_reader.getPage(page_num)
                text += page.extractText()
            return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None
    
def extract_text_from_pdf_link(url):

   try:
       # Download the PDF file
       response = requests.get(url, stream=True)
       response.raise_for_status()  # Raise an error for bad status codes (e.g., 404)

       # Save the PDF to a temporary file
       with open("temp_downloaded_pdf.pdf", "wb") as f:
           for chunk in response.iter_content(chunk_size=1024):
               f.write(chunk)

       # Extract text from the PDF
       with open("temp_downloaded_pdf.pdf", "rb") as pdf_file:
           pdf_reader = PyPDF2.PdfReader(pdf_file)
           text = ""
           for page_num in range(len(pdf_reader.pages)):
               page = pdf_reader.pages[page_num]
               text += page.extract_text()

       return text

   except requests.exceptions.RequestException as e:
       raise Exception(f"Error downloading PDF from URL: {e}")
   except PyPDF2.errors.PdfReadError as e:
       raise Exception(f"Error reading PDF content: {e}")
   finally:
       # Clean up the temporary file
       if os.path.exists("temp_downloaded_pdf.pdf"):
           os.remove("temp_downloaded_pdf.pdf")
           
def normalize_domain(target_domain):
    target_domain = target_domain.replace('http://', '').replace('https://', '').rstrip('/')
    return target_domain

def filter_links_by_domain(links, target_domain):
    target_domain = normalize_domain(target_domain)
    filtered_links = []

    for link in links:
        parsed_url = urlparse(link)
        link_domain = normalize_domain(parsed_url.netloc)

        if link_domain == target_domain:
            filtered_links.append(link)
    return 

def scrape_pdf_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        pdf_links = soup.find_all('a', string=lambda text: 'Download PDF' in str(text))
        pdf_links = [link.get('href') for link in pdf_links]
        return pdf_links

    except requests.exceptions.RequestException as e:
        print(f"Error accessing {url}: {e}")
        return []

def flatten_pdf_links(links):
  flat_data = [item for sublist in links for item in sublist]
  return [re.search(r'https?://[^\s]+', item).group(0) for item in flat_data if re.search(r'https?://[^\s]+', item)]