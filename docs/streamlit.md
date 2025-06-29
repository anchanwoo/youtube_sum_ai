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
   - https://share.streamlit.io/ 방문
   - GitHub 계정으로 로그인

2. **새 앱 배포**
   - "New app" 클릭
   - Repository: `anchanwoo/youtube_sum_ai`
   - Branch: `main`
   - Main file path: `streamlit_app.py`

3. **환경 변수 설정**
   - "Advanced settings" 클릭
   - Secrets에 다음 추가:
   ```toml
   OPENAI_API_KEY = "your_openai_api_key_here"
   
   # 노션 설정 (선택사항)
   NOTION_TOKEN = "your_notion_token_here"
   NOTION_DATABASE_ID = "your_database_id_here"
   ```

4. **배포 완료!**
   - 몇 분 후 https://your-app-name.streamlit.app/ 형태의 URL 생성
   - 이 URL을 핸드폰 브라우저에서 바로 접속 가능! 📱

### 3. 로컬 네트워크 접근 (임시)
현재 바로 테스트하려면:
```bash
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501
```
- 같은 WiFi의 핸드폰에서 `http://192.168.55.183:8501` 접속

## 장점
- ✅ 무료
- ✅ 24시간 접근 가능
- ✅ 자동 HTTPS
- ✅ GitHub 연동 자동 배포
- ✅ 핸드폰 최적화

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

## 🚀 무료 호스팅으로 핸드폰에서도 접근하기

### 1. GitHub에 코드 업로드 (이미 완료됨!)
✅ 이미 GitHub에 업로드되어 있음: https://github.com/anchanwoo/youtube_sum_ai.git

### 2. Streamlit Cloud 가입 및 배포

1. **Streamlit Cloud 접속**
   - https://share.streamlit.io/ 방문
   - GitHub 계정으로 로그인

2. **새 앱 배포**
   - "New app" 클릭
   - Repository: `anchanwoo/youtube_sum_ai`
   - Branch: `main`
   - Main file path: `streamlit_app.py`

3. **환경 변수 설정**
   - "Advanced settings" 클릭
   - Secrets에 다음 추가:
   ```toml
   OPENAI_API_KEY = "your_openai_api_key_here"
   
   # 노션 설정 (선택사항)
   NOTION_TOKEN = "your_notion_token_here"
   NOTION_DATABASE_ID = "your_database_id_here"
   ```

4. **배포 완료!**
   - 몇 분 후 https://your-app-name.streamlit.app/ 형태의 URL 생성
   - 24시간 접근 가능
   - 컴퓨터 꺼져도 작동

---

## 💰 API 비용 관리

### 📊 예상 비용 (OpenAI GPT-4)
- **비디오 1개 요약**: $0.50 ~ $2.00
- **월 100개 요약**: $50 ~ $200
- **Streamlit 호스팅**: 완전 무료 🆓

### 🛡️ 비용 제한 설정 (추천!)

1. **OpenAI 계정에서 사용량 제한**
   - https://platform.openai.com/account/billing/limits
   - "Soft limit" 설정: $20/월 (알림)
   - "Hard limit" 설정: $50/월 (차단)

2. **사용량 모니터링**
   - https://platform.openai.com/account/usage
   - 실시간 사용량 확인
   - 일별/월별 통계

3. **저렴한 모델 사용** (선택사항)
   - `utils/call_llm.py`에서 모델 변경
   - `gpt-4o` → `gpt-4o-mini` (약 80% 저렴)
   - `gpt-3.5-turbo` (약 95% 저렴)

### ⚠️ 주의사항
- **API 키 노출 금지**: GitHub에 직접 업로드 절대 금지
- **공유시 주의**: 친구들과 공유할 때 과도한 사용 방지
- **정기 확인**: 월 1회 사용량 체크

---

## 🔒 보안 팁

1. **API 키 관리**
   - 환경 변수로만 사용
   - 정기적으로 키 재생성
   - 의심스러운 활동시 즉시 비활성화

2. **접근 제어** (선택사항)
   - Streamlit 앱에 비밀번호 추가 가능
   - IP 기반 접근 제한 설정 가능

---

## 🚀 확장 방법

### 무료 대안들
1. **Hugging Face Spaces**: Streamlit 앱 호스팅
2. **Render.com**: 무료 웹앱 배포
3. **Railway.app**: 간단한 앱 호스팅

### 유료 업그레이드시
1. **AWS/GCP**: 더 강력한 성능
2. **Vercel**: 더 빠른 로딩
3. **Heroku**: 전문적인 배포 