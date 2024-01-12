from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.document import Document
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from utils import zip_folder,num_tokens_from_string
from decouple import config
import uuid 
import os

try:
    from md2pdf.core import md2pdf
except:
    print("md2pdf not installed, please install it using pip install md2pdf")

OPEN_API_KEY = config("OPEN_API_KEY")

llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k",api_key = OPEN_API_KEY)
map_template = """The following is a set of documents
{docs}
Based on this list of docs, please provide detailed summary of each document covering every important points.
Helpful Answer:"""
reduce_template = """The following is set of summaries:
{docs}
Take these and distill it into a final, consolidated summary of the main themes.
Helpful Answer:"""
reduce_prompt = PromptTemplate.from_template(reduce_template)

def get_text_chunks_langchain(text):
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = [Document(page_content=x) for x in text_splitter.split_text(text)]
    return docs

def chain_summarizer(text):
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = LLMChain(llm=llm, prompt=map_prompt)

    reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)

    combine_documents_chain = StuffDocumentsChain(
    llm_chain=reduce_chain, document_variable_name="docs"
    )

    reduce_documents_chain = ReduceDocumentsChain(
        combine_documents_chain=combine_documents_chain,
        collapse_documents_chain=combine_documents_chain,
        token_max=4000,
    )

    map_reduce_chain = MapReduceDocumentsChain(
        llm_chain=map_chain,
        reduce_documents_chain=reduce_documents_chain,
        document_variable_name="docs",
        return_intermediate_steps=False,
    )

    split_docs = get_text_chunks_langchain(text)

    final_summary = map_reduce_chain.run(split_docs)
    return final_summary

def content_gen_blog(text,modelname):
    prompt = ChatPromptTemplate.from_template('''
- Context:
You are a curator of fascinating stories and knowledge, crafting engaging newsletter blogs for a curious audience aged 12 and above.

- Input:
Summarized content: {description}

- Remember:
Headline: Craft a captivating headline that sparks curiosity and accurately reflects the blog's core message. Use power words and consider a question format for extra intrigue.
Storytelling: Weave the summarized content into a narrative, with a clear beginning, middle, and end. Inject personal anecdotes, relatable examples, or historical context to enhance connection with the reader.
Information Relevance: Ensure the blog accurately reflects the key points of the summarized content, but don't simply copy-paste. Add analysis, interpretation, and additional facts to enrich the information.
Engagement: Incorporate questions, thought-provoking prompts, or discussion points to encourage reader interaction in the comments.
Call to Action: Conclude with a clear call to action, inviting readers to explore further resources, share their thoughts, or subscribe to your newsletter.
Presentation: Remember to craft the template to me make it appealing for readers. Highlight quotes ,headlines etc and focus on giving proper new lines.
Use good fonts for styling of content

- Output:
Generate a 4-5 paragraph blog post in Markdown format, aiming for approximately 1.5 pages.
Use an active voice and concise language, avoiding jargon and complex terminology.
Focus on creating a conversational and engaging tone that resonates with your target audience.

- Success Metrics:
Assess the blog's attractiveness by evaluating the headline and overall presentation.
Analyze the storytelling aspect, checking for a clear narrative structure and engaging writing style.
Verify the information relevance by ensuring accurate representation of the summarized content and valuable additional insights.
''')
    model = ChatOpenAI(model_name=modelname, temperature=0.5, api_key= OPEN_API_KEY)
    output_parser = StrOutputParser()

    chain = prompt | model | output_parser
    content = chain.invoke({"description":text})
    return content


def content_gen_post(text,modelname):
    prompt = ChatPromptTemplate.from_template('''Context:You are a content creator who generates content for LinkedIn.
        Input:  I want to write a LinkedIn post. Here is the summarized description of the context on which you have to generate content.
        Description: {description}
  
        If relevant, include:
        - Emojis to highlight any word .  
        - Calls to action (to encourage engagement)
        - Hashtags (for social media posts) in the end
       
        Note:
        - Do not include external links
        - Do not inlcude author and date
        - Write in a clear and concise manner, avoiding jargon and unnecessary complexity.
        - Use active voice and strong verbs to keep the content engaging.
        - Check for grammar errors, typos, and factual inaccuracies.
        - Edit for clarity and flow.
        - if any unnecessary information is present remove it, because some of it is scrapped content.


        Output:
                                        ''')

    model = ChatOpenAI(model_name=modelname, temperature=0.3, api_key= OPEN_API_KEY)
    output_parser = StrOutputParser()

    chain = prompt | model | output_parser
    content = chain.invoke({"description":text})
    return content


