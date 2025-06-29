# YouTube Video Summarizer - Design Document

## 1. Project Requirements

### Core Entities
- **YouTube Video**: 입력 URL, 비디오 메타데이터 (제목, 썸네일)
- **Transcript**: 비디오의 텍스트 전사본
- **Topics**: 트랜스크립트에서 추출된 흥미로운 주제들
- **Q&A Pairs**: 각 주제에 대한 질문과 답변 쌍
- **Kid-Friendly Explanations**: 5살 아이가 이해할 수 있는 설명
- **HTML Summary**: 최종 시각화된 요약 페이지

### Functional Requirements

1. **Video Input Processing**
   - YouTube URL을 입력으로 받기
   - 비디오 ID, 제목, 썸네일 URL 추출
   - 비디오 트랜스크립트 가져오기

2. **Content Analysis**
   - 트랜스크립트에서 3-5개의 흥미로운 주제 추출
   - 각 주제가 비디오의 핵심 내용을 대표하도록 보장

3. **Q&A Generation**
   - 각 주제에 대해 2-3개의 관련 질문 생성
   - 각 질문에 대한 상세하고 정확한 답변 제공

4. **Kid-Friendly Explanation**
   - 모든 설명을 5살 아이 수준으로 단순화
   - 복잡한 개념을 친근한 비유와 예시로 설명
   - 어려운 단어를 쉬운 단어로 대체

5. **HTML Generation**
   - 요약 내용을 아름다운 HTML 페이지로 생성
   - 비디오 썸네일, 주제별 섹션, Q&A 포함
   - 모바일 친화적이고 읽기 쉬운 디자인

### Entity Interactions Flow
```
YouTube URL → Video Info Extraction → Transcript → Topic Extraction → Q&A Generation → Kid-Friendly Conversion → HTML Generation
```

## 2. Required Utility Functions

### 기존 유틸리티 함수들 (이미 구현됨)
- ✅ `utils/call_llm.py`: OpenAI GPT-4 LLM 호출 (Mock 버전 포함)
- ✅ `utils/youtube_processor.py`: YouTube 비디오 정보 및 트랜스크립트 추출
- ✅ `utils/html_generator.py`: 섹션 기반 HTML 페이지 생성

### 새로 구현된 유틸리티 함수들

#### `utils/topic_extractor.py` ✅
```python
def extract_interesting_topics(transcript: str, num_topics: int = 5, use_mock: bool = False) -> list:
    """
    트랜스크립트에서 흥미로운 주제들을 추출
    
    Args:
        transcript: 비디오 트랜스크립트 텍스트
        num_topics: 추출할 주제 개수
        use_mock: Mock 버전 사용 여부 (API 키 없이 테스트 가능)
    
    Returns:
        주제 리스트: [{"title": "주제명", "content": "관련 내용"}]
    """
```

#### `utils/qa_generator.py` ✅
```python
def generate_qa_pairs(topic_title: str, topic_content: str, num_questions: int = 3, use_mock: bool = False) -> list:
    """
    특정 주제에 대한 Q&A 쌍 생성
    
    Args:
        topic_title: 주제 제목
        topic_content: 주제 관련 내용
        num_questions: 생성할 질문 개수
        use_mock: Mock 버전 사용 여부
    
    Returns:
        Q&A 쌍 리스트: [{"question": "질문", "answer": "답변"}]
    """
```

#### `utils/kid_friendly_converter.py` ✅
```python
def convert_to_kid_friendly(text: str, target_age: int = 5, use_mock: bool = False) -> str:
    """
    복잡한 설명을 아이 친화적으로 변환
    
    Args:
        text: 원본 텍스트
        target_age: 대상 연령 (기본값: 5세)
        use_mock: Mock 버전 사용 여부
    
    Returns:
        아이 친화적으로 변환된 텍스트
    """

def simplify_vocabulary(text: str) -> str:
    """어려운 단어를 쉬운 단어로 대체"""

def add_friendly_examples(text: str, use_mock: bool = False) -> str:
    """친근한 비유와 예시 추가"""
```

#### `utils/content_validator.py` ✅
```python
def validate_transcript_quality(transcript: str) -> dict:
    """
    트랜스크립트 품질 검증 (길이, 언어, 내용 유무 등)
    
    Returns:
        {"is_valid": bool, "issues": [str], "word_count": int}
    """

def ensure_topic_diversity(topics: list) -> list:
    """주제들이 서로 다르고 다양한지 확인"""
```

### API 키 설정

**OpenAI API 키 설정 방법:**
1. https://platform.openai.com 에서 회원가입
2. API keys 메뉴에서 키 생성
3. 환경변수 설정:
   - Windows PowerShell: `$env:OPENAI_API_KEY='your_api_key_here'`
   - Windows CMD: `set OPENAI_API_KEY=your_api_key_here`
   - Mac/Linux: `export OPENAI_API_KEY=your_api_key_here`

**Mock 모드:** API 키가 없어도 모든 함수가 자동으로 Mock 버전으로 작동하여 개발 및 테스트 가능

### 유틸리티 함수 사용 매핑

| 기능 | 사용할 유틸리티 함수 |
|------|-------------------|
| YouTube 데이터 추출 | `youtube_processor.get_video_info()` |
| 주제 추출 | `topic_extractor.extract_interesting_topics()` + `call_llm()` |
| Q&A 생성 | `qa_generator.generate_qa_pairs()` + `call_llm()` |
| 아이 친화적 변환 | `kid_friendly_converter.convert_to_kid_friendly()` + `call_llm()` |
| 내용 검증 | `content_validator.validate_transcript_quality()` |
| HTML 생성 | `html_generator.html_generator()` |

### Next Steps (구현 단계)
1. ✅ 요구사항 정의 완료
2. ✅ 유틸리티 함수 구현 완료
3. 🔄 Flow 설계 (다음 단계)
4. 🔄 데이터 구조 설계 (다음 단계)
5. 🔄 Node 구현 (다음 단계)
6. �� Flow 구현 (다음 단계)

