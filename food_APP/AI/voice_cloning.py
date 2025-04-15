import numpy as np
import soundfile as sf
import os
import sys 

# Path to Real-Time Voice Cloning
RTVC_PATH = r"D:\Data Scientist\my project\.venv\Real-Time-Voice-Cloning"
sys.path.append(RTVC_PATH) 

from synthesizer.inference import Synthesizer

synthesizer = Synthesizer("synthesizer/saved_models/pretrained/pretrained.pt")

def clone_voice(text, reference_audio):
    """Generate cloned speech using RTVC"""
    generated_wav = synthesizer.synthesize_spectrograms([text])
    output_file = "cloned_voice.wav"
    sf.write(output_file, generated_wav[0], samplerate=16000)
    return output_file
