import streamlit as st
import os
import time
from datetime import datetime
from flow import create_youtube_processor_flow
import json

# 페이지 설정
st.set_page_config(
    page_title="YouTube 5살 아이용 요약기",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바에 설정
st.sidebar.title("⚙️ 설정")

# Session State 초기화 (맨 위로 이동)
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "selected_url" not in st.session_state:
    st.session_state.selected_url = ""

# API 키 자동 로드 (환경 변수에서)
env_api_key = os.getenv("OPENAI_API_KEY", "")

# API 키 설정
st.sidebar.markdown("### 🔑 API 키 설정")

# 환경 변수에서 API 키가 있으면 표시
if env_api_key:
    st.sidebar.success("✅ API 키가 환경 변수에서 자동 로드되었습니다!")
    os.environ["OPENAI_API_KEY"] = env_api_key
    
    # 환경 변수 키의 일부만 표시 (보안)
    if len(env_api_key) > 16:
        masked_key = env_api_key[:12] + "..." + env_api_key[-4:]
    else:
        masked_key = env_api_key[:4] + "..." + env_api_key[-2:]
    st.sidebar.code(f"🔐 {masked_key}")
    
else:
    # API 키 입력
    api_key_input = st.sidebar.text_input(
        "OpenAI API Key",
        value=st.session_state.api_key,
        type="password",
        help="OpenAI API 키를 입력하세요. 세션 동안 자동으로 기억됩니다.",
        placeholder="sk-proj-..."
    )
    
    # API 키 상태 업데이트
    if api_key_input:
        st.session_state.api_key = api_key_input
        os.environ["OPENAI_API_KEY"] = api_key_input
        st.sidebar.success("✅ API 키가 설정되었습니다! (세션 동안 유지)")
        
        # 키의 일부만 표시 (보안)
        if len(api_key_input) > 16:
            masked_key = api_key_input[:12] + "..." + api_key_input[-4:]
        else:
            masked_key = api_key_input[:4] + "..." + api_key_input[-2:]
        st.sidebar.code(f"🔐 {masked_key}")
        
    else:
        st.sidebar.warning("⚠️ Mock 모드로 동작합니다")
        st.sidebar.info("💡 실제 요약을 위해서는 OpenAI API 키가 필요합니다")

# API 키 지우기 버튼
if st.session_state.api_key or env_api_key:
    if st.sidebar.button("🗑️ API 키 지우기"):
        st.session_state.api_key = ""
        if "OPENAI_API_KEY" in os.environ and not env_api_key:
            del os.environ["OPENAI_API_KEY"]
        st.rerun()

# API 키 사용법 도움말
with st.sidebar.expander("❓ API 키 사용법"):
    st.markdown("""
    ### 🔑 API 키 얻는 방법
    1. [OpenAI 웹사이트](https://platform.openai.com) 방문
    2. 계정 생성 또는 로그인
    3. "API Keys" 메뉴에서 새 키 생성
    4. 여기에 붙여넣기
    
    ### 💡 팁
    - **세션 유지**: 탭을 닫지 않으면 계속 기억됩니다
    - **환경 변수**: `.env` 파일에 저장하면 자동 로드
    - **Mock 모드**: API 키 없이도 테스트 가능
    
    ### 🔒 보안
    - API 키는 메모리에만 저장됩니다
    - 브라우저 종료 시 자동 삭제
    - 서버에 전송되지 않음
    """)

# 노션 연동 설정 (나중에 추가)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📝 노션 연동 (곧 출시)")
notion_token = st.sidebar.text_input("노션 토큰", type="password", disabled=True)
database_id = st.sidebar.text_input("데이터베이스 ID", disabled=True)

# 메인 앱
st.title("📺 YouTube 5살 아이용 요약기")
st.markdown("""
🌟 **YouTube 비디오를 5살 아이가 이해할 수 있게 요약해드려요!**

- 🤖 AI가 자동으로 흥미로운 주제 추출
- 👶 5살 아이도 이해할 수 있는 쉬운 설명
- 🌍 다국어 비디오 → 한국어 요약
- ⚡ MapReduce로 빠른 처리 (기존 대비 6배 빠름!)
""")

# URL 입력
st.markdown("### 🎬 YouTube URL 입력")
col1, col2 = st.columns([3, 1])

with col1:
    youtube_url = st.text_input(
        "YouTube URL",
        value=st.session_state.get("selected_url", ""),
        placeholder="https://youtu.be/... 또는 https://www.youtube.com/watch?v=...",
        help="YouTube 비디오 URL을 입력하세요",
        label_visibility="collapsed"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)  # 높이 맞추기
    process_button = st.button("🚀 요약하기", type="primary", use_container_width=True)

# 예시 URLs
st.markdown("**📋 예시 URLs (클릭해서 테스트):**")
example_urls = [
    ("한국어 비디오", "https://youtu.be/FI8ozR1NLbA?si=EBTyq171a-vdTQB5"),
    ("Rick Roll 🎵", "https://youtu.be/dQw4w9WgXcQ"),
    ("교육 영상", "https://youtu.be/aircAruvnKk")
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
        # 프로그레스 바와 상태 메시지
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔍 YouTube 비디오 정보 가져오는 중...")
        progress_bar.progress(10)
        
        # Flow 실행
        flow = create_youtube_processor_flow()
        shared = {"url": youtube_url}
        
        status_text.text("📝 비디오 트랜스크립트 추출 중...")
        progress_bar.progress(30)
        
        start_time = time.time()
        
        # 실제 처리 (백그라운드에서 실행)
        with st.spinner("🤖 AI가 열심히 요약 중입니다... (1-2분 소요)"):
            flow.run(shared)
        
        processing_time = time.time() - start_time
        
        progress_bar.progress(100)
        status_text.text("✅ 요약 완료!")
        
        # 결과 표시
        if "html_output" in shared and shared["html_output"]:
            st.success(f"🎉 요약이 완성되었습니다! (처리 시간: {processing_time:.1f}초)")
            
            # 비디오 정보 표시
            video_info = shared.get("video_info", {})
            if video_info:
                st.markdown("### 📹 비디오 정보")
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if video_info.get("thumbnail_url"):
                        st.image(video_info["thumbnail_url"], width=300)
                
                with col2:
                    st.markdown(f"**제목:** {video_info.get('title', 'Unknown')}")
                    st.markdown(f"**비디오 ID:** {video_info.get('video_id', 'Unknown')}")
                    st.markdown(f"**언어:** {video_info.get('language_used', 'Unknown')}")
                    st.markdown(f"**트랜스크립트 길이:** {len(video_info.get('transcript', ''))} 글자")
            
            # HTML 요약 표시
            st.markdown("### 📄 요약 결과")
            
            # HTML을 컴포넌트로 렌더링
            st.components.v1.html(
                shared["html_output"], 
                height=800, 
                scrolling=True
            )
            
            # 다운로드 및 공유 옵션
            st.markdown("### 💾 다운로드 & 공유")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # HTML 파일 다운로드
                video_id = video_info.get('video_id', 'unknown')
                filename = f"youtube_summary_{video_id}.html"
                
                st.download_button(
                    label="📥 HTML 파일 다운로드",
                    data=shared["html_output"],
                    file_name=filename,
                    mime="text/html",
                    use_container_width=True
                )
            
            with col2:
                # JSON 데이터 다운로드
                summary_data = {
                    "video_info": video_info,
                    "topics": shared.get("final_topics", []),
                    "processed_at": datetime.now().isoformat(),
                    "processing_time": processing_time
                }
                
                st.download_button(
                    label="📊 JSON 데이터 다운로드",
                    data=json.dumps(summary_data, ensure_ascii=False, indent=2),
                    file_name=f"youtube_data_{video_id}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col3:
                # 노션 저장 (나중에 구현)
                st.button(
                    "📝 노션에 저장 (곧 출시)",
                    disabled=True,
                    use_container_width=True,
                    help="노션 연동 기능은 곧 추가될 예정입니다!"
                )
        else:
            st.error("❌ 요약 생성에 실패했습니다. URL을 확인해주세요.")
            
    except Exception as e:
        st.error(f"❌ 오류가 발생했습니다: {str(e)}")
        st.info("💡 문제가 계속 발생하면 다른 YouTube URL로 시도해보세요.")

elif process_button and not youtube_url:
    st.error("❌ YouTube URL을 입력해주세요!")

# 사용법 가이드
st.markdown("---")
with st.expander("📖 사용법 가이드"):
    st.markdown("""
    ### 🎯 사용 방법
    1. **YouTube URL 입력**: 요약하고 싶은 YouTube 비디오 링크를 붙여넣으세요
    2. **API 키 설정** (선택): 더 좋은 품질을 원하면 OpenAI API 키를 입력하세요
    3. **요약하기 클릭**: AI가 자동으로 5살 아이용 요약을 만들어줍니다
    4. **결과 확인**: 생성된 요약을 웹에서 바로 확인하거나 파일로 다운로드하세요
    
    ### ⚡ 특징
    - **빠른 처리**: MapReduce 병렬 처리로 6배 빠른 속도
    - **다국어 지원**: 영어, 일본어 등 → 한국어 요약
    - **아이 친화적**: 5살 아이도 이해할 수 있는 쉬운 설명
    - **모바일 지원**: 스마트폰에서도 완벽하게 작동
    
    ### 🔧 기술 스택
    - **AI**: OpenAI GPT-4
    - **패턴**: MapReduce 병렬 처리
    - **프레임워크**: PocketFlow + Streamlit
    - **배포**: Streamlit Cloud
    """)

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    Made with ❤️ using <a href='https://streamlit.io'>Streamlit</a> & 
    <a href='https://github.com/the-pocket/PocketFlow'>PocketFlow</a><br>
    🚀 <a href='https://github.com/anchanwoo/youtube_sum_ai'>GitHub Repository</a>
</div>
""", unsafe_allow_html=True) 