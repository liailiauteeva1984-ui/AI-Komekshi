
import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import os
import asyncio
import hashlib

import edge_tts

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


# ============================================================
# 1. БЕТ
# ============================================================

st.set_page_config(
    page_title="Адаптивті AI-көмекші",
    page_icon="🧩",
    layout="centered",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. ДИЗАЙН
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(135deg, #EAF4F1, #F7FBFA);
    }

    .block-container {
        max-width: 1100px;
        background:#F9FCFB;
        padding:2rem 3rem;
        border-radius:25px;
        margin-top:20px;
        margin-bottom:30px;
    }

    .main-title {
        text-align:center;
        font-size:34px;
        font-weight:700;
        color:#294C46;
        line-height:1.35;
    }

    .subtitle {
        text-align:center;
        font-size:18px;
        color:#5A716C;
        margin:10px 0 25px 0;
    }

    .problem-box {
        text-align:center;
        font-size:52px;
        font-weight:700;
        background:#FFFFFF;
        color:#263B37;
        padding:30px;
        border:2px solid #B9D8D0;
        border-radius:22px;
        margin:15px 0 25px 0;
    }

    .step-card {
        background:#FFFFFF;
        border-left:6px solid #86B9AC;
        border-radius:12px;
        padding:16px 18px;
        margin:10px 0;
        font-size:18px;
        color:#294C46;
    }

    .break-card {
        text-align:center;
        background:#EEF8F5;
        border:2px solid #B8D9D0;
        border-radius:24px;
        padding:28px;
        margin:20px 0;
    }

    .visual-group {
        text-align:center;
        background:#FFFFFF;
        border:1px solid #D5E8E3;
        border-radius:18px;
        padding:12px;
        min-height:90px;
        margin:5px;
    }

    div.stButton > button {
        min-height:52px;
        font-size:17px;
        font-weight:600;
        background:#D7EDE7;
        color:#294C46;
        border:1px solid #A9CEC4;
        border-radius:14px;
    }

    div.stButton > button:hover {
        background:#C5E3DB;
    }

    div[data-testid="stNumberInput"] input {
        font-size:28px;
        text-align:center;
    }

    </style>
    """,
    unsafe_allow_html=True
)


os.makedirs(
    "generated_audio",
    exist_ok=True
)


# ============================================================
# 3. SESSION STATE
# ============================================================

defaults = {

    "level": 1,
    "history": [],
    "wrong_problems": [],

    "retry_mode": False,
    "retry_attempts": 0,

    "hints_count": 0,
    "feedback": "",
    "answered": False,

    "problem_id": 0,

    "show_ai": False,
    "explanation_stage": 1,

    "audio_used": 0,
    "visual_used": 0,
    "video_used": 0,

    "youtube_searches": 0,
    "approved_videos": [],

    "main_tasks_completed": 0,

    "break_mode": False,
    "last_break_at": 0,
    "break_count": 0,

    "eye_breaks": 0,
    "hand_breaks": 0,
    "movement_breaks": 0,

    "selected_break": None,

    "show_student_analysis": False,

    "visual_object": "✏️",
    "visual_object_name": "Қарындаш"
}


for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# 4. ВИЗУАЛДЫ ЗАТТАР
# ============================================================

VISUAL_OBJECTS = {

    "✏️ Қарындаш": {
        "symbol": "✏️",
        "name": "Қарындаш"
    },

    "🚗 Машина": {
        "symbol": "🚗",
        "name": "Машина"
    },

    "🌳 Ағаш": {
        "symbol": "🌳",
        "name": "Ағаш"
    },

    "⚽ Доп": {
        "symbol": "⚽",
        "name": "Доп"
    },

    "⭐ Жұлдыз": {
        "symbol": "⭐",
        "name": "Жұлдыз"
    },

    "🧸 Ойыншық": {
        "symbol": "🧸",
        "name": "Ойыншық"
    },

    "🍎 Алма": {
        "symbol": "🍎",
        "name": "Алма"
    }
}


def show_visual_objects(symbol, count):

    objects = ""

    for _ in range(count):

        objects += (
            "<span style='"
            "font-size:52px;"
            "display:inline-block;"
            "margin:5px;"
            "line-height:1.15;"
            f"'>{symbol}</span>"
        )

    st.markdown(
        f"""
        <div class="visual-group">
            {objects}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 5. EDGE-TTS
# ============================================================

VOICE_OPTIONS = {

    "👩 Aigul — әйел дауысы":
        "kk-KZ-AigulNeural",

    "👨 Daulet — ер адам дауысы":
        "kk-KZ-DauletNeural"
}


def audio_filename(text, voice):

    digest = hashlib.md5(
        (text + voice).encode("utf-8")
    ).hexdigest()

    return os.path.join(
        "generated_audio",
        f"{digest}.mp3"
    )


async def create_audio_async(
    text,
    voice,
    path
):

    communicator = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate="-12%"
    )

    await communicator.save(path)


def create_audio(text, voice):

    path = audio_filename(
        text,
        voice
    )

    if os.path.exists(path):
        return path

    try:

        asyncio.run(
            create_audio_async(
                text,
                voice,
                path
            )
        )

    except RuntimeError:

        loop = asyncio.new_event_loop()

        try:

            loop.run_until_complete(
                create_audio_async(
                    text,
                    voice,
                    path
                )
            )

        finally:

            loop.close()

    return path


# ============================================================
# 6. YOUTUBE API
# ============================================================

def get_youtube_api_key():

    try:
        return st.secrets[
            "YOUTUBE_API_KEY"
        ]

    except Exception:
        return None


YOUTUBE_API_KEY = (
    get_youtube_api_key()
)


