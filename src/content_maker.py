from utils import scrape_pdf_links, flatten_pdf_links,regex_clean_links, extract_text_from_pdf_link, indivual_news_scrapper, get_longest_one, get_headlines, num_tokens_from_string, add_timestamp_column
from srcapper.llm import get_good_links
from srcapper.main import scrape_websites
from srcapper.data_store import append_to_database, retrieve_records
import pandas as pd

def scrapper_content(website_links, content_time = 'today'):

  links = ["https://resources.automotivemastermind.com/","https://www.autodealertodaymagazine.com/"]
  website_links.extend(links)
  df = scrape_websites(website_links)

  df['pdf_links_inside_pages'] = df['links'].apply(lambda links: [scrape_pdf_links(link) for link in links])
  df['pdf_links_inside_pages'] = df['pdf_links_inside_pages'].apply(flatten_pdf_links)
  df['links_final'] = ""
  for i in range(len(df['links'])):
      df['links_final'][i] = df['links'][i]

  df['prompt'] = ""
  for i in range(len(df['links'])):
      domain = df['website_link'][i].replace("www.","").split("https://")[1].split("/")[0].replace(".com","")
      print(domain)
      prompt = f"This are the links from the website: {domain}.com and i want you to check which links are relevant to news/Blogs not generic links of the website like about single cars and return me them in a list"
      df['prompt'][i] = prompt

  df['good_links'] = ""
  for i in range(len(df['links'])):
      print("Gpt : Getting Good Links", i, len(df['pdf_links_inside_pages']))
      if len(df['pdf_links_inside_pages'][i]) == 0:
        df['good_links'][i] = get_good_links(str(df['links_final'][i]),df['prompt'][i])
      else:
        df['good_links'][i] = []

  df['final_links'] = ""
  for i in range(len(df['good_links'])):
      if df['good_links'][i] is not None:
          if "sorry" not in df['good_links'][i]:
              print(i)
              if len(df['pdf_links_inside_pages'][i]) == 0:
                df['final_links'][i] = regex_clean_links(df['good_links'][i])
              else:
                df['final_links'][i] = []
                
  df['final_links'] = df['final_links'].apply(lambda x: x[:2]) ###
  
  df_news = pd.DataFrame(columns=['website_link', 'news_link', 'news_text'])
  for i in range(len(df['final_links'])):
    if len(df['final_links'][i]) == 0:
      for link in df['pdf_links_inside_pages'][i]:
        df_news = pd.concat([df_news,pd.DataFrame([{'website_link': df['website_link'][i], 'news_link': link, 'news_text': extract_text_from_pdf_link(link)}])], ignore_index=True)
    else:
      for link in df['final_links'][i]:
        if "search" or "auth" not in link.split("/"):
            # print(link, ":", df['website_link'][i])
            df_news = pd.concat([df_news,pd.DataFrame([{'website_link': df['website_link'][i], 'news_link': link, 'news_text': indivual_news_scrapper(link)}])], ignore_index=True)

  for i in range(len(df_news['news_text'])):
      if len(df_news['news_text'][i]) < 10:
          # drop the row
          df_news.drop(i, inplace=True)

  df_news['news_text_split'] = df_news['news_text'].apply(lambda x: x.lower().split("follow"))
  df_news['news_text_split_final'] = df_news['news_text_split'].apply(lambda x: get_longest_one(x))
  df_news['headlines'] = df_news['news_link'].apply(lambda x : get_headlines(x))

  df_news['news_text_split_final'] =  df_news['headlines'] + ":" + df_news['news_text_split_final']
  df_news['news_text_len'] = df_news['news_text'].apply(lambda x : num_tokens_from_string(x))

  df_news = add_timestamp_column(df_news)
  df_news = df_news.drop("news_text_split", axis=1)
  append_to_database(df_news)
  result_today = retrieve_records(date_range=content_time)