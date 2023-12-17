import base64
import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 環境変数を読み込む

# 環境変数からAPIキーを読み込む
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

st.title("音声文字起こしアプリ")

audio_file = st.file_uploader(
    "音声ファイルをアップロードしてください", type=["m4a", "mp3", "webm", "mp4", "mpga", "wav"]
)

if audio_file is not None:
    st.audio(audio_file, format="audio/wav")

    if st.button("音声文字起こしを実行する"):
        with st.spinner("音声文字起こしを実行中です..."):
            transcript = client.audio.transcriptions.create(
                model="whisper-1", file=audio_file, response_format="text"
            )
        st.success("音声文字起こしが完了しました！")
        st.write(transcript)

        # 文字起こしをバイトに変換し、それをbase64でエンコードする
        transcript_encoded = base64.b64encode(transcript.encode()).decode()
        # ダウンロードリンクを作成する
        st.markdown(
            f'<a href="data:file/txt;base64,{transcript_encoded}" download="transcript.txt">Download Result</a>',
            unsafe_allow_html=True,
        )
