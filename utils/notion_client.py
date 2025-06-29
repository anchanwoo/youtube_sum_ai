import os
import logging
from datetime import datetime
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

def get_notion_client():
    """Notion 클라이언트를 초기화합니다."""
    token = os.getenv('NOTION_TOKEN')
    if not token:
        raise ValueError("NOTION_TOKEN이 환경 변수에 설정되지 않았습니다.")
    
    return Client(auth=token)

def get_database_properties(client, database_id):
    """데이터베이스의 속성 정보를 가져와서 분석합니다."""
    try:
        database = client.databases.retrieve(database_id=database_id)
        properties = database.get('properties', {})
        
        # 속성 타입별로 분류
        title_prop = None
        url_prop = None
        date_prop = None
        number_props = []
        select_props = []
        multiselect_props = []
        
        for prop_name, prop_info in properties.items():
            prop_type = prop_info.get('type')
            if prop_type == 'title':
                title_prop = prop_name
            elif prop_type == 'url':
                url_prop = prop_name
            elif prop_type == 'date':
                date_prop = prop_name
            elif prop_type == 'number':
                number_props.append(prop_name)
            elif prop_type == 'select':
                select_props.append(prop_name)
            elif prop_type == 'multi_select':
                multiselect_props.append(prop_name)
        
        return {
            'title': title_prop,
            'url': url_prop,
            'date': date_prop,
            'numbers': number_props,
            'selects': select_props,
            'multiselects': multiselect_props,
            'all_properties': list(properties.keys())
        }
    except Exception as e:
        logger.error(f"데이터베이스 속성 조회 실패: {str(e)}")
        return None

