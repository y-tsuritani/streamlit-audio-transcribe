import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 環境変数を読み込む

# 環境変数からAPIキーを読み込む
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

with open("../audio/test.mp3", "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model="whisper-1", file=audio_file, response_format="text"
    )

print(transcript)
