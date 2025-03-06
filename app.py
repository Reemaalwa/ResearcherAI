import gradio as gr
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
if not load_dotenv():
    print("Warning: Could not load .env file. Ensure it's in the correct directory.")

# Fetch the API key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("Error: GROQ_API_KEY is not set. Ensure your .env file is correctly loaded.")

# Initialize Groq client
client = Groq(api_key=api_key)

# Initialize conversation history
conversation_history = []

def chat_with_researcher_ai(user_input, country_filter):
    """
    Handles user queries related to research with an option to filter results by country.
    """
    global conversation_history
    
    # Define the system message
    system_message = "You are ResearcherAI, an expert in research methodologies, data analysis, and academic writing. Provide structured and insightful responses."

    # Modify the query based on country selection
    if country_filter and country_filter != "All":
        system_message += f" When answering questions, only include information related to {country_filter}."
        user_input = f"Provide information specifically about {user_input} in {country_filter}. Include facts, studies, and relevant data from {country_filter} only."

    # Ensure system message is added only once
    if not any(msg["role"] == "system" for msg in conversation_history):
        conversation_history.insert(0, {"role": "system", "content": system_message})

    # Append user message
    conversation_history.append({"role": "user", "content": user_input})

    # Query AI model
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=conversation_history,
        temperature=0.7,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    
    response_content = completion.choices[0].message.content
    
    conversation_history.append({"role": "assistant", "content": response_content})
    
    return [(msg["content"] if msg["role"] == "user" else None, 
             msg["content"] if msg["role"] == "assistant" else None) 
            for msg in conversation_history]

# UI Styling and Layout
TITLE = """
<style>
h1 { text-align: center; font-size: 24px; margin-bottom: 10px; }
</style>
<h1>🧠 ResearcherAI - Your Research Assistant</h1>
"""

with gr.Blocks(theme=gr.themes.Glass(primary_hue="blue", secondary_hue="blue", neutral_hue="gray")) as demo:
    with gr.Tabs():
        with gr.TabItem("💌 Research Chat"):
            gr.HTML(TITLE)
            chatbot = gr.Chatbot(label="ResearcherAI - Chat Assistant")
            with gr.Row():
                user_input = gr.Textbox(
                    label="Your Query",
                    placeholder="Ask about research methodologies, data analysis, academic writing...",
                    lines=1
                )
                country_filter = gr.Dropdown(
                    label="Filter by Country",
                    choices=["All", "Canada", "USA", "UK", "Australia", "Germany", "China"],
                    value="All"
                )
            
            send_button = gr.Button("🔍 Ask ResearcherAI")
            
            send_button.click(
                fn=chat_with_researcher_ai,
                inputs=[user_input, country_filter],
                outputs=chatbot,
                queue=True
            )

demo.launch()
