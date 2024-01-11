from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.document import Document
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from utils import zip_folder
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

def content_gen(text,content_type):
    prompt = ChatPromptTemplate.from_template('''Context:You are a content creator who generates content for social media sites,blogs, etc in markdown format.
        Input:  I want to write a {type}. Here is the summarized description of the context on which you have to generate content.
        Description: {description}
        Consider this while generating the {type}:
        If relevant, include:
        - Emojis to highlight any word
        - Calls to action (to encourage engagement)
        - Hashtags (for social media posts) in the end
        Note:
        - Write in a clear and concise manner, avoiding jargon and unnecessary complexity.
        - Use active voice and strong verbs to keep the content engaging.
        - Check for grammar errors, typos, and factual inaccuracies.
        - Edit for clarity and flow.
        - if any unnesary information is present remove it, because some of it is scrapped content.

        Note: Generate the output in Markdown format
        Output:''')

    model = ChatOpenAI(model_name="gpt-3.5-turbo-1106", temperature=0.5, api_key= OPEN_API_KEY)
    output_parser = StrOutputParser()

    chain = prompt | model | output_parser
    content = chain.invoke({"description":text,"type":content_type})
    return content

def daily_news_summary(list_daily_news):
  news = ""
  for i in range(len(list_daily_news)):
    news = news + " " + list_daily_news[i]
  final_summary = chain_summarizer(news)
  return final_summary

def summarized_daily_news_blog(summary,content_type="blog"):
  blog = content_gen(summary,content_type)
  os.makedirs("Summarized_dailyBlog",  exist_ok=True)

  pdf_file_path = os.getcwd()+"/Summarized_dailyBlog/ "+str(uuid.uuid4())+".pdf"
  md2pdf(pdf_file_path,
       md_content=blog,
       md_file_path=None,
       css_file_path=None,
       base_url=None)
  return pdf_file_path

def daily_post_single(list_daily_news,content_type="LinkedIn Post"):

  for i,news in enumerate(list_daily_news):
    single_post = content_gen(news,content_type)
    os.makedirs("Single_dailyPosts",  exist_ok=True)
    folder = os.getcwd()+"/Single_dailyPosts"
    pdf_file_path = os.getcwd()+"/Single_dailyPosts/"+"pdf"+str(i) + ".pdf"
    md2pdf(pdf_file_path,
        md_content=single_post,
        md_file_path=None,
        css_file_path=None,
        base_url=None)

  zip_file_path = os.getcwd()+"/Single_dailyPosts/dailyPost.zip"
  zip_folder(folder, zip_file_path)
  return zip_file_path

def weekly_news_summary(list_weekly_news):
  news = ""
  for i in range(len(list_weekly_news)):
    news = news + " " + list_weekly_news[i]
  final_summary = chain_summarizer(news)
  return final_summary

def weekly_news_blog(summary,content_type="LinkedIn Post"):
  post = content_gen(summary,content_type)
  pdf_file_path = os.getcwd()+"/WeeklyBlog/abc.pdf"
  md2pdf(pdf_file_path,
       md_content=post,
       md_file_path=None,
       css_file_path=None,
       base_url=None)
  return pdf_file_path

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

  model = ChatOpenAI(model_name="gpt-3.5-turbo-1106", temperature=0.5, api_key= OPEN_API_KEY)
  output_parser = StrOutputParser()

  chain = prompt | model | output_parser
  content = chain.invoke({"data":content})
  return content