from langchain_together import ChatTogether
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

llm = ChatTogether(
    model = "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    temperature = 0
)