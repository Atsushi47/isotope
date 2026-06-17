import streamlit as st
import pandas as pd
import random
import os

# -----------------------------
# 設定
# -----------------------------
QUIZ_FILE = "quiz_data.csv"
HISTORY_FILE = "learning_history.csv"

st.set_page_config(
    page_title="一問一答",
    page_icon="📝",
    layout="centered"
)

# -----------------------------
# 問題データ読込
# -----------------------------
@st.cache_data
def load_data():
    return pd.read_csv(QUIZ_FILE, sep="\t")

try:
    df = load_data()
except FileNotFoundError:
    st.error(f"{QUIZ_FILE} が見つかりません。")
    st.stop()

# -----------------------------
# 学習履歴
# -----------------------------
def load_history():

    if os.path.exists(HISTORY_FILE):

        history = pd.read_csv(HISTORY_FILE)

        # 問題数が増えた場合に対応
        if len(history) < len(df):

            add_df = pd.DataFrame({
                "question_id": range(len(history), len(df)),
                "correct": 0,
                "wrong": 0
            })

            history = pd.concat(
                [history, add_df],
                ignore_index=True
            )

            history.to_csv(
                HISTORY_FILE,
                index=False
            )

        return history

    history = pd.DataFrame({
        "question_id": range(len(df)),
        "correct": 0,
        "wrong": 0
    })

    history.to_csv(
        HISTORY_FILE,
        index=False
    )

    return history


history_df = load_history()


def save_history():
    history_df.to_csv(
        HISTORY_FILE,
        index=False
    )

# -----------------------------
# セッション状態
# -----------------------------
if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

if "solved_count" not in st.session_state:
    st.session_state.solved_count = 0

if "answer_counted" not in st.session_state:
    st.session_state.answer_counted = False

# -----------------------------
# 出題
# -----------------------------
def next_question():

    if df.empty:
        return

    mode = st.session_state.get(
        "quiz_mode",
        "通常"
    )

    # -------------------------
    # 通常モード
    # -------------------------
    if mode == "通常":

        idx = random.randint(
            0,
            len(df) - 1
        )

    # -------------------------
    # 重点モード
    # -------------------------
    else:

        weights = []

        for i in range(len(df)):

            row = history_df.iloc[i]

            weight = (
                1
                + row["wrong"] * 3
                - row["correct"]
            )

            weight = max(weight, 1)

            weights.append(weight)

        idx = random.choices(
            range(len(df)),
            weights=weights,
            k=1
        )[0]

    st.session_state.current_question = df.iloc[idx]
    st.session_state.current_index = idx + 1
    st.session_state.show_answer = False
    st.session_state.answer_counted = False

# -----------------------------
# 正解
# -----------------------------
def mark_correct():

    idx = st.session_state.current_index - 1

    history_df.loc[
        history_df["question_id"] == idx,
        "correct"
    ] += 1

    save_history()

    next_question()

# -----------------------------
# 不正解
# -----------------------------
def mark_wrong():

    idx = st.session_state.current_index - 1

    history_df.loc[
        history_df["question_id"] == idx,
        "wrong"
    ] += 1

    save_history()

    next_question()

# -----------------------------
# 初回出題
# -----------------------------
if st.session_state.current_question is None:
    next_question()

# -----------------------------
# 集計
# -----------------------------
total_correct = int(
    history_df["correct"].sum()
)

total_wrong = int(
    history_df["wrong"].sum()
)

total_answered = (
    total_correct
    + total_wrong
)

if total_answered > 0:

    accuracy = (
        total_correct
        / total_answered
        * 100
    )

else:

    accuracy = 0

# -----------------------------
# UI
# -----------------------------
st.markdown("### 📝 一問一答")

st.markdown(
    """
    <div style='font-size:13px;
                color:gray;
                margin-top:-10px;
                margin-bottom:15px;'>
    第2種放射線取扱主任者資格試験勉強アプリ
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# モード選択
# -----------------------------
mode = st.radio(
    "出題モード",
    ["通常", "重点"],
    horizontal=True,
    key="quiz_mode"
)

# -----------------------------
# 学習状況
# -----------------------------
st.markdown(
    f"""
    <div style='font-size:14px;
                color:gray;
                margin-bottom:10px;'>

    問題番号：{st.session_state.current_index} / {len(df)}
    <br>
    解答数：{total_answered} 問
    <br>
    正解：{total_correct} 問
    <br>
    不正解：{total_wrong} 問
    <br>
    正答率：{accuracy:.1f} %

    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# 問題表示
# -----------------------------
if st.session_state.current_question is not None:

    category_text = ""

    if (
        "category"
        in st.session_state.current_question
        and pd.notna(
            st.session_state.current_question[
                "category"
            ]
        )
    ):

        category_text = (
            f" <span style='font-size:14px;"
            f"color:#FFA500;"
            f"margin-left:15px;'>"
            f"📂 "
            f"{st.session_state.current_question['category']}"
            f"</span>"
        )

    st.markdown(
        f"**【問題】**{category_text}",
        unsafe_allow_html=True
    )

    st.info(
        st.session_state.current_question[
            "question"
        ]
    )

    if st.button(
        "👀 答えを見る",
        use_container_width=True
    ):

        st.session_state.show_answer = True

    # -------------------------
    # 答え表示
    # -------------------------
    if st.session_state.show_answer:

        st.markdown("**【答え】**")

        st.success(
            st.session_state.current_question[
                "answer"
            ]
        )

        if (
            "explanation"
            in st.session_state.current_question
            and pd.notna(
                st.session_state.current_question[
                    "explanation"
                ]
            )
        ):

            st.markdown(
                "**【解説】**"
            )

            st.info(
                st.session_state.current_question[
                    "explanation"
                ]
            )

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:

            st.button(
                "⭕ 正解だった",
                on_click=mark_correct,
                use_container_width=True
            )

        with col2:

            st.button(
                "❌ 間違えた",
                on_click=mark_wrong,
                use_container_width=True
            )

# -----------------------------
# 手動スキップ
# -----------------------------
st.button(
    "➡️ 次の問題へ",
    on_click=next_question,
    use_container_width=True
)
