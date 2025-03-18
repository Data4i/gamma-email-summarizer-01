from AgentWorkflow.utils.state import State
from AgentWorkflow.utils.nodes import get_video_id_from_url, get_video_keypoints, get_video_summary, get_video_url, transcribe_youtube_video, generate_audio_summary, transcript_condition
from langgraph.graph import StateGraph, END

graph = StateGraph(State)

graph.add_node("get_video_url", get_video_url)
graph.add_node("get_video_id_from_url", get_video_id_from_url)
graph.add_node("transcribe_youtube_video", transcribe_youtube_video)
graph.add_node("get_video_summary", get_video_summary)
graph.add_node("generate_audio_summary", generate_audio_summary)
graph.add_node("get_video_keypoints", get_video_keypoints)

graph.add_edge("get_video_url", "get_video_id_from_url")
graph.add_edge("get_video_id_from_url", "transcribe_youtube_video")
graph.add_conditional_edges("transcribe_youtube_video", transcript_condition)
graph.add_edge("transcribe_youtube_video", "get_video_summary")
graph.add_edge("transcribe_youtube_video", "get_video_keypoints")
graph.add_edge("get_video_summary", "generate_audio_summary")

graph.add_edge("generate_audio_summary", END)
graph.add_edge("get_video_keypoints", END)

# Define entry and output nodes
graph.set_entry_point("get_video_url")

# Compile the LangGraph workflow
summary_workflow = graph.compile()

async def run_transcriber(video_name: str):
    initial_state = {"video_name": video_name, "url": "", "video_id": "", "transcript": "", "key_points": "", "summary": "", "audio_file": ""}
    final_state = await summary_workflow.ainvoke(initial_state)
    return final_state