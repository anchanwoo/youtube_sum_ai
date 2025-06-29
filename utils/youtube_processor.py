import re
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url):
    """Extract YouTube video ID from URL"""
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_video_info(url):
    """Get video title, transcript and thumbnail with multi-language support"""
    video_id = extract_video_id(url)
    if not video_id:
        return {"error": "Invalid YouTube URL"}
    
    try:
        # Get title using BeautifulSoup
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('title')
        title = title_tag.text.replace(" - YouTube", "").strip()
        
        # Get thumbnail
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        
        # Get transcript with multi-language support
        transcript, language_used = get_transcript_multi_language(video_id)
        
        return {
            "title": title,
            "transcript": transcript,
            "thumbnail_url": thumbnail_url,
            "video_id": video_id,
            "language_used": language_used
        }
    except Exception as e:
        return {"error": str(e)}

def get_transcript_multi_language(video_id):
    """
    Try to get transcript in multiple languages
    Priority: Korean → English → Japanese
    Returns: (transcript_text, language_used)
    """
    # Priority order: Korean, English, Japanese only
    language_priority = ['ko', 'en', 'ja']
    
    try:
        # First, try with priority languages only
        for lang in language_priority:
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                transcript = " ".join([entry["text"] for entry in transcript_list])
                language_name = {'ko': 'Korean', 'en': 'English', 'ja': 'Japanese'}[lang]
                print(f"✅ Found {language_name} ({lang}) transcript")
                return transcript, lang
            except:
                continue
        
        # If none of the priority languages are found, try auto-generated captions
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            available_languages = []
            auto_generated_found = None
            
            # Check available transcripts and look for auto-generated ones
            for transcript_info in transcript_list:
                lang_info = f"{transcript_info.language_code} ({transcript_info.language})"
                if transcript_info.is_generated:
                    lang_info += " [자동생성]"
                    if transcript_info.language_code in language_priority and not auto_generated_found:
                        auto_generated_found = transcript_info.language_code
                available_languages.append(lang_info)
            
            # Try auto-generated captions if available
            if auto_generated_found:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[auto_generated_found])
                transcript = " ".join([entry["text"] for entry in transcript_list])
                language_name = {'ko': 'Korean', 'en': 'English', 'ja': 'Japanese'}[auto_generated_found]
                print(f"✅ Found auto-generated {language_name} ({auto_generated_found}) transcript")
                return transcript, auto_generated_found
            
            # If still no luck, provide helpful error message
            suggestion = "🔍 **해결 방법:**\n"
            suggestion += "1. **다른 비디오 시도**: 자막이 있는 다른 YouTube 비디오를 사용해보세요\n"
            suggestion += "2. **인기 채널 추천**: 교육 채널이나 뉴스 채널은 보통 자막이 제공됩니다\n"
            suggestion += "3. **최신 비디오**: 최근 업로드된 비디오일수록 자막이 있을 확률이 높습니다\n\n"
            
            if available_languages:
                error_msg = f"😅 이 비디오는 한국어, 영어, 일본어 자막이 없어요!\n\n📋 **사용 가능한 언어**: {', '.join(available_languages)}\n\n{suggestion}"
            else:
                error_msg = f"😅 이 비디오에는 자막이 전혀 없어요!\n\n{suggestion}"
            
        except Exception as list_error:
            error_msg = f"😅 비디오 자막을 가져올 수 없어요!\n\n🔍 **해결 방법:**\n1. 다른 YouTube 비디오를 시도해보세요\n2. 자막이 있는 교육용 비디오를 추천합니다\n3. 최신 업로드 비디오를 선택해보세요\n\n📝 **기술적 오류**: {str(list_error)}"
        
        raise Exception(error_msg)
        
    except Exception as e:
        raise Exception(f"😅 비디오 자막을 가져올 수 없어요!\n\n🔍 **해결 방법:**\n1. 다른 YouTube 비디오를 시도해보세요\n2. 자막이 있는 교육용 비디오를 추천합니다\n3. 최신 업로드 비디오를 선택해보세요\n\n📝 **기술적 오류**: {str(e)}")

if __name__ == "__main__":
    # Test with Korean video
    test_url = "https://youtu.be/FI8ozR1NLbA?si=EBTyq171a-vdTQB5"
    print(f"Testing with URL: {test_url}")
    
    result = get_video_info(test_url)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Title: {result.get('title')}")
        print(f"✅ Language used: {result.get('language_used')}")
        print(f"✅ Transcript preview: {result.get('transcript', '')[:200]}...")
        print(f"✅ Video ID: {result.get('video_id')}")
        print(f"✅ Thumbnail URL: {result.get('thumbnail_url')}")