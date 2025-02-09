# Rizz The AI

from openai import OpenAI
import streamlit as st
import torch
torch.classes.__path__ = [] # resolving a bug https://github.com/VikParuchuri/marker/issues/442

MAX_PROMPTS = 10

# Audio pipeline
from kokoro import KPipeline
pipeline = KPipeline(lang_code="a")

def reset():
    st.session_state.messages = []

# Play audio
def read_prompt(prompt: str, gender: str):
    voice = "af_heart"
    if gender == "Male":
        voice = "am_puck"

    generator = pipeline(prompt, voice=voice)
    for (_, _, audio) in generator:
        st.audio(audio.detach().cpu().numpy(), sample_rate=24000, autoplay=True)
        # Make audio play invisible
        st.markdown("""
            <style>
                audio {
                    display: none;
                }
            </style>
            """, unsafe_allow_html=True)

# Create a sticky container for the header
# Create two main columns for the entire page layout
# Title
st.title("Rizz the AI 💕😨")
st.subheader("In 10 prompts, get to the highest rizz score possible!")
left_col, right_col = st.columns([1, 1])
with right_col:
    col1, col2 = st.columns([4, 1])
    with col1:
        # Select profiles based on gender
        gender = st.pills("Choose AI Gender", ["Female", "Male", "Neutral"], default="Female", on_change=reset)
    with col2:
        # Reset chat
        if st.button("↺"):
            reset()
            # st.rerun()
with left_col:
    st.image(f"./images/{gender}.png", width=180)

# Gender-based character descriptions
character_descriptions = {
    "Female": """You are a 20 year old female university student studying Physics. Your name is Sophie.""",
    "Male": """You are a 21 year old male university student studying Commerce. Your name is James.""",
    "Neutral": """You are a 22 year old university student with neutral gender studying Computer Science. Your name is Alex."""
}

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

num_prompts = 0
if prompt := st.chat_input(disabled=(num_prompts==MAX_PROMPTS)):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=None):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar=f"./images/{gender}.png"):
        messages = [{"role": "developer", "content": character_descriptions[gender] + """
                    You will receive prompts from a person who is trying to romantically attract you and flirt with you.
                    Your task is to engage in an active conversation with the person, and respond in a way that is consistent with your character.
                    Feel free to make up a backstory about your persona.
                    You should also evaluate how successful the person is in their attempts to flirt with you, on a score from 0 to 10 (to 1 decimal place).
                    Ensure your responses do not exceed 50 words.
                    Your first score should be 0.0. Each increment of the score from the previous prompt should not exceed 1.0.
                    In each response, you must start by returning the current score up to that point, for example, "[7.9] My name is Sophie."
                    """}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        completion = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=messages,
            stream=False,
        )
        response = completion.choices[0].message.content
        read_prompt(response[response.index(']')+1:], gender)
        st.write(response[response.index(']')+1:])
        
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Extract score from the last assistant message if it exists
    score = 0.0
    num_prompts = 0
    if st.session_state.messages and any(m["role"] == "assistant" for m in st.session_state.messages):
        num_prompts = len([m for m in st.session_state.messages if m["role"] == "assistant"])
        last_response = next(m["content"] for m in reversed(st.session_state.messages) if m["role"] == "assistant")
        try:
            score = float(last_response[1:last_response.index(']')])
            # Determine color based on score ranges
            if score <= 2:
                color = "rgb(255, 0, 0)"  # red
            elif score <= 4:
                color = "rgb(255, 165, 0)"  # orange
            elif score <= 6:
                color = "rgb(135, 206, 235)"  # light blue
            elif score <= 8:
                color = "rgb(144, 238, 144)"  # light green
            else:
                color = "rgb(0, 255, 0)"  # green
            
            st.markdown(
                f"""
                <style>
                    .stProgress > div > div > div > div {{
                        background-color: {color};
                    }}
                </style>""",
                unsafe_allow_html=True
            )
        except:
            st.progress(0, "Waiting for score...")

    if num_prompts >= MAX_PROMPTS or score == 10.0:
        st.info(f"Your Final Rizz Score is {score}! 😨😨😨 Start again!")
        st.stop()
    else:
        st.progress(score / 10, f"Current Rizz Score: {score}/10 | Prompts Left: {MAX_PROMPTS - num_prompts}/{MAX_PROMPTS}")
