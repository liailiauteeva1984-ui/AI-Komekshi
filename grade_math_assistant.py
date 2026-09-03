"""5–11-сыныптарға арналған қазақша математикалық көмекші."""

import math
import random
import time

import pandas as pd
import streamlit as st


COURSES = {
    "5-сынып": {
        "Натурал сандар": [("348+572 мәнін табыңыз.", "920", "Разрядтар бойынша қосыңыз."), ("900−376 мәнін табыңыз.", "524", "Азайтуды баған түрінде орындаңыз.")],
        "Жай бөлшектер": [("1/4+2/4 мәнін бөлшекпен жазыңыз.", "3/4", "Бөлімдері бірдей бөлшектердің алымдарын қосыңыз."), ("3/5−1/5 мәнін жазыңыз.", "2/5", "Алымдарын азайтыңыз.")],
        "Ондық бөлшектер": [("2,5+1,75 мәнін табыңыз.", "4.25", "Үтірлерді бірінің астына бірін келтіріңіз."), ("6,4·10 мәнін табыңыз.", "64", "Үтірді бір орын оңға жылжытыңыз.")],
        "Пайыз": [("200 санының 10%-ын табыңыз.", "20", "200·0,1."), ("80 санының 25%-ын табыңыз.", "20", "25%=1/4.")],
        "Геометриялық фигуралар": [("Қабырғасы 6 см квадраттың периметрін табыңыз.", "24", "P=4a."), ("Ұзындығы 8, ені 5 тіктөртбұрыштың ауданын табыңыз.", "40", "S=ab.")],
    },
    "6-сынып": {
        "Қатынастар және пропорциялар": [("3:5=x:20 пропорциясындағы x-ті табыңыз.", "12", "3·20=5x."), ("4 кг алма 2000 теңге. 1 кг бағасын табыңыз.", "500", "2000-ды 4-ке бөліңіз.")],
        "Рационал сандар": [("−7+12 мәнін табыңыз.", "5", "Сан түзуін қолданыңыз."), ("−4·(−6) мәнін табыңыз.", "24", "Теріс санды теріс санға көбейтсе, оң сан шығады.")],
        "Өрнектер": [("3a+2a өрнегін ықшамдағандағы коэффициентті табыңыз.", "5", "Ұқсас мүшелерді қосыңыз."), ("x=4 болса, 2x+3 мәнін табыңыз.", "11", "x орнына 4 қойыңыз.")],
        "Бір айнымалысы бар теңдеу": [("3x+5=20 теңдеуін шешіңіз.", "5", "Алдымен екі жақтан 5-ті азайтыңыз."), ("7x=42 теңдеуін шешіңіз.", "6", "42-ні 7-ге бөліңіз.")],
        "Координаталық жазықтық": [("A(−3;4) нүктесінің абсциссасын жазыңыз.", "-3", "Бірінші координата — абсцисса."), ("B(2;−5) нүктесінің ординатасын жазыңыз.", "-5", "Екінші координата — ордината.")],
    },
    "7-сынып": {
        "Бүтін көрсеткішті дәреже": [("2⁵ мәнін табыңыз.", "32", "2 санын бес рет көбейтіңіз."), ("3²·3³ өрнегінің дәреже көрсеткішін табыңыз.", "5", "Негіздері бірдей болса, көрсеткіштер қосылады.")],
        "Көпмүшелер": [("(x+3)(x−3) өрнегіндегі тұрақты мүшені табыңыз.", "-9", "Квадраттар айырымы."), ("2x+5x−3 өрнегіндегі x коэффициентін табыңыз.", "7", "Ұқсас мүшелерді біріктіріңіз.")],
        "Сызықтық функция": [("y=2x−1 болса, x=3 кезіндегі y-ті табыңыз.", "5", "x орнына 3 қойыңыз."), ("y=−4x+7 функциясының бұрыштық коэффициентін табыңыз.", "-4", "y=kx+b формуласындағы k.")],
        "Теңдеулер жүйесі": [("x+y=7, x−y=1 жүйесіндегі x-ті табыңыз.", "4", "Теңдеулерді қосыңыз."), ("x+y=9, x=5 болса, y-ті табыңыз.", "4", "5+y=9.")],
        "Үшбұрыштар": [("Үшбұрыш бұрыштары 50°, 60° және x°. x-ті табыңыз.", "70", "Бұрыштар қосындысы 180°."), ("Теңбүйірлі үшбұрыштың табан бұрышы 40°. Төбе бұрышын табыңыз.", "100", "Табан бұрыштары тең.")],
    },
    "8-сынып": {
        "Квадрат түбір": [("√144 мәнін табыңыз.", "12", "12²=144."), ("√50 өрнегін a√2 түріне келтіргендегі a-ны табыңыз.", "5", "50=25·2.")],
        "Квадрат теңдеу": [("x²−5x+6=0 түбірлерін үтірмен жазыңыз.", "2,3", "Көбейтіндісі 6, қосындысы 5."), ("x²−16=0 теңдеуінің оң түбірін табыңыз.", "4", "Квадраттар айырымы.")],
        "Рационал теңдеулер": [("1/x=1/4 теңдеуін шешіңіз.", "4", "Айқыш көбейтіңіз."), ("6/(x−1)=3 теңдеуін шешіңіз.", "3", "6=3(x−1).")],
        "Квадраттық функция": [("y=x²−4 функциясының оң нөлін табыңыз.", "2", "x²=4."), ("y=(x−3)² параболасының төбесінің абсциссасын табыңыз.", "3", "y=(x−a)² формуласын қараңыз.")],
        "Пифагор теоремасы": [("Катеттері 3 және 4 болатын үшбұрыштың гипотенузасын табыңыз.", "5", "c²=a²+b²."), ("Гипотенузасы 13, катеті 5. Екінші катетті табыңыз.", "12", "b²=13²−5².")],
    },
    "9-сынып": {
        "Квадрат теңсіздік": [("x²−9<0 теңсіздігінің ең үлкен бүтін шешімін табыңыз.", "2", "−3<x<3."), ("x²−4≥0 шешіміне кірмейтін бүтін санды табыңыз: −3, 0, 3.", "0", "x≤−2 немесе x≥2.")],
        "Прогрессиялар": [("2, 5, 8, ... арифметикалық прогрессиясының айырмасын табыңыз.", "3", "Келесі мүшеден алдыңғысын азайтыңыз."), ("3, 6, 12, ... геометриялық прогрессиясының еселігін табыңыз.", "2", "Келесі мүшені алдыңғысына бөліңіз.")],
        "Тригонометрия": [("sin30° мәнін табыңыз.", "0.5", "Негізгі бұрыш мәні."), ("tan45° мәнін табыңыз.", "1", "sin45°/cos45°.")],
        "Ықтималдық": [("Тиынды лақтырғанда елтаңба түсу ықтималдығын жазыңыз.", "0.5", "1 қолайлы, 2 мүмкін нәтиже."), ("Кубиктен жұп сан түсу ықтималдығын жазыңыз.", "0.5", "2,4,6 — үш қолайлы нәтиже.")],
        "Векторлар": [("a=(2;3), b=(4;−1). a+b векторының бірінші координатасын табыңыз.", "6", "Сәйкес координаталарды қосыңыз."), ("a=(3;4) векторының ұзындығын табыңыз.", "5", "√(3²+4²).")],
    },
    "10-сынып": {
        "Функция қасиеттері": [("f(x)=2x−3 болса, f(4)-ті табыңыз.", "5", "x орнына 4 қойыңыз."), ("y=x²−4 функциясының оң нөлін табыңыз.", "2", "x²=4.")],
        "Тригонометриялық функциялар": [("cos60° мәнін табыңыз.", "0.5", "Негізгі мәнді еске түсіріңіз."), ("0°≤x<360° аралығында tanx=1 теңдеуінің неше шешімі бар?", "2", "Периоды 180°.")],
        "Көрсеткіштік теңдеу": [("2ˣ=32 теңдеуін шешіңіз.", "5", "32=2⁵."), ("3ˣ=1/9 теңдеуін шешіңіз.", "-2", "1/9=3⁻².")],
        "Логарифм": [("log₂8 мәнін табыңыз.", "3", "2³=8."), ("log₅x=2 теңдеуін шешіңіз.", "25", "x=5².")],
        "Туынды": [("f(x)=x³ болса, f′(2)-ні табыңыз.", "12", "f′(x)=3x²."), ("f(x)=5x²−3x болса, f′(1)-ді табыңыз.", "7", "f′(x)=10x−3.")],
    },
    "11-сынып": {
        "Алғашқы функция және интеграл": [("∫₀²3x²dx мәнін табыңыз.", "8", "Алғашқы функциясы x³."), ("∫4dx өрнегіндегі x коэффициентін табыңыз.", "4", "∫a dx=ax+C.")],
        "Математикалық статистика": [("2,4,6,8 сандарының орта мәнін табыңыз.", "5", "Қосындыны 4-ке бөліңіз."), ("D(X)=9 болса, стандартты ауытқуды табыңыз.", "3", "σ=√D(X).")],
        "Дәрежелер және түбірлер": [("∛64 мәнін табыңыз.", "4", "4³=64."), ("16^(3/4) мәнін табыңыз.", "8", "⁴√16=2, одан кейін 2³.")],
        "Иррационал теңдеулер": [("√(x+1)=3 теңдеуін шешіңіз.", "8", "x+1=9."), ("√x=x түбірлерін үтірмен жазыңыз.", "0,1", "Квадраттап, ММЖ-ны тексеріңіз.")],
        "Комплекс сандар": [("i² мәнін табыңыз.", "-1", "Жорамал бірлік анықтамасы."), ("(2+i)(2−i) мәнін табыңыз.", "5", "i²=−1.")],
    },
}


