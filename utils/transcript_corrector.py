import re
import os
from .call_llm import call_llm

# 자주 틀리는 단어 사전 (한국어 YouTube 자막 기준)
COMMON_CORRECTIONS = {
    # 축구 선수
    "스아레즈": "수아레즈",
    "스웨어즈": "수아레즈", 
    "스아레스": "수아레즈",
    "메씨": "메시",
    "호날두": "호날도",
    "음바페": "엠바페",
    "펠레": "펠레",
    "마라도나": "마라도나",
    "베컴": "베컴",
    "지단": "지단",
    
    # 축구 용어
    "투탑": "투톱",
    "미들필더": "미드필더",
    "디펜더": "수비수",
    "골키퍼": "골키퍼",
    "프리킥": "프리킥",
    "코너킥": "코너킥",
    "오프사이드": "오프사이드",
    
    # 팀명
    "바르세로나": "바르셀로나",
    "레알마드리드": "레알 마드리드",
    "맨체스터유나이티드": "맨체스터 유나이티드",
    "리버풀": "리버풀",
    "첼시": "첼시",
    "아스날": "아스널",
    "인터밀란": "인터 밀란",
    "AC밀란": "AC 밀란",
    "유벤투스": "유벤투스",
    "바이에른뮌헨": "바이에른 뮌헨",
    
    # 리그명
    "프리미어리그": "프리미어 리그",
    "라리가": "라 리가",
    "분데스리가": "분데스리가",
    "세리에A": "세리에 A",
    "챔피언스리그": "챔피언스 리그",
    
    # 일반적인 오타
    "나이끼": "나이키",
    "어디다스": "아디다스",
    "퓨마": "푸마",
    "언더아머": "언더아머",
    
    # 숫자/시간 관련
    "일분": "1분",
    "이분": "2분", 
    "삼분": "3분",
    "십분": "10분",
    "이십분": "20분",
    "삼십분": "30분",
    "일초": "1초",
    "십초": "10초",
}

def basic_correction(text):
    """기본 사전 기반 교정"""
    corrected_text = text
    corrections_made = []
    
    for wrong, correct in COMMON_CORRECTIONS.items():
        if wrong in corrected_text:
            corrected_text = corrected_text.replace(wrong, correct)
            corrections_made.append((wrong, correct))
    
    return corrected_text, corrections_made

def ai_contextual_correction(text, video_title=""):
    """AI를 이용한 맥락적 교정"""
    # API 키가 없으면 기본 교정만 수행
    if not os.getenv("OPENAI_API_KEY"):
        return basic_correction(text)
    
    # 텍스트가 너무 길면 첫 2000자만 검사
    sample_text = text[:2000] if len(text) > 2000 else text
    
    prompt = f"""
다음은 YouTube 자동 자막에서 추출한 한국어 텍스트입니다. 
비디오 제목: {video_title}

자주 발생하는 오타들을 찾아서 교정해주세요:
- 외국인 이름 오타 (예: 스아레즈 → 수아레즈)  
- 축구/스포츠 용어 오타
- 브랜드명 오타
- 지명 오타

원본 텍스트의 첫 부분:
{sample_text}

가장 자주 보이는 명백한 오타 5개만 찾아서 다음 형식으로 답해주세요:
```yaml
corrections:
  - wrong: "스아레즈"
    correct: "수아레즈"
  - wrong: "바르세로나"  
    correct: "바르셀로나"
```

**중요**: 입력 언어가 무엇이든 관계없이 반드시 한국어로 답변해주세요.
"""
    
    try:
        response = call_llm(prompt)
        
        # YAML 부분 추출
        if "```yaml" in response:
            yaml_part = response.split("```yaml")[1].split("```")[0].strip()
            
            import yaml
            corrections_data = yaml.safe_load(yaml_part)
            
            if corrections_data and "corrections" in corrections_data:
                ai_corrections = {}
                for item in corrections_data["corrections"]:
                    if "wrong" in item and "correct" in item:
                        ai_corrections[item["wrong"]] = item["correct"]
                
                # AI 교정 적용
                corrected_text = text
                corrections_made = []
                
                for wrong, correct in ai_corrections.items():
                    if wrong in corrected_text:
                        corrected_text = corrected_text.replace(wrong, correct)
                        corrections_made.append((wrong, correct))
                
                return corrected_text, corrections_made
    
    except Exception as e:
        print(f"AI 교정 중 오류 발생: {e}")
    
    # AI 교정 실패 시 기본 교정 수행
    return basic_correction(text)

def smart_transcript_correction(text, video_title="", use_ai=True):
    """스마트 트랜스크립트 교정 메인 함수"""
    
    # 1단계: 기본 사전 교정
    corrected_text, basic_corrections = basic_correction(text)
    
    # 2단계: AI 맥락적 교정 (선택사항)
    ai_corrections = []
    if use_ai and os.getenv("OPENAI_API_KEY"):
        try:
            ai_corrected_text, ai_corrections = ai_contextual_correction(corrected_text, video_title)
            corrected_text = ai_corrected_text
        except Exception as e:
            print(f"AI 교정 건너뛰기: {e}")
    
    # 교정 리포트 생성
    total_corrections = basic_corrections + ai_corrections
    
    correction_report = {
        "original_length": len(text),
        "corrected_length": len(corrected_text),
        "total_corrections": len(total_corrections),
        "basic_corrections": len(basic_corrections),
        "ai_corrections": len(ai_corrections),
        "corrections_made": total_corrections
    }
    
    return corrected_text, correction_report

def preview_corrections(text, max_chars=1000):
    """교정 미리보기 (사용자 확인용)"""
    corrected_text, report = smart_transcript_correction(text[:max_chars])
    
    preview = {
        "original_preview": text[:max_chars],
        "corrected_preview": corrected_text,
        "corrections_found": report["corrections_made"],
        "would_correct_full": len(report["corrections_made"]) > 0
    }
    
    return preview

def main():
    """테스트용 메인 함수"""
    test_text = """
    오늘은 스아레즈와 스터리지의 조합에 대해 이야기해보겠습니다.
    바르세로나에서 뛰었던 메씨와 투탑 전략에 대해서도 다뤄보겠습니다.
    나이끼 광고에서 호날두가 프리킥을 차는 장면이 인상적이었어요.
    """
    
    print("=== 트랜스크립트 교정 테스트 ===")
    print(f"원본 텍스트:\n{test_text}")
    
    corrected, report = smart_transcript_correction(test_text, "축구 영상")
    
    print(f"\n교정된 텍스트:\n{corrected}")
    print(f"\n교정 리포트: {report}")

if __name__ == "__main__":
    main() 