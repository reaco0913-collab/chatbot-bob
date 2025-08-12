import streamlit as st
import nltk
from nltk.chat.util import Chat, reflections
from streamlit_javascript import st_javascript

# 下載 nltk 資料
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

st.set_page_config(page_title="聊天機器人 Bob", page_icon="🤖", layout="centered")
st.title("💬 聊天機器人 Bob")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "focus_cnt" not in st.session_state:
    st.session_state.focus_cnt = 0

def submit_callback():
    txt = st.session_state.get("user_input", "").strip()
    if not txt:
        return
    st.session_state.messages.append({"role": "user", "content": txt})
    resp = chatbot.respond(txt)
    st.session_state.messages.append({"role": "bot", "content": resp})
    st.session_state.user_input = ""
    st.session_state.focus_cnt += 1

# CSS 樣式
st.markdown(
    """
    <style>
    #msg-container {
        height: 400px;
        overflow-y: auto;
        border: 1px solid #ccc;
        padding: 10px;
        background: #f9f9f9;
        border-radius: 10px;
        font-size: 16px;
    }
    .msg-block {
        margin-bottom: 12px;
    }
    .user-msg {
        text-align: right; 
        background: #DCF8C6; 
        padding: 8px; 
        border-radius: 10px; 
        display: inline-block;
        max-width: 70%;
        word-wrap: break-word;
        white-space: pre-wrap;
    }
    .bot-msg {
        text-align: left; 
        background: #E8E8E8; 
        padding: 8px; 
        border-radius: 10px; 
        display: inline-block;
        max-width: 70%;
        word-wrap: break-word;
        white-space: pre-wrap;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 生成 HTML 訊息
messages_html = "<div id='msg-container'>"
for i in range(0, len(st.session_state.messages), 2):
    user_text = st.session_state.messages[i]["content"]
    bot_text = st.session_state.messages[i+1]["content"] if i+1 < len(st.session_state.messages) else ""
    messages_html += "<div class='msg-block'>"
    messages_html += f"<div class='user-msg'>{user_text}</div><br>"
    if bot_text:
        messages_html += f"<div class='bot-msg'>{bot_text}</div>"
    messages_html += "</div>"
messages_html += "</div>"

st.markdown(messages_html, unsafe_allow_html=True)

# 輸入框 + 送出按鈕
col1, col2 = st.columns([0.9, 0.1])
with col1:
    st.text_input("", key="user_input", placeholder="請輸入訊息，按 Enter 送出", on_change=submit_callback)
with col2:
    if st.button("送出"):
        submit_callback()

# JS 自動滾到底並聚焦輸入框
if st.session_state.focus_cnt > 0:
    js_code = """
    (function(){
        const msgContainer = window.parent.document.querySelector("#msg-container");
        if(msgContainer){
            msgContainer.scrollTop = msgContainer.scrollHeight;
        }
        const p = '請輸入訊息，按 Enter 送出';
        const inputEl = window.parent.document.querySelector(`input[placeholder="${p}"]`);
        if(inputEl){ 
            inputEl.focus(); 
            inputEl.selectionStart = inputEl.value.length; 
            return true; 
        }
        return false;
    })()
    """
    st_javascript(js_code, key=f"focus_scroll_js_{st.session_state.focus_cnt}")
