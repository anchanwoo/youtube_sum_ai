# Streamlit 웹 앱 배포 가이드

## 🚀 로컬 실행
```bash
streamlit run streamlit_app.py
```

브라우저에서 `http://localhost:8501` 접속

## 🌍 Streamlit Cloud 배포

### 1. GitHub 준비
- 코드가 이미 GitHub에 올라가 있음 ✅
- `streamlit_app.py` 파일 존재 ✅  
- `requirements.txt` 업데이트됨 ✅

### 2. Streamlit Cloud 배포 단계

1. **Streamlit Cloud 접속**
   - https://streamlit.io/cloud 방문
   - GitHub 계정으로 로그인

2. **앱 배포**
   - "New app" 클릭
   - Repository: `anchanwoo/youtube_sum_ai`
   - Branch: `main`
   - Main file path: `streamlit_app.py`

3. **환경 변수 설정** (선택사항)
   - Advanced settings에서 Secrets 설정
   - `OPENAI_API_KEY = "your-api-key"`

4. **배포!**
   - "Deploy!" 클릭
   - 2-3분 후 앱이 라이브로 배포됨
   - 고유 URL 생성: `https://your-app-name.streamlit.app`

### 3. 배포 후 기능들

#### 📱 모든 디바이스에서 접근
- PC, 모바일, 태블릿 모두 지원
- 반응형 디자인으로 최적화

#### 🔗 공유 가능한 URL
- 친구들에게 링크만 보내면 바로 사용 가능
- 소셜미디어 공유 가능

#### ⚡ 자동 업데이트
- GitHub에 push하면 자동으로 앱 업데이트
- CI/CD 파이프라인 자동 구성

## 🎯 고급 기능 확장 계획

### 1. 노션 연동 📝
```python
# utils/notion_integration.py (예정)
def save_to_notion(summary_data, notion_token, database_id):
    # 노션 API를 통해 요약 저장
    pass
```

### 2. 사용자 인증 🔐
```python
# 사용자별 요약 히스토리 관리
# Google/GitHub OAuth 연동
```

### 3. 배치 처리 📊
```python
# 여러 YouTube URL 동시 처리
# CSV 파일 업로드로 대량 처리
```

### 4. 고급 분석 📈
```python
# 비디오 감정 분석
# 주제 트렌드 분석
# 키워드 클라우드 생성
```

## 🔧 커스터마이징

### UI 테마 변경
```python
# .streamlit/config.toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### 캐싱 최적화
```python
@st.cache_data
def expensive_computation(url):
    # 비용이 많이 드는 계산 캐싱
    pass
```

## 📊 성능 모니터링

### Streamlit 내장 메트릭
```python
# 앱 사용량 통계 자동 수집
# 사용자 행동 분석
# 성능 병목 지점 파악
```

### 외부 분석 도구 연동
```python
# Google Analytics
# Mixpanel
# Sentry (에러 추적)
```

## 🔒 보안 및 제한사항

### API 키 보안
- Streamlit Secrets 사용 권장
- 환경 변수로 민감 정보 관리
- Mock 모드로 기본 동작

### 사용량 제한
- Streamlit Cloud: 무료 플랜 제한
- OpenAI API: 토큰 사용량 모니터링
- Rate limiting 구현 고려

## 🚀 배포 체크리스트

- [ ] GitHub 저장소 public으로 설정
- [ ] requirements.txt 모든 의존성 포함
- [ ] .env 파일 .gitignore에 추가
- [ ] 에러 핸들링 완료
- [ ] 모바일 반응형 테스트
- [ ] API 키 없이도 동작하는지 확인
- [ ] 사용법 가이드 작성 완료

배포 완료되면 전 세계 누구나 사용할 수 있는 AI 요약 서비스가 탄생합니다! 🌍✨ 