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

# 【改善点①】タイトル部分をスッキリ1行に統合
st.markdown("### 📝 一問一答 <span style='font-size: 14px; color: gray; margin-left: 10px;'>第2種放射線取扱主任者</span>", unsafe_allow_html=True)

if st.session_state.current_question is not None:
    
    # 【改善点②】「【問題】」と「カテゴリー」を同じ行に合体させて縦幅を大幅に節約！
    category_text = ""
    if "category" in st.session_state.current_question and pd.notna(st.session_state.current_question["category"]):
        category_text = f" <span style='font-size: 14px; color: #FFA500; margin-left: 15px;'>📂 {st.session_state.current_question['category']}</span>"
    
    st.markdown(f"**【問題】**{category_text}", unsafe_allow_html=True)
    
    # 問題文
    st.info(st.session_state.current_question["question"])
    
    # 「答えを見る」ボタン
    if st.button("👀 答えを見る", use_container_width=True):
        st.session_state.show_answer = True

    # 答えの表示
    if st.session_state.show_answer:
        st.markdown("**【答え】**")
        st.success(st.session_state.current_question["answer"])

# 【改善点③】無駄な区切り線（st.divider）を無くして直結
st.button("➡️ 次の問題へ", on_click=next_question, use_container_width=True)