@st.cache_data(
    ttl=3600,
    show_spinner=False
)
def search_youtube(
    query,
    api_key,
    max_results=3
):

    if not api_key:
        return []

    try:

        youtube = build(
            "youtube",
            "v3",
            developerKey=api_key
        )

        response = (
            youtube
            .search()
            .list(
                part="snippet",
                q=query,
                type="video",
                maxResults=max_results,
                safeSearch="strict",
                videoEmbeddable="true",
                regionCode="KZ",
                order="relevance"
            )
            .execute()
        )

        results = []

        for item in response.get(
            "items",
            []
        ):

            video_id = (
                item["id"].get(
                    "videoId"
                )
            )

            if not video_id:
                continue

            snippet = item[
                "snippet"
            ]

            results.append(
                {
                    "video_id":
                        video_id,

                    "title":
                        snippet.get(
                            "title",
                            ""
                        ),

                    "channel":
                        snippet.get(
                            "channelTitle",
                            ""
                        ),

                    "url":
                        (
                            "https://www.youtube.com/"
                            f"watch?v={video_id}"
                        )
                }
            )

        return results

    except HttpError:

        return []

    except Exception:

        return []


# ============================================================
# 7. ML DATASET
# ============================================================

@st.cache_data
def create_ml_dataset():

    rng = np.random.default_rng(42)

    rows = []

    for _ in range(220):

        accuracy = float(
            rng.uniform(
                0.10,
                1.00
            )
        )

        avg_time = float(
            np.clip(
                48
                - accuracy * 35
                + rng.normal(0, 5),
                5,
                55
            )
        )

        hints = int(
            np.clip(
                round(
                    (1 - accuracy) * 5
                    + rng.normal(0, 0.8)
                ),
                0,
                5
            )
        )

        retry = int(
            np.clip(
                round(
                    (1 - accuracy) * 4
                ),
                0,
                5
            )
        )

        visual = int(
            rng.integers(0, 5)
        )

        audio = int(
            rng.integers(0, 5)
        )

        video = int(
            rng.integers(0, 4)
        )


        if (
            accuracy < 0.50
            or hints >= 3
            or avg_time > 32
        ):

            target_level = 1

        elif (
            accuracy < 0.80
            or hints >= 1
            or avg_time > 18
        ):

            target_level = 2

        else:

            target_level = 3


        future_score = (
            accuracy * 100
            + 5
            - hints * 2.2
            - retry * 1.5
            + visual * 0.7
            + audio * 0.5
            + rng.normal(0, 4)
        )


        future_score = float(
            np.clip(
                future_score,
                0,
                100
            )
        )


        rows.append(
            {
                "accuracy": accuracy,
                "avg_time_sec": avg_time,
                "hints_used": hints,
                "retry_count": retry,
                "visual_used": visual,
                "audio_used": audio,
                "video_used": video,
                "target_level": target_level,
                "future_score": future_score
            }
        )

    return pd.DataFrame(rows)


ml_df = create_ml_dataset()


# ============================================================
# 8. RANDOM FOREST
# ============================================================

@st.cache_resource
def train_random_forest():

    X = ml_df[
        [
            "accuracy",
            "avg_time_sec",
            "hints_used"
        ]
    ]

    y = ml_df[
        "target_level"
    ]

    model = RandomForestClassifier(
        n_estimators=150,
        random_state=42
    )

    model.fit(X, y)

    return model


rf_model = (
    train_random_forest()
)


# ============================================================
# 9. LINEAR REGRESSION
# ============================================================

@st.cache_resource
def train_linear_regression():

    columns = [
        "accuracy",
        "avg_time_sec",
        "hints_used",
        "retry_count",
        "visual_used",
        "audio_used"
    ]

    X = ml_df[
        columns
    ]

    y = ml_df[
        "future_score"
    ]

    model = LinearRegression()

    model.fit(X, y)

    return model


reg_model = (
    train_linear_regression()
)


# ============================================================
# 10. PCA
# ============================================================

@st.cache_resource
def train_pca():

    columns = [
        "accuracy",
        "avg_time_sec",
        "hints_used",
        "retry_count",
        "visual_used",
        "audio_used",
        "video_used"
    ]

    X = ml_df[
        columns
    ]

    scaler = StandardScaler()

    scaled = scaler.fit_transform(
        X
    )

    pca = PCA(
        n_components=2
    )

    pca.fit(
        scaled
    )

    return (
        scaler,
        pca,
        columns
    )


(
    pca_scaler,
    pca_model,
    pca_columns
) = train_pca()


# ============================================================
# 11. ЕСЕП ГЕНЕРАТОРЫ
# ============================================================

def generate_problem(level):

    if level == 1:
        maximum = 5

    elif level == 2:
        maximum = 7

    else:
        maximum = 9


    operation = random.choice(
        [
            "multiply",
            "divide",
            "unknown_multiply",
            "unknown_divide"
        ]
    )

    a = random.randint(
        2,
        maximum
    )

    b = random.randint(
        2,
        maximum
    )

    product = (
        a * b
    )


    if operation == "multiply":

        return {
            "operation":
                operation,

            "a":
                a,

            "b":
                b,

            "product":
                product,

            "question":
                f"{a} × {b} = ?",

            "answer":
                product,

            "title":
                "Көбейту"
        }


    elif operation == "divide":

        return {
            "operation":
                operation,

            "a":
                a,

            "b":
                b,

            "product":
                product,

            "question":
                f"{product} ÷ {a} = ?",

            "answer":
                b,

            "title":
                "Бөлу"
        }


    elif operation == "unknown_multiply":

        return {
            "operation":
                operation,

            "a":
                a,

            "b":
                b,

            "product":
                product,

            "question":
                f"□ × {b} = {product}",

            "answer":
                a,

            "title":
                "Белгісіз көбейткіш"
        }


    return {
        "operation":
            operation,

        "a":
            a,

        "b":
            b,

        "product":
            product,

        "question":
            f"{product} ÷ □ = {b}",

        "answer":
            a,

        "title":
            "Белгісіз бөлгіш"
    }


# ============================================================
# 12. AI ТҮСІНДІРУ
# ============================================================

