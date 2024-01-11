import gradio as gr
import time
from srcapper.summariser import daily_news_summary, summarized_daily_news_blog, daily_post_single, weekly_news_summary, weekly_news_blog, rephrase
from content_maker import scrapper_content,get_news_content
from utils import extract_text_from_pdf

    
def daily_post_tqdm(new_exp_name, progress=gr.Progress()):
    progress(0.2, desc="Collecting Links")
    if scrapper_content:
        progress(0.5, desc="Cleaning Links")
        time.sleep(1.5)
        
    # Convert to content
    content_raw = get_news_content(content_time= 'today')
    
    progress(0.8, desc="Saving Data")
    time.sleep(1.5)
    return "done"

def daily_summarised_post_tqdm(exp_name, progress=gr.Progress()):
    progress(0.2, desc="Collecting Images")
    time.sleep(1)
    progress(0.5, desc="Cleaning Images")
    time.sleep(1.5)
    progress(0.8, desc="Sending Images")
    time.sleep(1.5)
    return "done"

def weekly_summarised_post_tqdm(exp_name, progress=gr.Progress()):
    progress(0.2, desc="Collecting Images")
    time.sleep(1)
    progress(0.5, desc="Cleaning Images")
    time.sleep(1.5)
    progress(0.8, desc="Sending Images")
    time.sleep(1.5)
    return "done"

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
        with gr.Row():
          links_textbox = gr.Textbox(label="Enter the links of the websites you want to scrape (comma separated)")
          pdf_files_upload = gr.File(label="Upload PDF files")
        with gr.Row():
            start_button_1 = gr.Button("Start")
        loading_bar_text_1 = gr.Textbox(label="PreProcess Loading Bar")
        
    with gr.Tab("Daily Summarised POST"):
        with gr.Row():
            start_button_2 = gr.Button("Start")
        loading_bar_text_2 = gr.Textbox(label="PreProcess Loading Bar")
        with gr.Row():
          download_button_2 = gr.Button("Download")
        
    with gr.Tab("Last Week Summarised POST"):
        with gr.Row():
            start_button_3 = gr.Button("Start")
        loading_bar_text_3 = gr.Textbox(label="PreProcess Loading Bar")
        with gr.Row():
          download_button_3 = gr.Button("Download")
        
    with gr.Tab("Pdf article Rephrasing"):
        with gr.Row():
          file_output = gr.File()
          pdf_files_upload_2 = gr.UploadButton("Click to Upload a File", file_types=["pdf"], file_count="multiple")
        
    start_button_1.click(daily_post_tqdm, outputs=loading_bar_text_1)
    start_button_2.click(daily_summarised_post_tqdm, outputs=loading_bar_text_2)
    start_button_3.click(weekly_summarised_post_tqdm, outputs=loading_bar_text_3)
    pdf_files_upload_2.upload(pdf_rephrasing_tqdm, pdf_files_upload_2, file_output)

demo.launch(server_name='0.0.0.0', server_port=7866)
