import streamlit as st
import nltk
from nltk.chat.util import Chat, reflections
import random

# 確保 NLTK 資料第一次自動下載
nltk.download('punkt', quiet=True)

pairs = [
    [r"hi|嗨|哈囉|您好",["日安!","哈囉!","您好,我可以幫您甚麼?"]],
    [r"你是誰", ["我是聊天機器人,您可以稱我是Bob。有甚麼需要幫忙的?"]],
    [r"(.*)", ["可以告訴我更多的訊息","請您再描述清楚一點"]]
]
chatbot = Chat(pairs, reflections)

st.set_page_config(page_title="Bob Chatbot", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 自動捲動的 CSS 與 JS
st.markdown("""
    <style>
    .chat-container {
        height: 70vh;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 10px;
    }
    .user-bubble {
        background-color: #dcf8c6;
        padding: 8px;
        border-radius: 10px;
        margin-bottom: 5px;
        display: inline-block;
    }
    .bot-bubble {
        background-color: #f1f0f0;
        padding: 8px;
        border-radius: 10px;
        margin-bottom: 5px;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

# 顯示訊息
st.markdown('<div class="chat-container" id="chat-box">', unsafe_allow_html=True)
for sender, text in st.session_state.messages:
    if sender == "user":
        st.markdown(f"<div class='user-bubble'>{text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'>{text}</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 自動捲動到最下方
st.markdown("""
<script>
    var chatBox = document.getElementById('chat-box');
    chatBox.scrollTop = chatBox.scrollHeight;
</script>
""", unsafe_allow_html=True)

# 輸入區
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("請輸入訊息，按 Enter 送出", "")
    submitted = st.form_submit_button("送出")
    if submitted and user_input.strip():
        st.session_state.messages.append(("user", user_input))
        bot_reply = chatbot.respond(user_input) or "我不太明白你的意思"
        st.session_state.messages.append(("bot", bot_reply))
        st.experimental_rerun()
