#!/usr/bin/env python3
"""
노션 연결 테스트 스크립트
.env 파일에 NOTION_TOKEN과 NOTION_DATABASE_ID가 설정되어 있으면 테스트 실행
"""

import os
from dotenv import load_dotenv
from utils.notion_client import save_to_notion

def test_notion_connection():
    """노션 연결 테스트"""
    # 환경 변수 로드
    load_dotenv()
    
    # 노션 설정 확인
    notion_token = os.getenv('NOTION_TOKEN')
    notion_db_id = os.getenv('NOTION_DATABASE_ID')
    
    if not notion_token:
        print("❌ NOTION_TOKEN이 .env 파일에 설정되지 않았습니다.")
        print("📋 설정 방법:")
        print("1. https://www.notion.so/my-integrations 에서 통합 생성")
        print("2. Internal Integration Token을 복사")
        print("3. .env 파일에 NOTION_TOKEN=secret_your_token_here 추가")
        return False
    
    if not notion_db_id:
        print("❌ NOTION_DATABASE_ID가 .env 파일에 설정되지 않았습니다.")
        print("📋 설정 방법:")
        print("1. 노션에서 새 페이지 생성")
        print("2. 데이터베이스 추가")
        print("3. 데이터베이스 ID를 복사")
        print("4. .env 파일에 NOTION_DATABASE_ID=your_db_id_here 추가")
        return False
    
    print("✅ 노션 설정이 발견되었습니다!")
    print(f"🔑 토큰: {notion_token[:20]}...")
    print(f"🗃️ 데이터베이스 ID: {notion_db_id}")
    
    # 테스트 데이터 생성
    test_video_info = {
        "title": "🧪 노션 연결 테스트",
        "url": "https://youtu.be/test123",
        "thumbnail_url": "https://img.youtube.com/vi/test123/maxresdefault.jpg",
        "description": "이것은 노션 연결 테스트를 위한 더미 데이터입니다."
    }
    
    test_topics = [
        "테스트 주제 1: 노션 API 연동",
        "테스트 주제 2: PocketFlow 시스템",
        "테스트 주제 3: YouTube 요약 기능"
    ]
    
    test_qa_pairs = [
        {"question": "노션이 무엇인가요?", "answer": "노션은 올인원 워크스페이스입니다."},
        {"question": "API는 무엇인가요?", "answer": "API는 서로 다른 소프트웨어가 소통하는 방법입니다."},
        {"question": "테스트가 왜 중요한가요?", "answer": "테스트를 통해 코드가 제대로 작동하는지 확인할 수 있습니다."}
    ]
    
    test_kid_friendly = [
        {"question": "노션이 뭐야?", "answer": "노션은 공부하고 일할 때 쓰는 아주 좋은 도구야!"},
        {"question": "API가 뭐야?", "answer": "API는 컴퓨터들이 서로 이야기하는 방법이야!"},
        {"question": "왜 테스트를 해야 해?", "answer": "테스트를 하면 우리 프로그램이 잘 작동하는지 알 수 있어!"}
    ]
    
    print("\n🚀 노션에 테스트 페이지 생성 중...")
    
    try:
        result = save_to_notion(test_video_info, test_topics, test_qa_pairs, test_kid_friendly)
        
        if result.get("success"):
            print("🎉 성공! 노션에 테스트 페이지가 생성되었습니다!")
            print(f"📝 페이지 URL: {result.get('page_url')}")
            print(f"🆔 페이지 ID: {result.get('page_id')}")
            print(f"📋 제목: {result.get('title')}")
            return True
        else:
            print(f"❌ 실패: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return False

def main():
    """메인 함수"""
    print("🔍 노션 연결 테스트를 시작합니다...\n")
    
    success = test_notion_connection()
    
    if success:
        print("\n✅ 노션 연결 테스트 완료!")
        print("이제 YouTube URL을 입력하면 자동으로 노션에도 저장됩니다! 🎯")
    else:
        print("\n⚠️ 노션 설정을 완료한 후 다시 테스트해보세요.")
        print("💡 노션 없이도 HTML 파일은 정상적으로 생성됩니다!")

if __name__ == "__main__":
    main() 