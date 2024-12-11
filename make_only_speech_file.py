# import
import struct 
import librosa # librosa==0.9.1
import webrtcvad # webrtcvad==2.0.10
import numpy as np
import torch
from pydub import AudioSegment
import simpleaudio as sa
#wave_obj = sa.WaveObject.from_wave_file("path/to/file.wav")
from datetime import timedelta
import os

from get_yamnet_analysis import make_yamnet_analysis
from time_converters import convert_to_ms_yamnet

class make_audio_with_only_speech():
    """Takes original audio and performs a voice activity detection. Returns new audio with only speech passages"""

    def __init__(self, audio, temp_dir, sub_folder_yamnet, filename, sample_size = 16000):
        """Args:
            audio (str): Path of original audio that should be processed
            sample_size (int): Sample size of audio, defaults to 16000 for 16 khz
            temp_dir (str): Path of dir for temporal storage of processed file
            sub_folder_yamnet(str): Path of Sub-Folder for YAMNet-Files that are semi-tempary and can only be deleted if documentation-process is finished and pickle-file is not needed any more
            filename (str): name of file that is used as name of temporal file
            """
        self.file_path = audio
        self.sample_size = sample_size
        self.temp_dir = temp_dir
        self.sub_folder_yamnet = sub_folder_yamnet
        self.name_file = filename
        #self.only_speech_file = self.make_file_only_speech()
        

    def analyze_audio_for_speech_passages(self):
        """Analyzes what parts of audio contain speech
        
        Returns:
            speech_timestamps(list): List of timestamps of audio parts, that contain spoken speech
            
            """
        # load the silerio vad model
        model, utils = torch.hub.load(repo_or_dir='snakers4_silero-vad_speech_activity_detection',
                                    model='silero_vad',
                                    force_reload=False,
                                    onnx=False, # perform `pip install -q onnxruntime` and set this to True, if you want to use ONNX
                                    source = 'local') 
        # get the helper functions out of util
        (get_speech_timestamps,
        save_audio,
        read_audio,
        VADIterator,
        collect_chunks) = utils

        # Option 1: Process complete audio
        wav = read_audio(self.file_path, sampling_rate=self.sample_size)
        speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=self.sample_size)
        # Output: [{'end': 31200, 'start': 1568},
        #  {'end': 73696, 'start': 42528}, ..]
        
        return(speech_timestamps)

    def make_file_only_speech(self):
        """Creates a new file that only consists of speech parts of original file
        
        Returns:
            Path(str): Path of new file
            
            """    
        #YAMNet-Filter
        file_path = self.file_path
        yamnet_main = make_yamnet_analysis(file_path, 'Excel_Lists_entities\\Class_Names_overview.xlsx', self.temp_dir, self.sub_folder_yamnet)
        yamnet_main.make_audio_yamnet_ready()
        yamnet_main.main_yamnet_analysis()
        yamnet_main.top10_classes()
        classes_summary = yamnet_main.classes_summary()
        classes_merged = yamnet_main.merge_classes(classes_summary)
        classes_filter_silence_other = yamnet_main.filter_silence_other(classes_merged)
        classes_remove_silence = yamnet_main.remove_silence(classes_filter_silence_other)
        classes_remove_other = yamnet_main.remove_other(classes_remove_silence)
        classes_filter_3s = yamnet_main.remove_music_speech_under_3s (classes_remove_other)
        timecodes_for_transcript = yamnet_main.get_timecodes_for_transcript(classes_filter_3s)
        #print(timecodes_for_transcript)
        #Filter YAMNET Music Parts - Speech Parts cannot be within these
        yamnet_starts_all = timecodes_for_transcript[0]
        yamnet_ends_all = timecodes_for_transcript[1]
        yamnet_status_all = timecodes_for_transcript[2]

        starts_music_yamnet = []
        ends_music_yamnet = []

        for m in range(len(yamnet_starts_all)):
            print(yamnet_status_all[m])
            if type(yamnet_status_all[m]) != float and 'music' in yamnet_status_all[m].lower():
                starts_music_yamnet.append(convert_to_ms_yamnet(yamnet_starts_all[m]))
                ends_music_yamnet.append(convert_to_ms_yamnet(yamnet_ends_all[m]))

        #Speech Activity Detection mit YAMnet-Filter
        start_speech = []
        end_speech = []
        sound = AudioSegment.from_file(self.file_path)
        temp_dir = self.temp_dir
        sound_combined = None
        timestamps = self.analyze_audio_for_speech_passages()
        
        for i in range(len(timestamps)):
            
            start_mseconds = (timestamps[i]['start']/16000)*1000
            end_mseconds = (timestamps[i]['end']/16000)*1000
            is_music = False
            #Check ob sich der Start des angeblichen Speech Files nicht innerhalb eines YAMnet-Musik-Teils befindet, dann handelt es sich vermutlich um eine Gesangseinlage und der Audioteil wird nicht zum neuen Gesamtaudio hinzugefügt
            for s in range(len(starts_music_yamnet)):
                if start_mseconds > starts_music_yamnet[s] and start_mseconds < ends_music_yamnet[s]:
                    is_music = True
                    #print('Found Speech that is Singing')
            if is_music == False:
                start_speech.append(timestamps[i]['start']/16000)
                end_speech.append(timestamps[i]['end']/16000)
                sound_part = sound[start_mseconds:end_mseconds]
                if sound_combined == None:
                    sound_combined = sound_part
                else:
                    sound_combined = sound_combined + sound_part
        #Wenn es sich um ein reines Musikfile handelt, dann haben wir nach dem Zuschneiden gar kein Audio mehr, weil alle Musik raus geschnitten wurde. In diesem Falle übernimm das originale Audiofile.
        if sound_combined == None:
            sound_combined = sound
            
        new_audio = sound_combined.export(f'{temp_dir}\\{self.name_file}_no_speech.wav', format = "wav")
        print(new_audio)
    
        return(f'{temp_dir}\\{self.name_file}_no_speech.wav')
    
    def erase_temp_file (self):
        """Erases temporal created only-speech file"""
        file = self.only_speech_file
        try:
            os.remove(file)
            print('File removed')
        except BaseException as e:
            print('Removing Error')
            print(str(e))