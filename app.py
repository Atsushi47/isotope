import streamlit as st
import pandas as pd
import random

# ページの設定（スマホ向けにタイトルの見栄えなどを調整）
st.set_page_config(page_title="一問一答アプリ", page_icon="📝", layout="centered")

# CSVデータの読み込み（キャッシュして高速化）
@st.cache_data
def load_data():
    return pd.read_csv("quiz_data.csv")

try:
    df = load_data()
except FileNotFoundError:
    st.error("quiz_data.csv が見つかりません。同じフォルダに配置してください。")
    st.stop()

# セッション状態（アプリの状態保持）の初期化
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

# 「次の問題」を選ぶ関数
def next_question():
    if not df.empty:
        # ランダムに1行選択
        random_row = df.sample(n=1).iloc[0]
        st.session_state.current_question = random_row
        st.session_state.show_answer = False

# 初回起動時に最初の問題を設定
if st.session_state.current_question is None:
    next_question()

# --- UIの構築 ---
st.title("📝 一問一答クイズ")
st.write("資格試験の勉強用アプリ")
st.divider()

# 問題文の表示
if st.session_state.current_question is not None:
    st.subheader("【問題】")
    st.info(st.session_state.current_question["question"])
    
    # 「答えを見る」ボタン
    if st.button("👀 答えを見る", use_container_width=True):
        st.session_state.show_answer = True

    # 答えの表示
    if st.session_state.show_answer:
        st.subheader("【答え】")
        st.success(st.session_state.current_question["answer"])

    st.divider()

# 「次の問題へ」ボタン（常に下部に配置）
if st.button("➡️ 次の問題へ", on_click=next_question, use_container_width=True):
    pass