def _fmt(number):
    value = round(float(number), 4)
    return str(int(value)) if value.is_integer() else str(value)


def _generated_question(grade, topic, i):
    """Әр тақырыпқа мазмұны дұрыс, параметрлері бөлек тапсырма жасайды."""
    r = random.Random(f"{grade}|{topic}|{i}")

    if topic == "Натурал сандар":
        a, b = r.randint(120, 950), r.randint(80, 780)
        return (f"{a}+{b} мәнін табыңыз.", str(a+b), "Разрядтар бойынша қосыңыз.")
    if topic == "Жай бөлшектер":
        d = r.randint(5, 15); a = r.randint(1, d//2); b = r.randint(1, d-a)
        g = math.gcd(a+b, d)
        return (f"{a}/{d}+{b}/{d} мәнін қысқартып жазыңыз.", f"{(a+b)//g}/{d//g}", "Алымдарды қосып, бөлшекті қысқартыңыз.")
    if topic == "Ондық бөлшектер":
        a, b = r.randint(11, 99)/10, r.randint(11, 99)/10
        return (f"{_fmt(a)}+{_fmt(b)} мәнін табыңыз.", _fmt(a+b), "Үтірлерді бірінің астына бірін келтіріңіз.")
    if topic == "Пайыз":
        p = r.choice([10, 20, 25, 50]); n = r.randint(2, 20)*20
        return (f"{n} санының {p}%-ын табыңыз.", _fmt(n*p/100), "Санды пайыздың ондық бөлшегіне көбейтіңіз.")
    if topic == "Геометриялық фигуралар":
        a, b = r.randint(3, 18), r.randint(3, 18)
        return (f"Ұзындығы {a} см, ені {b} см тіктөртбұрыштың ауданын табыңыз.", str(a*b), "S=a·b.")

    if topic == "Қатынастар және пропорциялар":
        a, b, k = r.randint(2, 9), r.randint(2, 9), r.randint(2, 8)
        return (f"{a}:{b}=x:{b*k} пропорциясындағы x-ті табыңыз.", str(a*k), "Айқыш көбейту қасиетін қолданыңыз.")
    if topic == "Рационал сандар":
        a, b = r.randint(-20, -2), r.randint(3, 25)
        return (f"{a}+{b} мәнін табыңыз.", str(a+b), "Сан түзуін немесе таңба ережесін қолданыңыз.")
    if topic == "Өрнектер":
        a, b = r.randint(2, 12), r.randint(2, 12)
        return (f"{a}x+{b}x өрнегін ықшамдағандағы x коэффициентін табыңыз.", str(a+b), "Ұқсас мүшелердің коэффициенттерін қосыңыз.")
    if topic == "Бір айнымалысы бар теңдеу":
        a, x, b = r.randint(2, 9), r.randint(2, 15), r.randint(1, 20)
        return (f"{a}x+{b}={a*x+b} теңдеуін шешіңіз.", str(x), "Алдымен бос мүшені азайтып, коэффициентке бөліңіз.")
    if topic == "Координаталық жазықтық":
        x, y = r.randint(-12, 12), r.randint(-12, 12)
        return (f"A({x};{y}) нүктесінің абсциссасын жазыңыз.", str(x), "Абсцисса — бірінші координата.")

    if topic == "Бүтін көрсеткішті дәреже":
        a, n = r.randint(2, 6), r.randint(2, 5)
        return (f"{a}^{n} мәнін табыңыз.", str(a**n), "Негізді дәреже көрсеткіші қанша болса, сонша рет көбейтіңіз.")
    if topic == "Көпмүшелер":
        a, b = r.randint(2, 12), r.randint(2, 12)
        return (f"({a}x+{b}x) өрнегіндегі x коэффициентін табыңыз.", str(a+b), "Ұқсас мүшелерді біріктіріңіз.")
    if topic == "Сызықтық функция":
        k, x, b = r.randint(-7, 8), r.randint(-6, 8), r.randint(-10, 10)
        return (f"y={k}x+{b} болса, x={x} кезіндегі y-ті табыңыз.", str(k*x+b), "x мәнін функцияға қойыңыз.")
    if topic == "Теңдеулер жүйесі":
        x, y = r.randint(1, 12), r.randint(1, 12)
        return (f"x+y={x+y}, x−y={x-y} жүйесіндегі x-ті табыңыз.", str(x), "Екі теңдеуді қосып, 2x-ті табыңыз.")
    if topic == "Үшбұрыштар":
        a, b = r.randint(25, 75), r.randint(25, 75)
        if a+b >= 170: b = 170-a
        return (f"Үшбұрыштың екі бұрышы {a}° және {b}°. Үшінші бұрышын табыңыз.", str(180-a-b), "Үшбұрыш бұрыштарының қосындысы 180°.")

    if topic == "Квадрат түбір":
        a = r.randint(3, 30)
        return (f"√{a*a} мәнін табыңыз.", str(a), "Арифметикалық квадрат түбірді табыңыз.")
    if topic == "Квадрат теңдеу":
        a, b = sorted(r.sample(range(1, 13), 2))
        return (f"x²−{a+b}x+{a*b}=0 түбірлерін үтірмен жазыңыз.", f"{a},{b}", "Қосындысы мен көбейтіндісі берілген сандарды табыңыз.")
    if topic == "Рационал теңдеулер":
        x, shift, k = r.randint(2, 15), r.randint(1, 8), r.randint(2, 9)
        return (f"{k*(x-shift)}/(x−{shift})={k} теңдеуінің ұсынылған шешімі x={x}. x мәнін жазыңыз.", str(x), "Бөлім нөлге тең емес екенін тексеріңіз.")
    if topic == "Квадраттық функция":
        a, b = r.randint(-8, 8), r.randint(-10, 10)
        return (f"y=(x−({a}))²+({b}) параболасы төбесінің абсциссасын табыңыз.", str(a), "y=(x−a)²+b формуласындағы a.")
    if topic == "Пифагор теоремасы":
        triple = r.choice([(3,4,5),(5,12,13),(8,15,17),(7,24,25)]); k = r.randint(1, 8)
        a, b, c = [v*k for v in triple]
        return (f"Катеттері {a} және {b} болатын тікбұрышты үшбұрыштың гипотенузасын табыңыз.", str(c), "c²=a²+b².")

    if topic == "Квадрат теңсіздік":
        a = r.randint(2, 12)
        return (f"x²−{a*a}<0 теңсіздігінің ең үлкен бүтін шешімін табыңыз.", str(a-1), f"−{a}<x<{a}.")
    if topic == "Прогрессиялар":
        a, d, n = r.randint(1, 20), r.randint(2, 9), r.randint(4, 12)
        return (f"a₁={a}, d={d} арифметикалық прогрессиясының a{n} мүшесін табыңыз.", str(a+(n-1)*d), "aₙ=a₁+(n−1)d.")
    if topic == "Тригонометрия":
        angle, ans = r.choice([(0,0),(30,0.5),(90,1),(150,0.5),(180,0)]); k = r.randint(1, 9)
        return (f"{k}·sin{angle}° мәнін табыңыз.", _fmt(k*ans), "Алдымен синустың негізгі мәнін тауып, коэффициентке көбейтіңіз.")
    if topic == "Ықтималдық":
        n = r.randint(4, 20); good = r.randint(1, n-1); g = math.gcd(good, n)
        return (f"{n} тең мүмкін нәтижесінің {good}-і қолайлы. Ықтималдықты бөлшекпен жазыңыз.", f"{good//g}/{n//g}", "Қолайлы нәтижені барлық нәтиже санына бөліңіз.")
    if topic == "Векторлар":
        x1, y1, x2, y2 = [r.randint(-9, 9) for _ in range(4)]
        return (f"a=({x1};{y1}), b=({x2};{y2}). a+b векторының бірінші координатасын табыңыз.", str(x1+x2), "Сәйкес координаталарды қосыңыз.")

    if topic == "Функция қасиеттері":
        k, b, x = r.randint(-8, 9), r.randint(-12, 12), r.randint(-6, 9)
        return (f"f(x)={k}x+{b} болса, f({x}) мәнін табыңыз.", str(k*x+b), "x орнына берілген санды қойыңыз.")
    if topic == "Тригонометриялық функциялар":
        angle, ans = r.choice([(0,1),(60,0.5),(90,0),(120,-0.5),(180,-1)]); k = r.randint(1, 9)
        return (f"{k}·cos{angle}° мәнін табыңыз.", _fmt(k*ans), "Алдымен косинустың негізгі мәнін тауып, коэффициентке көбейтіңіз.")
    if topic == "Көрсеткіштік теңдеу":
        base, x = r.randint(2, 6), r.randint(2, 6)
        return (f"{base}ˣ={base**x} теңдеуін шешіңіз.", str(x), "Оң жағын негіздің дәрежесі түрінде жазыңыз.")
    if topic == "Логарифм":
        base, x = r.randint(2, 7), r.randint(2, 5)
        return (f"log_{base}({base**x}) мәнін табыңыз.", str(x), "Логарифм анықтамасын қолданыңыз.")
    if topic == "Туынды":
        n, x = r.randint(2, 6), r.randint(1, 5)
        return (f"f(x)=x^{n} болса, f′({x}) мәнін табыңыз.", str(n*x**(n-1)), "(xⁿ)′=nxⁿ⁻¹.")

    if topic == "Алғашқы функция және интеграл":
        k, n, upper = r.randint(2, 8), r.randint(1, 4), r.randint(1, 5)
        value = k * upper**(n+1) / (n+1)
        return (f"∫₀^{upper} {k}x^{n} dx мәнін табыңыз.", _fmt(value), "Дәрежені 1-ге арттырып, жаңа дәрежеге бөліңіз.")
    if topic == "Математикалық статистика":
        nums = [r.randint(2, 20) for _ in range(3)]; total = sum(nums); nums.append((4-total%4)%4+4)
        return (f"{', '.join(map(str, nums))} сандарының арифметикалық ортасын табыңыз.", _fmt(sum(nums)/4), "Қосындыны сандар санына бөліңіз.")
    if topic == "Дәрежелер және түбірлер":
        root, n = r.randint(2, 9), r.choice([3, 4, 5])
        return (f"{n}-дәрежелі √({root**n}) мәнін табыңыз.", str(root), "Түбірге кері дәрежелеуді қолданыңыз.")
    if topic == "Иррационал теңдеулер":
        root, shift = r.randint(2, 12), r.randint(-8, 8); solution = root*root-shift
        sign = "+" if shift >= 0 else "−"
        return (f"√(x {sign} {abs(shift)})={root} теңдеуін шешіңіз.", str(solution), "Екі жағын квадраттап, ММЖ-ны тексеріңіз.")
    if topic == "Комплекс сандар":
        a, b, c, d = [r.randint(-9, 9) for _ in range(4)]
        return (f"({a}+{b}i)+({c}+{d}i) қосындысының нақты бөлігін табыңыз.", str(a+c), "Нақты бөліктерді бөлек қосыңыз.")

    raise ValueError(f"Тапсырма генераторы табылмады: {grade} / {topic}")


for _grade, _topics in COURSES.items():
    for _topic, _questions in _topics.items():
        _i = 1
        while len(_questions) < 20:
            candidate = _generated_question(_grade, _topic, _i)
            numbered = (f"{candidate[0]} 〔№{_i}〕", candidate[1], candidate[2])
            _questions.append(numbered)
            _i += 1


def _norm(value):
    return str(value).strip().lower().replace(" ", "").replace(";", ",").replace("−", "-").replace(",", ".")


def _correct(given, expected):
    a, b = _norm(given), _norm(expected)
    try:
        return abs(float(a) - float(b)) < 1e-7
    except ValueError:
        return a == b


BREAK_EXERCISES = {
    "👀 Көз жаттығуы": "20 секунд алыс нүктеге қараңыз. Содан кейін көзіңізбен баяу оңға, солға, жоғары және төмен қараңыз.",
    "✋ Қол жаттығуы": "Алақаныңызды 5 рет ашып-жұмыңыз. Білегіңізді әр бағытқа 5 рет айналдырыңыз.",
    "🧍 Қимыл жаттығуы": "Орныңыздан тұрып, иығыңызды 5 рет айналдырыңыз және екі жаққа баяу созылыңыз.",
}


def _pick_unseen(course, topic, seen, level):
    available = [q for q in course[topic] if q[0] not in seen.setdefault(topic, [])]
    if not available:
        return None
    # Жеңіл деңгейде алғашқы, күрделі деңгейде соңғы тапсырмалар басым таңдалады.
    if level == 1:
        return available[0]
    if level == 3:
        return available[-1]
    return random.choice(available)


def render_grade_assistant(section_label):
    grade = section_label.split(" ", 1)[1]
    course = COURSES[grade]
    prefix = f"grade_{grade}"
    history_key = f"{prefix}_history"
    question_key = f"{prefix}_question"
    start_key = f"{prefix}_start"
    feedback_key = f"{prefix}_feedback"
    hint_key = f"{prefix}_hint_used"
    seen_key = f"{prefix}_seen"
    level_key = f"{prefix}_level"
    answered_key = f"{prefix}_answered"
    retry_key = f"{prefix}_retry"
    attempt_key = f"{prefix}_attempt"
    last_break_key = f"{prefix}_last_break"
    break_count_key = f"{prefix}_break_count"

    st.session_state.setdefault(history_key, [])
    st.session_state.setdefault(question_key, None)
    st.session_state.setdefault(start_key, time.time())
    st.session_state.setdefault(feedback_key, "")
    st.session_state.setdefault(hint_key, False)
    st.session_state.setdefault(seen_key, {})
    st.session_state.setdefault(level_key, 1)
    st.session_state.setdefault(answered_key, False)
    st.session_state.setdefault(retry_key, False)
    st.session_state.setdefault(attempt_key, 0)
    st.session_state.setdefault(last_break_key, 0)
    st.session_state.setdefault(break_count_key, 0)

    st.markdown(f'<div class="main-title">{section_label} математика көмекшісі</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Тақырыпты таңдаңыз • тапсырманы орындаңыз • нәтижені бақылаңыз</div>', unsafe_allow_html=True)

    topic = st.selectbox("📚 Тақырып", list(course), key=f"{prefix}_topic")
    level_names = {1: "Жеңіл", 2: "Орташа", 3: "Күрделі"}
    st.info(f"🤖 AI ұсынған деңгей: **{level_names[st.session_state[level_key]]}**")

    main_completed = sum(1 for row in st.session_state[history_key] if not row.get("Қайта орындау", False))
    if main_completed > 0 and main_completed % 5 == 0 and st.session_state[last_break_key] != main_completed:
        st.markdown('<div class="break-card"><h2>🌿 Сергіту сәті</h2><p>5 тапсырма орындалды. Бір жаттығуды таңдап орындаңыз.</p></div>', unsafe_allow_html=True)
        exercise = st.radio("Жаттығу түрі", list(BREAK_EXERCISES), horizontal=True, key=f"{prefix}_break_choice")
        st.success(BREAK_EXERCISES[exercise])
        if st.button("✅ Жаттығуды аяқтадым", key=f"{prefix}_break_done", use_container_width=True):
            st.session_state[last_break_key] = main_completed
            st.session_state[break_count_key] += 1
            st.rerun()
        st.stop()

    lesson_tab, result_tab, teacher_tab = st.tabs([
        "🧩 Тапсырма",
        "📊 Нәтиже",
        "👩‍🏫 Мұғалімге арналған ақпарат",
    ])

    with lesson_tab:
        current = st.session_state[question_key]
        if current is None or current[0] != topic:
            picked = _pick_unseen(course, topic, st.session_state[seen_key], st.session_state[level_key])
            if picked:
                text, answer, hint = picked
                st.session_state[question_key] = (topic, text, answer, hint)
                st.session_state[seen_key].setdefault(topic, []).append(text)
                st.session_state[start_key] = time.time()
                st.session_state[feedback_key] = ""
                st.session_state[hint_key] = False
                st.session_state[answered_key] = False
                st.session_state[retry_key] = False
                current = st.session_state[question_key]
            else:
                current = None

        if current is None:
            st.success("✅ Бұл тақырыптағы қайталанбайтын тапсырмалардың барлығы орындалды. Басқа тақырыпты таңдаңыз.")
        else:
            _, text, expected, hint = current
            st.markdown(f'<div class="problem-box" style="font-size:30px">{text}</div>', unsafe_allow_html=True)
            given = st.text_input("Жауабыңыз", key=f"{prefix}_answer_{st.session_state[attempt_key]}")
            c1, c2 = st.columns(2)
            if c1.button("💡 Көмек", key=f"{prefix}_hint_{st.session_state[attempt_key]}", use_container_width=True, disabled=st.session_state[answered_key]):
                st.session_state[hint_key] = True
                st.info(hint)
            if c2.button("✅ Тексеру", key=f"{prefix}_check_{st.session_state[attempt_key]}", use_container_width=True, disabled=st.session_state[answered_key]):
                if not given.strip():
                    st.warning("Алдымен жауап енгізіңіз.")
                else:
                    ok = _correct(given, expected)
                    elapsed = round(time.time()-st.session_state[start_key], 1)
                    st.session_state[history_key].append({
                        "Тақырып": topic, "Тапсырма": text, "Дұрыс": ok,
                        "Уақыт": elapsed, "Көмек": int(st.session_state[hint_key]),
                        "Деңгей": level_names[st.session_state[level_key]],
                        "Қайта орындау": bool(st.session_state[retry_key]),
                    })
                    if ok and not st.session_state[hint_key] and elapsed <= 90:
                        st.session_state[level_key] = min(3, st.session_state[level_key] + 1)
                    elif not ok or st.session_state[hint_key]:
                        st.session_state[level_key] = max(1, st.session_state[level_key] - 1)
                    st.session_state[answered_key] = True
                    st.session_state[feedback_key] = "Дұрыс! Келесі тапсырма күрделірек болуы мүмкін. 🎉" if ok else f"Қате бар. Көмек: {hint}"
                    st.rerun()

            if st.session_state[feedback_key]:
                last_ok = st.session_state[history_key][-1]["Дұрыс"]
                if last_ok:
                    st.success(st.session_state[feedback_key])
                else:
                    st.error(st.session_state[feedback_key])
                b1, b2 = st.columns(2)
                if not last_ok and b1.button("🔄 Қатені түзету", key=f"{prefix}_retry_button"):
                    st.session_state[answered_key] = False
                    st.session_state[retry_key] = True
                    st.session_state[feedback_key] = ""
                    st.session_state[hint_key] = False
                    st.session_state[attempt_key] += 1
                    st.session_state[start_key] = time.time()
                    st.rerun()
                if b2.button("➡️ Келесі тапсырма", key=f"{prefix}_next"):
                    st.session_state[question_key] = None
                    st.session_state[answered_key] = False
                    st.session_state[retry_key] = False
                    st.session_state[feedback_key] = ""
                    st.session_state[hint_key] = False
                    st.session_state[attempt_key] += 1
                    st.rerun()

    with result_tab:
        history = st.session_state[history_key]
        if not history:
            st.info("Нәтиже шығуы үшін кемінде бір тапсырма орындаңыз.")
        else:
            df = pd.DataFrame(history)
            c1, c2, c3 = st.columns(3)
            c1.metric("Орындалды", len(df))
            c2.metric("Дұрыс", int(df["Дұрыс"].sum()))
            c3.metric("Дәлдік", f'{df["Дұрыс"].mean()*100:.0f}%')
            chart = df.groupby("Тақырып")["Дұрыс"].mean().mul(100)
            st.bar_chart(chart)
            weakest = chart.idxmin()
            st.info(f"🤖 Ұсыныс: **{weakest}** тақырыбын қайталаңыз.")

    with teacher_tab:
        history = st.session_state[history_key]
        st.subheader("📊 Оқушының оқу аналитикасы")
        if not history:
            st.info("Мұғалім аналитикасы шығуы үшін оқушы кемінде бір тапсырма орындауы керек.")
        else:
            df = pd.DataFrame(history)
            completed = int((~df["Қайта орындау"]).sum()) if "Қайта орындау" in df else len(df)
            correct_count = int(df["Дұрыс"].sum())
            wrong_count = completed - correct_count
            accuracy = df["Дұрыс"].mean() * 100
            avg_time = df["Уақыт"].mean()
            help_count = int(df["Көмек"].sum())
            retry_count = int(df["Қайта орындау"].sum()) if "Қайта орындау" in df else 0

            learning_table = pd.DataFrame({
                "Көрсеткіш": [
                    "🧩 Орындалған тапсырма",
                    "🌿 Сергіту сәті",
                    "💡 Көмек қолдану",
                    "🔊 Дыбыстық көмек",
                    "🎬 Видео түсіндіру",
                    "🔄 Қайта орындалған есеп",
                    "📚 Таңдалған тақырып",
                ],
                "Нәтиже": [completed, st.session_state[break_count_key], help_count, 0, 0, retry_count, topic],
            })
            st.dataframe(learning_table, hide_index=True, use_container_width=True)

            st.subheader("🎯 Оқу нәтижесі")
            result_table = pd.DataFrame({
                "Көрсеткіш": [
                    "✅ Дұрыс жауап",
                    "❌ Қате жауап",
                    "🎯 Жалпы нәтиже",
                    "⏱️ Орташа уақыт",
                    "💡 Көмек қолдану",
                    "📌 Қайта қаралатын есеп",
                ],
                "Нәтиже": [
                    correct_count,
                    wrong_count,
                    f"{accuracy:.0f}%",
                    f"{avg_time:.1f} сек",
                    help_count,
                    retry_count,
                ],
            })
            st.dataframe(result_table, hide_index=True, use_container_width=True)

            topic_stats = df.groupby("Тақырып").agg(
                Орындалған=("Дұрыс", "size"),
                Дұрыс=("Дұрыс", "sum"),
                Орташа_уақыт=("Уақыт", "mean"),
                Көмек_саны=("Көмек", "sum"),
            ).reset_index()
            topic_stats["Қате"] = topic_stats["Орындалған"] - topic_stats["Дұрыс"]
            topic_stats["Нәтиже (%)"] = (topic_stats["Дұрыс"] / topic_stats["Орындалған"] * 100).round(0)
            topic_stats["Орташа уақыт (сек)"] = topic_stats["Орташа_уақыт"].round(1)

            weakest = topic_stats.sort_values(["Нәтиже (%)", "Көмек_саны"], ascending=[True, False]).iloc[0]["Тақырып"]
            if accuracy >= 85:
                level, support, dynamics = "Жоғары", "Күрделендірілген тапсырмалар", "Нәтиже тұрақты"
            elif accuracy >= 60:
                level, support, dynamics = "Орташа", "Қысқа қадамдық түсіндіру", "Қосымша жаттығу қажет"
            else:
                level, support, dynamics = "Қосымша қолдау қажет", "Толық визуалды және қадамдық қолдау", "Негізгі ұғымдарды бекіту қажет"

            st.subheader("🤖 AI-дың оқушы бойынша ұсынысы")
            recommendation_table = pd.DataFrame({
                "Көрсеткіш": [
                    "🎯 Меңгеру деңгейі",
                    "🧩 Ұсынылатын қолдау",
                    "➡️ Оқу динамикасы",
                    "⚠️ Қиындық туғызған тақырып",
                    "💡 Тиімді көмек түрі",
                    "🔄 Қайта орындау қажет",
                    "👩‍🏫 Мұғалімге ұсыныс",
                ],
                "AI қорытындысы": [
                    level,
                    support,
                    dynamics,
                    weakest,
                    "Қазақша қадамдық түсіндіру",
                    f"{retry_count} тапсырма",
                    f"«{weakest}» тақырыбын қайталап, оқушыға жеке кері байланыс беріңіз.",
                ],
            })
            st.dataframe(recommendation_table, hide_index=True, use_container_width=True)

            st.subheader("🧮 Тақырыптар бойынша анализ")
            display_columns = ["Тақырып", "Орындалған", "Дұрыс", "Қате", "Нәтиже (%)", "Орташа уақыт (сек)", "Көмек_саны"]
            st.dataframe(topic_stats[display_columns], hide_index=True, use_container_width=True)
            st.bar_chart(topic_stats.set_index("Тақырып")["Нәтиже (%)"])

            csv_data = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 Толық нәтижені CSV жүктеу",
                csv_data,
                file_name=f"{grade}_matematika_analitika.csv",
                mime="text/csv",
                key=f"{prefix}_teacher_download",
            )
