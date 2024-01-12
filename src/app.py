import gradio as gr
import time
from srcapper.summariser import news_summary, summarized_daily_news_blog, daily_post_single, weekly_news_blog, rephrase
from content_maker import scrapper_content
from utils import extract_text_from_pdf
from srcapper.data_store import retrieve_records
import pandas as pd
    
def daily_post_tqdm(links_textbox,pdf_files_upload, progress=gr.Progress()):
    try:
      file_paths = [file.name for file in pdf_files_upload]
    except:
        print("No pdfs")
    print(links_textbox,pdf_files_upload)
    
    links_extra = links_textbox.split(",")

    progress(0.2, desc="Collecting Links")
    
    if scrapper_content(links_extra, pdf_files_upload):
        progress(0.5, desc="Cleaning Links")
    
    # Convert to content
    content_raw = retrieve_records(date_range='today')
    print(len(content_raw), "-->")
    print(content_raw.tail())
    # list_news = []
    # for result in content_raw:
    #     list_news.append(result['news_text'])

    zip_path_daily = daily_post_single(content_raw )
    
    progress(0.8, desc="Saving Data")
    time.sleep(1.5)
    return zip_path_daily

def daily_summarised_post_tqdm( progress=gr.Progress()):
    result_week = retrieve_records(date_range='today')
    progress(0.2, desc="Collecting Text")
    # list_news = []
    # for result in result_week:
    #     list_news.append(result['news_text'])
    progress(0.5, desc=" Daily News Summary")
    daily_news_summrised = news_summary(result_week)
    path_summarised_daily_post =  summarized_daily_news_blog(daily_news_summrised)
    progress(0.8, desc=" Generating PDF")
    return path_summarised_daily_post

def weekly_summarised_post_tqdm(progress=gr.Progress()):
    result_week = retrieve_records(date_range='week')
    progress(0.2, desc="Collecting Text")
    # list_news = []
    # for result in result_week:
    #     list_news.append(result['news_text'])
    weekly_news_summaried = news_summary(result_week)
    progress(0.5, desc="Summarising Weekly News")
    weekly_pdf_path = weekly_news_blog(weekly_news_summaried)
    progress(0.8, desc=" Generating PDF")
    return weekly_pdf_path

def pdf_rephrasing_tqdm(files, progress=gr.Progress()):
    file_paths = [file.name for file in files]
    total_text = ""
    for file_path in file_paths:
      text = extract_text_from_pdf(file_path)
      if text is not None:
        total_text = total_text + " " + text
    
    blog_pdf = rephrase(total_text)
    print(file_paths)
    progress(0.2, desc="Collecting Images")
    time.sleep(1)
    progress(0.5, desc="Cleaning Images")
    time.sleep(1.5)
    progress(0.8, desc="Sending Images")
    time.sleep(1.5)
    return blog_pdf

with gr.Blocks() as demo:
        
    with gr.Tab("Daily Post of the Day"):
        #daily_post_single
        with gr.Row():
          links_textbox = gr.Textbox(label="Enter the links of the websites you want to scrape (comma separated)")
          pdf_files_upload = gr.File(label="Upload PDF files", file_types=["pdf"], file_count="multiple")
        with gr.Row():
            start_button_1 = gr.Button("Start")
        loading_bar_text_1 = gr.Textbox(label="PreProcess Loading Bar")
        
    with gr.Tab("Daily Summarised BLOG"):
        #summarized_daily_news_blog
        with gr.Row():
            start_button_2 = gr.Button("Start")
        loading_bar_text_2 = gr.Textbox(label="PreProcess Loading Bar")
        
    with gr.Tab("Weekly Summarised POST (LAST)"):
        #weekly_news_blog but it is post
        with gr.Row():
            start_button_3 = gr.Button("Start")
        loading_bar_text_3 = gr.Textbox(label="PreProcess Loading Bar")
        
    with gr.Tab("Pdf article Rephrasing"):
        with gr.Row():
          file_output = gr.File()
          pdf_files_upload_2 = gr.UploadButton("Click to Upload a File", file_types=["pdf"], file_count="multiple")
        
    start_button_1.click(fn=daily_post_tqdm,inputs=[links_textbox, pdf_files_upload] ,outputs=loading_bar_text_1)
    start_button_2.click(daily_summarised_post_tqdm, outputs=loading_bar_text_2)
    start_button_3.click(weekly_summarised_post_tqdm, outputs=loading_bar_text_3)
    pdf_files_upload_2.upload(pdf_rephrasing_tqdm, pdf_files_upload_2, file_output)

demo.launch(server_name='0.0.0.0', server_port=8001,share = True)