def save_to_notion(video_info, topics, qa_pairs, kid_friendly_pairs):
    """
    YouTube 요약 결과를 노션 데이터베이스에 저장합니다.
    
    Args:
        video_info (dict): 비디오 정보 (title, url, thumbnail, etc.)
        topics (list): 추출된 주제 목록
        qa_pairs (list): 생성된 Q&A 쌍
        kid_friendly_pairs (list): 아이 친화적으로 변환된 Q&A 쌍
    
    Returns:
        dict: 저장된 페이지 정보
    """
    try:
        client = get_notion_client()
        database_id = os.getenv('NOTION_DATABASE_ID')
        
        if not database_id:
            raise ValueError("NOTION_DATABASE_ID가 환경 변수에 설정되지 않았습니다.")
        
        # 데이터베이스 속성 정보 가져오기
        db_props = get_database_properties(client, database_id)
        if not db_props:
            # 기본 속성만 사용 (Title만)
            logger.info("기본 Title 속성만 사용하여 저장합니다.")
            db_props = {'title': 'Name', 'url': None, 'date': None, 'numbers': []}
        
        logger.info(f"데이터베이스 속성: {db_props}")
        
        # 페이지 제목 생성
        title = f"📺 {video_info.get('title', 'YouTube 요약')}"
        
        # 페이지 속성 설정 (존재하는 속성만 사용)
        properties = {}
        
        # Title 속성 (필수)
        if db_props['title']:
            properties[db_props['title']] = {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        
        # URL 속성 (선택사항)
        if db_props['url']:
            properties[db_props['url']] = {
                "url": video_info.get('url', '')
            }
        
        # Date 속성 (선택사항)
        if db_props['date']:
            properties[db_props['date']] = {
                "date": {
                    "start": datetime.now().isoformat()
                }
            }
        
        # Number 속성들 (선택사항) - 스마트하게 매핑
        number_props = db_props['numbers']
        for i, prop_name in enumerate(number_props):
            prop_name_lower = prop_name.lower()
            if '주제' in prop_name_lower or 'topic' in prop_name_lower:
                properties[prop_name] = {"number": len(topics)}
            elif 'qa' in prop_name_lower or '질문' in prop_name_lower or 'question' in prop_name_lower:
                properties[prop_name] = {"number": len(qa_pairs)}
            elif '길이' in prop_name_lower or 'duration' in prop_name_lower or '시간' in prop_name_lower:
                # 비디오 길이 (분 단위로 변환)
                duration_str = video_info.get('duration', '0:00')
                try:
                    if ':' in duration_str:
                        parts = duration_str.split(':')
                        if len(parts) == 2:  # MM:SS
                            minutes = int(parts[0]) + int(parts[1]) / 60
                        elif len(parts) == 3:  # HH:MM:SS
                            minutes = int(parts[0]) * 60 + int(parts[1]) + int(parts[2]) / 60
                        else:
                            minutes = 0
                    else:
                        minutes = 0
                    properties[prop_name] = {"number": round(minutes, 1)}
                except:
                    properties[prop_name] = {"number": 0}
            elif i < 2:  # 기본 매핑 (이전 로직 유지)
                if i == 0:
                    properties[prop_name] = {"number": len(topics)}
                elif i == 1:
                    properties[prop_name] = {"number": len(qa_pairs)}
        
        # Select 속성들 자동 설정
        select_props = db_props.get('selects', [])
        for prop_name in select_props:
            prop_name_lower = prop_name.lower()
            
            # 언어 자동 감지
            if '언어' in prop_name_lower or 'language' in prop_name_lower:
                # 비디오 제목으로 언어 추정
                title = video_info.get('title', '')
                if any(char >= '\uac00' and char <= '\ud7af' for char in title):  # 한글 확인
                    properties[prop_name] = {"select": {"name": "한국어"}}
                elif any(char >= '\u3040' and char <= '\u309f' for char in title):  # 히라가나
                    properties[prop_name] = {"select": {"name": "일본어"}}
                elif any(char >= '\u4e00' and char <= '\u9fff' for char in title):  # 한자
                    properties[prop_name] = {"select": {"name": "중국어"}}
                else:
                    properties[prop_name] = {"select": {"name": "영어"}}
            
            # 카테고리 자동 분류
            elif '카테고리' in prop_name_lower or 'category' in prop_name_lower:
                title_lower = video_info.get('title', '').lower()
                if any(word in title_lower for word in ['ai', '인공지능', '기술', 'tech', 'programming', '프로그래밍']):
                    properties[prop_name] = {"select": {"name": "기술"}}
                elif any(word in title_lower for word in ['축구', '스포츠', 'football', 'soccer', 'sport']):
                    properties[prop_name] = {"select": {"name": "스포츠"}}
                elif any(word in title_lower for word in ['교육', '학습', 'education', 'learning', '강의']):
                    properties[prop_name] = {"select": {"name": "교육"}}
                elif any(word in title_lower for word in ['비즈니스', 'business', '경영', '투자', 'investment']):
                    properties[prop_name] = {"select": {"name": "비즈니스"}}
                elif any(word in title_lower for word in ['음악', 'music', '노래', 'song']):
                    properties[prop_name] = {"select": {"name": "음악"}}
                elif any(word in title_lower for word in ['뉴스', 'news', '정치', 'politics']):
                    properties[prop_name] = {"select": {"name": "뉴스"}}
                else:
                    properties[prop_name] = {"select": {"name": "엔터테인먼트"}}
            
            # 연령대 설정 (5살 아이 친화적이므로)
            elif '연령' in prop_name_lower or 'age' in prop_name_lower:
                properties[prop_name] = {"select": {"name": "5살"}}
            
            # 난이도 자동 설정
            elif '난이도' in prop_name_lower or 'difficulty' in prop_name_lower:
                properties[prop_name] = {"select": {"name": "쉬움"}}  # 5살 버전이므로
        
        # Multi-select 속성들 자동 설정
        multiselect_props = db_props.get('multiselects', [])
        for prop_name in multiselect_props:
            prop_name_lower = prop_name.lower()
            
            # 주제 태그 자동 생성
            if '태그' in prop_name_lower or 'tag' in prop_name_lower:
                tags = []
                title_lower = video_info.get('title', '').lower()
                
                # 키워드 기반 태그 생성
                tag_keywords = {
                    'AI': ['ai', '인공지능', 'artificial intelligence', 'machine learning'],
                    '축구': ['축구', 'football', 'soccer'],
                    '투자': ['투자', 'investment', '주식', 'stock'],
                    '요리': ['요리', 'cooking', '레시피', 'recipe'],
                    '게임': ['게임', 'game', 'gaming'],
                    '역사': ['역사', 'history'],
                    '과학': ['과학', 'science'],
                    '기술': ['기술', 'tech', 'technology'],
                    '음악': ['음악', 'music'],
                    '교육': ['교육', 'education', '학습', 'learning']
                }
                
                for tag, keywords in tag_keywords.items():
                    if any(keyword in title_lower for keyword in keywords):
                        tags.append({"name": tag})
                
                if tags:
                    properties[prop_name] = {"multi_select": tags}
        
        # 페이지 내용 생성
        children = []
        
        # 비디오 정보 섹션
        children.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "🎬 비디오 정보"}}]
            }
        })
        
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": f"📺 제목: {video_info.get('title', '제목 없음')}"}}]
            }
        })
        
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": f"🔗 URL: {video_info.get('url', '')}"}}]
            }
        })
        
        # 주제 섹션
        children.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "🎯 주요 주제"}}]
            }
        })
        
        for i, topic in enumerate(topics, 1):
            children.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": f"{i}. {topic}"}}]
                }
            })
        
        # Q&A 섹션
        children.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "❓ 5살 아이도 이해하는 Q&A"}}]
            }
        })
        
        for i, qa in enumerate(kid_friendly_pairs, 1):
            # 질문
            children.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": f"Q{i}. {qa['question']}"}}]
                }
            })
            
            # 답변
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": f"💡 {qa['answer']}"}}]
                }
            })
            
            # 구분선
            if i < len(kid_friendly_pairs):
                children.append({
                    "object": "block",
                    "type": "divider",
                    "divider": {}
                })
        
        # 노션 페이지 생성
        response = client.pages.create(
            parent={"database_id": database_id},
            properties=properties,
            children=children
        )
        
        logger.info(f"노션에 페이지 저장 완료: {response['url']}")
        
        return {
            "success": True,
            "page_url": response['url'],
            "page_id": response['id'],
            "title": title
        }
        
    except Exception as e:
        logger.error(f"노션 저장 중 오류 발생: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """테스트용 함수"""
    # 테스트 데이터
    test_video_info = {
        "title": "테스트 비디오",
        "url": "https://youtu.be/test123",
        "thumbnail": "https://img.youtube.com/vi/test123/maxresdefault.jpg"
    }
    
    test_topics = [
        "첫 번째 주제",
        "두 번째 주제",
        "세 번째 주제"
    ]
    
    test_qa_pairs = [
        {"question": "테스트 질문 1", "answer": "테스트 답변 1"},
        {"question": "테스트 질문 2", "answer": "테스트 답변 2"}
    ]
    
    test_kid_friendly = [
        {"question": "쉬운 질문 1", "answer": "쉬운 답변 1"},
        {"question": "쉬운 질문 2", "answer": "쉬운 답변 2"}
    ]
    
    result = save_to_notion(test_video_info, test_topics, test_qa_pairs, test_kid_friendly)
    print(f"결과: {result}")

if __name__ == "__main__":
    main() 