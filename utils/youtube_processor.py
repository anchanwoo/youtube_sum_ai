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
        
        # If none of the priority languages are found, raise error
        raise Exception("No transcript available in Korean, English, or Japanese")
        
    except Exception as e:
        # List available transcripts for debugging
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            available_languages = []
            for transcript_info in transcript_list:
                available_languages.append(f"{transcript_info.language_code} ({transcript_info.language})")
            
            error_msg = f"No transcript found in supported languages (Korean, English, Japanese). Available languages: {', '.join(available_languages)}"
        except:
            error_msg = f"Failed to get transcript: {str(e)}"
        
        raise Exception(error_msg)

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