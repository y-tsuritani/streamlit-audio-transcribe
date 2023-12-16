# Streamlit を利用して、音声ファイルをアップロードし、音声認識を行うアプリケーションを作成する
# アップロードファイルのサイズが大きい場合は、API上限に引っかかる可能性があるので、警告を表示する
# 文字起こし実行中は、ローディングアイコンを表示し、「音声文字起こしを実行中です...」というメッセージを表示する
# 文字起こしが完了したら、文字起こしが完了しました当メッセージの下部に、文字起こし結果を表示する
# 文字起こしした結果を、ダウンロードすることができるようにする
# 文字起こし結果を、OpenAI API と langchain を利用して、句読点の追加や、読みやすいように校正を実施するか確認する
# 文字起こし結果の校正を実施する場合は、OpenAI API を利用して、校正結果を表示する

import base64
import io
import os
from logging import DEBUG, StreamHandler, getLogger
from typing import Any, List

import streamlit as st
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
from pydub import AudioSegment
from pydub.silence import split_on_silence

load_dotenv()  # 環境変数を読み込む
api_key = os.getenv("OPENAI_API_KEY")  # 環境変数からAPIキーを読み込む
client = OpenAI(api_key=api_key)

# ログ出力の設定
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False


class JapaneseCharacterTextSplitter(RecursiveCharacterTextSplitter):
    def __init__(self, **kwargs: Any):
        separators = ["\n\n", "\n", "。", "、", " ", ""]
        super().__init__(separators=separators, **kwargs)


japanese_splitter = JapaneseCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=0,
)


def split_audio(
    file: Any, max_size: int = 20 * 1024 * 1024
) -> list[AudioSegment]:  # API上限は25MBだが、余裕を持たせて20MBに設定
    """
    音声ファイルを指定された最大サイズに分割します。

    Args:
        file (Any): 分割する音声ファイル。
        max_size (int, optional): 分割後の各ファイルの最大サイズ（バイト単位）。デフォルトは25MB。

    Returns:
        Any: 分割された音声ファイル。
    """
    audio = AudioSegment.from_file_using_temporary_files(file)
    chunks = split_on_silence(audio, min_silence_len=2000, silence_thresh=-40)

    combined_chunks = []
    current_chunk = chunks[0]
    for chunk in chunks[1:]:
        if len(current_chunk) + len(chunk) < max_size:
            current_chunk += chunk
        else:
            combined_chunks.append(current_chunk)
            current_chunk = chunk
    combined_chunks.append(current_chunk)

    return combined_chunks


def convert_audio(audio_file: AudioSegment) -> bytes:
    """
    AudioSegment 形式の音声ファイルをバイト形式に変換します。

    Args:
        audio_file (AudioSegment): バイト形式に変換する音声ファイル。

    Returns:
        bytes: バイト形式に変換された音声ファイル。
    """
    byte_io = io.BytesIO()
    audio_file.export(byte_io, format="wav")
    byte_audio = byte_io.getvalue()

    return byte_audio


def extract_text_from_audio(client: OpenAI, audio_file: bytes) -> str:
    """
    音声ファイルからテキストを抽出します。

    Args:
        audio_file (Any): 音声ファイル。

    Returns:
        str: 音声ファイルから抽出されたテキスト。
    """
    try:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file, response_format="text"
        )
    except Exception as e:
        raise e

    return transcript


def correct_japanese_text(client: OpenAI, text: str) -> str:
    """
    日本語のテキストを修正します。

    Args:
        client (OpenAI): 日本語のテキストを修正するためのクライアント。
        text (str): 修正する日本語のテキスト。

    Returns:
        str: 修正された日本語のテキスト。
    """
    try:
        # テキストをチャンクに分割
        chunks = japanese_splitter.split_text(text)

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


def main():
    # アプリケーションのタイトルを設定する
    st.title("音声文字起こしアプリ")

    # アップロードダイアログを表示する
    audio_file = st.file_uploader(
        "音声ファイルをアップロードしてください", type=["m4a", "mp3", "webm", "mp4", "mpga", "wav"]
    )

    # アップロードされた音声ファイルのサイズを確認して、25MBを超えていたら、分割する
    if audio_file is not None:
        # アップロードされた音声ファイルの文字起こしを実行する
        if st.button("音声文字起こしを実行する"):
            full_transcript = ""
            if audio_file.size > 25 * 1024 * 1024:
                st.warning("25 MBを超えるファイルがアップロードされました。音声ファイルを分割します")
                with st.spinner("音声ファイルを分割中です..."):
                    audio_segments = split_audio(audio_file)
                    st.info(f"音声ファイルを{len(audio_segments)}個に分割しました")
                    for i, audio_segment in enumerate(audio_segments):
                        st.info(f"{i + 1}個目の音声ファイルを変換中です...")
                        audio_file = convert_audio(audio_segment)
                        st.info(f"{i + 1}個目の音声ファイルの文字起こしを実行中です...")
                        transcript = extract_text_from_audio(client, audio_file)
                        st.info(f"{i + 1}個目の音声ファイルの文字起こしを校正中です...")
                        corrected_transcript = correct_japanese_text(client, transcript)
                        full_transcript += corrected_transcript
                st.success("音声ファイルの分割が完了しました！")
            else:
                st.info("音声ファイルを文字起こし中です...")
                transcript = extract_text_from_audio(client, audio_file)
                st.info("音声ファイルの文字起こしを校正中です...")
                corrected_transcript = correct_japanese_text(client, transcript)
                full_transcript += corrected_transcript

            st.success("全ての音声文字起こしが完了しました！")
            st.write(full_transcript)

            # 文字起こしをバイトに変換し、それをbase64でエンコードする
            transcript_encoded = base64.b64encode(full_transcript.encode()).decode()
            # ダウンロードリンクを作成する
            st.markdown(
                f'<a href="data:file/txt;base64,{transcript_encoded}" download="transcript.txt">Download Result</a>',
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
