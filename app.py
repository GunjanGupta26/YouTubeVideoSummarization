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
import os
import ffmpeg
import speech_recognition as sr
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import nltk
nltk.download('punkt')
app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
api = Api(app)

class Home(Resource):
    def get(self):
        return 'Welcome to, Test App API!'

    def convert_mp4_to_wav(self, input_file, output_file):
        ffmpeg.input(input_file).output(output_file).run()

    # def convert_mp4_to_wav(self,input_file, output_file):
    #     audio = AudioSegment.from_file(input_file, format="mp4")
    #     audio.export(output_file, format="wav")

    def solve(self,video_link):
        print(video_link)

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
                    print('mp4 done')
                    output_file = 'ytaudio.wav'
                    self.convert_mp4_to_wav(input_file, output_file)
                    print('hello')
                    model = SpeechRecognitionModel("jonatasgrosman/wav2vec2-large-xlsr-53-english", device="cuda" if torch.cuda.is_available() else "cpu")
                    print('model ->')
                    print(model)
                    audio_path = ['./ytaudio.wav']
                    transcriptions = model.transcribe(audio_path)
                    subtitle = ' '.join([t['transcription'] for t in transcriptions])
                    print(subtitle)

                # tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
                # model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
                # input_tensor = tokenizer.encode(subtitle, return_tensors="pt", max_length=512)
                # outputs_tensor = model.generate(input_tensor, max_length=160, min_length=120, length_penalty=2.0, num_beams=4, early_stopping=True)
                # summary = tokenizer.decode(outputs_tensor[0])
                # print(summary)
                tokenizer = AutoTokenizer.from_pretrained("Mr-Vicky-01/Bart-Finetuned-conversational-summarization")
                model = AutoModelForSeq2SeqLM.from_pretrained("Mr-Vicky-01/Bart-Finetuned-conversational-summarization")

                def generate_summary(text):
                    inputs = tokenizer([text], max_length=102400, return_tensors='pt', truncation=True)
                    summary_ids = model.generate(inputs['input_ids'], max_new_tokens=10000, do_sample=False)
                    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
                    return summary

                text_to_summarize = subtitle
                summary = generate_summary(text_to_summarize)

                print(summary)
                print('done')
                return summary
            except Exception as e:
                return (f"Error: {e}")


    def post(self):
        try:
            res = request.get_json()
            link = res['yt_link']
            value = self.solve(link)
            if (value):
                return value, 201

            return {"error": "Invalid format."}

        except Exception as error:
            return {'error': error}

api.add_resource(Home, '/')

if __name__ == "__main__":
    port = int(5000)
    app.run(host='0.0.0.0', port=port)
