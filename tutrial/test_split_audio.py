from pydub import AudioSegment
from pydub.silence import split_on_silence

audio_file = "sample.wav"
max_size = 60 * 1000  # 60 秒

# 音声ファイルを読み込む
sound = AudioSegment.from_file("sample.wav", format="wav")

# 無音区間ごとに分割する
chunks = split_on_silence(sound, min_silence_len=1000, silence_thresh=-50)

# 60秒以内に収まる範囲で、分割した音声ファイルを結合して適切なサイズにする
combined_chunks = []
current_chunk = chunks[0]
for chunk in chunks[1:]:
    if len(current_chunk) + len(chunk) < max_size:
        current_chunk += chunk
    else:
        combined_chunks.append(current_chunk)
        current_chunk = chunk
combined_chunks.append(current_chunk)

# 分割した音声ファイルを保存する
for i, chunk in enumerate(combined_chunks):
    chunk.export(f"sample_{i}.wav", format="wav")
