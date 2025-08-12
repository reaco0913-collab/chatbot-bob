import streamlit as st
import nltk
from nltk.chat.util import Chat, reflections
import html

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

st.set_page_config(page_title="聊天機器人 Bob", page_icon="🤖", layout="centered")
st.title("💬 聊天機器人 Bob (已修正自動捲動)")

# 初始化 session state
if "messages" not in st.session_state:
    st.session_state.messages = []  # 每個 item: {"role":"user"|"bot","content": "..."}
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

# 輸入區 (上面顯示訊息，下面輸入)
col1, col2 = st.columns([0.9, 0.1])
with col1:
    st.text_input("", key="user_input", placeholder="請輸入訊息，按 Enter 送出", on_change=submit_callback)
with col2:
    if st.button("送出"):
        submit_callback()

# 構造訊息 HTML（放到 component 裡面渲染）
def build_messages_html(messages):
    # CSS: 每則訊息一個 row，user 右對齊、bot 左對齊；bubble 支援換行
    css = """
    <style>
    #msg-container {
        height: 420px;
        overflow-y: auto;
        border: 1px solid #ddd;
        padding: 12px;
        background: #fafafa;
        border-radius: 10px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial;
    }
    .msg-row { width:100%; display:flex; margin-bottom:10px; }
    .msg-row.user { justify-content: flex-end; }
    .msg-row.bot { justify-content: flex-start; }
    .msg-bubble {
        padding: 10px 12px;
        border-radius: 12px;
        max-width: 72%;
        white-space: pre-wrap;      /* 允許換行 */
        word-wrap: break-word;
        line-height: 1.35;
        font-size: 15px;
    }
    .msg-user { background: #DCF8C6; }
    .msg-bot { background: #E8E8E8; }
    </style>
    """

    body = "<div id='msg-container'>"
    for m in messages:
        role = m.get("role","bot")
        content = m.get("content","")
        # escape html special chars, 保留換行
        esc = html.escape(content).replace("\n","<br>")
        if role == "user":
            body += f"<div class='msg-row user'><div class='msg-bubble msg-user'>{esc}</div></div>"
        else:
            body += f"<div class='msg-row bot'><div class='msg-bubble msg-bot'>{esc}</div></div>"
    body += "</div>"

    # JS: 在每次 component 重新渲染時執行 scrollBottom，並嘗試把 Streamlit 的輸入框 focus 回去（若允許）
    js = """
    <script>
    (function(){
        function scrollToBottom(){
            var c = document.getElementById('msg-container');
            if(c){
                c.scrollTop = c.scrollHeight;
            }
        }
        // 保證在 DOM load 後執行
        if (document.readyState === 'complete') {
            setTimeout(scrollToBottom, 50);
        } else {
            window.addEventListener('load', function(){ setTimeout(scrollToBottom, 50); });
        }
        // 嘗試 focus parent 的輸入框（若瀏覽器與平台允許）
        try {
            var p = '請輸入訊息，按 Enter 送出';
            var inputEl = window.parent.document.querySelector('input[placeholder="'+p+'"]');
            if(inputEl){ inputEl.focus(); inputEl.selectionStart = inputEl.value.length; }
        } catch(e) {
            // ignore
        }
    })();
    </script>
    """

    return css + body + js

# 把訊息 HTML 放到 components 裡，component height 要包含訊息高度
messages_html = build_messages_html(st.session_state.messages)
import streamlit.components.v1 as components
components.html(messages_html, height=460, scrolling=True)
