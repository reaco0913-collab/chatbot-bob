# chatbot_web.py - 修正版（只用 components.html 作為唯一訊息容器）
import streamlit as st
import nltk
from nltk.chat.util import Chat, reflections
import html
import streamlit.components.v1 as components

# 確保 nltk tokenizers/punkt 存在（第一次部署會自動下載）
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

pairs = [
    [r"hi|嗨|哈囉|您好", ["日安!", "哈囉!", "您好,我可以幫您甚麼?"]],
    [r"你是誰", ["我是聊天機器人,您可以稱我是Bob。有甚麼需要幫忙的?"]],
    [r"(.*)電腦無法開機", ["請問電源燈有亮嗎?", "硬碟指示燈有閃爍嗎?"]],
    [r"電源燈沒有亮", ["請確認電源線確實插好"]],
    [r"硬碟燈沒有閃", ["可能硬碟故障,請聯絡經銷商檢修"]],
    [r"電源燈有亮", ["還有其他現象嗎"]],
    [r"硬碟燈有閃", ["這表示硬碟是有作用的"]],
    [r"螢幕沒有畫面\??", ["請檢查螢幕訊號線是否牢固", "請確認訊號線插在正確位址"]],
    [r"作業系統停止運作\??", ["最近有安裝過新的軟體嗎", "請檢查工作管理員中是否有異常軟體正在執行"]],
    [r"(.*)", ["可以告訴我更多的訊息", "請您再描述清楚一點"]]
]

chatbot = Chat(pairs, reflections)

st.set_page_config(page_title="聊天機器人 Bob", page_icon="🤖", layout="wide")
st.title("💬 聊天機器人 Bob")

# session_state 初始
if "messages" not in st.session_state:
    st.session_state.messages = []  # 每項為 {"role": "...", "content": "..."}

# 建構訊息的 HTML（全部由這個 component 呈現，避免雙卷軸）
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
        role = m.get("role", "bot")
        content = m.get("content", "")
        # escape html, 保留換行
        esc = html.escape(content).replace("\n", "<br>")
        if role == "user":
            body += f"<div class='msg-row user'><div class='msg-bubble msg-user'>{esc}</div></div>"
        else:
            body += f"<div class='msg-row bot'><div class='msg-bubble msg-bot'>{esc}</div></div>"
    body += "</div>"

    # JS：component 重繪後自動滾動到底
    js = """
    <script>
    (function(){
        function scrollToBottom(){
            var c = document.getElementById('msg-container');
            if(c){ c.scrollTop = c.scrollHeight; }
        }
        // 若 DOM 已就緒就滾動，否則等 load
        if (document.readyState === 'complete') {
            setTimeout(scrollToBottom, 50);
        } else {
            window.addEventListener('load', function(){ setTimeout(scrollToBottom, 50); });
        }
    })();
    </script>
    """
    return css + body + js

# 先顯示訊息區（component）
messages_html = build_messages_html(st.session_state.messages)
components.html(messages_html, height=520, scrolling=True)

# 再顯示輸入區（確保輸入永遠在訊息區下方）
with st.form(key="chat_form", clear_on_submit=True):
    cols = st.columns([0.95, 0.05])
    with cols[0]:
        user_input = st.text_input("", placeholder="請輸入訊息，按 Enter 送出")
    with cols[1]:
        submitted = st.form_submit_button("送出")

    if submitted and user_input and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        resp = chatbot.respond(user_input.strip()) or ""
        st.session_state.messages.append({"role": "bot", "content": resp})
        # form 的 clear_on_submit=True 會自動清除輸入欄，Streamlit 會重新執行並重新 render component（自動滾到底）
