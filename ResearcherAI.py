import gradio as gr
import requests
import PyPDF2
import os
import pyttsx3
import xml.etree.ElementTree as ET
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("⚠️ OpenAI API key not found. Set it in your environment variables or .env file.")

client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize Text-to-Speech
tts_engine = pyttsx3.init()
paused = False

def search_research_articles(query):
    """Fetch 10 research articles from arXiv API."""
    API_URL = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": 10
    }
    response = requests.get(API_URL, params=params)
    if response.status_code != 200:
        return f"⚠️ Error fetching articles (Status: {response.status_code})."
    data = response.text
    root = ET.fromstring(data)
    articles = []
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        title = entry.find("{http://www.w3.org/2005/Atom}title").text
        link = entry.find("{http://www.w3.org/2005/Atom}id").text
        authors = ", ".join([author.find("{http://www.w3.org/2005/Atom}name").text for author in entry.findall("{http://www.w3.org/2005/Atom}author")])
        summary = entry.find("{http://www.w3.org/2005/Atom}summary").text[:300] + "..."
        articles.append(f"**📄 [{title}]({link})**\n👨‍🔬 Authors: {authors}\n📖 {summary}\n\n")
    return "### 🔎 Research Articles Found:\n\n" + "\n".join(articles) if articles else "⚠️ No articles found."

def chatgpt_response(prompt):
    """Get a response from ChatGPT-like model using OpenAI API."""
    try:
        response = client.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a helpful AI chatbot."},
                      {"role": "user", "content": prompt}],
            max_tokens=500
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def read_aloud(text):
    """Convert text to speech."""
    global paused
    paused = False
    tts_engine.say(text)
    tts_engine.runAndWait()
    return "🔊 Reading aloud..."

def pause_reading():
    """Pause text-to-speech."""
    global paused
    paused = True
    tts_engine.stop()
    return "⏸ Reading paused."

def resume_reading(text):
    """Resume text-to-speech."""
    global paused
    if paused:
        paused = False
        return read_aloud(text)
    return "▶ Reading already in progress."

def chatbot_function(input_text, cite_details, citation_format, file):
    """Main chatbot function to handle all tasks."""
    response = ""
    if input_text:
        chat_response = chatgpt_response(input_text)
        response += chat_response + "\n\n"
    if cite_details:
        try:
            title, author, year = [x.strip() for x in cite_details.split(",")]
            response += f"📖 **Citation ({citation_format})**: {author} ({year}). {title}.\n\n"
        except ValueError:
            response += "⚠️ Please enter citation details in the format: Title, Author, Year.\n\n"
    if file:
        response += "📂 **File uploaded successfully!**\n\n"
    return response

def main():
    """Launch the Gradio interface."""
    with gr.Blocks(theme=gr.themes.Default()) as demo:
        gr.Markdown("# 🤖 ChatGPT-Style Research Assistant Chatbot")
        
        with gr.Row():
            input_text = gr.Textbox(label="💬 Chat with AI", placeholder="Ask me anything...", lines=3)
        
        with gr.Row():
            cite_details = gr.Textbox(label="📖 Cite Paper (Title, Author, Year)", placeholder="e.g., AI Ethics, John Doe, 2023")
            citation_format = gr.Dropdown(["APA", "MLA", "Chicago"], label="Citation Format")
        
        with gr.Row():
            file = gr.File(label="📂 Upload File (PDF/TXT)")
        
        output = gr.Textbox(label="📋 Response", interactive=False, lines=15, show_copy_button=True)
        
        with gr.Row():
            submit_button = gr.Button("📩 Submit", variant="primary", size="lg")
        
        with gr.Row():
            read_button = gr.Button("🔊 Read Aloud", variant="secondary")
            pause_button = gr.Button("⏸ Pause", variant="secondary")
            resume_button = gr.Button("▶ Resume", variant="secondary")
        
        submit_button.click(chatbot_function, [input_text, cite_details, citation_format, file], output)
        read_button.click(read_aloud, [output], None)
        pause_button.click(pause_reading, [], None)
        resume_button.click(resume_reading, [output], None)
    
    demo.launch(share=True)

if __name__ == "__main__":
    main()
