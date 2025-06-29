import os
from openai import OpenAI

# .env 파일 로드 (python-dotenv가 있으면 사용, 없으면 무시)
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env 파일이 로드되었습니다.")
except ImportError:
    print("⚠️ python-dotenv가 설치되지 않았습니다. 환경변수를 직접 설정해주세요.")

def call_llm(prompt: str, model: str = "gpt-4") -> str:
    """
    OpenAI API를 사용하여 LLM 호출
    
    환경변수 설정 필요:
    - OPENAI_API_KEY: OpenAI API 키
    
    API 키 받는 방법:
    1. https://platform.openai.com 회원가입
    2. API keys 메뉴에서 키 생성
    3. 환경변수 설정: OPENAI_API_KEY=your_key_here
    """
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        return "⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다. API 키를 설정해주세요."
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ LLM 호출 오류: {str(e)}"

def call_llm_mock(prompt: str) -> str:
    """
    테스트용 Mock LLM 함수 (API 키 없이 테스트 가능)
    """
    # prompt 분석해서 적절한 mock 응답 반환
    prompt_lower = prompt.lower()
    
    if "주제" in prompt or "topic" in prompt_lower:
        return '''```json
[
    {
        "title": "YouTube 동영상의 주요 내용",
        "content": "이 동영상에서는 인공지능의 발전과 그것이 우리 일상생활에 미치는 영향에 대해 설명합니다."
    },
    {
        "title": "AI 기술의 실생활 활용",
        "content": "스마트폰, 자동차, 의료기기 등에서 AI 기술이 어떻게 사용되고 있는지 구체적인 예시를 보여줍니다."
    },
    {
        "title": "미래 전망과 고려사항",
        "content": "AI 기술의 미래 발전 방향과 함께 고려해야 할 윤리적, 사회적 문제들을 다룹니다."
    }
]
```'''
    
    elif "질문" in prompt or "question" in prompt_lower:
        return '''```json
[
    {
        "question": "인공지능이 우리 생활을 어떻게 바꾸고 있나요?",
        "answer": "인공지능은 스마트폰의 음성인식, 자동번역, 추천 시스템 등을 통해 이미 우리 일상에 깊숙이 들어와 있습니다. 예를 들어, 유튜브에서 우리가 좋아할 만한 영상을 추천해주거나, 구글 번역으로 외국어를 쉽게 이해할 수 있게 해줍니다."
    },
    {
        "question": "AI 기술의 장점과 단점은 무엇인가요?",
        "answer": "장점으로는 반복적인 작업을 자동화해서 효율성을 높이고, 사람이 할 수 없는 복잡한 계산이나 패턴 인식을 가능하게 합니다. 하지만 일부 일자리가 대체될 수 있고, 개인정보 보호나 AI의 편향성 같은 윤리적 문제들도 고려해야 합니다."
    },
    {
        "question": "앞으로 AI는 어떻게 발전할까요?",
        "answer": "AI는 더욱 자연스러운 대화가 가능해지고, 창작 활동이나 과학 연구에서도 인간의 파트너 역할을 할 것으로 예상됩니다. 또한 의료, 교육, 환경 보호 등 다양한 분야에서 인류의 문제 해결에 도움을 줄 것입니다."
    }
]
```'''
    
    elif "아이" in prompt or "kid" in prompt_lower or "5살" in prompt or "쉽게" in prompt:
        return """인공지능은 마치 아주 아주 똑똑한 로봇 친구 같아요! 

이 로봇 친구는 정말 신기한 일들을 많이 할 수 있어요:
- 우리가 말하는 걸 알아듣고 대답해줘요 (마치 시리나 구글 어시스턴트처럼!)
- 그림도 그려주고, 이야기도 만들어줘요
- 복잡한 수학 문제도 빨리빨리 풀어줘요
- 우리가 좋아할 만한 게임이나 영상도 찾아서 추천해줘요

마치 마법사가 가진 수정구슬 같아서, 많은 것들을 알고 있고 도와줄 수 있답니다! 하지만 사람처럼 감정이 있는 건 아니고, 컴퓨터가 매우 똑똑해진 거예요."""
    
    elif "html" in prompt_lower or "페이지" in prompt or "웹" in prompt:
        return "Mock HTML generation complete! 이 부분은 실제로는 HTML 코드가 생성됩니다."
    
    else:
        return f"이것은 테스트용 Mock 응답입니다. 실제 OpenAI API 키를 설정하면 진짜 AI 응답을 받을 수 있어요!\n\n입력된 프롬프트: {prompt[:100]}..."

if __name__ == "__main__":
    print("=== OpenAI LLM 연결 테스트 ===")
    
    # API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ OPENAI_API_KEY 발견됨: {api_key[:20]}...")
    else:
        print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
    
    # 실제 API 테스트
    test_prompt = "안녕하세요! 간단한 인사말로 답변해주세요."
    print("\n1. 실제 OpenAI API 테스트:")
    response = call_llm(test_prompt)
    print(f"응답: {response}")
    
    # Mock API 테스트
    print("\n2. Mock API 테스트:")
    mock_response = call_llm_mock("5살 아이에게 인공지능을 설명해주세요")
    print(f"Mock 응답: {mock_response[:200]}...")
    
    print("\n=== 환경변수 설정 방법 ===")
    print("1. .env 파일에 OPENAI_API_KEY=your_api_key_here 추가")
    print("2. 또는 환경변수로 직접 설정:")
    print("   Windows PowerShell: $env:OPENAI_API_KEY='your_api_key_here'")
    print("   Windows CMD: set OPENAI_API_KEY=your_api_key_here")
    print("   Mac/Linux: export OPENAI_API_KEY=your_api_key_here")