def remove_page_not_found(df):
    # Filter rows where 'news_text' contains "Page Not Found"
    df = df[~df['news_text'].str.contains("Page Not Found")]

    return df

def summarizer_function(text):
    prompt = ChatPromptTemplate.from_template('''Provide me summary of the provided text.
    Text : {text}
    Note: only include important points and ignore unwanted text as it scrapped data with lot of noise
        Output:''')

    model = ChatOpenAI(model_name="gpt-3.5-turbo-1106", temperature=0.5, api_key=  "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")
    output_parser = StrOutputParser()

    chain = prompt | model | output_parser
    content = chain.invoke({"text":text})
    return content

def process_token(text , token, max_length):
    if token <= 300:
        return text
    elif token > max_length:
        return summarizer_function(text)
    else:
      return text
    

def news_summary(df):
  news = ""
  df_news = remove_page_not_found(df)
  good_pages = df_news['news_text']
  for i in range(len(good_pages)):
    news = news + " " + good_pages[i]
  final_summary = chain_summarizer(news)
  return final_summary

def summarized_daily_news_blog(summary):
  token = num_tokens_from_string(summary)
  token_check = process_token(summary, token, max_length = 127000)
  blog = content_gen_blog(token_check, model = "gpt-4-1106-preview")
  os.makedirs("Summarized_dailyBlog",  exist_ok=True)
  pdf_file_path = os.getcwd()+"/Summarized_dailyBlog" +str(uuid.uuid4())+".pdf"
  md2pdf(pdf_file_path,
       md_content=blog,
       md_file_path=None,
       css_file_path=None,
       base_url=None)
  return pdf_file_path



from datetime import datetime
def daily_post_single(df_news, content_type="LinkedIn Post"):
    # Get the current date for creating a folder with the date as its name
    current_date = datetime.now().strftime("%Y_%m_%d")
    
    # Create a folder for the current date
    folder_path = os.path.join(os.getcwd(), "Single_daily_Posts", current_date)
    os.makedirs(folder_path, exist_ok=True)
    df_news = remove_page_not_found(df_news)
    for index, row in df_news.iterrows():
        token = num_tokens_from_string(row['news_text'])
        token_check = process_token(row['news_text'], token, max_length = 16000)
        single_post = content_gen_post(token_check, model = "gpt-3.5-turbo-1106")
        print(single_post)
        # Create a PDF file for each news item
        txt_file_path = os.path.join(folder_path, f"{row['headlines']}.txt")
        with open(txt_file_path , "w") as f:
          f.write(single_post )
        
    # Create a zip file for the entire folder
    zip_file_path = os.path.join(os.getcwd(), "Single_daily_Posts", f"{current_date}/{current_date}.zip")
    zip_folder(folder_path, zip_file_path)
    
    return zip_file_path

def weekly_news_blog(summary):
  post = content_gen_post(summary)
  os.makedirs(os.getcwd()+"/WeeklyBlog",exist_ok = True)
  folder_path = os.getcwd()+"/WeeklyBlog"
  txt_file_path = os.getcwd()+"/WeeklyBlog/" + str(uuid.uuid4())+".txt"
  token = num_tokens_from_string(summary)
  token_check = process_token(summary, token, max_length = 127000)
  single_post = content_gen_post(token_check,model = "gpt-4-1106-preview")
  print(single_post)
  filename = single_post.split("\n")[0]
  # Create a PDF file for each news item
  txt_file_path = os.path.join(folder_path, f"{filename}.txt")
  with open(txt_file_path , "w") as f:
    f.write(single_post )
  return txt_file_path



def rephrase(content):
  prompt = ChatPromptTemplate.from_template("""
  '''Context: I'm a content creator working on a project. I've generated a piece of content, and I need your help to polish it.
        Input: {data}
        Rephrase the content and improve it while focusing on:
        1. SEO & Readability
        3. Plagarism
        2. Tone & Voice
        3. Action Verbs
        4. Freshness & Relevance
        Note: Generate the content in Markdown format
    Output:
    """)

  model = ChatOpenAI(model_name="gpt-3.5-turbo-1106", temperature=0.4, api_key= OPEN_API_KEY)
  output_parser = StrOutputParser()

  chain = prompt | model | output_parser
  content = chain.invoke({"data":content})
  os.makedirs("rephrased_content",  exist_ok=True)
  pdf_file_path = os.getcwd()+"/rephrased_content/" + str(uuid.uuid4())+".pdf"
  md2pdf(pdf_file_path,
       md_content=content,
       md_file_path=None,
       css_file_path=None,
       base_url=None)
  return pdf_file_path