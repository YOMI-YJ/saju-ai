import streamlit as st
from datetime import datetime
from openai import OpenAI
import os

from dotenv import load_dotenv
load_dotenv()

# OpenAI 설정
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_gpt(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 명리학 전문가야. 간지 정보를 바탕으로 성격과 궁합을 논리적으로 분석해줘."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# 사주팔자 계산
heavenly_stems = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
earthly_branches = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]
gapja_cycle = [heavenly_stems[i % 10] + earthly_branches[i % 12] for i in range(60)]

def get_year_ganji(year: int) -> str:
    base_year = 1984
    return gapja_cycle[(year - base_year) % 60]

def get_month_branch(month: int) -> str:
    return earthly_branches[(month + 1) % 12]

def get_day_ganji(dt: datetime) -> str:
    base_date = datetime(1900, 1, 1)
    return gapja_cycle[(dt - base_date).days % 60]

def get_hour_branch(hour: int) -> str:
    return earthly_branches[((hour + 1) // 2) % 12]

def get_four_pillars(birth_str: str):
    dt = datetime.strptime(birth_str, "%Y-%m-%d %H:%M")
    return {
        "년주": get_year_ganji(dt.year),
        "월지": get_month_branch(dt.month),
        "일주": get_day_ganji(dt),
        "시지": get_hour_branch(dt.hour)
    }

# Streamlit UI
st.set_page_config(page_title="🔮 사주팔자 해석 챗봇", layout="centered")
st.title("🔮 GPT 기반 사주팔자 해석 챗봇")

# 생년월일 입력 폼
with st.form("birth_form"):
    birth_date = st.date_input("생년월일", min_value=datetime(1900, 1, 1))
    birth_time = st.time_input("출생 시각")
    submitted = st.form_submit_button("사주팔자 계산")

# 계산 시 session_state에 저장
if submitted:
    birth_str = f"{birth_date} {birth_time.strftime('%H:%M')}"
    st.session_state["birth_str"] = birth_str
    st.session_state["pillars"] = get_four_pillars(birth_str)

# 계산된 사주 출력 및 질문
if "pillars" in st.session_state:
    pillars = st.session_state["pillars"]
    st.subheader("🧧 사주팔자 결과")
    st.markdown(f"""
    - **년주**: {pillars['년주']}
    - **월지**: {pillars['월지']}
    - **일주**: {pillars['일주']}
    - **시지**: {pillars['시지']}
    """)

    user_prompt = st.text_input("✏️ 이 사주에 대해 궁금한 점을 입력하세요", placeholder="예: 성격과 궁합 특징을 알려줘")

    if user_prompt:
        prompt = f"""
아래 사주팔자를 기반으로, 사용자의 질문에 대해 명리학 전문가로서 해석해줘.

사주팔자:
- 년주: {pillars['년주']}
- 월지: {pillars['월지']}
- 일주: {pillars['일주']}
- 시지: {pillars['시지']}

질문:
{user_prompt}
"""
        with st.spinner("GPT가 해석 중입니다..."):
            response = ask_gpt(prompt)
        st.subheader("🧠 GPT의 해석 결과")
        st.write(response)
