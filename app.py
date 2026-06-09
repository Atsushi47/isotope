import streamlit as st
import pandas as pd
import random

# ページの設定
st.set_page_config(page_title="一問一答", page_icon="📝", layout="centered")

# CSVデータの読み込み（タブ区切り）
@st.cache_data
def load_data():
    return pd.read_csv("quiz_data.csv", sep="\t")

try:
    df = load_data()
except FileNotFoundError:
    st.error("quiz_data.csv が見つかりません。")
    st.stop()

# セッション状態の初期化
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

# 「次の問題」を選ぶ関数
def next_question():
    if not df.empty:
        random_row = df.sample(n=1).iloc[0]
        st.session_state.current_question = random_row
        st.session_state.show_answer = False

if st.session_state.current_question is None:
    next_question()

# --- UIの構築 ---

# タイトル部分
st.markdown("### 📝 一問一答")
st.markdown("<div style='font-size: 13px; color: gray; margin-top: -10px; margin-bottom: 15px;'>第2種放射線取扱主任者資格試験勉強アプリ</div>", unsafe_allow_html=True)

if st.session_state.current_question is not None:
    
    # 「【問題】」と「カテゴリー」の統合表示
    category_text = ""
    if "category" in st.session_state.current_question and pd.notna(st.session_state.current_question["category"]):
        category_text = f" <span style='font-size: 14px; color: #FFA500; margin-left: 15px;'>📂 {st.session_state.current_question['category']}</span>"
    
    st.markdown(f"**【問題】**{category_text}", unsafe_allow_html=True)
    
    # 問題文
    st.info(st.session_state.current_question["question"])
    
    # 「答えを見る」ボタン
    if st.button("👀 答えを見る", use_container_width=True):
        st.session_state.show_answer = True

    # 答えと解説の表示
    if st.session_state.show_answer:
        st.markdown("**【答え】**")
        st.success(st.session_state.current_question["answer"])
        
        # 【新機能】解説の表示（CSVに explanation 列がある場合）
        if "explanation" in st.session_state.current_question and pd.notna(st.session_state.current_question["explanation"]):
            st.markdown("**【解説】**")
            st.info(st.session_state.current_question["explanation"])

# 次の問題へボタン
st.button("➡️ 次の問題へ", on_click=next_question, use_container_width=True)
