import os
import yaml
from .call_llm import call_llm

def review_and_correct_summary(topics_with_qa, video_title="", video_context=""):
    """
    최종 요약본을 AI가 검토하고 개선하는 함수
    
    Args:
        topics_with_qa: [{topic: str, qa_pairs: [...]}, ...]
        video_title: 비디오 제목
        video_context: 비디오 맥락 정보
    
    Returns:
        improved_topics_with_qa: 개선된 요약본
        review_report: 검토 리포트
    """
    
    # API 키가 없으면 원본 그대로 반환
    if not os.getenv("OPENAI_API_KEY"):
        return topics_with_qa, {"status": "skipped", "reason": "no_api_key"}
    
    improved_topics = []
    total_corrections = 0
    review_details = []
    
    for topic_data in topics_with_qa:
        topic = topic_data["topic"]
        qa_pairs = topic_data["qa_pairs"]
        
        # 각 주제별로 검토 및 개선
        improved_qa_pairs, corrections = review_topic_qa_pairs(topic, qa_pairs, video_title)
        
        improved_topics.append({
            "topic": topic,
            "qa_pairs": improved_qa_pairs
        })
        
        total_corrections += len(corrections)
        review_details.append({
            "topic": topic,
            "corrections_made": corrections,
            "corrections_count": len(corrections)
        })
    
    review_report = {
        "status": "completed",
        "total_corrections": total_corrections,
        "topics_reviewed": len(topics_with_qa),
        "details": review_details
    }
    
    return improved_topics, review_report

def review_topic_qa_pairs(topic, qa_pairs, video_title=""):
    """
    특정 주제의 Q&A들을 검토하고 개선
    """
    
    # Q&A를 텍스트로 변환
    qa_text = f"주제: {topic}\n\n"
    for i, qa in enumerate(qa_pairs, 1):
        qa_text += f"Q{i}: {qa['question']}\n"
        qa_text += f"A{i}: {qa['answer']}\n\n"
    
    prompt = f"""
당신은 5살 아이용 YouTube 요약본을 검토하는 전문가입니다.

비디오 제목: {video_title}

다음 Q&A를 검토하고 개선해주세요:

{qa_text}

다음 사항들을 중점적으로 검토해주세요:

1. **오타 교정** (예: 스아레즈 → 수아레즈, 메씨 → 메시)
2. **사실 확인** (잘못된 정보가 있다면 수정)
3. **5살 아이 수준** (너무 어려운 표현은 더 쉽게)
4. **명확성 개선** (애매한 표현을 더 구체적으로)
5. **재미 요소** (지루하지 않게 흥미롭게)

개선된 Q&A를 다음 형식으로 답해주세요:

```yaml
improvements:
  - question_number: 1
    original_question: "원래 질문"
    improved_question: "개선된 질문"  
    original_answer: "원래 답변"
    improved_answer: "개선된 답변"
    changes_made: ["오타 교정: 스아레즈→수아레즈", "표현 단순화"]
  
  - question_number: 2
    original_question: "원래 질문"
    improved_question: "개선된 질문"
    original_answer: "원래 답변" 
    improved_answer: "개선된 답변"
    changes_made: ["사실 확인", "재미 요소 추가"]
```

**중요**: 
- 반드시 한국어로 답변해주세요
- 개선이 필요없는 경우 원래 내용을 그대로 사용해주세요
- 5살 아이가 이해할 수 있는 수준을 유지해주세요
"""
    
    try:
        response = call_llm(prompt)
        
        # YAML 파싱
        if "```yaml" in response:
            yaml_part = response.split("```yaml")[1].split("```")[0].strip()
            improvements_data = yaml.safe_load(yaml_part)
            
            if improvements_data and "improvements" in improvements_data:
                improved_qa_pairs = []
                corrections_made = []
                
                for improvement in improvements_data["improvements"]:
                    q_num = improvement.get("question_number", 1) - 1
                    
                    if q_num < len(qa_pairs):
                        # 개선된 버전 사용
                        improved_qa = {
                            "question": improvement.get("improved_question", qa_pairs[q_num]["question"]),
                            "answer": improvement.get("improved_answer", qa_pairs[q_num]["answer"])
                        }
                        improved_qa_pairs.append(improved_qa)
                        
                        # 변경사항 기록
                        changes = improvement.get("changes_made", [])
                        if changes:
                            corrections_made.append({
                                "question_number": q_num + 1,
                                "changes": changes,
                                "original_question": improvement.get("original_question", ""),
                                "improved_question": improvement.get("improved_question", ""),
                                "original_answer": improvement.get("original_answer", ""),
                                "improved_answer": improvement.get("improved_answer", "")
                            })
                
                # 개선되지 않은 Q&A는 원본 유지
                while len(improved_qa_pairs) < len(qa_pairs):
                    improved_qa_pairs.append(qa_pairs[len(improved_qa_pairs)])
                
                return improved_qa_pairs, corrections_made
    
    except Exception as e:
        print(f"검토 중 오류 발생: {e}")
    
    # 오류 발생시 원본 반환
    return qa_pairs, []

def generate_review_summary(review_report):
    """검토 리포트를 사용자가 읽기 쉬운 형태로 요약"""
    
    if review_report["status"] == "skipped":
        return "❌ AI 검토를 건너뛰었습니다 (API 키 없음)"
    
    total_corrections = review_report["total_corrections"]
    topics_count = review_report["topics_reviewed"]
    
    if total_corrections == 0:
        return f"✅ {topics_count}개 주제 검토 완료 - 추가 개선사항 없음"
    
    summary = f"🔍 AI 검토 완료: {topics_count}개 주제에서 총 {total_corrections}개 개선사항 발견\n\n"
    
    for detail in review_report["details"]:
        if detail["corrections_count"] > 0:
            summary += f"📝 **{detail['topic']}**: {detail['corrections_count']}개 개선\n"
            
            # 주요 변경사항 표시 (최대 3개)
            for correction in detail["corrections_made"][:3]:
                changes_text = ", ".join(correction["changes"])
                summary += f"   - Q{correction['question_number']}: {changes_text}\n"
    
    return summary

def main():
    """테스트용 메인 함수"""
    test_topics = [
        {
            "topic": "축구 선수들",
            "qa_pairs": [
                {
                    "question": "스아레즈는 어떤 선수인가요?",
                    "answer": "스아레즈는 골을 많이 넣는 공격수예요. 우루과이라는 나라에서 왔어요."
                },
                {
                    "question": "메씨는 왜 유명한가요?", 
                    "answer": "메씨는 아르헨티나의 축구 선수로서 매우 뛰어난 실력을 보여주는 사람이에요."
                }
            ]
        }
    ]
    
    print("=== AI 최종 검토 테스트 ===")
    
    improved_topics, review_report = review_and_correct_summary(
        test_topics, 
        "축구 레전드 이야기"
    )
    
    print("검토 리포트:")
    print(generate_review_summary(review_report))
    
    print("\n개선된 내용:")
    for topic_data in improved_topics:
        print(f"\n주제: {topic_data['topic']}")
        for i, qa in enumerate(topic_data['qa_pairs'], 1):
            print(f"Q{i}: {qa['question']}")
            print(f"A{i}: {qa['answer']}")

if __name__ == "__main__":
    main() 