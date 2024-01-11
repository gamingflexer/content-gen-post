from langchain.chat_models import ChatOpenAI
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema.document import Document
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain import hub
from decouple import config

OPEN_API_KEY = config("OPEN_API_KEY")

llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k",api_key = OPEN_API_KEY)
map_template = """The following is a set of documents
{docs}
Based on this list of docs, please identify the main themes
Helpful Answer:"""
reduce_prompt = hub.pull("rlm/map-prompt")

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
        return_intermediate_steps=False)

    split_docs = get_text_chunks_langchain(text)

    final_summary = map_reduce_chain.run(split_docs)
    return final_summary

def daily_news_summary(list_daily_news):
  news = ""
  for i in range(len(list_daily_news)):
    news = news + " " + list_daily_news[i]
  final_summary = chain_summarizer(news)
  return final_summary