def explanation_steps(problem):

    a = problem["a"]
    b = problem["b"]
    product = problem["product"]
    operation = problem["operation"]


    if operation == "multiply":

        return [
            "Бұл есепте көбейту амалын орындаймыз.",

            (
                f"{a} топ бар. "
                f"Әр топта {b} заттан."
            ),

            (
                f"{a} санын {b} санына "
                "көбейтеміз."
            ),

            (
                f"{a} көбейту {b} "
                f"тең {product}."
            )
        ]


    elif operation == "divide":

        return [
            f"Барлығы {product} зат бар.",

            (
                f"Оларды {a} бірдей "
                "топқа бөлеміз."
            ),

            (
                f"{product} санын "
                f"{a} санына бөлеміз."
            ),

            f"Жауабы {b}."
        ]


    elif operation == "unknown_multiply":

        return [
            "Белгісіз компонент — көбейткіш.",

            (
                "Белгісіз көбейткішті табу үшін "
                "кері амал — бөлуді қолданамыз."
            ),

            (
                f"{product} бөлу "
                f"{b} тең {a}."
            ),

            (
                f"Тексеру: {a} көбейту "
                f"{b} тең {product}."
            )
        ]


    return [
        "Белгісіз компонент — бөлгіш.",

        (
            "Белгісіз бөлгішті табу үшін "
            "бөлінгішті бөліндінің мәніне бөлеміз."
        ),

        (
            f"{product} бөлу "
            f"{b} тең {a}."
        ),

        (
            f"Тексеру: {product} бөлу "
            f"{a} тең {b}."
        )
    ]


# ============================================================
# 13. ЕСЕПТІ ДАЙЫНДАУ
# ============================================================

def prepare_problem(problem):

    st.session_state.problem = problem

    st.session_state.problem_id += 1

    st.session_state.start_time = (
        time.time()
    )

    st.session_state.hints_count = 0

    st.session_state.feedback = ""

    st.session_state.answered = False

    st.session_state.show_ai = False

    st.session_state.explanation_stage = 1

    st.session_state.pop(
        "current_audio",
        None
    )


def new_problem():

    prepare_problem(
        generate_problem(
            st.session_state.level
        )
    )


if "problem" not in st.session_state:

    st.session_state.problem = (
        generate_problem(
            st.session_state.level
        )
    )


if "start_time" not in st.session_state:

    st.session_state.start_time = (
        time.time()
    )


# ============================================================
# 14. ML FEATURES
# ============================================================

def student_features():

    main_history = [
        x
        for x in st.session_state.history
        if not x["retry"]
    ]


    if not main_history:

        accuracy = 0.5
        avg_time = 25.0
        hints = 1.0

    else:

        recent = main_history[-5:]

        accuracy = (
            sum(
                x["correct"]
                for x in recent
            )
            / len(recent)
        )

        avg_time = (
            sum(
                x["time"]
                for x in recent
            )
            / len(recent)
        )

        hints = (
            sum(
                x["hints"]
                for x in recent
            )
            / len(recent)
        )


    return {

        "accuracy":
            float(accuracy),

        "avg_time_sec":
            float(avg_time),

        "hints_used":
            float(hints),

        "retry_count":
            float(
                st.session_state.retry_attempts
            ),

        "visual_used":
            float(
                st.session_state.visual_used
            ),

        "audio_used":
            float(
                st.session_state.audio_used
            ),

        "video_used":
            float(
                st.session_state.video_used
            )
    }


def predict_level():

    f = student_features()

    X = pd.DataFrame(
        [
            {
                "accuracy":
                    f["accuracy"],

                "avg_time_sec":
                    f["avg_time_sec"],

                "hints_used":
                    f["hints_used"]
            }
        ]
    )

    return int(
        rf_model.predict(X)[0]
    )


def predict_score():

    f = student_features()

    X = pd.DataFrame(
        [
            {
                "accuracy":
                    f["accuracy"],

                "avg_time_sec":
                    f["avg_time_sec"],

                "hints_used":
                    f["hints_used"],

                "retry_count":
                    f["retry_count"],

                "visual_used":
                    f["visual_used"],

                "audio_used":
                    f["audio_used"]
            }
        ]
    )

    score = float(
        reg_model.predict(X)[0]
    )

    return float(
        np.clip(
            score,
            0,
            100
        )
    )


def pca_profile():

    f = student_features()

    row = pd.DataFrame(
        [
            {
                column:
                    f[column]

                for column
                in pca_columns
            }
        ]
    )

    scaled = (
        pca_scaler.transform(
            row
        )
    )

    point = (
        pca_model.transform(
            scaled
        )[0]
    )

    return (
        float(point[0]),
        float(point[1])
    )


# ============================================================
# 15. SIDEBAR
# ============================================================

from grade_math_assistant import render_grade_assistant

MAIN_SECTIONS = [
    "♿ Инклюзия",
    "📘 5-сынып",
    "📗 6-сынып",
    "📙 7-сынып",
    "📕 8-сынып",
    "📓 9-сынып",
    "🎓 10-сынып",
    "🏆 11-сынып",
]

selected_main_section = st.radio(
    "Негізгі бөлімді таңдаңыз",
    MAIN_SECTIONS,
    horizontal=True,
    key="main_section_navigation",
)

if selected_main_section != "♿ Инклюзия":
    render_grade_assistant(selected_main_section)
    st.stop()

st.caption("♿ Инклюзия бөлімі: көбейту мен бөлуді меңгеруге арналған мультимодальды адаптивті AI-көмекші")

st.sidebar.header(
    "⚙️ Жеке баптау"
)


voice_label = (
    st.sidebar.selectbox(
        "🔊 Қазақша AI дауысы:",
        list(
            VOICE_OPTIONS.keys()
        )
    )
)


selected_voice = (
    VOICE_OPTIONS[
        voice_label
    ]
)


object_label = (
    st.sidebar.selectbox(
        "🎨 Қандай суретпен оқығың келеді?",
        list(
            VISUAL_OBJECTS.keys()
        )
    )
)


visual_object = (
    VISUAL_OBJECTS[
        object_label
    ]["symbol"]
)


visual_object_name = (
    VISUAL_OBJECTS[
        object_label
    ]["name"]
)


st.session_state.visual_object = (
    visual_object
)

st.session_state.visual_object_name = (
    visual_object_name
)


if YOUTUBE_API_KEY:

    st.sidebar.success(
        "🎬 Видео-көмекші дайын"
    )

else:

    st.sidebar.warning(
        "⚠️ YouTube API key табылмады"
    )


# ============================================================
# 16. HEADER
# ============================================================

