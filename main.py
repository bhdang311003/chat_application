import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from handle_chat import handle_core_chat, handle_csv_chat

# --- UI config ---s
st.set_page_config(page_title="Core Chat", layout="wide")
st.title("💬 Core Chat — Multi-turn Conversation")


if "image_key" not in st.session_state:
    st.session_state.image_key = 0

# --- Upload optional inputs ---
with st.expander("📎 Upload image"):
    uploaded_image = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png"],
        key=f"uploader_{st.session_state.image_key}"
    )

with st.expander("📎 Upload or link a CSV"):
    uploaded_csv = st.file_uploader("Upload a CSV file", type=["csv"])
    csv_url = st.text_input("Or paste a CSV URL (e.g. raw GitHub CSV link)")


# --- User input ---
user_input = st.chat_input("Type here...")

# --- Chat logic ---
if user_input:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        role = msg["role"].capitalize()
        with st.chat_message(msg["role"]):
            st.markdown(f"**{role}** — *{msg['time']}*")

            if msg["role"] == 'assistant':
                st.markdown(f"**{msg['content']}**")
            else:
                for part in msg['content']:
                    if part["type"] == "text":
                        st.markdown(f"**{part['text']}**")
                    if part["type"] == "image_url":
                        img_url = part['image_url']
                        image_markdown = f"![Uploaded Image]({img_url})"
                        st.markdown(f"{image_markdown}", unsafe_allow_html=True)


    # User message
    user_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if uploaded_image:
        image_bytes = uploaded_image.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        mime = "image/png" if uploaded_image.type == "image/png" else "image/jpeg"
        img_url = f"data:{mime};base64,{image_base64}"

        st.session_state.image_key += 1

        content = [
            {"type": "text", "text": user_input},
            {"type": "image_url", "image_url": img_url}
        ]

        with st.chat_message("user"):
            image_markdown = f"![Uploaded Image]({img_url})"
            st.markdown(f"**User** — *{user_time}*\n\n**{user_input}**\n\n{image_markdown}", unsafe_allow_html=True)
        
        st.session_state.messages.append({"role": "user", "content": content, "time": user_time})

        answer = handle_core_chat()
        
    elif uploaded_csv:
        df = pd.read_csv(uploaded_csv)
        st.write("#### Preview:")
        st.dataframe(df.sample(5))

        content = [
            {"type": "text", "text": user_input},
        ]

        with st.chat_message("user"):
            st.markdown(f"**User** — *{user_time}*\n\n**{user_input}**")

        st.session_state.messages.append({"role": "user", "content": content, "time": user_time})

        answer = handle_csv_chat(df, user_input)

    elif csv_url:
        try:
            df = pd.read_csv(csv_url)
        except Exception as e:
            st.error(f"Cannot load CSV from URL: {e}")  

        st.write("#### Preview:")
        st.dataframe(df.sample(5))

        content = [
            {"type": "text", "text": user_input},
        ]

        with st.chat_message("user"):
            st.markdown(f"**User** — *{user_time}*\n\n**{user_input}**")

        st.session_state.messages.append({"role": "user", "content": content, "time": user_time})

        answer = handle_csv_chat(df, user_input)

    else:
        content = [
            {"type": "text", "text": user_input},
        ]

        with st.chat_message("user"):
            st.markdown(f"**User** — *{user_time}*\n\n**{user_input}**")
    
        st.session_state.messages.append({"role": "user", "content": content, "time": user_time})

        answer = handle_core_chat()

    # Assistant message
    bot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.messages.append({"role": "assistant", "content": answer, "time": bot_time})
    with st.chat_message("assistant"):
        st.markdown(f"**Assistant** — *{bot_time}*\n\n**{answer}**")

if st.button("🗑️ Delete history"):
    st.session_state.messages = []
    st.rerun()