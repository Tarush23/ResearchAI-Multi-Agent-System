from langchain.chat_models import init_chat_model
import os

from dotenv import load_dotenv

load_dotenv()

llm1 = init_chat_model(
    "google_genai:gemini-3.5-flash",
    api_key=os.getenv("GEMINI_API_KEY_1"),
    temperature=0
)

llm2 = init_chat_model(
    "google_genai:gemini-3.5-flash",
    api_key=os.getenv("GEMINI_API_KEY_2"),
    temperature=0.2
)

print(llm1.invoke("hello gemini").content)

print("\n------\n")

print(llm2.invoke("hello gemini").content)