st.markdown(
    """
    <div class="main-title">

    🧩 Көбейту мен бөлуді меңгеруге арналған<br>
    мультимодальды адаптивті AI-көмекші

    </div>

    <div class="subtitle">

    🌿 Асықпай үйрен • 👀 Көр •
    🔊 Тыңда • 🤖 Түсін • 🔄 Қайта орында

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 17. 5 ТАПСЫРМА -> ҮЗІЛІС
# ============================================================

if (
    st.session_state.main_tasks_completed > 0
    and
    st.session_state.main_tasks_completed % 5 == 0
    and
    st.session_state.last_break_at
    != st.session_state.main_tasks_completed
):

    st.session_state.break_mode = True


# ============================================================
# 18. СЕРГІТУ
# ============================================================

if st.session_state.break_mode:

    st.markdown(
        """
        <div class="break-card">

        <h2>🌿 Сергіту сәті</h2>

        <p style="font-size:20px;">
        Сен 5 тапсырма орындадың.<br>
        Қысқа үзіліс жасайық.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    c1, c2, c3 = (
        st.columns(3)
    )


    with c1:

        if st.button(
            "👀 Көз жаттығуы",
            use_container_width=True
        ):

            st.session_state.selected_break = "eye"
            st.session_state.eye_breaks += 1

            st.rerun()


    with c2:

        if st.button(
            "🤲 Қол жаттығуы",
            use_container_width=True
        ):

            st.session_state.selected_break = "hand"
            st.session_state.hand_breaks += 1

            st.rerun()


    with c3:

        if st.button(
            "🧘 Сергіту сәті",
            use_container_width=True
        ):

            st.session_state.selected_break = "movement"
            st.session_state.movement_breaks += 1

            st.rerun()


    break_queries = {

        "eye":
            (
                "балаларға арналған көз жаттығуы "
                "гимнастика для глаз детям"
            ),

        "hand":
            (
                "балаларға арналған қол саусақ жаттығуы "
                "пальчиковая гимнастика для детей"
            ),

        "movement":
            (
                "балаларға арналған сергіту сәті "
                "физминутка для детей"
            )
    }


    break_titles = {

        "eye":
            "👀 Көз жаттығуы",

        "hand":
            "🤲 Қол жаттығуы",

        "movement":
            "🧘 Сергіту сәті"
    }


    selected_break = (
        st.session_state.selected_break
    )


    if selected_break:

        st.subheader(
            break_titles[
                selected_break
            ]
        )


        if YOUTUBE_API_KEY:

            break_key = (
                f"break_video_"
                f"{selected_break}_"
                f"{st.session_state.main_tasks_completed}"
            )


            if break_key not in st.session_state:

                with st.spinner(
                    "🤖 AI YouTube-тан "
                    "жаттығу видеоларын іздеуде..."
                ):

                    st.session_state[
                        break_key
                    ] = search_youtube(
                        break_queries[
                            selected_break
                        ],
                        YOUTUBE_API_KEY,
                        3
                    )

                    st.session_state.youtube_searches += 1


            videos = (
                st.session_state[
                    break_key
                ]
            )


            for index, video in enumerate(
                videos
            ):

                st.markdown(
                    f"**{index + 1}. "
                    f"{video['title']}**"
                )

                st.caption(
                    f"Арна: "
                    f"{video['channel']}"
                )

                st.video(
                    video["url"]
                )


                if st.button(
                    "👩‍🏫 Осы видеоны мақұлдау",
                    key=(
                        f"approve_break_"
                        f"{selected_break}_"
                        f"{index}_"
                        f"{st.session_state.main_tasks_completed}"
                    ),
                    use_container_width=True
                ):

                    approved = (
                        video.copy()
                    )

                    approved["purpose"] = (
                        f"break_{selected_break}"
                    )


                    if approved not in (
                        st.session_state.approved_videos
                    ):

                        st.session_state.approved_videos.append(
                            approved
                        )


                    st.success(
                        "✅ Видео мақұлданды."
                    )


        else:

            st.info(
                "YouTube API key қажет."
            )


        if st.button(
            "✅ Жаттығуды аяқтадым — сабақты жалғастыру",
            type="primary",
            use_container_width=True
        ):

            st.session_state.break_count += 1

            st.session_state.last_break_at = (
                st.session_state.main_tasks_completed
            )

            st.session_state.break_mode = False
            st.session_state.selected_break = None

            new_problem()

            st.rerun()


# ============================================================
# 19. НЕГІЗГІ САБАҚ
# ============================================================

else:

    problem = (
        st.session_state.problem
    )

    a = problem["a"]
    b = problem["b"]

    product = (
        problem["product"]
    )


    # --------------------------------------------------------
    # AI ДЕҢГЕЙІ
    # --------------------------------------------------------

    if st.session_state.retry_mode:

        st.warning(
            "🔄 Қателермен жұмыс режимі"
        )

    else:

        level_names = {

            1:
                "🟢 Толық визуалды қолдау",

            2:
                "🟡 Жартылай визуалды қолдау",

            3:
                "🔵 Өздігінен орындау"
        }


        st.info(
            f"**AI режимі:** "
            f"{level_names[st.session_state.level]}"
        )


    # --------------------------------------------------------
    # ПРОГРЕСС
    # --------------------------------------------------------

    remaining = (
        5
        - (
            st.session_state.main_tasks_completed
            % 5
        )
    )


    st.caption(
        f"📝 Орындалған тапсырма: "
        f"{st.session_state.main_tasks_completed} "
        f"| 🌿 Сергітуге дейін: {remaining}"
    )


    # --------------------------------------------------------
    # ТАПСЫРМА
    # --------------------------------------------------------

    st.caption(
        f"📚 Тапсырма түрі: "
        f"{problem['title']}"
    )


    st.markdown(
        f"""
        <div class="problem-box">

        {problem["question"]}

        </div>
        """,
        unsafe_allow_html=True
    )


    display_level = (

        1

        if st.session_state.retry_mode

        else st.session_state.level
    )


    # ========================================================
    # ВИЗУАЛДЫ ҚОЛДАУ
    # ========================================================

    if display_level == 1:

        st.subheader(
            "🖼️ Суретпен ойланып көр"
        )


        st.caption(
            f"🎨 Сен таңдаған сурет: "
            f"{visual_object} {visual_object_name}"
        )


        if problem["operation"] == "multiply":

            st.write(
                f"**{a} топ бар. "
                f"Әр топта {b} заттан.**"
            )

            cols = st.columns(
                a
            )

            for col in cols:

                with col:

                    show_visual_objects(
                        visual_object,
                        b
                    )


        elif problem["operation"] == "divide":

            st.write(
                f"**{product} затты "
                f"{a} бірдей топқа бөл.**"
            )

            cols = st.columns(
                a
            )

            for col in cols:

                with col:

                    show_visual_objects(
                        visual_object,
                        b
                    )


        elif problem["operation"] == "unknown_multiply":

            st.write(
                f"**{product} зат бар. "
                f"Әр топта {b} заттан. "
                f"Неше топ бар?**"
            )

            cols = st.columns(
                a
            )

            for col in cols:

                with col:

                    show_visual_objects(
                        visual_object,
                        b
                    )


        else:

            st.write(
                f"**{product} затты топтарға бөл. "
                f"Әр топта {b} зат болуы керек.**"
            )

            cols = st.columns(
                a
            )

            for col in cols:

                with col:

                    show_visual_objects(
                        visual_object,
                        b
                    )


        st.session_state.visual_used += 0


    # ========================================================
    # 2-ДЕҢГЕЙ
    # ========================================================

    elif display_level == 2:

        st.subheader(
            "🔲 Тор арқылы ойланып көр"
        )


        grid = (
            "<div style='"
            "display:grid;"
            f"grid-template-columns:repeat({b},48px);"
            "gap:8px;"
            "justify-content:center;"
            "margin:20px;'>"
        )


        for _ in range(product):

            grid += """
            <div style="
                width:48px;
                height:48px;
                background:#CFE7E1;
                border:2px solid #76A99C;
                border-radius:9px;">
            </div>
            """


        grid += "</div>"


        st.markdown(
            grid,
            unsafe_allow_html=True
        )


    # ========================================================
    # 3-ДЕҢГЕЙ
    # ========================================================

    else:

        st.subheader(
            "🧠 Есепті өзің орында"
        )


    # ========================================================
    # ЖАУАП
    # ========================================================

    st.divider()


    answer_key = (
        f"answer_"
        f"{st.session_state.problem_id}"
    )


    user_answer = st.number_input(
        "✏️ Жауабың:",
        min_value=0,
        max_value=100,
        value=0,
        step=1,
        key=answer_key,
        disabled=st.session_state.answered
    )


    # ========================================================
    # КӨМЕК
    # ========================================================

    if not st.session_state.answered:

        if st.button(
            "💡 Көмек алу",
            use_container_width=True
        ):

            st.session_state.hints_count += 1

            st.info(
                "💡 Көбейту мен бөлу — "
                "бір-біріне кері амалдар."
            )


    # ========================================================
    # ТЕКСЕРУ
    # ========================================================

    if st.button(
        "✅ Жауапты тексеру",
        use_container_width=True,
        disabled=st.session_state.answered
    ):

        elapsed = (
            time.time()
            - st.session_state.start_time
        )


        correct = (
            int(user_answer)
            ==
            int(problem["answer"])
        )


        st.session_state.answered = True


        if correct:

            st.session_state.feedback = (
                "🎉 Жарайсың! "
                "Жауабың дұрыс!"
            )


            if st.session_state.retry_mode:

                st.session_state.wrong_problems = [
                    x
                    for x
                    in st.session_state.wrong_problems
                    if x["question"]
                    != problem["question"]
                ]


        else:

            st.session_state.feedback = (
                "🌱 Жауап дұрыс емес. "
                "AI-көмекшімен бірге түсінейік."
            )


            exists = any(
                x["question"]
                == problem["question"]

                for x
                in st.session_state.wrong_problems
            )


            if not exists:

                st.session_state.wrong_problems.append(
                    problem.copy()
                )


        if not st.session_state.retry_mode:

            st.session_state.main_tasks_completed += 1


        st.session_state.history.append(
            {
                "question":
                    problem["question"],

                "type":
                    problem["title"],

                "student_answer":
                    int(user_answer),

                "correct_answer":
                    int(problem["answer"]),

                "correct":
                    1 if correct else 0,

                "time":
                    round(
                        elapsed,
                        1
                    ),

                "hints":
                    st.session_state.hints_count,

                "level":
                    display_level,

                "retry":
                    st.session_state.retry_mode,

                "visual":
                    visual_object_name
            }
        )


        if len(
            st.session_state.history
        ) >= 3:

            st.session_state.level = (
                predict_level()
            )


        st.rerun()


    # ========================================================
    # FEEDBACK
    # ========================================================

    last_correct = None


    if st.session_state.history:

        last_correct = (
            st.session_state
            .history[-1]["correct"]
        )


    if st.session_state.feedback:

        if last_correct == 1:

            st.success(
                st.session_state.feedback
            )

        else:

            st.info(
                st.session_state.feedback
            )


    # ========================================================
    # ҚАТЕНІ ТҮСІНДІРУ
    # ========================================================

    if (
        st.session_state.answered
        and
        last_correct == 0
    ):

        if st.button(
            "🤖 Қатені AI-көмекшімен түсіндіру",
            type="primary",
            use_container_width=True
        ):

            st.session_state.show_ai = True

            st.rerun()


    if (
        st.session_state.show_ai
        and
        last_correct == 0
    ):

        steps = explanation_steps(
            problem
        )

        full_text = " ".join(
            steps
        )


        st.subheader(
            "🤖 AI-көмекшінің түсіндіруі"
        )


        tabs = st.tabs(
            [
                "👣 4 қадам",
                "🔊 Қазақша дауыс",
                "🎬 YouTube видео"
            ]
        )


        # ----------------------------------------------------
        # 4 ҚАДАМ
        # ----------------------------------------------------

        with tabs[0]:

            stage = (
                st.session_state.explanation_stage
            )


            for i in range(stage):

                st.markdown(
                    f"""
                    <div class="step-card">

                    <b>{i + 1}-қадам</b><br>

                    {steps[i]}

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            if stage < 4:

                if st.button(
                    "➡️ Келесі қадам",
                    key="next_step",
                    use_container_width=True
                ):

                    st.session_state.explanation_stage += 1

                    st.rerun()


        # ----------------------------------------------------
        # ҚАЗАҚША ДАУЫС
        # ----------------------------------------------------

        with tabs[1]:

            st.write(
                f"🔊 **{voice_label}**"
            )


            if st.button(
                "🎙️ Қазақша түсіндіруді дайындау",
                key=(
                    f"audio_"
                    f"{st.session_state.problem_id}"
                ),
                use_container_width=True
            ):

                try:

                    with st.spinner(
                        "Қазақша дауыс дайындалуда..."
                    ):

                        path = create_audio(
                            full_text,
                            selected_voice
                        )


                    st.session_state.current_audio = path

                    st.session_state.audio_used += 1


                except Exception as error:

                    st.error(
                        f"Дыбыс қатесі: {error}"
                    )


            if (
                "current_audio"
                in st.session_state
                and
                os.path.exists(
                    st.session_state.current_audio
                )
            ):

                st.audio(
                    st.session_state.current_audio,
                    format="audio/mp3"
                )

                st.caption(
                    "▶️ Ойнату • ⏸️ Пауза • "
                    "уақыт жолағымен алға/артқа өту"
                )


        # ----------------------------------------------------
        # YOUTUBE
        # ----------------------------------------------------

        with tabs[2]:

            lesson_queries = {

                "multiply":
                    (
                        "көбейту амалы математика "
                        "балаларға түсіндіру"
                    ),

                "divide":
                    (
                        "бөлу амалы математика "
                        "балаларға түсіндіру"
                    ),

                "unknown_multiply":
                    (
                        "белгісіз көбейткішті табу "
                        "математика"
                    ),

                "unknown_divide":
                    (
                        "белгісіз бөлгішті табу "
                        "математика"
                    )
            }


            if YOUTUBE_API_KEY:

                result_key = (
                    f"lesson_results_"
                    f"{st.session_state.problem_id}"
                )


                if result_key not in st.session_state:

                    with st.spinner(
                        "🤖 AI YouTube-тан "
                        "сәйкес видеоларды іздеуде..."
                    ):

                        st.session_state[
                            result_key
                        ] = search_youtube(
                            lesson_queries[
                                problem["operation"]
                            ],
                            YOUTUBE_API_KEY,
                            3
                        )

                        st.session_state.youtube_searches += 1


                videos = (
                    st.session_state[
                        result_key
                    ]
                )


                if videos:

                    for index, video in enumerate(
                        videos
                    ):

                        st.markdown(
                            f"**{index + 1}. "
                            f"{video['title']}**"
                        )

                        st.caption(
                            f"Арна: "
                            f"{video['channel']}"
                        )

                        st.video(
                            video["url"]
                        )


                        if st.button(
                            "👩‍🏫 Осы видеоны мақұлдау",
                            key=(
                                f"approve_lesson_"
                                f"{st.session_state.problem_id}_"
                                f"{index}"
                            ),
                            use_container_width=True
                        ):

                            approved = (
                                video.copy()
                            )

                            approved["purpose"] = (
                                problem["operation"]
                            )


                            if approved not in (
                                st.session_state.approved_videos
                            ):

                                st.session_state.approved_videos.append(
                                    approved
                                )


                            st.session_state.video_used += 1


                            st.success(
                                "✅ Видео мақұлданды."
                            )


                else:

                    st.warning(
                        "Сәйкес видео табылмады."
                    )


            else:

                st.warning(
                    "YouTube API key қажет."
                )


        # ----------------------------------------------------
        # ҚАЙТА ОРЫНДАУ
        # ----------------------------------------------------

        if st.button(
            "🔄 Есепті қайта орындау",
            use_container_width=True
        ):

            st.session_state.retry_mode = True

            st.session_state.retry_attempts += 1

            prepare_problem(
                problem.copy()
            )

            st.rerun()


    # ========================================================
    # КЕЛЕСІ ЕСЕП
    # ========================================================

    if (
        st.session_state.answered
        and
        last_correct == 1
    ):

        st.divider()


        if st.session_state.retry_mode:

            if st.session_state.wrong_problems:

                if st.button(
                    "➡️ Келесі қате есеп",
                    use_container_width=True
                ):

                    prepare_problem(
                        st.session_state
                        .wrong_problems[0]
                        .copy()
                    )

                    st.rerun()


            else:

                st.success(
                    "🏆 Барлық қате есептер "
                    "дұрыс орындалды!"
                )


                if st.button(
                    "🌿 Негізгі жаттығуға оралу",
                    use_container_width=True
                ):

                    st.session_state.retry_mode = False

                    new_problem()

                    st.rerun()


        else:

            if (
                st.session_state.main_tasks_completed
                % 5
                == 0
            ):

                if st.button(
                    "🌿 Сергіту сәтіне өту",
                    type="primary",
                    use_container_width=True
                ):

                    st.session_state.break_mode = True

                    st.rerun()


            else:

                if st.button(
                    "➡️ Келесі есеп",
                    use_container_width=True
                ):

                    new_problem()

                    st.rerun()


    # ========================================================
    # ҚАТЕЛЕРМЕН ЖҰМЫС
    # ========================================================

    if (
        st.session_state.wrong_problems
        and
        not st.session_state.retry_mode
        and
        not (
            st.session_state.answered
            and
            last_correct == 0
        )
    ):

        st.subheader(
            "🌱 Қателермен жұмыс"
        )

        st.info(
            f"Қайта орындауға "
            f"{len(st.session_state.wrong_problems)} есеп бар."
        )


        if st.button(
            "🔄 Қате есептерді қайта орындау",
            use_container_width=True
        ):

            st.session_state.retry_mode = True

            prepare_problem(
                st.session_state
                .wrong_problems[0]
                .copy()
            )

            st.rerun()


# ============================================================
# 20. ОҚУШЫНЫҢ НӘТИЖЕСІ
# ============================================================

st.divider()

st.markdown(
    "## 📊 Менің нәтижем"
)


if st.button(
    "📊 Нәтижемді көру",
    key="student_result_button",
    type="primary",
    use_container_width=True
):

    st.session_state.show_student_analysis = (
        not st.session_state.show_student_analysis
    )


if st.session_state.show_student_analysis:

    if not st.session_state.history:

        st.info(
            "📝 Алдымен бірнеше тапсырма орында."
        )

    else:

        student_df = pd.DataFrame(
            st.session_state.history
        )


        main_df = (
            student_df[
                student_df["retry"]
                == False
            ]
            .copy()
        )


        total_tasks = len(
            main_df
        )


        if total_tasks:

            correct_tasks = int(
                main_df[
                    "correct"
                ].sum()
            )

            wrong_tasks = (
                total_tasks
                - correct_tasks
            )

            percentage = (
                correct_tasks
                / total_tasks
                * 100
            )

            avg_student_time = float(
                main_df[
                    "time"
                ].mean()
            )

        else:

            correct_tasks = 0
            wrong_tasks = 0
            percentage = 0
            avg_student_time = 0


        c1, c2, c3 = (
            st.columns(3)
        )


        with c1:

            st.metric(
                "📝 Тапсырма",
                total_tasks
            )


        with c2:

            st.metric(
                "✅ Дұрыс",
                correct_tasks
            )


        with c3:

            st.metric(
                "⭐ Нәтиже",
                f"{percentage:.0f}%"
            )


        st.markdown(
            "### 🎯 Менің прогресім"
        )


        st.progress(
            max(
                0.0,
                min(
                    percentage / 100,
                    1.0
                )
            )
        )


        result_table = pd.DataFrame(
            {
                "Көрсеткіш": [
                    "📝 Орындаған тапсырмам",
                    "✅ Дұрыс жауап",
                    "❌ Қате жауап",
                    "⭐ Нәтижем",
                    "⏱ Орташа уақытым",
                    "🔄 Қайта орындау керек",
                    "🌿 Сергіту сәті"
                ],

                "Нәтиже": [
                    total_tasks,
                    correct_tasks,
                    wrong_tasks,
                    f"{percentage:.0f}%",
                    f"{avg_student_time:.1f} сек",
                    len(
                        st.session_state.wrong_problems
                    ),
                    st.session_state.break_count
                ]
            }
        )


        st.dataframe(
            result_table,
            use_container_width=True,
            hide_index=True
        )


        if percentage >= 90:

            st.success(
                "🏆 Өте жақсы! Керемет нәтиже!"
            )

        elif percentage >= 75:

            st.success(
                "🌟 Жарайсың! Осылай жалғастыр!"
            )

        elif percentage >= 60:

            st.info(
                "🌱 Жақсы! Тағы біраз жаттығайық."
            )

        else:

            st.info(
                "💚 Асықпа. "
                "Қате есептерді қайта орындап көрейік."
            )


        if not main_df.empty:

            st.markdown(
                "### 🧮 Тақырыптар бойынша нәтижем"
            )


            topic_result = (
                main_df
                .groupby("type")
                .agg(
                    Тапсырма=(
                        "correct",
                        "count"
                    ),

                    Дұрыс=(
                        "correct",
                        "sum"
                    )
                )
                .reset_index()
            )


            topic_result["Қате"] = (
                topic_result["Тапсырма"]
                - topic_result["Дұрыс"]
            )


            topic_result["Нәтиже"] = (
                topic_result["Дұрыс"]
                / topic_result["Тапсырма"]
                * 100
            ).round(0)


            topic_result["Нәтиже"] = (
                topic_result["Нәтиже"]
                .astype(int)
                .astype(str)
                + "%"
            )


            topic_result.columns = [
                "Тақырып",
                "Тапсырма",
                "Дұрыс",
                "Қате",
                "Нәтиже"
            ]


            st.dataframe(
                topic_result,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# 21. МҰҒАЛІМ АНАЛИТИКАСЫ
# ============================================================

with st.expander(
    "👩‍🏫 Мұғалімге арналған ақпарат"
):

    st.subheader(
        "📊 Оқушының оқу аналитикасы"
    )


    if st.session_state.history:

        teacher_df = pd.DataFrame(
            st.session_state.history
        )

        total_all = len(
            teacher_df
        )

        correct_all = int(
            teacher_df[
                "correct"
            ].sum()
        )

        wrong_all = (
            total_all
            - correct_all
        )

        accuracy_percent = (
            correct_all
            / total_all
            * 100
        )

        avg_time = float(
            teacher_df[
                "time"
            ].mean()
        )

        total_hints = int(
            teacher_df[
                "hints"
            ].sum()
        )

        retry_count = int(
            teacher_df[
                "retry"
            ].sum()
        )


    else:

        teacher_df = (
            pd.DataFrame()
        )

        total_all = 0
        correct_all = 0
        wrong_all = 0
        accuracy_percent = 0
        avg_time = 0
        total_hints = 0
        retry_count = 0


    # --------------------------------------------------------
    # ӘРЕКЕТ
    # --------------------------------------------------------

    activity_table = pd.DataFrame(
        {
            "Көрсеткіш": [
                "📝 Орындалған тапсырма",
                "🌿 Сергіту үзілісі",
                "👀 Көз жаттығуы",
                "🤲 Қол жаттығуы",
                "🧘 Сергіту сәті",
                "🔊 Дыбыстық көмек",
                "🎬 Видео түсіндіру",
                "🔄 Қайта орындалған есеп",
                "🎨 Таңдаған сурет"
            ],

            "Нәтиже": [
                st.session_state.main_tasks_completed,
                st.session_state.break_count,
                st.session_state.eye_breaks,
                st.session_state.hand_breaks,
                st.session_state.movement_breaks,
                st.session_state.audio_used,
                st.session_state.video_used,
                retry_count,
                (
                    f"{visual_object} "
                    f"{visual_object_name}"
                )
            ]
        }
    )


    st.dataframe(
        activity_table,
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # ОҚУ НӘТИЖЕСІ
    # --------------------------------------------------------

    st.markdown(
        "### 🎯 Оқу нәтижесі"
    )


    result_table_teacher = (
        pd.DataFrame(
            {
                "Көрсеткіш": [
                    "✅ Дұрыс жауап",
                    "❌ Қате жауап",
                    "🎯 Жалпы нәтиже",
                    "⏱ Орташа уақыт",
                    "💡 Көмек қолдану",
                    "📌 Қайта қаралатын есеп"
                ],

                "Нәтиже": [
                    correct_all,
                    wrong_all,
                    f"{accuracy_percent:.0f}%",
                    f"{avg_time:.1f} сек",
                    total_hints,
                    len(
                        st.session_state.wrong_problems
                    )
                ]
            }
        )
    )


    st.dataframe(
        result_table_teacher,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # ML ФОНДА ЖҰМЫС ІСТЕЙДІ
    # ========================================================

    rf_level = predict_level()

    future_score = predict_score()

    pc1, pc2 = pca_profile()


    if accuracy_percent >= 80:

        mastery = (
            "🌟 Жоғары"
        )

    elif accuracy_percent >= 60:

        mastery = (
            "🌱 Орташа"
        )

    else:

        mastery = (
            "🌿 Қосымша қолдау қажет"
        )


    if rf_level == 1:

        support = (
            "🖼️ Толық визуалды және "
            "қадамдық қолдау"
        )

    elif rf_level == 2:

        support = (
            "🔲 Жартылай визуалды қолдау"
        )

    else:

        support = (
            "🧠 Өздігінен орындауға "
            "көбірек мүмкіндік беру"
        )


    if (
        future_score
        > accuracy_percent + 5
    ):

        dynamics = (
            "📈 Нәтиже жоғарылау бағытында"
        )

    elif (
        future_score
        < accuracy_percent - 5
    ):

        dynamics = (
            "📉 Қосымша қолдау қажет"
        )

    else:

        dynamics = (
            "➡️ Нәтиже тұрақты"
        )


    difficult_topic = (
        "Әзірге анықталған жоқ"
    )


    if not teacher_df.empty:

        topic_stats = (
            teacher_df
            .groupby("type")[
                "correct"
            ]
            .mean()
        )

        if len(topic_stats) > 0:

            difficult_topic = (
                topic_stats.idxmin()
            )


    support_usage = {

        "🔊 Қазақша дауыстық түсіндіру":
            st.session_state.audio_used,

        "🖼️ Визуалды түсіндіру":
            st.session_state.visual_used,

        "🎬 Видео түсіндіру":
            st.session_state.video_used
    }


    if sum(
        support_usage.values()
    ) > 0:

        preferred_support = max(
            support_usage,
            key=support_usage.get
        )

    else:

        preferred_support = (
            "Әзірге анықталған жоқ"
        )


    if total_all == 0:

        recommendation = (
            "Қорытынды жасау үшін "
            "бірнеше тапсырма орындау қажет."
        )

    elif accuracy_percent >= 80:

        recommendation = (
            "Қолдауды біртіндеп азайтып, "
            "өздігінен орындауға мүмкіндік беру."
        )

    elif accuracy_percent >= 60:

        recommendation = (
            f"«{difficult_topic}» тақырыбы бойынша "
            "қосымша жаттығу ұйымдастыру."
        )

    else:

        recommendation = (
            f"«{difficult_topic}» тақырыбын "
            "визуалды, қазақша дауыстық және "
            "қадамдық түсіндіру арқылы қайта бекіту."
        )


    st.markdown(
        "### 🤖 AI-дың оқушы бойынша ұсынысы"
    )


    ai_table = pd.DataFrame(
        {
            "Көрсеткіш": [
                "🎯 Меңгеру деңгейі",
                "🧩 Ұсынылатын қолдау",
                "📈 Оқу динамикасы",
                "⚠️ Қиындық туғызған тақырып",
                "💡 Тиімді көмек түрі",
                "🔄 Қайта орындау қажет",
                "👩‍🏫 Мұғалімге ұсыныс"
            ],

            "AI қорытындысы": [
                mastery,
                support,
                dynamics,
                difficult_topic,
                preferred_support,
                (
                    f"{len(st.session_state.wrong_problems)} "
                    "тапсырма"
                ),
                recommendation
            ]
        }
    )


    st.dataframe(
        ai_table,
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # ТАҚЫРЫП БОЙЫНША
    # --------------------------------------------------------

    st.markdown(
        "### 🧮 Тапсырма түрлері бойынша анализ"
    )


    if not teacher_df.empty:

        type_analysis = (
            teacher_df
            .groupby("type")
            .agg(
                Орындалған=(
                    "correct",
                    "count"
                ),

                Дұрыс=(
                    "correct",
                    "sum"
                ),

                Орташа_уақыт=(
                    "time",
                    "mean"
                ),

                Көмек=(
                    "hints",
                    "sum"
                )
            )
            .reset_index()
        )


        type_analysis["Қате"] = (
            type_analysis["Орындалған"]
            - type_analysis["Дұрыс"]
        )


        type_analysis[
            "Нәтиже (%)"
        ] = (
            type_analysis["Дұрыс"]
            / type_analysis["Орындалған"]
            * 100
        ).round(0)


        type_analysis[
            "Орташа_уақыт"
        ] = (
            type_analysis[
                "Орташа_уақыт"
            ].round(1)
        )


        type_analysis = (
            type_analysis[
                [
                    "type",
                    "Орындалған",
                    "Дұрыс",
                    "Қате",
                    "Нәтиже (%)",
                    "Орташа_уақыт",
                    "Көмек"
                ]
            ]
        )


        type_analysis.columns = [
            "Тапсырма түрі",
            "Орындалған",
            "Дұрыс",
            "Қате",
            "Нәтиже (%)",
            "Орташа уақыт (сек)",
            "Көмек саны"
        ]


        st.dataframe(
            type_analysis,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# 22. БАСҚАРУ
# ============================================================

with st.expander(
    "⚙️ Бағдарламаны басқару"
):

    if st.button(
        "🔄 Барлық нәтижені өшіру және қайта бастау",
        use_container_width=True
    ):

        for key in list(
            st.session_state.keys()
        ):

            del st.session_state[
                key
            ]

        st.rerun()


# ============================================================
# 23. FOOTER
# ============================================================

st.divider()


st.markdown(
    """
    <div style="
        text-align:center;
        color:#71827E;
        font-size:15px;
        padding:12px;
    ">

    🌿 Асықпай үйрен •
    👀 Көр •
    🔊 Тыңда •
    🤖 Түсін •
    🔄 Қайта орында

    </div>
    """,
    unsafe_allow_html=True
)
