from google.cloud import texttospeech

def generate_speech(text):
    """Generate persuasive AI speech using Google WaveNet"""
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(ssml=f"""
    <speak>
        <prosody pitch="+10%" rate="fast">{text}</prosody>
    </speak>
    """)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Wavenet-D",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    audio_file = "output.mp3"
    with open(audio_file, "wb") as out:
        out.write(response.audio_content)

    return audio_file
