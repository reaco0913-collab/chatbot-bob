# chatbot_web.py (推薦版 - 支援自動聚焦)
import streamlit as st
import nltk
from nltk.chat.util import Chat, reflections
from streamlit_javascript import st_javascript  # 需安裝 streamlit-javascript

# nltk 資料
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
st.title("💬 聊天機器人 Bob (自動聚焦版)")

# session state
if "messages" not in st.session_state:
    st.session_state.messages = []
# 用來觸發 focus 的計數器（每次送出 +1）
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
    st.session_state.focus_cnt += 1  # 讓下方 JS 執行

# 輸入與按鈕
col1, col2 = st.columns([0.9, 0.1])
with col1:
    st.text_input("", key="user_input", placeholder="請輸入訊息，按 Enter 送出", on_change=submit_callback)
with col2:
    if st.button("送出"):
        submit_callback()

# 顯示訊息
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f"<div style='text-align:right; background:#DCF8C6; padding:8px; border-radius:10px; display:inline-block; margin:5px;'>{msg['content']}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div style='text-align:left; background:#E8E8E8; padding:8px; border-radius:10px; display:inline-block; margin:5px;'>{msg['content']}</div>",
            unsafe_allow_html=True,
        )

# 使用 streamlit-javascript 把游標聚焦回輸入框（利用 placeholder 做為 selector）
# 這段 JS 會在每次 focus_cnt 變動時執行一次
try:
    if st.session_state.focus_cnt > 0:
        js_code = """
        (function(){
            const p = '請輸入訊息，按 Enter 送出';
            const el = window.parent.document.querySelector(`input[placeholder="${p}"]`);
            if(el){ el.focus(); el.selectionStart = el.value.length; return true; }
            return false;
        })()
        """
        # st_javascript 會執行並回傳值；加上 key 保證每次 focus_cnt 變動時會重新執行
        st_javascript(js_code, key=f"focus_js_{st.session_state.focus_cnt}")
except Exception:
    # 若 cloud 環境沒安裝或 JS 權限被阻擋，就不用擔心，功能只是改善使用體驗
    pass
