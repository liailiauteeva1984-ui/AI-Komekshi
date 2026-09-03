import asyncio
import io
import random
import time
from dataclasses import dataclass

import numpy as np
import pandas as pd
import requests
import streamlit as st
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

try:
    import edge_tts
except ImportError:
    edge_tts = None


st.set_page_config(page_title="Алгебра және анализ бастамалары — AI-көмекші", page_icon="📘", layout="wide")


TOPICS = {
    "Функция және оның қасиеттері": [
        ("f(x)=2x−3 болса, f(4) мәнін табыңыз.", "5", "x орнына 4 қойыңыз: 2·4−3."),
        ("y=x²−4 функциясының нөлдерін табыңыз. Жауапты үтірмен жазыңыз.", "-2,2", "x²−4=0, яғни x²=4."),
        ("y=3x+1 функциясының өсу коэффициентін табыңыз.", "3", "y=kx+b формуласындағы k санын табыңыз."),
    ],
    "Квадрат теңдеулер мен теңсіздіктер": [
        ("x²−5x+6=0 теңдеуінің түбірлерін үтірмен жазыңыз.", "2,3", "Көбейтіндісі 6, қосындысы 5 болатын сандарды табыңыз."),
        ("x²−9=0 теңдеуінің оң түбірін табыңыз.", "3", "Квадраттар айырымы формуласын қолданыңыз."),
        ("x²−4<0 теңсіздігінің бүтін шешімдерінің санын табыңыз.", "3", "−2<x<2 аралығындағы бүтін сандарды санаңыз."),
    ],
    "Тригонометриялық функциялар": [
        ("sin 30° мәнін табыңыз.", "0.5", "Бірлік шеңбердегі негізгі мәнді еске түсіріңіз."),
        ("cos 60° мәнін табыңыз.", "0.5", "30°–60°–90° үшбұрышын пайдаланыңыз."),
        ("tan 45° мәнін табыңыз.", "1", "tan α=sin α/cos α."),
    ],
    "Тригонометриялық теңдеулер": [
        ("0°≤x≤360° аралығында sin x=0 теңдеуінің неше шешімі бар?", "3", "sin x нөл болатын 0°, 180°, 360° нүктелерін белгілеңіз."),
        ("0°≤x<360° аралығында cos x=1 теңдеуінің шешімін табыңыз.", "0", "Бірлік шеңбердегі (1;0) нүктесін қараңыз."),
        ("0°≤x<360° аралығында tan x=1 теңдеуінің неше шешімі бар?", "2", "Периоды 180° екенін қолданыңыз."),
    ],
    "Көрсеткіштік функция және теңдеулер": [
        ("2ˣ=32 теңдеуін шешіңіз.", "5", "32 санын 2 санының дәрежесі түрінде жазыңыз."),
        ("3ˣ=1/9 теңдеуін шешіңіз.", "-2", "1/9=3⁻²."),
        ("5⁰+2³ өрнегінің мәнін табыңыз.", "9", "Нөлінші дәреже 1-ге тең."),
    ],
    "Логарифм және логарифмдік теңдеулер": [
        ("log₂8 мәнін табыңыз.", "3", "2-нің қандай дәрежесі 8-ге тең?"),
        ("log₃(1/9) мәнін табыңыз.", "-2", "1/9=3⁻²."),
        ("log₅x=2 теңдеуін шешіңіз.", "25", "Логарифм анықтамасы бойынша x=5²."),
    ],
    "Туынды және оның қолданылуы": [
        ("f(x)=x³ функциясының туындысын x=2 нүктесінде табыңыз.", "12", "f′(x)=3x² формуласын қолданыңыз."),
        ("f(x)=5x²−3x функциясының f′(1) мәнін табыңыз.", "7", "Алдымен f′(x)=10x−3."),
        ("s(t)=t²+2t болса, t=3 мезетіндегі жылдамдықты табыңыз.", "8", "Жылдамдық v(t)=s′(t)."),
    ],
    "Комбинаторика және ықтималдық": [
        ("5 түрлі кітаптың ішінен 2 кітапты таңдаудың неше тәсілі бар?", "10", "C(5,2)=5!/(2!·3!)."),
        ("Әділ тиынды бір рет лақтырғанда елтаңба түсу ықтималдығын жазыңыз.", "0.5", "Қолайлы жағдай саны 1, барлық жағдай саны 2."),
        ("Кубикті лақтырғанда жұп сан түсу ықтималдығын жазыңыз.", "0.5", "Жұп нәтижелер: 2, 4, 6."),
    ],
}

LEVEL_NAMES = {1: "Қолдауы жоғары", 2: "Орташа", 3: "Күрделі"}

# Кітап мазмұнын толық қамтитын кеңейтілген тапсырмалар жинағы
from curriculum import TOPICS


