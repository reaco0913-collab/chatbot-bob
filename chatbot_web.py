# chatbot_web.py - 修正版（解決 AttributeError 問題）
import streamlit as st
import re
import html
import streamlit.components.v1 as components

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
    """查詢紙箱尺寸"""
    query = user_input.strip().upper()
    # 精確匹配
    if query in box_data:
        return f"{query} 的尺寸是 {box_data[query]} 公分"
    # 模糊匹配
    for code, size in box_data.items():
        if query in code:
            return f"{code} 的尺寸是 {size} 公分"
    return "抱歉，查無此紙箱代號，請確認輸入是否正確。"

def get_bot_response(user_input):
    """處理用戶輸入並返回機器人回應"""
    user_input = user_input.strip()
    user_input_lower = user_input.lower()
    
    # 問候語
    if re.search(r"hi|嗨|哈囉|您好|你好", user_input_lower):
        return "日安！我是紙箱小幫手 Boxy，您可以輸入紙箱代號查詢尺寸"
    
    # 自我介紹
    if re.search(r"你是誰|你是什麼", user_input_lower):
        return "我是紙箱小幫手 Boxy，專門幫您查紙箱尺寸"
    
    # 查詢紙箱（含"查詢紙箱"關鍵字）
    match = re.search(r"查詢紙箱\s*(\w+)", user_input, re.IGNORECASE)
    if match:
        return find_box_size(match.group(1))
    
    # 直接輸入紙箱代號
    match = re.search(r"^(\w+)$", user_input)
    if match:
        return find_box_size(match.group(1))
    
    # 其他情況
    return "請輸入紙箱代號查詢，例如：A10 或 查詢紙箱 A10"

st.set_page_config(page_title="紙箱小幫手 Boxy", page_icon="📦", layout="wide")
st.title("📦 紙箱小幫手 Boxy")

# 初始化對話紀錄
if "messages" not in st.session_state:
    st.session_state.messages = []

# 處理用戶輸入
with st.form(key="chat_form", clear_on_submit=True):
    cols = st.columns([0.95, 0.05])
    with cols[0]:
        user_input = st.text_input("", placeholder="請輸入紙箱代號，例如 A10 或 查詢紙箱 A10")
    with cols[1]:
        submitted = st.form_submit_button("送出")

    if submitted and user_input.strip():
        # 添加用戶訊息
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        # 獲取機器人回應
        bot_response = get_bot_response(user_input.strip())
        # 添加機器人回應
        st.session_state.messages.append({"role": "bot", "content": bot_response})

# 顯示對話紀錄
def build_messages_html(messages):
    """構建對話紀錄的 HTML"""
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
    .msg-row { 
        width: 100%; 
        display: flex; 
        margin-bottom: 10px; 
    }
    .msg-row.user { 
        justify-content: flex-end; 
    }
    .msg-row.bot { 
        justify-content: flex-start; 
    }
    .msg-bubble {
        padding: 10px 14px;
        border-radius: 14px;
        max-width: 72%;
        white-space: pre-wrap;
        word-wrap: break-word;
        line-height: 1.4;
        font-size: 15px;
    }
    .msg-user { 
        background: #DCF8C6; 
        color: #000;
    }
    .msg-bot { 
        background: #E8E8E8; 
        color: #000;
    }
    </style>
    """
    
    body = "<div class='msg-container' id='msg-container'>"
    for msg in messages:
        escaped_content = html.escape(msg["content"]).replace("\n", "<br>")
        if msg["role"] == "user":
            body += f"<div class='msg-row user'><div class='msg-bubble msg-user'>{escaped_content}</div></div>"
        else:
            body += f"<div class='msg-row bot'><div class='msg-bubble msg-bot'>{escaped_content}</div></div>"
    body += "</div>"
    
    # JavaScript 自動滾動到底部
    js = """
    <script>
    (function(){
        function scrollToBottom(){
            var container = document.getElementById('msg-container');
            if(container){ 
                container.scrollTop = container.scrollHeight; 
            }
        }
        if (document.readyState === 'complete') {
            setTimeout(scrollToBottom, 50);
        } else {
            window.addEventListener('load', function(){ 
                setTimeout(scrollToBottom, 50); 
            });
        }
    })();
    </script>
    """
    return css + body + js

# 渲染對話界面
if st.session_state.messages:
    messages_html = build_messages_html(st.session_state.messages)
    components.html(messages_html, height=520, scrolling=True)
else:
    # 顯示歡迎訊息
    st.info("👋 歡迎使用紙箱小幫手 Boxy！請輸入紙箱代號查詢尺寸。")

# 顯示可用的紙箱代號
with st.expander("📋 可查詢的紙箱代號"):
    col1, col2, col3 = st.columns(3)
    box_codes = list(box_data.keys())
    
    for i, code in enumerate(box_codes):
        if i % 3 == 0:
            col1.write(f"**{code}**: {box_data[code]} 公分")
        elif i % 3 == 1:
            col2.write(f"**{code}**: {box_data[code]} 公分")
        else:
            col3.write(f"**{code}**: {box_data[code]} 公分")
