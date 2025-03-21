from youtube_transcript_api.proxies import WebshareProxyConfig
from AgentWorkflow.utils.state import State
from AgentWorkflow.utils.model import llm
from langchain_community.tools import YouTubeSearchTool
from youtube_transcript_api import YouTubeTranscriptApi
import ast
import re
from langchain_core.prompts import PromptTemplate
from langgraph.graph import END
from langchain_core.output_parsers.string import StrOutputParser
from gtts import gTTS

async def get_video_url(state: State):
    """
    Searches YouTube for a given query and returns a video URL.

    Args:
        query (str): The search query.

    Returns:
        str: A YouTube video URL, or None if no results are found.
    """
    print("get video url")
    refined_query = state['video_name'].replace(",", " ")+", 1"
    tool = YouTubeSearchTool()
    result = tool.run(refined_query)

    try:
        result_list = ast.literal_eval(result)  # Convert string to list
        return {"url": result_list[0]} if result_list else {"url": None}  
    except (SyntaxError, ValueError):
        print("Error parsing YouTube search results.")
        return {"url": None}
    
    
async def get_video_id_from_url(state: State) -> str:
    """
    Extracts the video ID from a YouTube URL.
    
    Args:
        youtube_url (str): The full YouTube video URL.

    Returns:
        str: The extracted video ID, or None if not found.
    """
    print("get video id from url")
    match = re.search(r"(?:v=|\/embed\/|\/v\/|\/vi\/|youtu\.be\/|\/e\/|watch\?v=|&v=)([a-zA-Z0-9_-]{11})", state['url'])
    return {"video_id": match.group(1)} if match else {"video_id": None}


async def transcribe_youtube_video(state: State):
    """
    Fetches and transcribes a YouTube video using its video ID.

    Args:
        video_id (str): The YouTube video ID.

    Returns:
        str: The transcript text, or an error message if unavailable.
    """
    print('transcribe youtube video')
    try:
        transcript = YouTubeTranscriptApi(
                proxy_config=WebshareProxyConfig(
            proxy_username="qojeceia",
            proxy_password="ze0fe6rqefkf",
        )
            ).get_transcript(state['video_id'])
        transcript_text = " ".join([entry["text"] for entry in transcript])
        return {"transcript": transcript_text}
    except Exception as e:
        print(f"Error fetching transcript: {str(e)}")
        return {"transcript": None}
    

async def get_video_summary(state: State):
    """
    Generates a summary of a YouTube video transcript.

    This function takes a video transcript stored in the given state 
    and processes it using an AI-powered summarization pipeline. 
    The summary captures the core points and main message of the video.

    Args:
        state (State): A state object containing the 'transcript' key 
                      with the video transcript as its value.

    Returns:
        dict: A dictionary containing the summary of the video 
              with the key 'summary'.
    """
    print("get video summary")
    summarizer_prompt = """
    You are a video summarizer that summarizes YouTube video transcripts. 
    Given this transcription: {transcription}
    You are to create a summary that includes includes the crux of the video and contains the core points of the video.
    """
    summarizer_prompt_template = PromptTemplate(
        input_variables = ['transcripiton'],
        template = summarizer_prompt
    )
    summarizer_chain = summarizer_prompt_template | llm | StrOutputParser()
    summary = await summarizer_chain.ainvoke({"transcription": state['transcript']})
    
    return {"summary": summary}

async def generate_audio_summary(state: State):
    """
    Converts the video summary into an audio file.

    Args:
        state (State): Contains the 'summary' key with the summary text.

    Returns:
        dict: Dictionary containing the filename of the generated audio file.
    """
    print("get audio summary")
    summary_text = state["summary"]
    
    if not summary_text:
        return {"audio_file": None}

    try:
        audio_filename = "summary.mp3"
        tts = gTTS(text=summary_text, lang="en")
        tts.save(audio_filename)
        return {"audio_file": audio_filename}
    except Exception as e:
        print(f"Error generating audio: {e}")
        return {"audio_file": None}


async def get_video_keypoints(state: State):
    """
    Generates a summary of a YouTube video transcript.

    This function takes a video transcript stored in the given state 
    and processes it using an AI-powered summarization pipeline. 
    The summary captures the core points and main message of the video.

    Args:
        state (State): A state object containing the 'transcript' key 
                      with the video transcript as its value.

    Returns:
        dict: A dictionary containing the summary of the video 
              with the key 'summary'.
    """
    key_points_prompt = """
    You are a transcript Note-Taker that give the key-points of a YouTube video transcripts. 
    Given this transcription: {transcription}
    You are to give 5 crucial keypoints that hit the crux of the video and contains the core points of the video.
    """
    key_points_prompt_template = PromptTemplate(
        input_variables = ['transcripiton'],
        template = key_points_prompt
    )
    
    key_points_chain = key_points_prompt_template | llm | StrOutputParser()
    key_points = await key_points_chain.ainvoke({"transcription": state['transcript']})
    
    return {"key_points": key_points}

def transcript_condition(state):
    """Decides the next step based on transcript availability."""
    transcript = state.get("transcript")
    if transcript is None or transcript.startswith("Error"):  
        return END  # If no transcript, go to END
    return "get_video_summary"