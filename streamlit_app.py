import streamlit as st
import os
import time
from datetime import datetime
from flow import create_youtube_processor_flow
import json

# 페이지 설정
st.set_page_config(
    page_title="SUM-Q",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# SUM-Q 미니멀 스타일 CSS (삿포로 테마)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka+One:wght@400&family=Noto+Sans+JP:wght@300;400;700;900&display=swap');

/* 전체 배경 - 삿포로 거리 풍경 */
.stApp {
    background: linear-gradient(
        135deg,
        rgba(135, 206, 235, 0.9) 0%,
        rgba(176, 224, 230, 0.9) 30%,
        rgba(240, 248, 255, 0.9) 70%,
        rgba(255, 250, 240, 0.9) 100%
    ),
    /* 도시 실루엣 효과 */
    linear-gradient(
        to bottom,
        transparent 0%,
        transparent 60%,
        rgba(70, 130, 180, 0.1) 60%,
        rgba(70, 130, 180, 0.2) 80%,
        rgba(70, 130, 180, 0.3) 100%
    );
    font-family: 'Noto Sans JP', sans-serif;
    min-height: 100vh;
    position: relative;
}

/* 배경 장식 - 건물과 산 실루엣 */
.stApp::before {
    content: "";
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 200px;
    background: 
        /* 산 실루엣 */
        radial-gradient(ellipse 300px 120px at 20% 100%, rgba(176, 196, 222, 0.4) 0%, transparent 70%),
        radial-gradient(ellipse 400px 150px at 80% 100%, rgba(176, 196, 222, 0.3) 0%, transparent 70%),
        /* 건물 실루엣 */
        linear-gradient(to top, rgba(70, 130, 180, 0.1) 0%, transparent 50%);
    z-index: -1;
    pointer-events: none;
}

/* 메인 컨테이너 - 투명하고 깔끔하게 */
.main .block-container {
    background: transparent;
    border: none;
    padding: 2rem 1rem;
    margin: 0;
    max-width: 600px;
    margin: 0 auto;
}

/* 사이드바 숨기기 */
.css-1d391kg {
    display: none;
}

/* SUM-Q 로고 - Popeyes 스타일 */
.sumq-logo {
    background: linear-gradient(145deg, #E53E3E 0%, #C53030 50%, #9B2C2C 100%);
    color: #FFFFFF;
    font-family: 'Fredoka One', cursive;
    font-size: 4rem;
    text-align: center;
    padding: 2rem 3rem;
    border-radius: 50px;
    margin: 3rem auto 2rem auto;
    width: fit-content;
    box-shadow: 
        0 8px 25px rgba(229, 62, 62, 0.4),
        inset 0 4px 8px rgba(255, 255, 255, 0.3),
        inset 0 -4px 8px rgba(0, 0, 0, 0.2);
    transform: perspective(500px) rotateX(10deg);
    position: relative;
    letter-spacing: 2px;
}

.sumq-logo::before {
    content: "";
    position: absolute;
    top: -5px;
    left: -5px;
    right: -5px;
    bottom: -5px;
    background: linear-gradient(145deg, #F56565, #E53E3E);
    border-radius: 55px;
    z-index: -1;
    opacity: 0.3;
}

.sumq-logo:hover {
    transform: perspective(500px) rotateX(10deg) translateY(-5px);
    transition: all 0.3s ease;
}

/* URL 입력 컨테이너 */
.url-container {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 25px;
    padding: 2rem;
    margin: 2rem auto;
    max-width: 500px;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    border: 2px solid rgba(255, 255, 255, 0.3);
}

/* 입력 필드 - 깔끔한 스타일 */
.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.9);
    border: 3px solid #E53E3E;
    border-radius: 20px;
    color: #2D3748;
    font-family: 'Noto Sans JP', sans-serif;
    font-size: 18px;
    padding: 1rem 1.5rem;
    box-shadow: 0 5px 15px rgba(229, 62, 62, 0.2);
    transition: all 0.3s ease;
    text-align: center;
}

.stTextInput > div > div > input:focus {
    border-color: #C53030;
    box-shadow: 0 0 0 4px rgba(229, 62, 62, 0.2);
    outline: none;
    transform: translateY(-2px);
}

.stTextInput > div > div > input::placeholder {
    color: #A0AEC0;
    font-weight: 300;
}

/* 메인 버튼 - SUM-Q 스타일 */
.stButton > button[kind="primary"] {
    background: linear-gradient(145deg, #E53E3E 0%, #C53030 100%);
    color: #FFFFFF;
    border: none;
    border-radius: 20px;
    font-family: 'Fredoka One', cursive;
    font-weight: 400;
    font-size: 18px;
    padding: 1rem 2.5rem;
    transition: all 0.3s ease;
    text-transform: none;
    letter-spacing: 1px;
    box-shadow: 0 8px 20px rgba(229, 62, 62, 0.3);
    width: 100%;
    margin-top: 1rem;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(145deg, #C53030 0%, #9B2C2C 100%);
    box-shadow: 0 12px 30px rgba(229, 62, 62, 0.4);
    transform: translateY(-3px);
}

/* 예시 버튼들 - 간소화 */
.stButton > button {
    background: rgba(255, 255, 255, 0.8);
    color: #4A5568;
    border: 2px solid #E2E8F0;
    border-radius: 15px;
    font-family: 'Noto Sans JP', sans-serif;
    font-weight: 500;
    font-size: 14px;
    padding: 0.75rem 1rem;
    transition: all 0.3s ease;
    text-transform: none;
}

.stButton > button:hover {
    background: rgba(229, 62, 62, 0.1);
    border-color: #E53E3E;
    color: #E53E3E;
    transform: translateY(-2px);
}

/* 예시 버튼 컨테이너 */
.example-buttons {
    display: flex;
    gap: 0.75rem;
    justify-content: center;
    margin: 1.5rem 0;
    flex-wrap: wrap;
}

/* 숨김 처리 */
.stProgress, 
.stSuccess, 
.stWarning, 
.stError, 
.stInfo {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 15px;
    border: none;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

/* 깔끔한 텍스트 */
.stMarkdown {
    color: #4A5568;
    font-family: 'Noto Sans JP', sans-serif;
}

/* 스크롤바 간소화 */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: #E53E3E;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #C53030;
}
</style>
""", unsafe_allow_html=True)

# Session State 초기화
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "selected_url" not in st.session_state:
    st.session_state.selected_url = ""

# API 키 자동 로드 (환경 변수에서)
env_api_key = os.getenv("OPENAI_API_KEY", "")
if env_api_key:
    os.environ["OPENAI_API_KEY"] = env_api_key

# 메인 앱 - SUM-Q 미니멀 디자인
st.markdown("""
<div class="sumq-logo">
SUM-Q
</div>
""", unsafe_allow_html=True)



# URL 입력
youtube_url = st.text_input(
    "YouTube URL",
    value=st.session_state.get("selected_url", ""),
    placeholder="🎬 YouTube URL을 입력하세요",
    help="YouTube 비디오 URL을 입력하세요",
    label_visibility="collapsed"
)

# 요약 버튼
process_button = st.button("✨ 요약 시작하기", type="primary", use_container_width=True)

# 예시 URLs - 간단하게
st.markdown("<div style='text-align: center; margin: 2rem 0 1rem 0; color: #A0AEC0; font-size: 0.9rem;'>또는 예시로 체험해보세요</div>", unsafe_allow_html=True)

example_urls = [
    ("⚽ 축구", "https://youtu.be/FI8ozR1NLbA?si=EBTyq171a-vdTQB5"),
    ("🎵 음악", "https://youtu.be/dQw4w9WgXcQ"),
    ("📚 교육", "https://youtu.be/aircAruvnKk")
]

cols = st.columns(len(example_urls))
for i, (title, url) in enumerate(example_urls):
    with cols[i]:
        if st.button(f"{title}", key=f"example_{i}"):
            st.session_state.selected_url = url
            st.rerun()

# URL이 변경되면 session state 업데이트
if youtube_url != st.session_state.get("selected_url", ""):
    st.session_state.selected_url = youtube_url

# 요약 처리
if process_button and youtube_url:
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🎬 요약 생성 중...")
        progress_bar.progress(50)
        
        # Flow 실행
        flow = create_youtube_processor_flow()
        shared = {"url": youtube_url}
        flow.run(shared)
        
        progress_bar.progress(100)
        status_text.text("✅ 완료!")
        
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        # 결과 표시
        if "html_output" in shared:
            # HTML 요약 표시
            st.markdown(shared["html_output"], unsafe_allow_html=True)
            
            # 다운로드
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📄 HTML 다운로드",
                    data=shared["html_output"],
                    file_name=f"sum-q_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )
            with col2:
                if "final_topics" in shared:
                    summary_data = {
                        "video_info": shared.get("video_info", {}),
                        "topics": shared.get("final_topics", [])
                    }
                    st.download_button(
                        label="📊 JSON 다운로드",
                        data=json.dumps(summary_data, ensure_ascii=False, indent=2),
                        file_name=f"sum-q_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
        else:
            st.error("❌ 요약 생성 실패")
            
    except Exception as e:
        st.error(f"❌ 오류: {str(e)}")

elif process_button and not youtube_url:
    st.warning("⚠️ YouTube URL을 입력해주세요!")

 