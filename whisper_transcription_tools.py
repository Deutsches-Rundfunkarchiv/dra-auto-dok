import whisper
from time_converters import convert_milliseconds_to_time_format
import PySimpleGUI as sg
import torch

class transcribe_with_whisper():
    """Transkription_Process with Whisper-Model"""

    def __init__(self, model_to_use):
        """Inputs:
                model_to_use(str): Name of Whisper Model chosen (official Whisper-Name) z.B. large-v3
                
                """
        self.model_to_use = model_to_use
        self.loaded_model = self.load_whisper_model()

    def load_whisper_model(self):
        """Loading the Whisper model to cache once so it can be used again and again within the process
        
        Returns:
            model (Whisper Object): Loaded Whisper Model
        """
        print(f"CUDA verfügbar: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA Version: {torch.version.cuda}")
            print(f"CUDA Geräte: {torch.cuda.device_count()}")
            print(f"CUDA aktuelles Gerät: {torch.cuda.current_device()}")
            print(f"CUDA Geräte Name: {torch.cuda.get_device_name(torch.cuda.current_device())}")
            
        if torch.cuda.is_available() == False:
            model = whisper.load_model(self.model_to_use)
            print('No CUDA found')
        else:
            model = whisper.load_model(self.model_to_use, device="cuda")
            print('Run on CUDA')
        return(model)

    def make_transcription(self, audiofile, language = 'de', verbose = True):
        """Performing Transcription on Audio
        Inputs:
            audiofile(str): Path to audiofile to perform transcription on
            language(str): Language code, if language should be preset, default = de
            verbose (bool): If True, single lines that are transcribed are shown in real time, defaults to True.

        Returns:
            result(json): Result of Transcription as json format
        """
        result = self.loaded_model.transcribe(audiofile, language = language, verbose = verbose)
        
        return(result)
    
    def detect_language(self, audiofile):
        """Detects the language(s) spoken in audio with Whisper functionality
        
        Args:
            audiofile(str): Path to audiofile to detect language from

        Returns:
           f"Detected language: {max(probs, key=probs.get)}"(str): Name of detected language coming from Whisper analysis.
        """
        # detect the spoken language
        mel = whisper.log_mel_spectrogram(audiofile).to(self.loaded_model.device)
        _, probs = self.loaded_model.detect_language(mel)
        print(f'Detected language: {probs}') #{max(probs, key=probs.get)}
        return(f"Detected language: {max(probs, key=probs.get)}")
    
    def split_json_to_lists(self, json_source):
        """Handler for Whisper raw-output. Json-Output of Whisper contains timecode-parts that are written to lists byy handler for easier further processing.
        
        Args:
            json_source(json): Original raw Whisper Output for audio transcription analysis

        Returns:
            speech_all(list): List of party of written transcript of audio as devided by whisper.
            start_all(list): List of starting timecodes for parts in speech_all
            end_all(list): List of starting timecodes for parts in speech_all
            no_speech_prob_all(list): Probability that part of audio is no speech, evaluated by whisper. Not very precise, therefor currently not used for any further functionality.

        """
        self.source_json = json_source
        speech_all = []
        start_all = []
        end_all = []
        no_speech_prob_all = []
        for k in range(len(self.source_json['segments'])):
            speech = self.source_json['segments'][k]['text']
            speech_all.append(speech)
            start = self.source_json['segments'][k]['start']
            start_all.append(start)
            end = self.source_json['segments'][k]['end']
            end_all.append(convert_milliseconds_to_time_format(end))
            no_speech_prob = self.source_json['segments'][k]['no_speech_prob']
            no_speech_prob_all.append(no_speech_prob)

        return(speech_all, start_all, end_all, no_speech_prob_all)
