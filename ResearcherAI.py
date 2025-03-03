import gradio as gr
import requests
import PyPDF2
import os
import pyttsx3
import xml.etree.ElementTree as ET

tts_engine = pyttsx3.init()
paused = False

def search_research_articles(query):
    """Fetch 10 research articles from arXiv API."""
    
    API_URL = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": 10  # Get 10 articles
    }
    
    response = requests.get(API_URL, params=params)
    
    if response.status_code != 200:
        return f"⚠️ Error fetching articles (Status: {response.status_code})."

    data = response.text  # arXiv returns XML, needs parsing
    root = ET.fromstring(data)
    
    articles = []
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        title = entry.find("{http://www.w3.org/2005/Atom}title").text
        link = entry.find("{http://www.w3.org/2005/Atom}id").text
        authors = ", ".join([author.find("{http://www.w3.org/2005/Atom}name").text for author in entry.findall("{http://www.w3.org/2005/Atom}author")])
        summary = entry.find("{http://www.w3.org/2005/Atom}summary").text[:300] + "..."  # Shortened summary

        articles.append(f"**📄 [{title}]({link})**\n👨‍🔬 Authors: {authors}\n📖 {summary}\n\n")

    return "### 🔎 Research Articles Found:\n\n" + "\n".join(articles) if articles else "⚠️ No articles found."

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
    global paused
    if not paused:
        tts_engine.say(text)
        tts_engine.runAndWait()
    return "Reading aloud..."

def pause_reading():
    """Pause text-to-speech."""
    global paused
    paused = True
    tts_engine.stop()
    return "Paused reading."

def resume_reading(text):
    """Resume text-to-speech."""
    global paused
    paused = False
    return read_aloud(text)

def chatbot_function(input_text, cite_details, citation_format, file):
    """Main chatbot function to handle all tasks."""
    response = ""
    
    if input_text:
        response += search_research_articles(input_text) + "\n\n"
    
    if cite_details:
        try:
            title, author, year = [x.strip() for x in cite_details.split(",")]
            response += cite_paper(title, author, year, citation_format) + "\n\n"
        except ValueError:
            response += "⚠️ Please enter citation details in the format: Title, Author, Year.\n\n"
    
    if file:
        response += summarize_file(file) + "\n\n"
    
    return response

def main():
    """Launch the Gradio interface."""
    with gr.Blocks() as demo:
        gr.Markdown("# 📚 Research Assistant Chatbot")
        
        with gr.Row():
            input_text = gr.Textbox(label="🔎 Search Research Articles", placeholder="Enter research topic...")
        
        with gr.Row():
            cite_details = gr.Textbox(label="📖 Cite Paper (Title, Author, Year)", placeholder="e.g., AI Ethics, John Doe, 2023")
            citation_format = gr.Dropdown(["APA", "MLA", "Chicago"], label="Citation Format")
        
        file = gr.File(label="📂 Upload File (PDF/TXT)")
        output = gr.Textbox(label="📋 Response", interactive=False, lines=15)  # Multiline output
        read_button = gr.Button("🔊 Read Aloud")
        pause_button = gr.Button("⏸ Pause")
        resume_button = gr.Button("▶ Resume")
        submit_button = gr.Button("📩 Submit")
        
        submit_button.click(chatbot_function, [input_text, cite_details, citation_format, file], output)
        read_button.click(read_aloud, [output], None)
        pause_button.click(pause_reading, [], None)
        resume_button.click(resume_reading, [output], None)
        
    demo.launch(share=True)

if __name__ == "__main__":
    main()