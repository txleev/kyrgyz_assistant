from transformers import pipeline

pipe = pipeline(
    task="automatic-speech-recognition",
    model="the-cramer-project/AkylAI-STT-small"
)

def transcribe(audio):
    text = pipe(audio)["text"]
    return text


if __name__ == "__main__":
    # This only runs when you do: python stt.py
    path_to_audio = '''tts_mini/test.wav'''
    text = transcribe(path_to_audio)
    print(text)
    