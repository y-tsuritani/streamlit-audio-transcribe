import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="streamlit-audio-transcribe",
    version="0.0.1",
    author="y-tsuritani",
    author_email="",
    description="Audio transcription component for streamlit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/y-tsuritani/streamlit-audio-transcribe",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.10",
    install_requires=[
        "streamlit >= 1.29.0",
        "pydub >= 0.25",
        "openai >= 1.4.0",
        "python-dotenv >= 1.0.0",
        "langchain >=0.0.350",
    ],
)
