from .call_llm import call_llm, call_llm_mock
import os

def convert_to_kid_friendly(text: str, target_age: int = 5, use_mock: bool = False) -> str:
    """
    복잡한 설명을 아이 친화적으로 변환
    
    Args:
        text: 원본 텍스트
        target_age: 대상 연령 (기본값: 5세)
        use_mock: True면 Mock 버전 사용 (API 키 없이 테스트 가능)
    
    Returns:
        아이 친화적으로 변환된 텍스트
    """
    # API 키가 없으면 자동으로 Mock 사용
    if not os.getenv("OPENAI_API_KEY"):
        use_mock = True
        print("⚠️ OPENAI_API_KEY가 없어서 Mock 버전을 사용합니다.")
    
    prompt = f"""
다음 텍스트를 {target_age}살 아이가 이해할 수 있도록 쉽게 설명해주세요.

원본 텍스트:
{text}

다음 규칙을 따라주세요:
1. 어려운 단어를 쉬운 단어로 바꾸기
2. 복잡한 개념은 친근한 비유나 예시로 설명하기 (동물, 장난감, 일상생활)
3. 짧고 간단한 문장 사용하기
4. "마치 ~처럼", "~와 비슷해" 같은 표현 사용하기
5. 아이들이 재미있어할 수 있도록 친근한 톤으로 작성하기

아이 친화적인 설명만 제공해주세요 (다른 설명 없이):
"""
    
    try:
        if use_mock:
            response = call_llm_mock(prompt)
        else:
            response = call_llm(prompt, model="gpt-4")
        return response.strip()
    except Exception as e:
        print(f"Error converting to kid-friendly: {e}")
        return text  # 실패 시 원본 텍스트 반환

def simplify_vocabulary(text: str) -> str:
    """
    어려운 단어를 쉬운 단어로 대체
    """
    # 일반적인 어려운 단어 -> 쉬운 단어 매핑
    word_mappings = {
        "인공지능": "똑똑한 컴퓨터",
        "AI": "똑똑한 컴퓨터",
        "머신러닝": "컴퓨터 학습",
        "딥러닝": "컴퓨터가 깊게 생각하기",
        "알고리즘": "컴퓨터가 문제를 푸는 방법",
        "데이터": "정보",
        "빅데이터": "아주 많은 정보",
        "클라우드": "인터넷 창고",
        "프로그래밍": "컴퓨터에게 일 시키기",
        "소프트웨어": "컴퓨터 프로그램",
        "하드웨어": "컴퓨터 부품",
        "기술": "새로운 도구",
        "혁신": "새롭고 좋은 변화",
        "개발": "만들기",
        "구현": "실제로 만들기",
        "최적화": "더 좋게 만들기",
        "효율적": "빠르고 좋은",
        "분석": "자세히 살펴보기",
        "시스템": "큰 기계",
        "프로세스": "순서대로 하는 일",
        "인터페이스": "사용하는 방법",
        "플랫폼": "기본 바탕",
        "네트워크": "연결된 길"
    }
    
    simplified_text = text
    for difficult_word, easy_word in word_mappings.items():
        simplified_text = simplified_text.replace(difficult_word, easy_word)
    
    return simplified_text

def add_friendly_examples(text: str, use_mock: bool = False) -> str:
    """
    친근한 비유와 예시 추가
    """
    # API 키가 없으면 자동으로 Mock 사용
    if not os.getenv("OPENAI_API_KEY"):
        use_mock = True
    
    prompt = f"""
다음 텍스트에 아이들이 이해하기 쉬운 비유나 예시를 추가해주세요.
동물, 장난감, 일상생활의 예시를 사용하여 설명을 더 재미있게 만들어주세요.

원본 텍스트:
{text}

비유와 예시가 추가된 텍스트만 제공해주세요:
"""
    
    try:
        if use_mock:
            response = call_llm_mock(prompt)
        else:
            response = call_llm(prompt, model="gpt-4")
        return response.strip()
    except Exception as e:
        print(f"Error adding friendly examples: {e}")
        return text

def main():
    """테스트용 함수"""
    test_text = """
    인공지능은 머신러닝 알고리즘을 통해 데이터를 분석하고 
    패턴을 인식하여 의사결정을 최적화하는 시스템입니다.
    """
    
    print("원본 텍스트:")
    print(test_text)
    
    print("\n단어 단순화:")
    simplified = simplify_vocabulary(test_text)
    print(simplified)
    
    print("\n=== Mock 버전 테스트 ===")
    print("5살 아이 버전:")
    kid_friendly = convert_to_kid_friendly(test_text, use_mock=True)
    print(kid_friendly)

if __name__ == "__main__":
    main() 