@dataclass
class Question:
    topic: str
    text: str
    answer: str
    hint: str


def normalize_answer(value):
    return str(value).strip().lower().replace(" ", "").replace(";", ",").replace("−", "-")


def is_correct(given, expected):
    a, b = normalize_answer(given), normalize_answer(expected)
    try:
        return abs(float(a.replace(",", ".")) - float(b.replace(",", "."))) < 1e-7
    except ValueError:
        return a == b


def make_question(topic):
    text, answer, hint = random.choice(TOPICS[topic])
    return Question(topic, text, answer, hint)


def train_models():
    X = np.array([
        [0.25, 80, 3], [0.40, 65, 3], [0.50, 55, 2],
        [0.60, 45, 2], [0.70, 38, 1], [0.78, 32, 1],
        [0.85, 27, 0], [0.92, 22, 0], [1.00, 18, 0],
    ])
    y = np.array([1, 1, 1, 2, 2, 2, 3, 3, 3])
    forest = RandomForestClassifier(n_estimators=100, random_state=42).fit(X, y)
    scaler = StandardScaler().fit(X)
    pca = PCA(n_components=2, random_state=42).fit(scaler.transform(X))
    trend = LinearRegression().fit(np.arange(len(y)).reshape(-1, 1), X[:, 0])
    return forest, scaler, pca, trend


@st.cache_resource
def models():
    return train_models()


def predicted_level():
    if not st.session_state.history:
        return 2
    df = pd.DataFrame(st.session_state.history)
    accuracy = df["correct"].mean()
    avg_time = df["time_sec"].mean()
    hints = df["hint_used"].mean()
    forest, _, _, _ = models()
    return int(forest.predict([[accuracy, avg_time, hints]])[0])


async def _speech_bytes(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    data = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            data.extend(chunk["data"])
    return bytes(data)


@st.cache_data(show_spinner=False)
def speech(text, voice):
    if edge_tts is None:
        return None
    try:
        return asyncio.run(_speech_bytes(text, voice))
    except Exception:
        return None


def youtube_search(query):
    try:
        key = st.secrets.get("YOUTUBE_API_KEY", "")
    except Exception:
        key = ""
    if not key:
        return []
    try:
        response = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={"part": "snippet", "q": query, "type": "video", "maxResults": 3, "key": key, "relevanceLanguage": "kk"},
            timeout=8,
        )
        response.raise_for_status()
        return [(i["snippet"]["title"], f"https://www.youtube.com/watch?v={i['id']['videoId']}") for i in response.json().get("items", [])]
    except Exception:
        return []


