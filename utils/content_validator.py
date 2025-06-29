import re
from typing import Dict, List

def validate_transcript_quality(transcript: str) -> dict:
    """
    트랜스크립트 품질 검증 (길이, 언어, 내용 유무 등)
    
    Args:
        transcript: 검증할 트랜스크립트
    
    Returns:
        {"is_valid": bool, "issues": [str], "word_count": int}
    """
    issues = []
    
    # 기본 검증
    if not transcript or not transcript.strip():
        issues.append("트랜스크립트가 비어있습니다")
        return {"is_valid": False, "issues": issues, "word_count": 0}
    
    # 단어 수 계산
    word_count = len(transcript.split())
    
    # 최소 길이 검증
    if word_count < 50:
        issues.append(f"트랜스크립트가 너무 짧습니다 (현재: {word_count}단어, 최소: 50단어)")
    
    # 최대 길이 검증 (너무 길면 처리 시간이 오래 걸림)
    if word_count > 10000:
        issues.append(f"트랜스크립트가 너무 깁니다 (현재: {word_count}단어, 최대: 10000단어)")
    
    # 의미 있는 내용 검증
    meaningful_content_ratio = _check_meaningful_content(transcript)
    if meaningful_content_ratio < 0.3:  # 30% 미만이면 의미있는 내용이 부족
        issues.append("의미있는 내용이 부족합니다 (반복되는 단어나 무의미한 내용이 많음)")
    
    # 언어 검증 (한국어나 영어 내용이 있는지)
    if not _has_valid_language_content(transcript):
        issues.append("인식할 수 있는 언어 내용이 없습니다")
    
    is_valid = len(issues) == 0
    
    return {
        "is_valid": is_valid,
        "issues": issues,
        "word_count": word_count,
        "meaningful_content_ratio": meaningful_content_ratio
    }

def ensure_topic_diversity(topics: List[dict]) -> List[dict]:
    """
    주제들이 서로 다르고 다양한지 확인
    
    Args:
        topics: 주제 리스트 [{"title": str, "content": str}]
    
    Returns:
        다양성이 확보된 주제 리스트
    """
    if not topics:
        return topics
    
    # 중복 제목 제거
    seen_titles = set()
    unique_topics = []
    
    for topic in topics:
        title = topic.get("title", "").lower().strip()
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_topics.append(topic)
    
    # 내용 유사도 검사 (간단한 키워드 기반)
    diverse_topics = []
    for topic in unique_topics:
        if not _is_too_similar_to_existing(topic, diverse_topics):
            diverse_topics.append(topic)
    
    return diverse_topics

def _check_meaningful_content(text: str) -> float:
    """
    텍스트의 의미있는 내용 비율 계산
    
    Returns:
        의미있는 내용의 비율 (0.0 ~ 1.0)
    """
    if not text:
        return 0.0
    
    words = text.split()
    total_words = len(words)
    
    if total_words == 0:
        return 0.0
    
    # 고유 단어 수 계산
    unique_words = set(word.lower() for word in words if len(word) > 2)
    
    # 의미있는 내용 비율 = 고유단어수 / 전체단어수
    # 하지만 너무 엄격하지 않게 조정
    meaningful_ratio = len(unique_words) / total_words
    
    # 0.0 ~ 1.0 범위로 정규화
    return min(meaningful_ratio * 2, 1.0)

def _has_valid_language_content(text: str) -> bool:
    """
    인식 가능한 언어 내용이 있는지 확인
    """
    # 한글 확인
    korean_pattern = re.compile(r'[가-힣]')
    has_korean = bool(korean_pattern.search(text))
    
    # 영어 확인 (최소 3글자 이상의 연속된 알파벳)
    english_pattern = re.compile(r'[a-zA-Z]{3,}')
    has_english = bool(english_pattern.search(text))
    
    # 숫자나 특수문자만 있는 경우 제외
    meaningful_chars = re.sub(r'[^가-힣a-zA-Z]', '', text)
    
    return (has_korean or has_english) and len(meaningful_chars) > 10

def _is_too_similar_to_existing(new_topic: dict, existing_topics: List[dict]) -> bool:
    """
    새 주제가 기존 주제들과 너무 유사한지 확인
    """
    if not existing_topics:
        return False
    
    new_title = new_topic.get("title", "").lower()
    new_content_words = set(new_topic.get("content", "").lower().split())
    
    for existing_topic in existing_topics:
        existing_title = existing_topic.get("title", "").lower()
        existing_content_words = set(existing_topic.get("content", "").lower().split())
        
        # 제목 유사도 확인
        if _calculate_similarity(new_title, existing_title) > 0.7:
            return True
        
        # 내용 유사도 확인 (공통 단어 비율)
        if new_content_words and existing_content_words:
            common_words = new_content_words & existing_content_words
            similarity = len(common_words) / len(new_content_words | existing_content_words)
            if similarity > 0.5:
                return True
    
    return False

def _calculate_similarity(text1: str, text2: str) -> float:
    """
    두 텍스트 간의 유사도 계산 (간단한 방법)
    """
    if not text1 or not text2:
        return 0.0
    
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    return len(intersection) / len(union) if union else 0.0

def main():
    """테스트용 함수"""
    # 테스트 트랜스크립트
    test_transcript = """
    안녕하세요 여러분! 오늘은 인공지능에 대해 이야기해보겠습니다.
    AI는 우리 생활을 많이 바꾸고 있어요. 스마트폰에서부터 자동차까지
    곳곳에서 인공지능 기술을 만날 수 있습니다.
    """
    
    print("Transcript validation:")
    validation_result = validate_transcript_quality(test_transcript)
    print(f"Valid: {validation_result['is_valid']}")
    print(f"Word count: {validation_result['word_count']}")
    print(f"Issues: {validation_result['issues']}")
    
    # 테스트 주제들
    test_topics = [
        {"title": "인공지능의 발전", "content": "AI 기술이 빠르게 발전하고 있습니다"},
        {"title": "인공지능의 발전", "content": "다른 내용이지만 제목이 같습니다"},
        {"title": "머신러닝 기술", "content": "기계학습은 AI의 핵심 기술입니다"},
        {"title": "AI의 활용", "content": "AI 기술이 빠르게 발전하고 있습니다"}  # 내용 유사
    ]
    
    print("\nTopic diversity check:")
    diverse_topics = ensure_topic_diversity(test_topics)
    print(f"Original topics: {len(test_topics)}")
    print(f"Diverse topics: {len(diverse_topics)}")
    for topic in diverse_topics:
        print(f"- {topic['title']}")

if __name__ == "__main__":
    main() 