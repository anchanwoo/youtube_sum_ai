#!/usr/bin/env python3
"""
AI 검토 기능 단독 테스트 스크립트

현재 요약본에서 "스아레즈" 같은 오타가 실제로 교정되는지 테스트합니다.
"""

import os
from utils.final_reviewer import review_and_correct_summary, generate_review_summary

def test_ai_reviewer():
    """AI 검토 기능을 테스트합니다"""
    
    print("🔍 AI 최종 검토관 시스템 테스트")
    print("=" * 50)
    
    # API 키 확인
    if os.getenv("OPENAI_API_KEY"):
        print("✅ OpenAI API 키 발견 - 실제 AI 검토 수행")
    else:
        print("⚠️  API 키 없음 - Mock 모드로 진행")
        return
    
    # 축구 영상에서 나올만한 오타가 있는 테스트 데이터
    test_topics_with_issues = [
        {
            "topic": "축구 투톱 전략",
            "qa_pairs": [
                {
                    "question": "스아레즈는 어떤 선수인가요?",
                    "answer": "스아레즈는 우루과이 출신의 공격수로서 골 결정력이 뛰어나며 리버풀과 바르세로나에서 활약했습니다."
                },
                {
                    "question": "투탑 전략이 어떻게 작동하나요?",
                    "answer": "투탑 전략은 두 명의 공격수가 상대방 수비를 분산시키는 전술적 접근 방식입니다."
                },
                {
                    "question": "메씨는 왜 유명한가요?",
                    "answer": "메씨는 아르헨티나의 축구 선수로서 매우 뛰어난 기술적 역량을 보여주는 선수입니다."
                }
            ]
        },
        {
            "topic": "유명한 축구 선수들",
            "qa_pairs": [
                {
                    "question": "호날두는 어떤 선수인가요?",
                    "answer": "호날두는 포르투갈 출신의 윙어이자 공격수로서 뛰어난 신체 능력과 득점 능력을 갖춘 선수입니다."
                },
                {
                    "question": "나이끼 광고에 나오는 선수는 누구인가요?",
                    "answer": "나이끼 광고에는 여러 유명한 축구 선수들이 등장하며, 그 중 대표적인 선수로는 호날두가 있습니다."
                }
            ]
        }
    ]
    
    print("\n📝 테스트 데이터 (교정 전):")
    print("-" * 30)
    for i, topic in enumerate(test_topics_with_issues, 1):
        print(f"\n주제 {i}: {topic['topic']}")
        for j, qa in enumerate(topic['qa_pairs'], 1):
            print(f"  Q{j}: {qa['question']}")
            print(f"  A{j}: {qa['answer'][:100]}...")
    
    print("\n🤖 AI 검토 시작...")
    print("-" * 30)
    
    # AI 검토 실행
    improved_topics, review_report = review_and_correct_summary(
        topics_with_qa=test_topics_with_issues,
        video_title="축구 레전드들의 투톱 전략",
        video_context="축구 전술과 유명 선수들에 대한 설명"
    )
    
    # 검토 결과 출력
    print(f"\n📊 검토 리포트:")
    review_summary = generate_review_summary(review_report)
    print(review_summary)
    
    print("\n✨ 개선된 데이터 (교정 후):")
    print("-" * 30)
    for i, topic in enumerate(improved_topics, 1):
        print(f"\n주제 {i}: {topic['topic']}")
        for j, qa in enumerate(topic['qa_pairs'], 1):
            print(f"  Q{j}: {qa['question']}")
            print(f"  A{j}: {qa['answer'][:100]}...")
    
    # 변화 감지 및 하이라이트
    print("\n🔍 교정 사항 분석:")
    print("-" * 30)
    
    changes_found = []
    for i, (original, improved) in enumerate(zip(test_topics_with_issues, improved_topics)):
        for j, (orig_qa, imp_qa) in enumerate(zip(original['qa_pairs'], improved_topics[i]['qa_pairs'])):
            # 질문 변화 확인
            if orig_qa['question'] != imp_qa['question']:
                changes_found.append(f"주제 {i+1}, Q{j+1} 질문: '{orig_qa['question']}' → '{imp_qa['question']}'")
            
            # 답변 변화 확인  
            if orig_qa['answer'] != imp_qa['answer']:
                changes_found.append(f"주제 {i+1}, A{j+1} 답변: 내용 개선됨")
    
    if changes_found:
        print("✅ 발견된 개선사항:")
        for change in changes_found[:5]:  # 최대 5개만 표시
            print(f"  - {change}")
        if len(changes_found) > 5:
            print(f"  ... 및 {len(changes_found) - 5}개 더")
    else:
        print("ℹ️  명시적 변경사항 없음 (또는 AI가 개선 불필요하다고 판단)")
    
    print("\n🎯 테스트 완료!")
    print("=" * 50)
    
    return improved_topics, review_report

def test_specific_corrections():
    """특정 오타 교정 테스트"""
    
    print("\n🎯 특정 오타 교정 집중 테스트")
    print("=" * 40)
    
    # 명백한 오타들이 포함된 테스트 케이스
    test_cases = [
        {
            "topic": "오타 교정 테스트",
            "qa_pairs": [
                {
                    "question": "스아레즈와 메씨가 함께 뛰었나요?",
                    "answer": "스아레즈와 메씨는 바르세로나에서 함께 뛰었으며, 나이끼 스폰서십도 공유했습니다."
                }
            ]
        }
    ]
    
    print("교정 전:", test_cases[0]['qa_pairs'][0]['question'])
    print("교정 전:", test_cases[0]['qa_pairs'][0]['answer'])
    
    if os.getenv("OPENAI_API_KEY"):
        improved, report = review_and_correct_summary(test_cases, "축구 오타 테스트")
        
        print("\n교정 후:", improved[0]['qa_pairs'][0]['question'])
        print("교정 후:", improved[0]['qa_pairs'][0]['answer'])
        
        print(f"\n리포트: {generate_review_summary(report)}")
    else:
        print("\n⚠️  API 키 없음 - 실제 교정 불가")

if __name__ == "__main__":
    print("🚀 AI 검토 시스템 테스트 시작!")
    
    # 메인 테스트
    improved_topics, review_report = test_ai_reviewer()
    
    # 추가 집중 테스트
    test_specific_corrections()
    
    print("\n✅ 모든 테스트 완료!")
    print("\n💡 실제 Flow에서는 이 검토 단계가 자동으로 실행됩니다.")
    print("   ConvertToKidFriendly → ReviewAndCorrect → GenerateHTML") 