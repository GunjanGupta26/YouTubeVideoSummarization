from flask import Flask, request, redirect
from flask_restful import Resource, Api
# from flask_cors import CORS
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

app = Flask(__name__)
# cors = CORS(app, resources={r"*": {"origins": "*"}})
api = Api(app)

class Home(Resource):
    def get(self):
        return 'Welcome to, Test App API!'

    
    def convert_mp4_to_wav(self,input_file, output_file):
        audio = AudioSegment.from_file(input_file, format="mp4")
        audio.export(output_file, format="wav")

    def solve(self):
        link = "https://youtu.be/RIJ2Jclv9Dg?si=SPwk1Dhw3W2EeMwe" # without subtitle
        video_link = link

        if video_link:
            try:
                # Extract the unique ID from the video link
                unique_id = video_link.split("=")[-1]

                try:
                    sub = YouTubeTranscriptApi.get_transcript(unique_id)
                    subtitle = " ".join([x['text'] for x in sub])
                except TranscriptsDisabled as e:
                    print("Subtitles are disabled for this video. You may need to handle this case differently.")

                    yt = YouTube(video_link)
                    audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
                    audio_stream.download(filename='ytaudio.mp4')
                    input_file = 'ytaudio.mp4'
                    output_file = 'ytaudio.wav'
                    self.convert_mp4_to_wav(input_file, output_file)
                    model = SpeechRecognitionModel("jonatasgrosman/wav2vec2-large-xlsr-53-english", device="cuda" if torch.cuda.is_available() else "cpu")
                    audio_path = ['/content/ytaudio.wav']
                    transcriptions = model.transcribe(audio_path)
                    subtitle = ' '.join([t['transcription'] for t in transcriptions])

                tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
                model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
                input_tensor = tokenizer.encode(subtitle, return_tensors="pt", max_length=512)
                outputs_tensor = model.generate(input_tensor, max_length=160, min_length=120, length_penalty=2.0, num_beams=4, early_stopping=True)
                summary = tokenizer.decode(outputs_tensor[0])

                print(summary)
                print('done')
            except Exception as e:
                return (f"Error: {e}")


    def post(self):
        try:
            value = request.get_json()
            self.solve()
            if (value):
                return "Data received", 201

            return {"error": "Invalid format."}

        except Exception as error:
            return {'error': error}

api.add_resource(Home, '/')

if __name__ == "__main__":
    port = int(5000)
    app.run(host='0.0.0.0', port=port)
