from typing import List, Dict, Any
import logging
import os
from pocketflow import Node, BatchNode, Flow
from utils.call_llm import call_llm
from utils.youtube_processor import get_video_info
from utils.html_generator import html_generator, streamlit_html_generator
from utils.topic_extractor import extract_interesting_topics
from utils.qa_generator import generate_qa_pairs
from utils.kid_friendly_converter import convert_to_kid_friendly
from utils.content_validator import validate_transcript_quality, ensure_topic_diversity
from utils.final_reviewer import review_and_correct_summary, generate_review_summary
from utils.notion_client import save_to_notion

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProcessYouTubeURL(Node):
    """Process YouTube URL to extract video information"""
    def prep(self, shared):
        """Get URL from shared"""
        # 중단 확인
        stop_flag = shared.get("stop_flag", {})
        if hasattr(stop_flag, 'should_stop') and stop_flag.should_stop:
            raise InterruptedError("처리가 중단되었습니다.")
        
        # 진행상황 업데이트
        callback = shared.get("progress_callback")
        if callback:
            callback("비디오 분석", "YouTube URL 검증 중...", 15)
        
        return shared.get("url", "")
    
    def exec(self, url):
        """Extract video information"""
        if not url:
            raise ValueError("No YouTube URL provided")
        
        logger.info(f"Processing YouTube URL: {url}")
        video_info = get_video_info(url)
        
        if "error" in video_info:
            raise ValueError(f"Error processing video: {video_info['error']}")
        
        # Validate transcript quality
        transcript = video_info.get("transcript", "")
        validation = validate_transcript_quality(transcript)
        
        if not validation["is_valid"]:
            logger.warning(f"Transcript quality issues: {validation['issues']}")
            # Continue anyway, but log the issues
        
        logger.info(f"Transcript word count: {validation['word_count']}")
        return video_info
    
    def post(self, shared, prep_res, exec_res):
        """Store video information in shared"""
        shared["video_info"] = exec_res
        logger.info(f"Video title: {exec_res.get('title')}")
        logger.info(f"Transcript length: {len(exec_res.get('transcript', ''))}")
        
        # 진행상황 업데이트
        callback = shared.get("progress_callback")
        if callback:
            title = exec_res.get('title', 'Unknown Video')[:50]
            callback("비디오 정보 완료", f"✅ 비디오 '{title}...' 정보 추출 완료", 20)
        
        return "default"

class ExtractTopics(Node):
    """Extract interesting topics from the video transcript"""
    def prep(self, shared):
        """Get transcript from video_info"""
        # 중단 확인
        stop_flag = shared.get("stop_flag", {})
        if hasattr(stop_flag, 'should_stop') and stop_flag.should_stop:
            raise InterruptedError("처리가 중단되었습니다.")
        
        # 진행상황 업데이트
        callback = shared.get("progress_callback")
        if callback:
            callback("주제 추출", "트랜스크립트에서 흥미로운 주제 찾는 중...", 25)
        
        video_info = shared.get("video_info", {})
        transcript = video_info.get("transcript", "")
        return transcript
    
    def exec(self, transcript):
        """Extract topics using our topic_extractor utility"""
        if not transcript:
            raise ValueError("No transcript available for topic extraction")
        
        logger.info("Extracting interesting topics...")
        
        # API 키 확인
        use_mock = not os.getenv("OPENAI_API_KEY")
        if use_mock:
            logger.info("Using Mock mode for topic extraction")
        
        topics = extract_interesting_topics(transcript, num_topics=5, use_mock=use_mock)
        
        if not topics:
            raise ValueError("Failed to extract topics from transcript")
        
        # Ensure topic diversity
        topics = ensure_topic_diversity(topics)
        
        return topics
    
    def post(self, shared, prep_res, exec_res):
        """Store topics in shared"""
        shared["topics"] = exec_res
        logger.info(f"Extracted {len(exec_res)} diverse topics")
        for i, topic in enumerate(exec_res, 1):
            logger.info(f"  {i}. {topic.get('title', 'No title')}")
        
        # 진행상황 업데이트
        callback = shared.get("progress_callback")
        if callback:
            topic_titles = [t.get('title', 'Unknown')[:30] for t in exec_res[:3]]
            callback("주제 추출 완료", f"✅ 주제 {len(exec_res)}개 발견: {', '.join(topic_titles)}...", 35)
        
        return "default"

