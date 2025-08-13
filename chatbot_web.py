# chatbot_web.py - 修正版（即時顯示 Q&A，無延遲）
import streamlit as st
import nltk
from nltk.chat.util import Chat, reflections
import html
import streamlit.components.v1 as components
import re

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

# 紙箱尺寸資料
box_data = {
    "A10": "25 × 18 × 17",
    "A20": "51 × 20 × 18",
    "A40": "51 × 38 × 18",
    "DM": "48 × 32 × 20",
    "DMCL": "48 × 32 × 20",
    "DT": "53 × 36 × 27",
    "i10": "40 × 40 × 20",
    "i12": "40 × 40 × 24",
    "LR01": "39 × 34 × 33",
    "S10": "35 × 35 × 22",
    "S20": "70 × 35 × 25",
    "S3": "35 × 35 × 9",
    "T10": "60 × 35 × 28",
    "VM": "49 × 29 × 23"
}

def find_box_size(user_input):
    query = user_input.strip().upper()
    # 精確匹配
    if query in box_data:
        return f"{query} 的尺寸是 {box_data[query]} 公分"
    # 模糊匹配
    for code, size in box_data.items():
        if query in code:
            return f"{code} 的尺寸是 {size} 公分"
    return "抱歉，查無此紙箱代號，請確認輸入是否正確。"

# 對話規則
pairs = [
    [r"hi|嗨|哈囉|您好", ["日安!", "哈囉!", "您好，我是紙箱小幫手 Boxy，您可以輸入紙箱代號查詢尺寸"]],
    [r"你是誰", ["我是紙箱小幫手 Boxy，專門幫您查紙箱尺寸"]],
    [r"查詢紙箱\s*(\w+)", [lambda matches: find_box_size(matches.group(1))]],
    [r"(\w+)", [lambda matches: find_box_size(matches.group(1))]]
]

chatbot = Chat(pairs, reflections)

st.set_page_config(page_title="紙箱小幫手 Boxy", page_icon="📦", layout="wide")
st.title("📦 紙箱小幫手 Boxy")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 1️⃣ 處理輸入，先更新對話紀錄
with st.form(key="chat_form", clear_on_submit=True):
    cols = st.columns([0.95, 0.05])
    with cols[0]:
        user_input = st.text_input("", placeholder="請輸入紙箱代號，例如 A10 或 查詢紙箱 A10")
    with cols[1]:
        submitted = st.form_submit_button("送出")

    if submitted and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        resp = chatbot.respond(user_input.strip()) or ""
        st.session_state.messages.append({"role": "bot", "content": resp})

# 2️⃣ 再顯示對話（包含最新一輪 Q&A）
def build_messages_html(messages):
    css = """
    <style>
    .msg-container {
        height: 60vh;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        padding: 12px;
        background: #ffffff;
        border-radius: 10px;
        box-shadow: 0 0 0 1px rgba(0,0,0,0.02);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial;
    }
    .msg-row { width:100%; display:flex; margin-bottom:10px; }
    .msg-row.user { justify-content:flex-end; }
    .msg-row.bot { justify-content:flex-start; }
    .msg-bubble {
        padding: 10px 14px;
        border-radius: 14px;
        max-width: 72%;
        white-space: pre-wrap;
        word-wrap: break-word;
        line-height: 1.4;
        font-size: 15px;
    }
    .msg-user { background: #DCF8C6; }
    .msg-bot { background: #E8E8E8; }
    </style>
    """
    body = "<div class='msg-container' id='msg-container'>"
    for m in messages:
        esc = html.escape(m["content"]).replace("\n", "<br>")
        if m["role"] == "user":
            body += f"<div class='msg-row user'><div class='msg-bubble msg-user'>{esc}</div></div>"
        else:
            body += f"<div class='msg-row bot'><div class='msg-bubble msg-bot'>{esc}</div></div>"
    body += "</div>"
    js = """
    <script>
    (function(){
        function scrollToBottom(){
            var c = document.getElementById('msg-container');
            if(c){ c.scrollTop = c.scrollHeight; }
        }
        if (document.readyState === 'complete') {
            setTimeout(scrollToBottom, 50);
        } else {
            window.addEventListener('load', function(){ setTimeout(scrollToBottom, 50); });
        }
    })();
    </script>
    """
    return css + body + js

messages_html = build_messages_html(st.session_state.messages)
components.html(messages_html, height=520, scrolling=True)
