import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # .env から環境変数を読み込む

# 環境変数からAPIキーを読み込む
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

transcript = "お電話ありがとうございます大変申し訳ございませんが本日の営業はすべて終了させていただきましたまたのお電話をお待ちしております"

# プロンプト内容は、文字起こししたい内容に合わせて、適宜変更してください
prompt = f"##音声文字起こしで不自然な文を修正し、自然な文章にしてください。文章の修正は句読点の追加と誤字脱字の修正にとどめ、要約は絶対にしないでください。\n##音声文字起こし\n{transcript}\n##修正した文章\n"
messages = [
    {"role": "system", "content": "あなたは優秀な日本語の編集者です。"},
    {"role": "user", "content": prompt},
]
# 言語モデルは応答速度を重視して、gpt-3.5-turbo-1106を使用する
text_modified = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=messages,
    temperature=0,
)
print(text_modified.choices[0].message.content)
