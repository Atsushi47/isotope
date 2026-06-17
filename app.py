
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
# 学習履歴読込
# -----------------------------
def load_history():

    columns = [
        "question_id",
        "confident_correct",
        "weak_correct",
        "weak_wrong",
        "strong_wrong"
    ]

    if os.path.exists(HISTORY_FILE):

        history = pd.read_csv(HISTORY_FILE)

        # 古い形式なら作り直し
        if list(history.columns) != columns:

            history = pd.DataFrame({
                "question_id": range(len(df)),
                "confident_correct": 0,
                "weak_correct": 0,
                "weak_wrong": 0,
                "strong_wrong": 0
            })

            history.to_csv(
                HISTORY_FILE,
                index=False
            )

        # 問題追加対応
        if len(history) < len(df):

            add_df = pd.DataFrame({
                "question_id": range(
                    len(history),
                    len(df)
                ),
                "confident_correct": 0,
                "weak_correct": 0,
                "weak_wrong": 0,
                "strong_wrong": 0
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
        "confident_correct": 0,
        "weak_correct": 0,
        "weak_wrong": 0,
        "strong_wrong": 0
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

if "quiz_mode" not in st.session_state:
    st.session_state.quiz_mode = "通常"

# -----------------------------
# 重点度計算
# -----------------------------
def calculate_weight(row):

    weight = (
        1
        + row["weak_correct"] * 1
        + row["weak_wrong"] * 3
        + row["strong_wrong"] * 5
        - row["confident_correct"] * 1
    )

    return max(weight, 1)

# -----------------------------
# 次の問題
# -----------------------------
def next_question():

    if len(df) == 0:
        return

    mode = st.session_state.quiz_mode

    # 通常モード
    if mode == "通常":

        idx = random.randint(
            0,
            len(df) - 1
        )

    # 重点モード
    else:

        weights = [
            calculate_weight(
                history_df.iloc[i]
            )
            for i in range(len(df))
        ]

        idx = random.choices(
            range(len(df)),
            weights=weights,
            k=1
        )[0]

    st.session_state.current_question = df.iloc[idx]
    st.session_state.current_index = idx + 1
    st.session_state.show_answer = False

# -----------------------------
# 評価記録
# -----------------------------
def register_result(column_name):

    idx = (
        st.session_state.current_index - 1
    )

    history_df.loc[
        history_df["question_id"] == idx,
        column_name
    ] += 1

    save_history()

    next_question()

# -----------------------------
# 評価ボタン用
# -----------------------------
def mark_confident_correct():
    register_result(
        "confident_correct"
    )

def mark_weak_correct():
    register_result(
        "weak_correct"
    )

def mark_weak_wrong():
    register_result(
        "weak_wrong"
    )

def mark_strong_wrong():
    register_result(
        "strong_wrong"
    )

# -----------------------------
# 初回出題
# -----------------------------
if st.session_state.current_question is None:
    next_question()

# -----------------------------
# 統計集計
# -----------------------------
confident_correct = int(
    history_df["confident_correct"].sum()
)

weak_correct = int(
    history_df["weak_correct"].sum()
)

weak_wrong = int(
    history_df["weak_wrong"].sum()
)

strong_wrong = int(
    history_df["strong_wrong"].sum()
)

total_answered = (
    confident_correct
    + weak_correct
    + weak_wrong
    + strong_wrong
)

if total_answered > 0:

    accuracy = (
        (confident_correct + weak_correct)
        / total_answered
        * 100
    )

else:

    accuracy = 0

# -----------------------------
# UI
# -----------------------------

# タイトル
st.markdown("### 📝 一問一答")

st.markdown(
    """
    <div style='font-size:13px;
                color:gray;
                margin-top:-10px;
                margin-bottom:10px;'>
    第2種放射線取扱主任者資格試験勉強アプリ
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# モード切替
# -----------------------------
st.radio(
    "出題モード",
    ["通常", "重点"],
    horizontal=True,
    key="quiz_mode"
)

# -----------------------------
# 統計表示（スマホ向け）
# -----------------------------
st.markdown(
    f"""
    <div style="
        text-align:center;
        font-size:11px;
        color:gray;
        margin-bottom:8px;
        white-space:nowrap;
        overflow-x:auto;
    ">
        No.{st.session_state.current_index}/{len(df)}
        ｜解答:{total_answered}
        ｜😊:{confident_correct}
        ｜🙂:{weak_correct}
        ｜😓:{weak_wrong}
        ｜😭:{strong_wrong}
        ｜{accuracy:.0f}%
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

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
            f"<span style='color:#FFA500;"
            f"font-size:14px;'>"
            f"📂 "
            f"{st.session_state.current_question['category']}"
            f"</span>"
        )

    st.markdown(
        f"**【問題】** {category_text}",
        unsafe_allow_html=True
    )

    st.info(
        st.session_state.current_question[
            "question"
        ]
    )

    # -------------------------
    # 答えを見る
    # -------------------------
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

        # ---------------------
        # 解説
        # ---------------------
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

        st.divider()

        st.markdown(
            """
            <div style='font-size:13px;
                        color:gray;
                        margin-bottom:5px;'>
            理解度を選択してください
            </div>
            """,
            unsafe_allow_html=True
        )

        # ---------------------
        # 4段階評価
        # ---------------------
        col1, col2 = st.columns(2)

        with col1:

            st.button(
                "😊 自信あり",
                on_click=mark_confident_correct,
                use_container_width=True
            )

            st.button(
                "😓 あやふや不正解",
                on_click=mark_weak_wrong,
                use_container_width=True
            )

        with col2:

            st.button(
                "🙂 あやふや正解",
                on_click=mark_weak_correct,
                use_container_width=True
            )

            st.button(
                "😭 全く分からない",
                on_click=mark_strong_wrong,
                use_container_width=True
            )

# -----------------------------
# スキップ
# -----------------------------
st.button(
    "➡️ 次の問題へ",
    on_click=next_question,
    use_container_width=True
)
