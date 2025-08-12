import streamlit as st
import random
import re
import nltk
from nltk.chat.util import Chat, reflections

# 確保第一次部署時會下載 nltk 資料
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

# 聊天規則
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
    [r"最近有安裝過新的軟體\??", ["請試著移除該軟體後再試試是否正常", "請停止該軟體運行"]],
    [r"quit|結束|掰掰|再見", ["再見", "好的,歡迎再來"]],
    [r"(.*)", ["可以告訴我更多的訊息", "請您再描述清楚一點"]]
]

chatbot = Chat(pairs, reflections)

# Streamlit 頁面設定
st.set_page_config(page_title="聊天機器人 Bob", page_icon="🤖", layout="centered")
st.title("💬 聊天機器人 Bob")
st.write("輸入訊息與 Bob 對話。")

# 初始化聊天紀錄
if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示歷史訊息（氣泡樣式）
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f"<div style='text-align: right; background-color: #DCF8C6; padding: 8px; border-radius: 10px; margin: 5px;'>{msg['content']}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div style='text-align: left; background-color: #E8E8E8; padding: 8px; border-radius: 10px; margin: 5px;'>{msg['content']}</div>",
            unsafe_allow_html=True
        )

# 輸入框
user_input = st.text_input("輸入訊息：", "")

if user_input:
    # 使用者訊息
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 機器人回應
    response = chatbot.respond(user_input)
    st.session_state.messages.append({"role": "bot", "content": response})

    st.experimental_rerun()