class GenerateQA(BatchNode):
    """Generate Q&A pairs for each topic"""
    def prep(self, shared):
        """Return list of topics for batch processing"""
        # 중단 확인
        stop_flag = shared.get("stop_flag", {})
        if hasattr(stop_flag, 'should_stop') and stop_flag.should_stop:
            raise InterruptedError("처리가 중단되었습니다.")
        
        # 진행상황 업데이트
        callback = shared.get("progress_callback")
        if callback:
            callback("Q&A 생성", "각 주제별로 질문과 답변 만드는 중...", 40)
        
        topics = shared.get("topics", [])
        return topics
    
    def exec(self, topic):
        """Generate Q&A pairs for a single topic"""
        topic_title = topic.get("title", "")
        topic_content = topic.get("content", "")
        
        logger.info(f"Generating Q&A for topic: {topic_title}")
        
        # API 키 확인
        use_mock = not os.getenv("OPENAI_API_KEY")
        
        qa_pairs = generate_qa_pairs(
            topic_title=topic_title,
            topic_content=topic_content,
            num_questions=3,
            use_mock=use_mock
        )
        
        return {
            "title": topic_title,
            "content": topic_content,
            "qa_pairs": qa_pairs
        }
    
    def post(self, shared, prep_res, exec_res_list):
        """Store topics with Q&A pairs in shared"""
        shared["topics_with_qa"] = exec_res_list
        
        total_questions = sum(len(topic["qa_pairs"]) for topic in exec_res_list)
        logger.info(f"Generated {total_questions} Q&A pairs across {len(exec_res_list)} topics")
        
        # 진행상황 업데이트
        callback = shared.get("progress_callback")
        if callback:
            callback("Q&A 생성 완료", f"✅ 총 {total_questions}개의 질문-답변 쌍 생성완료!", 55)
        
        return "default"

class ConvertToKidFriendly(BatchNode):
    """Convert content to kid-friendly explanations"""
    def prep(self, shared):
        """Return list of topics with Q&A pairs for batch processing"""
        # 중단 확인
        stop_flag = shared.get("stop_flag", {})
        if hasattr(stop_flag, 'should_stop') and stop_flag.should_stop:
            raise InterruptedError("처리가 중단되었습니다.")
        
        # 진행상황 업데이트
        callback = shared.get("progress_callback")
        if callback:
            callback("아이 친화적 변환", "5살 아이도 이해할 수 있도록 쉽게 바꾸는 중...", 60)
        
        topics_with_qa = shared.get("topics_with_qa", [])
        
        # Flatten Q&A pairs for individual processing
        items = []
        for topic in topics_with_qa:
            for qa_pair in topic["qa_pairs"]:
                items.append({
                    "topic_title": topic["title"],
                    "question": qa_pair["question"],
                    "answer": qa_pair["answer"]
                })
        
        return items
    
    def exec(self, item):
        """Convert a single Q&A pair to kid-friendly version"""
        topic_title = item["topic_title"]
        question = item["question"]
        answer = item["answer"]
        
        logger.info(f"Converting to kid-friendly: {question[:50]}...")
        
        # API 키 확인
        use_mock = not os.getenv("OPENAI_API_KEY")
        
        # Convert question to kid-friendly
        kid_friendly_question = convert_to_kid_friendly(
            text=question,
            target_age=5,
            use_mock=use_mock
        )
        
        # Convert answer to kid-friendly
        kid_friendly_answer = convert_to_kid_friendly(
            text=answer,
            target_age=5,
            use_mock=use_mock
        )
        
        return {
            "topic_title": topic_title,
            "original_question": question,
            "original_answer": answer,
            "kid_friendly_question": kid_friendly_question,
            "kid_friendly_answer": kid_friendly_answer
        }
    
    def post(self, shared, prep_res, exec_res_list):
        """Reorganize kid-friendly content by topic"""
        # Group by topic
        topics_dict = {}
        for item in exec_res_list:
            topic_title = item["topic_title"]
            if topic_title not in topics_dict:
                topics_dict[topic_title] = {
                    "title": topic_title,
                    "qa_pairs": []
                }
            
            topics_dict[topic_title]["qa_pairs"].append({
                "original_question": item["original_question"],
                "original_answer": item["original_answer"],
                "kid_friendly_question": item["kid_friendly_question"],
                "kid_friendly_answer": item["kid_friendly_answer"]
            })
        
        # Convert back to list
        final_topics = list(topics_dict.values())
        shared["final_topics"] = final_topics
        
        logger.info(f"Converted {len(exec_res_list)} Q&A pairs to kid-friendly format")
        
        # 진행상황 업데이트
        callback = shared.get("progress_callback")
        if callback:
            callback("친화적 변환 완료", f"✅ {len(exec_res_list)}개 질문-답변을 아이 친화적으로 변환완료!", 75)
        
        return "default"

