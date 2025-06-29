from typing import List, Dict, Any
import logging
import os
from pocketflow import Node, BatchNode, Flow
from utils.call_llm import call_llm
from utils.youtube_processor import get_video_info
from utils.html_generator import html_generator
from utils.topic_extractor import extract_interesting_topics
from utils.qa_generator import generate_qa_pairs
from utils.kid_friendly_converter import convert_to_kid_friendly
from utils.content_validator import validate_transcript_quality, ensure_topic_diversity

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
        return "default"

class ExtractTopics(Node):
    """Extract interesting topics from the video transcript"""
    def prep(self, shared):
        """Get transcript from video_info"""
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
        return "default"

class GenerateQA(BatchNode):
    """Generate Q&A pairs for each topic"""
    def prep(self, shared):
        """Return list of topics for batch processing"""
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
        return "default"

class ConvertToKidFriendly(BatchNode):
    """Convert content to kid-friendly explanations"""
    def prep(self, shared):
        """Return list of topics with Q&A pairs for batch processing"""
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
        return "default"

class GenerateHTML(Node):
    """Generate HTML output from processed content"""
    def prep(self, shared):
        """Get video info and final topics from shared"""
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
        
        # Generate HTML
        html_content = html_generator(title, thumbnail_url, sections)
        return html_content
    
    def post(self, shared, prep_res, exec_res):
        """Store HTML output and save to file"""
        shared["html_output"] = exec_res
        
        # Write HTML to file
        output_file = "output.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(exec_res)
        
        logger.info(f"Generated HTML output and saved to {output_file}")
        return "default"

def create_youtube_processor_flow():
    """Create and connect the nodes for the YouTube processor flow"""
    # Create nodes with retry configuration
    process_url = ProcessYouTubeURL(max_retries=2, wait=5)
    extract_topics = ExtractTopics(max_retries=3, wait=2)
    generate_qa = GenerateQA(max_retries=3, wait=2)
    convert_kid_friendly = ConvertToKidFriendly(max_retries=3, wait=2)
    generate_html = GenerateHTML(max_retries=2, wait=1)
    
    # Connect nodes in sequence
    process_url >> extract_topics >> generate_qa >> convert_kid_friendly >> generate_html
    
    # Create flow
    flow = Flow(start=process_url)
    
    logger.info("YouTube processor flow created successfully")
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
