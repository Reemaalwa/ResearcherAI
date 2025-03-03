import gradio as gr
import requests
import PyPDF2
import os
import pyttsx3

def search_research_articles(query):
    """Fetch at least 10 research articles using Semantic Scholar API."""
    
    API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "fields": "title,authors,year,url",
        "limit": 10  # Fetch 10 papers
    }
    
    response = requests.get(API_URL, params=params)
    
    if response.status_code != 200:
        return "Error fetching research papers. Please try again later."
    
    data = response.json()
    
    if "data" not in data or not data["data"]:
        return "No relevant research papers found. Try a different query."
    
    response_text = "### 🔎 Research Articles Found:\n\n"
    for idx, paper in enumerate(data["data"][:10]):  # Limit to 10 articles
        title = paper.get("title", "No Title")
        year = paper.get("year", "Unknown Year")
        authors = ", ".join([author["name"] for author in paper.get("authors", [])])
        link = paper.get("url", "#")
        
        response_text += f"**{idx + 1}. [{title}]({link})** ({year})\n"
        response_text += f"   👨‍🔬 Authors: {authors}\n\n"

    return response_text

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
        submit_button = gr.Button("📩 Submit")
        
        submit_button.click(chatbot_function, [input_text, cite_details, citation_format, file], output)
        read_button.click(read_aloud, [output], None)
        
    demo.launch(share=True)

if __name__ == "__main__":
    main()
