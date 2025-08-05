import streamlit as st
from datetime import datetime
from openai import OpenAI
import os
from dotenv import load_dotenv

# ===== API 키 로드 =====
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=API_KEY)

# ===== GPT 호출 함수 =====
def ask_gpt(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 명리학 전문가야. 사주팔자 정보를 바탕으로 성격, 오행, 궁합을 분석해줘."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# ===== 사주팔자 계산 함수 =====
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

# ===== Streamlit 앱 시작 =====
st.set_page_config(page_title="🔮 사주팔자 해석 챗봇", layout="centered")
st.markdown("<h1>🔮 재미로 보는 GPT 기반 사주 해석</h1>", unsafe_allow_html=True)
st.markdown("<small>(feat. 4천년의 통계학!)</small>", unsafe_allow_html=True)



# 사용자 생년월일 입력
with st.form("birth_form"):
    birth_date = st.date_input("생년월일", min_value=datetime(1900, 1, 1))
    birth_time = st.time_input("출생 시각")
    submitted = st.form_submit_button("내 사주 보기!")

# 사주 계산 + 기본 해석 저장
if submitted:
    birth_str = f"{birth_date} {birth_time.strftime('%H:%M')}"
    st.session_state["birth_str"] = birth_str
    st.session_state["pillars"] = get_four_pillars(birth_str)

    # 기본 해석 프롬프트
    pillars = st.session_state["pillars"]
    default_prompt = f"""
아래 사주팔자를 바탕으로 이 사람의 전반적인 성격, 오행 경향, 특징을 분석해줘.

사주팔자:
- 년주: {pillars['년주']}
- 월지: {pillars['월지']}
- 일주: {pillars['일주']}
- 시지: {pillars['시지']}
"""
    st.session_state["default_response"] = ask_gpt(default_prompt)

# 사주 결과 및 기본 해석 출력
if "pillars" in st.session_state:
    pillars = st.session_state["pillars"]

    st.subheader("🧧 사주팔자")
    st.markdown(f"""
    - **년주**: {pillars['년주']}
    - **월지**: {pillars['월지']}
    - **일주**: {pillars['일주']}
    - **시지**: {pillars['시지']}
    """)

    if "default_response" in st.session_state:
        st.subheader("🧠 기본 해석")
        st.write(st.session_state["default_response"])

    # 사용자 질문 입력
    user_prompt = st.text_input("✏️ 더 궁금한 점을 물어보세요!", placeholder="예: 직업운은 어떤가요?")
    if user_prompt:
        followup_prompt = f"""
사주팔자:
- 년주: {pillars['년주']}
- 월지: {pillars['월지']}
- 일주: {pillars['일주']}
- 시지: {pillars['시지']}

사용자 질문:
{user_prompt}
"""
        with st.spinner("GPT가 해석 중입니다..."):
            followup_response = ask_gpt(followup_prompt)
        st.subheader("🔍 추가 해석")
        st.write(followup_response)
