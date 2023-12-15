# Streamlit を利用して、音声ファイルをアップロードし、音声認識を行うアプリケーションを作成する
# アップロードファイルのサイズが大きい場合は、API上限に引っかかる可能性があるので、警告を表示する
# 文字起こし実行中は、ローディングアイコンを表示し、「音声文字起こしを実行中です...」というメッセージを表示する
# 文字起こしが完了したら、文字起こしが完了しました当メッセージの下部に、文字起こし結果を表示する
# 文字起こしした結果を、ダウンロードすることができるようにする
# 文字起こし結果を、OpenAI API と langchain を利用して、句読点の追加や、読みやすいように校正を実施するか確認する
# 文字起こし結果の校正を実施する場合は、OpenAI API を利用して、校正結果を表示する

import base64
import os
from typing import Any, List

import streamlit as st
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter

# from langchain.chains import OpenAIChain
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
            prompt = f"##音声文字起こしで不自然な文を修正し、自然な文章にしてください。文章の修正は句読点の追加と誤字脱字の修正にとどめ、要約は絶対にしないでください。\n##音声文字起こし\n{chunk}\n##修正した文章\n"
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


# アプリケーションのタイトルを設定する
st.title("音声文字起こしアプリ")

# アップロードダイアログを表示する
audio_file = st.file_uploader(
    "音声ファイルをアップロードしてください", type=["m4a", "mp3", "webm", "mp4", "mpga", "wav"]
)
# アップロードファイルのサイズが大きい場合は、警告を表示する
if audio_file is not None:
    if audio_file.size > 25000000:
        st.warning("25 MBを超えるファイルは、API 制限のためアップロードできません。")

if audio_file is not None:
    st.audio(audio_file, format="audio/wav")

    if st.button("音声文字起こしを実行する"):
        with st.spinner("音声文字起こしを実行中です..."):
            transcript = client.audio.transcriptions.create(
                model="whisper-1", file=audio_file, response_format="text"
            )
        st.success("音声文字起こしが完了しました！")
        st.write(transcript)

        with st.spinner("校正中です..."):
            corrected_text = correct_japanese_text(client, transcript)
        st.success("校正が完了しました！")
        st.write("校正結果")
        st.write(corrected_text)

        # 文字起こしをバイトに変換し、それをbase64でエンコードする
        transcript_encoded = base64.b64encode(corrected_text.encode()).decode()
        # ダウンロードリンクを作成する
        st.markdown(
            f'<a href="data:file/txt;base64,{transcript_encoded}" download="transcript.txt">Download Result</a>',
            unsafe_allow_html=True,
        )
