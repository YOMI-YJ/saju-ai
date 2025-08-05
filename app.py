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
        temperature=0.7,
        messages=[
            {
                "role": "system",
                "content": "당신은 전문 명리학 상담가입니다. 사용자의 사주 정보를 바탕으로 전통 명리학에 기반하여 성격, 직업, 궁합 등을 분석해 주세요."
            },
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
st.markdown(
    "<span style='font-size:14px; color: gray;'>GPT는 거짓말을 할 수도 있어요~ 재미로만 봐주세요!</span>",
    unsafe_allow_html=True
)


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
다음 사주 정보를 바탕으로 아래 형식에 따라 해석해주세요.

사주 정보:
- 년주: {pillars['년주']}
- 월지: {pillars['월지']}
- 일주: {pillars['일주']}
- 시지: {pillars['시지']}

[출력 형식]

1. 🔍 사주 구성 요약  
년주, 월지, 일주, 시지를 바탕으로 전반적인 특징 요약

2. 💡 성격 및 성향  
성격, 대인관계 스타일, 행동 경향

3. ⚖️ 오행의 균형  
오행의 과다/부족 및 성향 해석

4. 🎯 직업 및 적성  
어울리는 직업, 활동 영역

5. ❤️ 연애 및 궁합 경향  
연애 스타일, 궁합에 잘 맞는 상대 유형

6. 🧾 종합 평가 및 조언  
종합적인 운세 흐름과 조심할 점
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
당신은 전문 명리학 상담가입니다.  
아래 사주 정보를 바탕으로 사용자 질문에 대해 해석해주세요.  
추측보다는 전통 명리학 기준으로 설명하고, 사주 구조를 기반으로 한 논리적인 해석을 해주세요.

사주 정보:
- 년주: {pillars['년주']}
- 월지: {pillars['월지']}
- 일주: {pillars['일주']}
- 시지: {pillars['시지']}

질문:
"{user_prompt}"

[출력 형식]

🔍 질문 요약  
→ 사용자가 궁금해한 내용을 요약해주세요.

💡 사주 기반 해석  
→ 사주 구성요소와 오행을 토대로 질문에 대한 명리학적 해석을 제공해주세요.

📌 종합 조언  
→ 주의점이나 참고할 점을 짧게 정리해주세요.
"""
        with st.spinner("GPT가 해석 중입니다..."):
            followup_response = ask_gpt(followup_prompt)
        st.subheader("🔍 추가 해석")
        st.write(followup_response)
