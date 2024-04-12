import streamlit as st
import torch
import youtube_transcript_api
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import BartTokenizer, BartForConditionalGeneration
from pytube import YouTube
import librosa
import soundfile as sf
from huggingsound import SpeechRecognitionModel
import os
import moviepy.editor as mp
from youtube_transcript_api import TranscriptsDisabled
from pydub import AudioSegment

# def convert_mp4_to_wav(input_file, output_file):
#     audio = AudioSegment.from_file(input_file, format="mp4")
#     audio.export(output_file, format="wav")



def convert_mp4_to_wav(input_file, output_file):
    audio = AudioSegment.from_file(input_file, format="mp4")
    audio.export(output_file, format="wav")






def main():
    st.title("YouTube Summarizer")

    # Get the YouTube video link from the user
    video_link = st.text_input("Enter the YouTube video link:")

    if video_link:
        try:
            # Extract the unique ID from the video link
            unique_id = video_link.split("=")[-1]

            # Get the video transcript
                    
            try:
                sub = YouTubeTranscriptApi.get_transcript(unique_id)
                subtitle = " ".join([x['text'] for x in sub])
            except TranscriptsDisabled as e:
                print("Subtitles are disabled for this video. You may need to handle this case differently.")

                # Proceed with audio-based transcription
                yt = YouTube(video_link)
                audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
                audio_stream.download(filename='ytaudio.mp4')
                input_file = 'ytaudio.mp4'
                output_file = 'ytaudio.wav'
                convert_mp4_to_wav(input_file, output_file)
                model = SpeechRecognitionModel("jonatasgrosman/wav2vec2-large-xlsr-53-english", device="cuda" if torch.cuda.is_available() else "cpu")
                audio_path = ['./content/ytaudio.wav']
                transcriptions = model.transcribe(audio_path)
                subtitle = ' '.join([t['transcription'] for t in transcriptions])

            # Summarize the transcript using BART
            tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
            model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
            input_tensor = tokenizer.encode(subtitle, return_tensors="pt", max_length=512)
            outputs_tensor = model.generate(input_tensor, max_length=160, min_length=120, length_penalty=2.0, num_beams=4, early_stopping=True)
            summary = tokenizer.decode(outputs_tensor[0])

            # Display the summary
            st.header("Summary:")
            st.write(summary)

        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()