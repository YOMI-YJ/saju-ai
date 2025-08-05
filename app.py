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
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 명리학 전문가야. 사주팔자 정보를 바탕으로 성격, 오행, 궁합, 운세를 분석해줘."},
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
st.markdown("<h3>🔮 4천년의 통계학! 재미로 보는 GPT 기반 사주 해석</h3>", unsafe_allow_html=True)
st.markdown("<span style='font-size:14px; color: gray;'>GPT는 거짓말을 할 수도 있어요~</span>", unsafe_allow_html=True)

# 사용자 생년월일 입력
with st.form("birth_form"):
    birth_date = st.date_input("생년월일", min_value=datetime(1900, 1, 1))
    birth_time = st.time_input("출생 시각")
    submitted = st.form_submit_button("내 사주 보기!")

# 사주 계산 + 기본 해석
if submitted:
    birth_str = f"{birth_date} {birth_time.strftime('%H:%M')}"
    st.session_state["birth_str"] = birth_str
    st.session_state["pillars"] = get_four_pillars(birth_str)

    # 기본 해석
    pillars = st.session_state["pillars"]
    default_prompt = f"""
다음 사주 정보를 바탕으로, 이 사람의 전반적인 사주 해석을 아래 형식에 따라 출력해줘.

사주팔자:
- 년주: {pillars['년주']}
- 월지: {pillars['월지']}
- 일주: {pillars['일주']}
- 시지: {pillars['시지']}

[출력 형식]

1. 🧬 성격 요약: 한 줄로 요약
2. 🔥 오행 분석: 오행의 균형, 강점, 약점
3. 💡 사주 특징 요약: 특이사항, 눈에 띄는 점
4. 🧭 전반적 조언: 전체적인 삶의 방향성에 대한 조언
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

    st.markdown("---")

    # 🎯 연도별 운세 해석
    st.subheader("📅 연도별 운세 보기")
    selected_year = st.selectbox("운세를 보고 싶은 연도", list(range(2024, 2036)))
    selected_topic = st.selectbox("운세 항목", ["전체운", "직업운", "연애운", "재물운", "건강운"])

    if st.button("운세 해석 보기"):
        prompt = f"""
    다음 사주 정보를 기반으로, {selected_year}년의 {selected_topic}을 중심으로 해석해줘.

    사주팔자:
    - 년주: {pillars['년주']}
    - 월지: {pillars['월지']}
    - 일주: {pillars['일주']}
    - 시지: {pillars['시지']}

    다음 형식으로 출력해줘:

    1. 🔍 운세 요약: 한 줄 요약
    2. 📌 상세 운세:
    - 성향 분석:
    - 주의할 점:
    - 추천 행동:
    3. 🧭 종합 조언: 전체적인 마무리 조언
    """
        with st.spinner("GPT가 운세를 보는 중..."):
            fortune = ask_gpt(prompt)
        st.subheader(f"🔮 {selected_year}년 {selected_topic} 운세")
        st.write(fortune)


    # 사용자 자유 질문
    st.markdown("---")
    user_prompt = st.text_input("✏️ 추가로 궁금한 점이 있다면 질문해보세요!", placeholder="예: 결혼운은 언제쯤 좋을까요?")
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
