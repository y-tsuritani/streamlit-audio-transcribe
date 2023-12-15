import base64
import os
from typing import Any, List

import streamlit as st
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI

load_dotenv()  # 環境変数を読み込む
api_key = os.getenv("OPENAI_API_KEY")  # 環境変数からAPIキーを読み込む
client = OpenAI(api_key=api_key)


class JapaneseCharacterTextSplitter(RecursiveCharacterTextSplitter):
    def __init__(self, **kwargs: Any):
        separators = ["\n\n", "\n", "。", "、", " ", ""]
        super().__init__(separators=separators, **kwargs)


japanese_spliter = JapaneseCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=0,
)


def correct_japanese_text(client, text: str) -> str:
    try:
        # テキストをチャンクに分割
        chunks = japanese_spliter.split_text(text)

        # 各チャンクを校正
        corrected_chunks = []
        for chunk in chunks:
            prompt = (
                f"##音声文字起こしで不自然な文を削除し、自然な文章に修正してください。\n##音声文字起こし\n{chunk}\n##修正した文章\n"
            )
            messages = [
                {"role": "system", "content": "あなたは優秀な日本語の編集者です。"},
                {"role": "user", "content": prompt},
            ]
            text_modified = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=messages,
                temperature=0,
            )
            corrected_chunks.append(text_modified.choices[0].message.content)
    except Exception as e:
        raise e

    # 校正されたチャンクを結合
    return "".join(corrected_chunks)


# このファイルを実行したときに、以下のコードが実行される
if __name__ == "__main__":
    text = "ここに校正したいテキストを入力しすま。ｗたしｎ名前は、たろうでｓ。"
    modified_text = correct_japanese_text(client, text=text)
    print(modified_text)
