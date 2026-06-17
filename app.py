import streamlit as st
import pandas as pd
import random

# ページの設定
st.set_page_config(
    page_title="一問一答",
    page_icon="📝",
    layout="centered"
)

# CSVデータの読み込み（タブ区切り）
@st.cache_data
def load_data():
    return pd.read_csv("quiz_data.csv", sep="\t")

try:
    df = load_data()
except FileNotFoundError:
    st.error("quiz_data.csv が見つかりません。")
    st.stop()

# -----------------------------
# セッション状態の初期化
# -----------------------------
if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

# アプリ起動後に何問解いたか
if "solved_count" not in st.session_state:
    st.session_state.solved_count = 0

# 同じ問題で重複カウントしないため
if "answer_counted" not in st.session_state:
    st.session_state.answer_counted = False


# -----------------------------
# 次の問題を選ぶ
# -----------------------------
def next_question():
    if not df.empty:

        idx = random.randint(0, len(df) - 1)

        st.session_state.current_question = df.iloc[idx]
        st.session_state.current_index = idx + 1  # 1始まり
        st.session_state.show_answer = False
        st.session_state.answer_counted = False


# 初回起動時
if st.session_state.current_question is None:
    next_question()


# -----------------------------
# UI
# -----------------------------

# タイトル
st.markdown("### 📝 一問一答")
st.markdown(
    "<div style='font-size: 13px; color: gray; margin-top: -10px; margin-bottom: 15px;'>"
    "第2種放射線取扱主任者資格試験勉強アプリ"
    "</div>",
    unsafe_allow_html=True
)

# 進捗表示
st.markdown(
    f"""
    <div style='font-size:14px; color:gray; margin-bottom:10px;'>
    問題番号：{st.session_state.current_index} / {len(df)}
    <br>
    解答数：{st.session_state.solved_count} 問
    </div>
    """,
    unsafe_allow_html=True
)

if st.session_state.current_question is not None:

    # カテゴリー表示
    category_text = ""

    if (
        "category" in st.session_state.current_question
        and pd.notna(st.session_state.current_question["category"])
    ):
        category_text = (
            f" <span style='font-size: 14px; color: #FFA500; "
            f"margin-left: 15px;'>📂 "
            f"{st.session_state.current_question['category']}</span>"
        )

    st.markdown(
        f"**【問題】**{category_text}",
        unsafe_allow_html=True
    )

    # 問題文
    st.info(st.session_state.current_question["question"])

    # 答えを見る
    if st.button("👀 答えを見る", use_container_width=True):
        st.session_state.show_answer = True

        # 同じ問題で複数回カウントしない
        if not st.session_state.answer_counted:
            st.session_state.solved_count += 1
            st.session_state.answer_counted = True

    # 答え表示
    if st.session_state.show_answer:

        st.markdown("**【答え】**")
        st.success(st.session_state.current_question["answer"])

        # 解説表示
        if (
            "explanation" in st.session_state.current_question
            and pd.notna(
                st.session_state.current_question["explanation"]
            )
        ):
            st.markdown("**【解説】**")
            st.info(
                st.session_state.current_question["explanation"]
            )

# 次の問題へ
st.button(
    "➡️ 次の問題へ",
    on_click=next_question,
    use_container_width=True
)