class ReviewAndCorrect(Node):
    """AI가 최종 요약본을 검토하고 개선"""
    def prep(self, shared):
        """Get final topics and video info for review"""
        # 진행상황 업데이트
        callback = shared.get("progress_callback")
        if callback:
            callback("AI 검토", "AI가 요약 내용의 품질과 정확성을 검토하는 중...", 80)
        
        final_topics = shared.get("final_topics", [])
        video_info = shared.get("video_info", {})
        
        # Convert to format expected by reviewer
        review_topics = []
        for topic in final_topics:
            qa_pairs = []
            for qa in topic["qa_pairs"]:
                qa_pairs.append({
                    "question": qa["kid_friendly_question"],
                    "answer": qa["kid_friendly_answer"]
                })
            
            review_topics.append({
                "topic": topic["title"],
                "qa_pairs": qa_pairs
            })
        
        return {
            "topics": review_topics,
            "video_title": video_info.get("title", ""),
            "video_context": video_info.get("description", "")
        }
    
    def exec(self, data):
        """AI가 요약본 검토 및 개선"""
        logger.info("AI가 최종 요약본을 검토하고 개선하는 중...")
        
        improved_topics, review_report = review_and_correct_summary(
            topics_with_qa=data["topics"],
            video_title=data["video_title"],
            video_context=data["video_context"]
        )
        
        return {
            "improved_topics": improved_topics,
            "review_report": review_report
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store improved content and review report"""
        improved_topics = exec_res["improved_topics"]
        review_report = exec_res["review_report"]
        
        # Convert back to original format
        final_topics = []
        for topic in improved_topics:
            qa_pairs = []
            for qa in topic["qa_pairs"]:
                qa_pairs.append({
                    "kid_friendly_question": qa["question"],
                    "kid_friendly_answer": qa["answer"],
                    "original_question": qa["question"],  # Keep for compatibility
                    "original_answer": qa["answer"]      # Keep for compatibility
                })
            
            final_topics.append({
                "title": topic["topic"],
                "qa_pairs": qa_pairs
            })
        
        # Update shared store
        shared["final_topics"] = final_topics
        shared["review_report"] = review_report
        
        # Log review summary
        review_summary = generate_review_summary(review_report)
        logger.info(f"AI 검토 완료: {review_summary}")
        
        # 진행상황 업데이트
        callback = shared.get("progress_callback")
        if callback:
            callback("AI 검토 완료", f"✅ AI 검토 완료: {review_summary[:50]}...", 85)
        
        return "default"

class SaveToNotion(Node):
    """Save the processed content to Notion database"""
    def prep(self, shared):
        """Get video info and final topics from shared"""
        # 진행상황 업데이트
        callback = shared.get("progress_callback")
        if callback:
            if os.getenv('NOTION_TOKEN') and os.getenv('NOTION_DATABASE_ID'):
                callback("노션 저장", "노션 데이터베이스에 요약 결과 저장 중...", 90)
            else:
                callback("노션 건너뛰기", "노션 설정이 없어 이 단계를 건너뜁니다...", 90)
        
        video_info = shared.get("video_info", {})
        final_topics = shared.get("final_topics", [])
        
        return {
            "video_info": video_info,
            "final_topics": final_topics
        }
    
    def exec(self, data):
        """Save to Notion database"""
        video_info = data["video_info"]
        final_topics = data["final_topics"]
        
        # 노션 API 토큰과 데이터베이스 ID가 있는지 확인
        if not os.getenv('NOTION_TOKEN') or not os.getenv('NOTION_DATABASE_ID'):
            logger.info("노션 설정이 없어 건너뛰기")
            return {"success": False, "error": "노션 설정이 없습니다"}
        
        logger.info("노션에 저장 중...")
        
        # 노션용 데이터 변환
        topics_list = [topic["title"] for topic in final_topics]
        qa_pairs = []
        kid_friendly_pairs = []
        
        for topic in final_topics:
            for qa in topic["qa_pairs"]:
                qa_pairs.append({
                    "question": qa.get("original_question", qa.get("kid_friendly_question", "")),
                    "answer": qa.get("original_answer", qa.get("kid_friendly_answer", ""))
                })
                kid_friendly_pairs.append({
                    "question": qa.get("kid_friendly_question", ""),
                    "answer": qa.get("kid_friendly_answer", "")
                })
        
        # 노션에 저장
        result = save_to_notion(video_info, topics_list, qa_pairs, kid_friendly_pairs)
        
        return result
    
    def post(self, shared, prep_res, exec_res):
        """Store notion result in shared"""
        shared["notion_result"] = exec_res
        
        if exec_res.get("success"):
            logger.info(f"✅ 노션 저장 완료: {exec_res.get('page_url', '')}")
        else:
            logger.warning(f"⚠️ 노션 저장 실패: {exec_res.get('error', '알 수 없는 오류')}")
        
        # 진행상황 업데이트
        callback = shared.get("progress_callback")
        if callback:
            if exec_res.get("success"):
                callback("노션 저장 완료", "✅ 노션 데이터베이스에 성공적으로 저장되었습니다!", 95)
            else:
                callback("노션 저장 건너뛰기", "ℹ️ 노션 설정이 없어 이 단계를 건너뛰었습니다", 95)
        
        return "default"

class GenerateHTML(Node):
    """Generate HTML output from processed content"""
    def prep(self, shared):
        """Get video info and final topics from shared"""
        # 진행상황 업데이트
        callback = shared.get("progress_callback")
        if callback:
            callback("HTML 생성", "최종 HTML 페이지를 생성하는 중...", 98)
        
        video_info = shared.get("video_info", {})
        final_topics = shared.get("final_topics", [])
        
        return {
            "video_info": video_info,
            "final_topics": final_topics
        }
    
    def exec(self, data):
        """Generate HTML using html_generator"""
        video_info = data["video_info"]
        final_topics = data["final_topics"]
        
        title = video_info.get("title", "YouTube Video Summary")
        thumbnail_url = video_info.get("thumbnail_url", "")
        
        logger.info("Generating HTML output...")
        
        # Prepare sections for HTML generator
        sections = []
        for topic in final_topics:
            topic_title = topic["title"]
            qa_pairs = topic["qa_pairs"]
            
            # Skip topics without Q&A pairs
            if not qa_pairs:
                continue
            
            # Prepare bullets (question-answer pairs)
            bullets = []
            for qa in qa_pairs:
                question = qa["kid_friendly_question"]
                answer = qa["kid_friendly_answer"]
                
                # Only add if both question and answer have content
                if question.strip() and answer.strip():
                    bullets.append((f"Q: {question}", f"A: {answer}"))
            
            # Only include section if it has bullets
            if bullets:
                sections.append({
                    "title": topic_title,
                    "bullets": bullets
                })
        
        # Generate HTML for both purposes
        file_html = html_generator(title, thumbnail_url, sections)
        streamlit_html = streamlit_html_generator(title, thumbnail_url, sections)
        
        return {
            "file_html": file_html,
            "streamlit_html": streamlit_html
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store HTML output and save to file"""
        shared["html_output"] = exec_res["streamlit_html"]  # Streamlit용 HTML
        shared["file_html"] = exec_res["file_html"]  # 파일 다운로드용 HTML
        
        # Write HTML to file
        output_file = "output.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(exec_res["file_html"])
        
        logger.info(f"Generated HTML output and saved to {output_file}")
        
        # 진행상황 업데이트
        callback = shared.get("progress_callback")
        if callback:
            callback("HTML 생성 완료", "✅ 아름다운 HTML 페이지가 완성되었습니다!", 100)
        
        return "default"

def create_youtube_processor_flow():
    """Create and connect the nodes for the YouTube processor flow"""
    # Create nodes with retry configuration
    process_url = ProcessYouTubeURL(max_retries=2, wait=5)
    extract_topics = ExtractTopics(max_retries=3, wait=2)
    generate_qa = GenerateQA(max_retries=3, wait=2)
    convert_kid_friendly = ConvertToKidFriendly(max_retries=3, wait=2)
    review_and_correct = ReviewAndCorrect(max_retries=2, wait=2)  # AI 검토 단계!
    save_to_notion = SaveToNotion(max_retries=2, wait=1)  # 노션 저장 단계!
    generate_html = GenerateHTML(max_retries=2, wait=1)
    
    # Connect nodes in sequence with AI Review and Notion Save steps
    process_url >> extract_topics >> generate_qa >> convert_kid_friendly >> review_and_correct >> save_to_notion >> generate_html
    
    # Create flow
    flow = Flow(start=process_url)
    
    logger.info("YouTube processor flow created successfully with AI Review & Notion Save")
    return flow

if __name__ == "__main__":
    # Test flow creation
    flow = create_youtube_processor_flow()
    print("Flow created successfully!")
    
    # Check API key status
    if os.getenv("OPENAI_API_KEY"):
        print("✅ OPENAI_API_KEY is set - will use real OpenAI API")
    else:
        print("⚠️  OPENAI_API_KEY not set - will use Mock mode for testing")
