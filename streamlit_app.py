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
    background: 
        /* 반투명 오버레이 - 더 투명하게 */
        linear-gradient(
            135deg,
            rgba(240, 248, 255, 0.65) 0%,
            rgba(255, 255, 255, 0.45) 50%,
            rgba(240, 248, 255, 0.65) 100%
        ),
        /* 삿포로 거리 이미지 - 사용자 제공 이미지 */
        url('./assets/sapporo_street.jpg'),
        /* 폴백 이미지 */
        url('https://images.unsplash.com/photo-1590559899731-a382839e5549?q=80&w=2068&auto=format&fit=crop')
        center/cover no-repeat fixed;
    font-family: 'Noto Sans JP', sans-serif;
    min-height: 100vh;
    position: relative;
}

/* 배경 이미지 폴백 - 삿포로 거리 스타일 그라데이션 */
.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        /* 삿포로 거리 스타일 */
        linear-gradient(
            135deg,
            rgba(135, 206, 235, 0.3) 0%,
            rgba(176, 224, 230, 0.2) 30%,
            rgba(240, 248, 255, 0.1) 70%,
            rgba(255, 250, 240, 0.2) 100%
        ),
        /* 도시 건물 실루엣 */
        linear-gradient(
            to top,
            rgba(70, 130, 180, 0.1) 0%,
            rgba(70, 130, 180, 0.05) 30%,
            transparent 60%
        );
    z-index: -2;
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

