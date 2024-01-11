import gradio as gr
import time
from uuid import uuid4
from content_maker import scrapper_content

def load_dataset_local():
    time.sleep(10)

# Manual progress function
def daily_post_tqdm(new_exp_name, progress=gr.Progress()):
    progress(0.2, desc="Collecting Images")
    time.sleep(1)
    progress(0.5, desc="Cleaning Images")
    time.sleep(1.5)
    progress(0.8, desc="Sending Images")
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

def pdf_rephrasing_tqdm(exp_name, progress=gr.Progress()):
    progress(0.2, desc="Collecting Images")
    time.sleep(1)
    progress(0.5, desc="Cleaning Images")
    time.sleep(1.5)
    progress(0.8, desc="Sending Images")
    time.sleep(1.5)
    return "done"

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
            pdf_files_upload_2 = gr.File(label="Upload PDF files")
            start_button_4 = gr.Button("Start")
        loading_bar_text_4 = gr.Textbox(label="PreProcess Loading Bar")
        with gr.Row():
          download_button_4 = gr.Button("Download")
        
    start_button_1.click(daily_post_tqdm, outputs=loading_bar_text_1)
    start_button_2.click(daily_summarised_post_tqdm, outputs=loading_bar_text_2)
    start_button_3.click(weekly_summarised_post_tqdm, outputs=loading_bar_text_3)
    start_button_4.click(pdf_rephrasing_tqdm, outputs=loading_bar_text_4)

demo.launch(server_name='0.0.0.0', server_port=7866)