def init_state():
    defaults = {
        "history": [], "question": None, "started": time.time(), "hint_used": False,
        "message": "", "student": "", "avatar": "📘", "answered": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#f4f8ff,#eefbf4);}
.hero {padding:22px;border-radius:22px;background:linear-gradient(120deg,#3157a5,#4a9d75);color:white;margin-bottom:16px}
.hero h1 {margin:0;font-size:2.1rem}.hero p {margin:6px 0 0}
.card {background:white;padding:18px;border-radius:16px;border:1px solid #dce7f5;box-shadow:0 4px 16px #3157a512}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>📘 Алгебра және анализ бастамалары: адаптивті AI-көмекші</h1><p>Кітаптың барлық бөлімі • қазақша дыбыс • бейімделетін тапсырма • мұғалім аналитикасы</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("👤 Оқушы профилі")
    st.session_state.student = st.text_input("Оқушының аты", st.session_state.student, placeholder="Атыңызды жазыңыз")
    uploaded = st.file_uploader("Өз суретіңізді таңдаңыз", type=["png", "jpg", "jpeg"])
    if uploaded:
        st.image(uploaded, width=130)
    else:
        st.markdown(f"## {st.session_state.avatar}")
    st.session_state.avatar = st.selectbox("Белгіше", ["📘", "🧑‍🎓", "👩‍🎓", "🧠", "🚀"])
    voice_label = st.radio("Дауыс", ["Айгүл", "Дәулет"], horizontal=True)
    voice = "kk-KZ-AigulNeural" if voice_label == "Айгүл" else "kk-KZ-DauletNeural"
    topic = st.selectbox("Бөлімді таңдаңыз", list(TOPICS))
    level = predicted_level()
    st.info(f"🤖 AI ұсынған деңгей: **{LEVEL_NAMES[level]}**")
    try:
        has_key = bool(st.secrets.get("YOUTUBE_API_KEY", ""))
    except Exception:
        has_key = False
    st.success("🎬 Видео-көмекші дайын") if has_key else st.warning("YouTube API key табылмады")

tab1, tab2, tab3 = st.tabs(["🧩 Тапсырма", "📊 Менің нәтижем", "👩‍🏫 Мұғалім аналитикасы"])

with tab1:
    if st.session_state.question is None or st.session_state.question.topic != topic:
        st.session_state.question = make_question(topic)
        st.session_state.started = time.time()
        st.session_state.hint_used = False
        st.session_state.answered = False
        st.session_state.message = ""
    q = st.session_state.question
    st.subheader(q.topic)
    st.markdown(f'<div class="card"><h3>{q.text}</h3></div>', unsafe_allow_html=True)
    cols = st.columns([2, 1, 1])
    answer = cols[0].text_input("Жауабыңыз", key=f"answer_{len(st.session_state.history)}")
    if cols[1].button("💡 Көмек", use_container_width=True):
        st.session_state.hint_used = True
        st.info(q.hint)
    if cols[2].button("🔊 Тыңдау", use_container_width=True):
        audio = speech(q.text, voice)
        if audio:
            st.audio(io.BytesIO(audio), format="audio/mp3")
        else:
            st.warning("Дыбысты қазір жүктеу мүмкін болмады.")
    if st.button("✅ Жауапты тексеру", type="primary", disabled=st.session_state.answered):
        if not answer.strip():
            st.warning("Алдымен жауап енгізіңіз.")
        else:
            correct = is_correct(answer, q.answer)
            elapsed = round(time.time() - st.session_state.started, 1)
            st.session_state.history.append({
                "student": st.session_state.student or "Оқушы", "topic": q.topic,
                "question": q.text, "answer": answer, "correct": correct,
                "time_sec": elapsed, "hint_used": int(st.session_state.hint_used),
            })
            st.session_state.answered = True
            st.session_state.message = "Дұрыс! Жарайсың! 🎉" if correct else f"Қайта ойланып көріңіз. Дұрыс жауап: {q.answer}. {q.hint}"
            st.rerun()
    if st.session_state.message:
        (st.success if st.session_state.history[-1]["correct"] else st.error)(st.session_state.message)
        if st.button("➡️ Келесі тапсырма"):
            st.session_state.question = make_question(topic)
            st.session_state.started = time.time()
            st.session_state.hint_used = False
            st.session_state.answered = False
            st.session_state.message = ""
            st.rerun()
    completed = len(st.session_state.history)
    if completed > 0 and completed % 5 == 0:
        st.info("🌿 5 тапсырма орындалды. 2–3 минут сергіту жаттығуын жасаңыз!")
    with st.expander("🎬 Осы тақырып бойынша бейнесабақтар"):
        videos = youtube_search(f"10 сынып алгебра {topic} қазақша")
        if videos:
            for title, url in videos:
                st.markdown(f"- [{title}]({url})")
        else:
            st.caption("Видео табылмады немесе API key енгізілмеген.")

with tab2:
    if not st.session_state.history:
        st.info("Нәтиже шығуы үшін кемінде бір тапсырма орындаңыз.")
    else:
        df = pd.DataFrame(st.session_state.history)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Орындалды", len(df))
        c2.metric("Дұрыс", int(df.correct.sum()))
        c3.metric("Дәлдік", f"{df.correct.mean()*100:.0f}%")
        c4.metric("Орташа уақыт", f"{df.time_sec.mean():.1f} сек")
        by_topic = df.groupby("topic")["correct"].mean().mul(100).round(0)
        st.bar_chart(by_topic)
        weak = by_topic.idxmin()
        st.info(f"🤖 Ұсыныс: **{weak}** бөлімін қосымша қайталаңыз.")

with tab3:
    password = st.text_input("Мұғалім коды", type="password")
    teacher_code = "1234"
    try:
        teacher_code = st.secrets.get("TEACHER_CODE", "1234")
    except Exception:
        pass
    if password == teacher_code:
        if not st.session_state.history:
            st.info("Әзірге нәтиже жоқ.")
        else:
            df = pd.DataFrame(st.session_state.history)
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Нәтижені CSV жүктеу", df.to_csv(index=False).encode("utf-8-sig"), "10_synyp_algebra_natizhe.csv", "text/csv")
            forest, scaler, pca, trend = models()
            features = np.column_stack([
                df.correct.expanding().mean(),
                df.time_sec.expanding().mean(),
                df.hint_used.expanding().mean(),
            ])
            if len(df) >= 2:
                coords = pca.transform(scaler.transform(features))
                st.caption("PCA арқылы оқу нәтижесінің өзгерісі")
                st.line_chart(pd.DataFrame(coords, columns=["PCA-1", "PCA-2"]))
                forecast = float(trend.predict([[min(len(df), 8)]])[0])
                st.write(f"Linear Regression болжамы бойынша ықтимал келесі дәлдік: **{max(0,min(1,forecast))*100:.0f}%**")
    elif password:
        st.error("Мұғалім коды қате.")
    else:
        st.caption("Алғашқы код: 1234. Онлайн нұсқада TEACHER_CODE құпия параметрін өзгертіңіз.")