/* SUM-Q 로고 - 일본 도시 스타일 */
.sumq-logo {
    background: linear-gradient(145deg, #2D3748 0%, #4A5568 50%, #1A202C 100%);
    color: #FFFFFF;
    font-family: 'Fredoka One', cursive;
    font-size: 4rem;
    text-align: center;
    padding: 2rem 3rem;
    border-radius: 50px;
    margin: 3rem auto 2rem auto;
    width: fit-content;
    box-shadow: 
        0 8px 25px rgba(45, 55, 72, 0.4),
        inset 0 4px 8px rgba(255, 255, 255, 0.3),
        inset 0 -4px 8px rgba(0, 0, 0, 0.2);
    transform: perspective(500px) rotateX(10deg);
    position: relative;
    letter-spacing: 2px;
    border: 2px solid rgba(255, 255, 255, 0.2);
}

.sumq-logo::before {
    content: "";
    position: absolute;
    top: -5px;
    left: -5px;
    right: -5px;
    bottom: -5px;
    background: linear-gradient(145deg, #4A5568, #2D3748);
    border-radius: 55px;
    z-index: -1;
    opacity: 0.3;
}

.sumq-logo:hover {
    transform: perspective(500px) rotateX(10deg) translateY(-5px);
    transition: all 0.3s ease;
    box-shadow: 
        0 12px 35px rgba(45, 55, 72, 0.5),
        inset 0 4px 8px rgba(255, 255, 255, 0.4),
        inset 0 -4px 8px rgba(0, 0, 0, 0.3);
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

/* 입력 필드 - 일본 도시 스타일 */
.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.92);
    border: 3px solid #4299E1;
    border-radius: 20px;
    color: #2D3748;
    font-family: 'Noto Sans JP', sans-serif;
    font-size: 18px;
    padding: 1rem 1.5rem;
    box-shadow: 0 5px 15px rgba(66, 153, 225, 0.2);
    transition: all 0.3s ease;
    text-align: center;
    backdrop-filter: blur(5px);
}

.stTextInput > div > div > input:focus {
    border-color: #3182CE;
    box-shadow: 0 0 0 4px rgba(66, 153, 225, 0.2);
    outline: none;
    transform: translateY(-2px);
    background: rgba(255, 255, 255, 0.95);
}

.stTextInput > div > div > input::placeholder {
    color: #A0AEC0;
    font-weight: 300;
}

/* 메인 버튼 - 일본 도시 스타일 */
.stButton > button[kind="primary"] {
    background: linear-gradient(145deg, #4299E1 0%, #3182CE 100%);
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
    box-shadow: 0 8px 20px rgba(66, 153, 225, 0.3);
    width: 100%;
    margin-top: 1rem;
    border: 2px solid rgba(255, 255, 255, 0.2);
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(145deg, #3182CE 0%, #2B6CB0 100%);
    box-shadow: 0 12px 30px rgba(66, 153, 225, 0.4);
    transform: translateY(-3px);
    border-color: rgba(255, 255, 255, 0.3);
}

/* 중단 버튼 - 빨간색 스타일 */
.stButton > button[kind="secondary"] {
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
    border: 2px solid rgba(255, 255, 255, 0.2);
    animation: pulse 2s infinite;
}

.stButton > button[kind="secondary"]:hover {
    background: linear-gradient(145deg, #C53030 0%, #9C2A2A 100%);
    box-shadow: 0 12px 30px rgba(229, 62, 62, 0.5);
    transform: translateY(-3px);
    border-color: rgba(255, 255, 255, 0.3);
}

/* 중단 버튼 펄스 애니메이션 */
@keyframes pulse {
    0% { box-shadow: 0 8px 20px rgba(229, 62, 62, 0.3); }
    50% { box-shadow: 0 12px 30px rgba(229, 62, 62, 0.6); }
    100% { box-shadow: 0 8px 20px rgba(229, 62, 62, 0.3); }
}
</style>
""", unsafe_allow_html=True)

# 페이지 나가기 전 경고 JavaScript + 추가 스타일
st.markdown("""
<script>
// 페이지 나가기 전 경고 (처리 중일 때만)
window.addEventListener('beforeunload', function (e) {
    // Streamlit session state를 직접 확인할 수는 없으므로 
    // 중단 버튼이 존재하는지로 판단
    const stopButton = document.querySelector('button[kind="secondary"]');
    if (stopButton) {
        e.preventDefault();
        e.returnValue = '요약이 진행 중입니다. 페이지를 나가면 처리가 중단됩니다. 정말 나가시겠습니까?';
        return e.returnValue;
    }
});
</script>

<style>
/* 추가 스타일 - 깔끔한 UI */
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
if "processing" not in st.session_state:
    st.session_state.processing = False
if "should_stop" not in st.session_state:
    st.session_state.should_stop = False

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

# 버튼 영역 - 상태에 따라 버튼 변경
if not st.session_state.processing:
    # 요약 시작 버튼 (파란색)
    process_button = st.button("✨ 요약 시작하기", type="primary", use_container_width=True)
    stop_button = False
else:
    # 중단 버튼 (빨간색, 펄스 애니메이션)
    stop_button = st.button("🛑 중단하기", type="secondary", use_container_width=True)
    if stop_button:
        st.session_state.should_stop = True
    process_button = False

# URL이 변경되면 session state 업데이트
if youtube_url != st.session_state.get("selected_url", ""):
    st.session_state.selected_url = youtube_url

# 요약 처리
if process_button and youtube_url:
    try:
        # 처리 시작
        st.session_state.processing = True
        st.session_state.should_stop = False
        st.rerun()
        
    except InterruptedError:
        st.session_state.processing = False
        st.session_state.should_stop = False
        st.warning("🛑 사용자가 처리를 중단했습니다.")
        
    except Exception as e:
        st.session_state.processing = False
        # 친화적인 에러 메시지 표시
        if "자막" in str(e) or "transcript" in str(e).lower():
            st.error(str(e))
            # 추천 비디오 제안
            st.info("🎯 **자막이 있는 추천 비디오들:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("⚽ 축구 영상", use_container_width=True):
                    st.session_state.selected_url = "https://youtu.be/FI8ozR1NLbA?si=EBTyq171a-vdTQB5"
                    st.rerun()
            with col2:
                if st.button("🎵 음악 영상", use_container_width=True):
                    st.session_state.selected_url = "https://youtu.be/dQw4w9WgXcQ"
                    st.rerun()
            with col3:
                if st.button("📚 교육 영상", use_container_width=True):
                    st.session_state.selected_url = "https://youtu.be/kJQP7kiw5Fk"
                    st.rerun()
        else:
            st.error(f"❌ 오류: {str(e)}")

elif process_button and not youtube_url:
    st.warning("⚠️ YouTube URL을 입력해주세요!")

# 실제 처리 로직 (처리 중일 때만 실행)
if st.session_state.processing:
    try:
        # 진행 상황 표시
        st.info("🎬 요약 생성 중... 중단하려면 위의 빨간 버튼을 클릭하세요!")
        
        progress_bar = st.progress(0)
        status_container = st.container()
        
        with status_container:
            status_text = st.empty()
            detail_text = st.empty()
            
        # 진행상황 업데이트 함수
        def update_progress(stage, message, progress=None):
            if progress is not None:
                progress_bar.progress(progress)
            status_text.text(f"📍 {stage}")
            detail_text.info(f"ℹ️ {message}")
            
        update_progress("초기화", "YouTube 처리 시스템 준비 중...", 5)
        
        # 중단 확인
        if st.session_state.should_stop:
            st.warning("🛑 사용자가 중단했습니다.")
            st.session_state.processing = False
            st.session_state.should_stop = False
            st.rerun()
            
        # Flow 실행
        flow = create_youtube_processor_flow()
        
        # 공유된 상태에 progress callback 추가
        shared = {
            "url": youtube_url, 
            "stop_flag": st.session_state,
            "progress_callback": update_progress  # 실시간 업데이트 함수
        }
        
        update_progress("비디오 처리", "YouTube 비디오 정보 가져오는 중...", 10)
        
        # 중단 확인
        if st.session_state.should_stop:
            st.warning("🛑 사용자가 중단했습니다.")
            st.session_state.processing = False
            st.session_state.should_stop = False
            st.rerun()
        
        # 단계별 진행상황 업데이트
        try:
            # 실제 Flow 실행
            update_progress("주제 추출", "흥미로운 주제 5개 찾는 중...", 25)
            
            # Flow 실행 (실제 처리는 여기서)
            flow.run(shared)
            
            # 완료
            progress_bar.progress(100)
            status_text.text("✅ 모든 단계 완료!")
            detail_text.success("🎉 YouTube 비디오 요약이 성공적으로 생성되었습니다!")
            
        except Exception as flow_error:
            # Flow 실행 중 에러 처리
            if "중단" in str(flow_error) or "InterruptedError" in str(type(flow_error).__name__):
                st.warning("🛑 사용자가 중단했습니다.")
            else:
                raise flow_error
        
        # 중단 확인
        if st.session_state.should_stop:
            st.warning("🛑 사용자가 중단했습니다.")
            st.session_state.processing = False
            st.session_state.should_stop = False
            st.rerun()
        
        # 처리 완료
        st.session_state.processing = False
        
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        detail_text.empty()
        
        # 결과 표시
        if "html_output" in shared:
            # 노션 저장 결과 먼저 표시
            if "notion_result" in shared:
                notion_result = shared["notion_result"]
                if notion_result.get("success"):
                    st.success(f"🎉 노션에 저장 완료!")
                    st.markdown(f"📝 [노션 페이지 보기]({notion_result.get('page_url')})")
                else:
                    # 노션 설정이 없으면 안내 메시지
                    if "노션 설정이 없습니다" in notion_result.get("error", ""):
                        st.info("💡 **노션 연결하고 싶으신가요?**  \n.env 파일에 `NOTION_TOKEN`과 `NOTION_DATABASE_ID`를 추가하면 자동으로 노션에도 저장됩니다!")
                    else:
                        st.warning(f"⚠️ 노션 저장 실패: {notion_result.get('error', '알 수 없는 오류')}")
            
            # 처리 결과 요약 표시
            if "final_topics" in shared:
                st.success("🎯 **처리 완료 요약**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📝 추출된 주제", len(shared["final_topics"]))
                with col2:
                    total_qa = sum(len(topic["qa_pairs"]) for topic in shared["final_topics"])
                    st.metric("❓ 생성된 Q&A", total_qa)
                with col3:
                    video_info = shared.get("video_info", {})
                    duration = video_info.get("duration", "N/A")
                    st.metric("⏱️ 비디오 길이", duration)
            
            # HTML 요약 표시
            st.markdown(shared["html_output"], unsafe_allow_html=True)
            
            # 다운로드
            col1, col2 = st.columns(2)
            with col1:
                # 파일용 HTML 다운로드
                download_html = shared.get("file_html", shared["html_output"])
                st.download_button(
                    label="📄 HTML 다운로드",
                    data=download_html,
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
            
    except InterruptedError:
        st.session_state.processing = False
        st.session_state.should_stop = False
        st.warning("🛑 사용자가 처리를 중단했습니다.")
        
    except Exception as e:
        st.session_state.processing = False
        # 친화적인 에러 메시지 표시
        if "자막" in str(e) or "transcript" in str(e).lower():
            st.error(str(e))
            # 추천 비디오 제안
            st.info("🎯 **자막이 있는 추천 비디오들:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("⚽ 축구 영상", key="rec1", use_container_width=True):
                    st.session_state.selected_url = "https://youtu.be/FI8ozR1NLbA?si=EBTyq171a-vdTQB5"
                    st.rerun()
            with col2:
                if st.button("🎵 음악 영상", key="rec2", use_container_width=True):
                    st.session_state.selected_url = "https://youtu.be/dQw4w9WgXcQ"
                    st.rerun()
            with col3:
                if st.button("📚 교육 영상", key="rec3", use_container_width=True):
                    st.session_state.selected_url = "https://youtu.be/kJQP7kiw5Fk"
                    st.rerun()
        else:
            st.error(f"❌ 오류: {str(e)}")

 