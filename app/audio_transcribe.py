import base64
import io
import os
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
from pydub import AudioSegment
from pydub.silence import split_on_silence

load_dotenv()  # 環境変数を読み込む
api_key = os.getenv("OPENAI_API_KEY")  # 環境変数からAPIキーを読み込む
client = OpenAI(api_key=api_key)


class JapaneseCharacterTextSplitter(RecursiveCharacterTextSplitter):
    def __init__(self, **kwargs: Any):
        separators = ["\n\n", "\n", "。", "、", " ", ""]
        super().__init__(separators=separators, **kwargs)


japanese_splitter = JapaneseCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=0,
)


def split_audio(file: bytes, max_size: int = 600000) -> list[AudioSegment]:
    """
    音声ファイルを指定された最大サイズに分割します。

    Args:
        file (bytes): 分割する音声ファイル。
        max_size (int, optional): 分割後の各ファイルの最大長（ミリ秒）

    Returns:
        list[AudioSegment]: 分割された音声ファイル。
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


def convert_audio_to_mp3(audio_file: AudioSegment) -> io.BytesIO:
    """
    AudioSegment 形式の音声ファイルをMP3形式に変換します。

    Args:
        audio_file (AudioSegment): バイト形式に変換する音声ファイル。

    Returns:
        io.BytesIO: バイト形式に変換された音声ファイル。
    """
    byte_io = io.BytesIO()
    audio_file.export(byte_io, format="mp3")
    byte_io.seek(0)  # ポインタをファイルの先頭に戻す

    return byte_io


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
            prompt = f"##以下は、データ分析基盤の構築に関するコンサルティング会社における会議の会話の音声認識テキストです。特定の専門用語やIT用語が誤って認識されている可能性があります。誤認識された用語を正しい用語に修正してください。また、音声文字起こしで不自然な文を修正し、自然な文章にしてください。文章の修正は句読点の追加と誤字脱字の修正にとどめ、要約は絶対にしないでください。\n##音声文字起こし\n{chunk}\n##修正した文章\n"
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


def save_temporary_file(file: bytes) -> None:
    """
    バイト形式のファイルを一時ファイルとして保存します。

    Args:
        file (bytes): 保存するファイル。
        file_name (str): 保存するファイルの名前。
    """
    temp_file_name = "temp_audio.mp3"
    with open(temp_file_name, "wb") as f:
        f.write(file)


def main():
    # Set the title of the application
    st.title("Streamlit Audio Transcribe(音声文字起こしアプリ)")

    # Display upload dialog
    audio_file = st.file_uploader(
        "Please upload audio file", type=["m4a", "mp3", "webm", "mp4", "mpga", "wav"]
    )

    # Check the size of the uploaded audio file and split it if it exceeds 25MB
    if audio_file is not None:
        # Perform transcription of uploaded audio files
        if st.button("Start Audio Transcription"):
            full_transcript = ""
            if audio_file.size > 25 * 1024 * 1024:
                st.warning(
                    "Larger than 25 MB file has been uploaded. Audio file will be split"
                )
                with st.spinner(
                    "Audio files are being split... This may take a few minutes..."
                ):
                    audio_segments = split_audio(audio_file)
                st.success(f"Audio files are split into {len(audio_segments)} segments")
                with st.spinner("Audio file is being transcribed..."):
                    for i, audio_segment in enumerate(audio_segments):
                        with st.spinner(
                            f"Transcribing the {i + 1}th audio segments..."
                        ):
                            byte_audio_io = convert_audio_to_mp3(audio_segment)
                            temp_file_name = "./audio/temp_audio.mp3"
                            with open(temp_file_name, "wb") as f:
                                f.write(byte_audio_io.read())
                            with open(temp_file_name, "rb") as audio_file:
                                transcript = extract_text_from_audio(client, audio_file)
                            corrected_transcript = correct_japanese_text(
                                client, transcript
                            )
                            full_transcript += corrected_transcript
            else:
                with st.spinner("Audio file is being transcribed..."):
                    transcript = extract_text_from_audio(client, audio_file)
                    corrected_transcript = correct_japanese_text(client, transcript)
                    full_transcript += corrected_transcript

            st.success("All audio transcription has been completed!")
            st.info("Displays voice transcription results")
            st.write(full_transcript)

            # Convert the transcription to bytes and encode it in base64
            transcript_encoded = base64.b64encode(full_transcript.encode()).decode()
            # Create a download link
            st.markdown(
                f'<a href="data:file/txt;base64,{transcript_encoded}" download="transcript.txt">Download Result</a>',
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
