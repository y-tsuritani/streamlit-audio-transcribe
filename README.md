# streamlit-audio-transcribe

## An audio transcribe for streamlit

### Descriptionds

This is a speech recognition application that runs on Streamlit.
Upload an audio file and press the Start Speech Recognition button to start speech recognition and transcription.
When speech recognition is complete, the transcribed text is automatically proofread using the OpenAI API.
When proofreading is complete, the proofread text will be displayed.
The text can be downloaded.

Streamlit 上で動作する音声認識アプリケーションです。
音声ファイルをアップロードして、音声認識を開始するボタンを押すと、音声認識が開始され、文字起こしが行われます。
音声認識が終了すると、文字起こしされたテキストは、OpenAI API を用いて、自動で校正されます。
校正が完了すると、校正されたテキストが表示されます。
テキストはダウンロード可能です。

### Installation

To install the application, install the following libraries.

以下のライブラリをインストールしてください。

```bash
pip install openai
pip install streamlit
pip install langchain
pip install python-dotenv
pip install pydub
```

Note: This package uses ffmpeg, so it should be installed for this app to work properly.

注意：このパッケージは ffmpeg を使用しているので、このアプリが正常に動作するためには、ffmpeg をインストールする必要があります。

On ubuntu/debian: `sudo apt update && sudo apt install ffmpeg`
On mac: `brew install ffmpeg`
On windows: `choco install ffmpeg`

詳しい使用方法は、以下のブログ記事を参照してください。

1. [Streamlit と Whisper で簡単文字起こしアプリ作ってみた](https://zenn.dev/gixo/articles/54062bd7814f41)

2. [OpenAI API による音声認識の精度改善：文字起こしポストプロセッシングの実践](https://zenn.dev/gixo/articles/f515309f1582be)

### Usage

#### how to use

To start the application, execute the following command in a terminal.

アプリをスタートするにはターミナルで以下のコマンドを実行する必要があります。

```python
streamlit run app/audio_transcribe.py
```

#### API key

You will need an OpenAI API Key; register with OpenAI to get one. Please note that you will be charged according to the amount you use.

OpenAI の API Key が必要です。OpenAI に登録して API Key の発行をしてください。使用量に応じてお金がかかるので注意してください。

### Author

- Twitter : [https://twitter.com/tsunotto](https://twitter.com/tsunotto)
- zenn : https://zenn.dev/kanaotto

Thank you! Please follow me!

ありがとうございます！よければ、フォローお願いします！
