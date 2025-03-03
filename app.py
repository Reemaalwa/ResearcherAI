import gradio as gr
import requests
import PyPDF2
import os
import pyttsx3
from langdetect import detect

def search_research_articles(query, region, language):
    """Search for research articles using a web tool."""
    # Using a web search tool (placeholder for actual implementation)
    response = f"Searching for articles on '{query}' in {language} ({region})..."
    return response

def summarize_file(file):
    """Read and summarize uploaded PDF or text file."""
    if file is None:
        return "No file uploaded."
    
    file_path = file.name
    try:
        if file_path.endswith(".pdf"):
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        elif file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            return "Unsupported file format. Please upload a PDF or TXT file."
        
        summary = text[:500] + "..." if len(text) > 500 else text
        return summary
    except Exception as e:
        return f"Error reading file: {str(e)}"

def cite_paper(title, author, year, format_):
    """Generate citations in different formats."""
    citations = {
        "APA": f"{author} ({year}). {title}.",
        "MLA": f"{author}. \"{title}.\" {year}.",
        "Chicago": f"{author}. {year}. \"{title}.\""
    }
    return citations.get(format_, "Format not supported.")

def read_aloud(text):
    """Convert text to speech."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    return "Reading aloud..."

def chatbot_function(input_text, region, language, cite_details, citation_format, file):
    """Main chatbot function to handle all tasks."""
    response = ""
    
    if input_text:
        response += search_research_articles(input_text, region, language) + "\n\n"
    
    if cite_details:
        title, author, year = cite_details.split(",")
        response += cite_paper(title.strip(), author.strip(), year.strip(), citation_format) + "\n\n"
    
    if file:
        response += summarize_file(file) + "\n\n"
    
    return response

def main():
    """Launch the Gradio interface."""
    with gr.Blocks() as demo:
        gr.Markdown("# Research Assistant Chatbot")
        
        with gr.Row():
            input_text = gr.Textbox(label="Search Research Articles")
            region = gr.Dropdown(["Global", "North America", "Europe", "Asia"], label="Region")
            language = gr.Dropdown(["English", "French", "Spanish", "German"], label="Language")
        
        with gr.Row():
            cite_details = gr.Textbox(label="Cite Paper (Title, Author, Year)")
            citation_format = gr.Dropdown(["APA", "MLA", "Chicago"], label="Citation Format")
        
        file = gr.File(label="Upload File (PDF/TXT)")
        output = gr.Textbox(label="Response", interactive=False)
        read_button = gr.Button("Read Aloud")
        submit_button = gr.Button("Submit")
        
        submit_button.click(chatbot_function, [input_text, region, language, cite_details, citation_format, file], output)
        read_button.click(read_aloud, [output], None)
        
    demo.launch(share=True)

if __name__ == "__main__":
    main()
