from .call_llm import call_llm, call_llm_mock
import os

def generate_qa_pairs(topic_title: str, topic_content: str, num_questions: int = 3, use_mock: bool = False) -> list:
    """
    특정 주제에 대한 Q&A 쌍 생성
    
    Args:
        topic_title: 주제 제목
        topic_content: 주제 관련 내용
        num_questions: 생성할 질문 개수
        use_mock: True면 Mock 버전 사용 (API 키 없이 테스트 가능)
    
    Returns:
        Q&A 쌍 리스트: [{"question": "질문", "answer": "답변"}]
    """
    # API 키가 없으면 자동으로 Mock 사용
    if not os.getenv("OPENAI_API_KEY"):
        use_mock = True
        print("⚠️ OPENAI_API_KEY가 없어서 Mock 버전을 사용합니다.")
    
    prompt = f"""
다음 주제와 내용을 바탕으로 {num_questions}개의 흥미로운 질문과 답변을 생성해주세요.
질문은 호기심을 자극하고 학습에 도움이 되어야 합니다.
답변은 상세하고 이해하기 쉬워야 합니다.

주제: {topic_title}
내용: {topic_content}

다음 JSON 형식으로만 응답해주세요 (다른 설명 없이):
```json
[
    {{
        "question": "구체적이고 흥미로운 질문",
        "answer": "상세하고 이해하기 쉬운 답변"
    }},
    {{
        "question": "두 번째 질문",
        "answer": "두 번째 답변"
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
            qa_pairs = json.loads(json_str)
            return qa_pairs[:num_questions]  # 요청한 개수만큼만 반환
        else:
            return []
    except Exception as e:
        print(f"Error generating Q&A pairs: {e}")
        return []

def main():
    """테스트용 함수"""
    test_title = "인공지능의 사회적 영향"
    test_content = "AI는 헬스케어부터 교통까지 많은 산업을 혁신하고 있습니다. 하지만 윤리적 고려사항도 중요합니다."
    
    print("=== Mock 버전 테스트 ===")
    qa_pairs = generate_qa_pairs(test_title, test_content, num_questions=2, use_mock=True)
    print("생성된 Q&A:")
    for i, pair in enumerate(qa_pairs, 1):
        print(f"\n{i}. Q: {pair.get('question', 'No question')}")
        print(f"   A: {pair.get('answer', 'No answer')[:200]}...")

if __name__ == "__main__":
    main() 