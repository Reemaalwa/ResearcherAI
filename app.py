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
    
    system_message = "You are ResearcherAI, an expert in research methodologies, data analysis, and academic writing. Provide structured and insightful responses."

    if country_filter and country_filter != "All":
        system_message += f" When answering questions, only include information related to {country_filter}."
        user_input = f"Provide information specifically about {user_input} in {country_filter}. Include facts, studies, and relevant data from {country_filter} only."

    if not any(msg["role"] == "system" for msg in conversation_history):
        conversation_history.insert(0, {"role": "system", "content": system_message})

    conversation_history.append({"role": "user", "content": user_input})

    # Query AI model
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=conversation_history,
        temperature=0.7,
        max_tokens=1024,
        top_p=1,
        stream=False,
    )
    
    response_content = completion.choices[0].message.content
    
    conversation_history.append({"role": "assistant", "content": response_content})
    
    return [(msg["content"] if msg["role"] == "user" else None, 
             msg["content"] if msg["role"] == "assistant" else None) 
            for msg in conversation_history]

# JavaScript Animations and Theme Toggle
js_code = """
<script>
function load_animate() {
    var text = " Welcome to ResearcherAI, your personalized research assistant! ";
    var container = document.createElement('div');
    container.id = 'gradio-animation';
    container.style.fontSize = '32pt';
    container.style.fontWeight = 'bold';
    container.style.textAlign = 'center';
    document.body.insertBefore(container, document.body.firstChild);
    let delay = 0;
    for (let i = 0; i < text.length; i++) {
        let letter = document.createElement('span');
        letter.innerText = text[i];
        letter.style.opacity = '0';
        letter.style.transition = 'opacity 0.75s';
        container.appendChild(letter);
        setTimeout(() => { letter.style.opacity = '1'; }, delay * 100);
        delay++;
    }
}

function toggleTheme() {
    var theme = localStorage.getItem("theme");
    var isDarkMode = theme === "dark" || theme === null;
    var body = document.body;
    if (isDarkMode) {
        body.classList.remove("dark-mode");
        body.classList.add("light-mode");
    } else {
        body.classList.remove("light-mode");
        body.classList.add("dark-mode");
    }
    localStorage.setItem("theme", isDarkMode ? "light" : "dark");
    document.getElementById("theme-toggle-btn").innerHTML = isDarkMode ? "☼" : "☾";
}

window.onload = function() {
    load_animate();
    if (localStorage.getItem("theme") === "light") {
        document.body.classList.add("light-mode");
        document.getElementById("theme-toggle-btn").innerHTML = "☼";
    } else {
        document.body.classList.add("dark-mode");
        document.getElementById("theme-toggle-btn").innerHTML = "☾";
    }
};
</script>
"""

TITLE = """
<div class='header-container'>
    <h1 id='gradio-animation'>🧠 ResearcherAI - Your Research Assistant</h1>
    <button id='theme-toggle-btn' onclick='toggleTheme()'>☾</button>
</div>
"""

STYLE = """
<style>
  body { transition: background-color 0.3s ease-in-out; }
  .header-container {
    text-align: center;
    margin: 50px auto;
    position: relative;
  }
  #gradio-animation {
    font-size: 55px;
    font-weight: bold;
    transition: opacity 1.5s ease-in-out;
    text-align: center;
  }
  #theme-toggle-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    padding: 10px 15px;
    font-size: 18px;
    border: none;
    cursor: pointer;
    background-color: #007bff;
    color: white;
    border-radius: 50px;
  }
  .light-mode { background-color: #ffffff !important; color: #000000 !important; }
  .dark-mode { background-color: #181818 !important; color: #ffffff !important; }
  .query-box, .country-box { width: 100%; height: auto; border-radius: 25px; }
  .gradio-button { border-radius: 25px !important; }
</style>
"""

with gr.Blocks() as demo:
    with gr.Tabs():
        with gr.TabItem("💬 Research Chat"):
            gr.HTML(TITLE + STYLE + js_code)
            chatbot = gr.Chatbot()
            with gr.Row():
                user_input = gr.Textbox(
                    label="Your Query",
                    placeholder="Ask about research methodologies, data analysis, academic writing...",
                    lines=5
                )
                country_filter = gr.Dropdown(
                    label="Filter by Country",
                    choices=["All", "Canada", "USA", "UK", "Australia", "Germany"],
                    value="All"
                )
            
            send_button = gr.Button("🔍 Ask ResearcherAI")
            
            send_button.click(
                fn=chat_with_researcher_ai,
                inputs=[user_input, country_filter],
                outputs=chatbot
            )

demo.launch(share=True)
