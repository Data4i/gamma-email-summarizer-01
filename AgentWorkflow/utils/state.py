from typing_extensions import TypedDict

class State(TypedDict):
    video_name: str
    url: str
    video_id: str
    transcript: str
    key_points: str
    summary: str