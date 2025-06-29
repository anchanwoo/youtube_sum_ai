from .call_llm import call_llm, call_llm_mock
import os

def extract_interesting_topics(transcript: str, num_topics: int = 5, use_mock: bool = False) -> list:
    """
    트랜스크립트에서 흥미로운 주제들을 추출
    
    Args:
        transcript: 비디오 트랜스크립트 텍스트
        num_topics: 추출할 주제 개수
        use_mock: True면 Mock 버전 사용 (API 키 없이 테스트 가능)
    
    Returns:
        주제 리스트: [{"title": "주제명", "content": "관련 내용"}]
    """
    # API 키가 없으면 자동으로 Mock 사용
    if not os.getenv("OPENAI_API_KEY"):
        use_mock = True
        print("⚠️ OPENAI_API_KEY가 없어서 Mock 버전을 사용합니다.")
    
    prompt = f"""
다음 비디오 트랜스크립트를 분석하여 가장 흥미로운 주제 {num_topics}개를 추출해주세요.
각 주제는 비디오의 핵심 내용을 대표해야 하며, 서로 다른 관점이나 영역을 다루어야 합니다.

**중요**: 입력 언어가 무엇이든 관계없이 반드시 한국어로 답변해주세요.

트랜스크립트:
{transcript[:3000]}  

다음 JSON 형식으로만 응답해주세요 (다른 설명 없이):
```json
[
    {{
        "title": "주제 제목 (간결하고 명확하게)",
        "content": "해당 주제와 관련된 트랜스크립트의 핵심 내용 요약"
    }},
    {{
        "title": "두 번째 주제 제목",
        "content": "두 번째 주제 관련 내용 요약"
    }}
]
```
"""
    
    try:
        if use_mock:
            response = call_llm_mock(prompt)
        else:
            response = call_llm(prompt, model="gpt-4")
            
        # JSON 부분만 추출
        if "```json" in response:
            json_start = response.find("```json") + 7
            json_end = response.find("```", json_start)
            json_str = response[json_start:json_end].strip()
        else:
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            json_str = response[json_start:json_end] if json_start != -1 and json_end != -1 else response
        
        if json_str:
            import json
            topics = json.loads(json_str)
            return topics[:num_topics]  # 요청한 개수만큼만 반환
        else:
            return []
    except Exception as e:
        print(f"Error extracting topics: {e}")
        return []

def main():
    """테스트용 함수"""
    test_transcript = """
    Artificial intelligence is revolutionizing the way we live and work. 
    From healthcare to transportation, AI is transforming industries.
    However, there are important ethical considerations we must address.
    """
    
    print("=== Mock 버전 테스트 (영어 입력, 한국어 출력) ===")
    topics = extract_interesting_topics(test_transcript, num_topics=3, use_mock=True)
    print("추출된 주제:")
    for i, topic in enumerate(topics, 1):
        print(f"\n{i}. 제목: {topic.get('title', 'No title')}")
        print(f"   내용: {topic.get('content', 'No content')[:100]}...")

if __name__ == "__main__":
    main() 