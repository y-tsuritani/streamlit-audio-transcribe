import os

from dotenv import load_dotenv
from openai import OpenAI


def correct_text(client: OpenAI, text: str) -> str:
    prompt = f"以下の文章を校正してください:\n\n{text}\n\n校正後の文章:"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
            {"role": "system", "content": "あなたは優秀な日本語の編集者です。"},
            {"role": "user", "content": prompt},
        ],
    )
    print(response)
    print(response.choices[0].message.content)
    return response.choices[0].message.content


# 使用例
load_dotenv()  # 環境変数を読み込む
api_key = os.getenv("OPENAI_API_KEY")  # 環境変数からAPIキーを読み込む
client = OpenAI(api_key=api_key)
text = "ここに校正したいテキストを入力しすま。ｗたしｎ名前は、たろうでｓ。"
corrected_text = correct_text(client, text)
print(corrected_text)
