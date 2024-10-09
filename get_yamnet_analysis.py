#import

#Global Imports
#TensorFlow
import tensorflow as tf
import tensorflow_hub as hub

#Utilities
import urllib3
import subprocess
import os
import requests
import numpy as  np
import csv
import matplotlib.pyplot as plt
from datetime import timedelta
import datetime
import pandas
pandas.options.mode.copy_on_write = True

#For Audio Extraction and convertion
import shutil
import subprocess
import sys
from pydub import AudioSegment
from scipy.io import wavfile
from matplotlib.dates import MinuteLocator

class make_yamnet_analysis():
    """Identify music, speech, silence and applause in an audiofile with yamnet."""

    def __init__(self, audiofile, excel_class_names, temp_dir, sub_folder_yamnet):
        """Args:
            folder_audiofiles (str): folder name where the original file is saved.
            temp_dir (str): folder name where the yamnet analysis is saved.
            excel_class_names (str): Sheet with yamnet class names and categories.
            """
        self.audiofile = audiofile
        print(self.audiofile)
        self.folder_yamnet_analysis = temp_dir
        self.sub_folder_yamnet = sub_folder_yamnet
        self.yamnet_model = self.load_yamnet_model()
        self.manage_threshold()
        self.read_class_names(excel_class_names)

    #inital functions

    def load_yamnet_model(self):
        """Load yamnet model from website."""

        model = hub.load('yamnet_main')

        print('Yamnet model loaded.')
        return model
    
    def manage_threshold(self, thresh1 = 0.8, thresh2 = 0.1, thresh1_silence = 0.8, thresh2_silence = 0.5):
        """Enter threshold (min/max) or keep standard values."""

        #Music, Speech, Applause
        self.thresh1 = thresh1
        self.thresh2 = thresh2 #ursprünglich 0.3 für Speech und 0.1 für Music

        #Silence
        self.thresh1_silence = thresh1_silence
        self.thresh2_silence = thresh2_silence

        print('Threshold: thresh1 = 0.8, thresh2 = 0.1, thresh1_silence = 0.8, thresh2_silence = 0.5')
       
    def read_class_names(self, excel_class_names):
        """Read list of class names with categorization (music, speech, applause, silence)

        Args:
            excel_class_names (str): Excel sheet with class names
        
        Returns:
            dataframe of the sheet
            
            """
        
        df = pandas.read_excel(excel_class_names)

        self.class_name = df['Class_Names']
        self.class_number = df['Class_Number']
        self.is_music = df['Is_Music']
        self.is_speech = df['Is_Speech']
        self.is_applause = df['Is_Applause']
        self.is_silence = df['Is_Silence']

        print('Class names loaded.')

    def define_id(self,id):

        self.id = id

        print('\n', f'Analysis of ID {id}.', '\n')

    #audio preparations

    def make_audio_yamnet_ready(self):
        """Convert audiofile from mp3 to wav (mono, 16bit).

        Args:
            id (str): Konf-ID, digits only, no leading zeros, no letters
        
        Returns:
            id_yamnet.wav, saved in folder_audiofiles.
            
            """
        print(str(self.audiofile))
        sound = AudioSegment.from_mp3(self.audiofile)
        sound = sound.set_channels(1)
        sound = sound.set_frame_rate(16000)
        name_audiofile_single = self.audiofile.split('/')
        self.name_audiofile_single = name_audiofile_single[len(name_audiofile_single)-1]
        sound.export(f'{self.sub_folder_yamnet}\\{self.name_audiofile_single}_yamnet.wav', format='wav')
        print('YAMnet-File is here:', f'{self.sub_folder_yamnet}\\{self.name_audiofile_single}_yamnet.wav')

        print(f'Audiofile converted.')

    #functions for yamnet analysis
    
    #subfunction
    def class_names_from_csv(self):
        """Returns list of class names corresponding to score vector.

        Returns:
            class names
    
            """
        class_names = []
        class_map_path = self.yamnet_model.class_map_path().numpy()
        with tf.io.gfile.GFile(class_map_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                class_names.append(row['display_name'])

        return class_names

    #main function
    def main_yamnet_analysis(self):
        wav_file_name = f'{self.sub_folder_yamnet}\\{self.name_audiofile_single}_yamnet.wav'
        sample_rate, wav_data = wavfile.read(wav_file_name, 'rb')
        self.sample_rate = sample_rate
        self.wav_data = wav_data
    
        # Show some basic information about the audio.
        duration = len(wav_data)/sample_rate
        duration_min = datetime.timedelta(seconds = round(duration))
        print('Yamnet analysis running.')
        print(f'Sample rate: {sample_rate} Hz')
        print('Total duration:', duration_min, 'min')
        print(f'Size of the input: {len(wav_data)}')

        waveform = wav_data / tf.int16.max
        # Run the model, check the output.
        scores, embeddings, spectrogram = self.yamnet_model(waveform)
        scores_np = scores.numpy()
        self.scores_np = scores_np
        spectrogram_np = spectrogram.numpy()
        class_names = self.class_names_from_csv()
        infered_class = class_names[scores_np.mean(axis=0).argmax()]
        print(f'The main sound is: {infered_class}')

        #set time to minutes
        duration_min = duration/60
        time_min = np.linspace(0, duration_min, len(wav_data))

        #Visualisation
        #plt.figure(figsize=(20, 10))
        # Plot the waveform.
        #plt.subplot(3, 1, 1)
        #plt.plot(time_min, waveform)
        #plt.xticks(np.arange(min(time_min), max(time_min)+2, 2.0))
        #plt.xlim(left = 0, right = max(time_min))
        #plt.xlabel('Time [min]')
        #plt.ylabel('Amplitude')
        # Plot the log-mel spectrogram (returned by the model).
        #plt.subplot(3, 1, 3)
        #plt.imshow(spectrogram_np.T, aspect='auto', interpolation='nearest', origin='lower')
        # Plot and label the model output scores for the top-scoring classes.
        mean_scores = np.mean(scores, axis=0)
        top_n = 10
        top_class_indices = np.argsort(mean_scores)[::-1][:top_n]
        self.top_class_indices = top_class_indices
        #plt.subplot(3, 1, 2)
        #plt.imshow(scores_np[:, top_class_indices].T, aspect='auto', interpolation='nearest', cmap='gray_r')
        # patch_padding = (PATCH_WINDOW_SECONDS / 2) / PATCH_HOP_SECONDS
        # values from the model documentation
        patch_padding = (0.025 / 2) / 0.01
        #plt.xlim([-patch_padding-0.5, scores.shape[0] + patch_padding-0.5])
        # Label the top_N classes.
        yticks = range(0, top_n, 1)
        #plt.yticks(yticks, [class_names[top_class_indices[x]] for x in yticks])
        #_ = plt.ylim(-0.5 + np.array([top_n, 0]))

        #save figure
        #plt.savefig(os.path.join(self.folder_yamnet_analysis, f'{self.id}_yamnet_plot.png'))
        #print(f'Figure saved in folder {self.folder_yamnet_analysis}.')

    #subfunction
    def get_time_index (self):

        time = []
        milliseconds_time = []
        for zahl0 in range(len(self.scores_np)):
            time_in_seconds = zahl0 * 0.48
            delta = timedelta(seconds=time_in_seconds)
            time.append(str(delta))
            milliseconds_time.append(time_in_seconds*1000)

        return time, milliseconds_time
    
    #subfunction
    def build_top_class_score_index (self, indice_class):
        scorelist = []
        for zahl0 in range(len(self.scores_np)):
            scorefortime = self.scores_np[zahl0][self.top_class_indices[indice_class]]
            scorelist.append(scorefortime)

        return scorelist
    
    #main function
    def top10_classes(self):

        """Build the 10 score indexes for the top Audio classes as an excel output including time index"""

        top_class_1_score = self.build_top_class_score_index (0)
        top_class_2_score = self.build_top_class_score_index (1)
        top_class_3_score = self.build_top_class_score_index (2)
        top_class_4_score = self.build_top_class_score_index (3)
        top_class_5_score = self.build_top_class_score_index (4)
        top_class_6_score = self.build_top_class_score_index (5)
        top_class_7_score = self.build_top_class_score_index (6)
        top_class_8_score = self.build_top_class_score_index (7)
        top_class_9_score = self.build_top_class_score_index (8)
        top_class_10_score = self.build_top_class_score_index (9)

        time, milliseconds_time = self.get_time_index()
    
        df_all_classes = pandas.DataFrame({
            'Timecode': time,
            'Timecode (ms)': milliseconds_time,
            f'{self.class_name[self.top_class_indices[0]]}': top_class_1_score,
            f'{self.class_name[self.top_class_indices[1]]}': top_class_2_score,
            f'{self.class_name[self.top_class_indices[2]]}': top_class_3_score,
            f'{self.class_name[self.top_class_indices[3]]}': top_class_4_score,
            f'{self.class_name[self.top_class_indices[4]]}': top_class_5_score,
            f'{self.class_name[self.top_class_indices[5]]}': top_class_6_score,
            f'{self.class_name[self.top_class_indices[6]]}': top_class_7_score,
            f'{self.class_name[self.top_class_indices[7]]}': top_class_8_score,
            f'{self.class_name[self.top_class_indices[8]]}': top_class_9_score,
            f'{self.class_name[self.top_class_indices[9]]}': top_class_10_score,
            })
        df_all_classes.to_excel(os.path.join(self.folder_yamnet_analysis, f'_1_Overview_All_Classes.xlsx'))
        self.df_all_classes = df_all_classes
        print(f'_1_Overview_All_Classes.xlsx created.')
        

    #subfunction
    def cluster_classes(self):
        """Cluster classes as music/speech/applause/silence."""

        top_class_is_what = []

        for zahl0 in range(len(self.top_class_indices)):
            if self.is_music[self.top_class_indices[zahl0]] == 'yes':
                top_class_is_what.append('music')

            elif self.is_speech[self.top_class_indices[zahl0]] == 'yes':
                top_class_is_what.append('speech')

            elif self.is_applause[self.top_class_indices[zahl0]] == 'yes':
                top_class_is_what.append('applause')
            
            elif self.is_silence[self.top_class_indices[zahl0]] == 'yes':
                top_class_is_what.append('silence')

            else:
                top_class_is_what.append('other')

        return top_class_is_what
    
    #subfunction (unused?)
    def get_word_score (self, input_score, index):

        top_class_is_what = self.cluster_classes()

        what_is_list = []
        for zahl0 in range(len(input_score)):
            if top_class_is_what[index] == 'speech':
                if input_score[zahl0] > self.thresh1:
                    what_is_list.append('SPEECH')
                elif input_score[zahl0] > self.thresh2:
                    what_is_list.append('speech')
                else:
                    what_is_list.append('')
            elif top_class_is_what[index] == 'music':
                if input_score[zahl0] > self.thresh1:
                    what_is_list.append('MUSIC')
                elif input_score[zahl0] > self.thresh2:
                    what_is_list.append('music')
                else:
                    what_is_list.append('')
            elif top_class_is_what[index] == 'applause':
                if input_score[zahl0] > self.thresh1:
                    what_is_list.append('APPLAUSE')
                elif input_score[zahl0] > self.thresh2:
                    what_is_list.append('applause')
                else:
                    what_is_list.append('')
            elif top_class_is_what[index] == 'silence':
                if input_score[zahl0] > self.thresh1_silence:
                    what_is_list.append('SILENCE')
                elif input_score[zahl0] > self.thresh2_silence:
                    what_is_list.append('silence')
                else:
                    what_is_list.append('')
            else: 
                if input_score[zahl0] > self.thresh1:
                    what_is_list.append('OTHER')
                elif input_score[zahl0] > self.thresh2:
                    what_is_list.append('OTHER')
                else:
                    what_is_list.append('')
        
        return what_is_list
    
    #main function (unused?)
    def top10_classes_words(self):
        """Build the 10 score indexes for the top Audio classes as an excel output including time index, the number indices are translated in words"""

        top_class_1_score = self.build_top_class_score_index (0)
        top_class_2_score = self.build_top_class_score_index (1)
        top_class_3_score = self.build_top_class_score_index (2)
        top_class_4_score = self.build_top_class_score_index (3)
        top_class_5_score = self.build_top_class_score_index (4)
        top_class_6_score = self.build_top_class_score_index (5)
        top_class_7_score = self.build_top_class_score_index (6)
        top_class_8_score = self.build_top_class_score_index (7)
        top_class_9_score = self.build_top_class_score_index (8)
        top_class_10_score = self.build_top_class_score_index (9)

        top_class1_what_is = self.get_word_score (top_class_1_score, 0)
        top_class2_what_is = self.get_word_score (top_class_2_score, 1)
        top_class3_what_is = self.get_word_score (top_class_3_score, 2)
        top_class4_what_is = self.get_word_score (top_class_4_score, 3)
        top_class5_what_is = self.get_word_score (top_class_5_score, 4)
        top_class6_what_is = self.get_word_score (top_class_6_score, 5)
        top_class7_what_is = self.get_word_score (top_class_7_score, 6)
        top_class8_what_is = self.get_word_score (top_class_8_score, 7)
        top_class9_what_is = self.get_word_score (top_class_9_score, 8)
        top_class10_what_is = self.get_word_score (top_class_10_score, 9)

        time, milliseconds_time = self.get_time_index()
        
        df_word_classes = pandas.DataFrame({
        'Timecode': time,
        'Timecode (ms)': milliseconds_time,
        f'{self.class_name[self.top_class_indices[0]]}': top_class1_what_is,
        f'{self.class_name[self.top_class_indices[1]]}': top_class2_what_is,
        f'{self.class_name[self.top_class_indices[2]]}': top_class3_what_is,
        f'{self.class_name[self.top_class_indices[3]]}': top_class4_what_is,
        f'{self.class_name[self.top_class_indices[4]]}': top_class5_what_is,
        f'{self.class_name[self.top_class_indices[5]]}': top_class6_what_is,
        f'{self.class_name[self.top_class_indices[6]]}': top_class7_what_is,
        f'{self.class_name[self.top_class_indices[7]]}': top_class8_what_is,
        f'{self.class_name[self.top_class_indices[8]]}': top_class9_what_is,
        f'{self.class_name[self.top_class_indices[9]]}': top_class10_what_is,
        })

        return df_word_classes

    #subfunction
    def sum_up_main_classes (self, small_name, big_name):
        """Sum up ALL classes of the top 10 classes that belong to ONE cluster to a total score for Music and Speech"""

        top_class_is_what = self.cluster_classes()

        class_whole_score = []
        class_word_score = []
        for zahl0 in range(len(self.scores_np)):
            class_score = 0
            for zahl1 in range(len(top_class_is_what)):
                if top_class_is_what[zahl1] == small_name:
                    class_score = class_score + self.scores_np[zahl0][self.top_class_indices[zahl1]]
            class_whole_score.append(class_score)

        #Convert in Word-Score
        for zahl2 in range(len(class_whole_score)):
            if class_whole_score[zahl2] > self.thresh1:
                class_word_score.append(big_name)
            elif class_whole_score[zahl2] > self.thresh2:
                class_word_score.append(small_name)
            else:
                class_word_score.append('')
        
        return class_word_score

    #subfunction
    def filter_single_scores (self, small_name, input):
        """Build filter, that erases single small word scores, that do not have a neirby neighbor"""

        class_score_filter = []
        for zahl1 in range(len(input)):
            try:
                if input[zahl1] == small_name and input[zahl1-1] == '' and   input[zahl1-2] == '' and input[zahl1-3]== '' and input [zahl1-4] == '' and input[zahl1-5] == '' and input[zahl1+1] == '' and     input[zahl1+2] == '' and input[zahl1+3] == '' and input[zahl1+4] == '' and input[zahl1+5] == '':
                    class_score_filter.append('')
                else:
                    class_score_filter.append(input[zahl1])
            except IndexError:
                try:
                    if input[zahl1] == small_name and input[zahl1+1] == '' and input[zahl1+2] == '' and input[zahl1+3] == '' and input[zahl1+4] == '' and input[zahl1+5] == '':
                        class_score_filter.append('')
                    else:
                        class_score_filter.append(input[zahl1])
                except IndexError:
                    if input[zahl1] == small_name and input[zahl1-1] == '' and input[zahl1-2] == '' and input[zahl1-3] == '' and input[zahl1-4] == '' and input[zahl1-5] == '':
                        class_score_filter.append('')
                else:
                    class_score_filter.append(input[zahl1])
        return class_score_filter
    
    #subfunction
    def get_final_status(self, word_scores, small_name, big_name):
        """Get final status if there is Music/Speech/Applause/Silence in the audiofile"""
        status = False
        if small_name in word_scores or big_name in word_scores:
            status = True
        return status

    #main function
    def classes_summary (self):
        """Build a new list that sums up the word scores into one category"""
    
        class_speech_sum = self.sum_up_main_classes('speech', 'SPEECH')
        class_music_sum = self.sum_up_main_classes('music', 'MUSIC')
        class_applause_sum = self.sum_up_main_classes('applause', 'APPLAUSE')
        class_silence_sum = self.sum_up_main_classes('silence', 'SILENCE')

        class_speech_word_score = self.filter_single_scores ('speech',class_speech_sum)
        class_music_word_score = self.filter_single_scores ('music', class_music_sum)
        class_applause_word_score = self.filter_single_scores ('applause', class_applause_sum)
        class_silence_word_score = self.filter_single_scores ('silence', class_silence_sum)

        music_status = self.get_final_status(class_music_word_score, 'music', 'MUSIC')
        speech_status = self.get_final_status(class_speech_word_score, 'speech', 'SPEECH')
        applause_status = self.get_final_status(class_applause_word_score, 'applause', 'APPLAUSE')
        silence_status = self.get_final_status(class_silence_word_score, 'silence', 'SILENCE')


        data = {'Music Status': [music_status], 'Speech Status': [speech_status], 'Applause Status': [applause_status], 'Silence Status': [silence_status]}
        df_class_status = pandas.DataFrame(data)
        df_class_status.to_excel(os.path.join(self.folder_yamnet_analysis, f'_0_Class_Status.xlsx'))
        print(f'_0_Class_Status.xlsx created.')
        print(df_class_status)

        time, milliseconds_time = self.get_time_index()

        df_word_classes_sum = pandas.DataFrame({
        'Timecode': time,
        'Timecode (ms)': milliseconds_time,
        'Speech': class_speech_word_score,
        'Music': class_music_word_score,
        'Applause': class_applause_word_score,
        'Silence': class_silence_word_score,
        })

        print('Class summary processed. Previous Length:', len(self.df_all_classes), '/ Summarized:', len(df_word_classes_sum))

        return df_word_classes_sum        

    #subfunction
    def find_class_shifts(self, df_word_classes_sum):
        """find class shifts (from music to speech etc.), do not consider upper and lower case"""

        #convert all word scores to lower case
        df_word_classes_sum_lower = df_word_classes_sum.apply(lambda x: x.astype(str).str.lower())

        #convert dataframe to work only with word classes
        #set timecodes (ms) as index
        df_timecode_index = df_word_classes_sum_lower.set_index('Timecode (ms)')
        #remove all columns that are not Speech, Music, Applause, Silence
        for column_name in df_timecode_index:
            if column_name != "Speech" and column_name != "Music" and column_name != "Applause" and column_name != "Silence":
                df_timecode_index.drop(column_name, axis=1, inplace=True)

        #list of dataframes with class shifts
        list_df_new = []

        #check if word score is the same as previous
        for column in df_timecode_index:
            df_new = df_timecode_index[column].ne(df_timecode_index[column].shift())
            list_df_new.append(df_new)

        #merge all dataframes in the list to one dataframe
        #True = there is a shift / False = the value stays the same
        df_class_shift = pandas.concat(list_df_new, axis=1)

        #filter the dataframe: keep all rows with a class shift
        df_class_shift_filtered = df_class_shift[df_class_shift.any(axis=1)]

        #reconvert boolean to word scores

        #create list of timecodes with a class shift
        timecodes_list = list(df_class_shift_filtered.index.values)

        #convert strings to float
        timecodes_list_float = [float(i) for i in timecodes_list]

        #filter original dataframe with classes by timecodes with a class shift
        df_word_classes_sum_filtered = df_word_classes_sum[df_word_classes_sum['Timecode (ms)'].isin(timecodes_list_float)]
        print('Same classes merged. Previous Length:', len(df_word_classes_sum), '/ Summarized:', len(df_word_classes_sum_filtered))

        return df_word_classes_sum_filtered
    
    #subfunction
    def add_duration_between_timecodes(self, df_word_classes_sum_filtered):
        """add duration between timecodes"""

        #Create list of durations
        duration_list = []

        df_list = df_word_classes_sum_filtered['Timecode (ms)'].to_list()

        for i, timecode in enumerate(df_list):
            if i < len(df_list) - 1:
                timecode_next = df_list[i+1]
                duration = timecode_next - timecode
                duration_list.append(duration)

        file_duration = (len(self.wav_data)/self.sample_rate)*1000

        #Check this with Kim! Temporäre Umgehung Error
        try:
            duration_list.append(file_duration - (df_list[-1]))
        except IndexError:
            print('Error YAMNet add duration between timecodes')

        #change milliseconds to timecodes

        duration_min = []

        for element in duration_list:
            delta = timedelta(milliseconds=element)
            delta_new =str(delta)
            duration_min.append(delta_new)

        #drop old duration
        for column_name in df_word_classes_sum_filtered:
            if column_name == 'Duration' or column_name == 'Duration (ms)':
                df_word_classes_sum_filtered.drop(column_name, axis=1, inplace=True)
        #add new duration
        df_word_classes_sum_filtered.insert(2,"Duration",duration_min)
        df_word_classes_sum_filtered.insert(3,"Duration (ms)", duration_list)

        print('Duration added.')
        
        return df_word_classes_sum_filtered
    
    #main function
    def merge_classes(self, df_word_classes_sum):

        df_word_classes_sum_filtered = self.find_class_shifts(df_word_classes_sum)
        df_word_classes_duration = self.add_duration_between_timecodes(df_word_classes_sum_filtered)

        df_word_classes_duration.to_excel(os.path.join(self.folder_yamnet_analysis, f'_2_Overview_Music_Speech_Applause_Silence.xlsx'))
        print(f'_2_Overview_Music_Speech_Applause_Silence.xlsx created.')

        return df_word_classes_duration
    
    #main function
    def filter_silence_other(self, df_word_classes_duration):
        #Silence weglassen, wenn Zeitspanne kleiner als 1500 ms (0:00:01.500000)
        df_word_classes_sum_filtered_time = df_word_classes_duration.loc[~((df_word_classes_duration['Silence'] != '') &
                                            (df_word_classes_duration['Duration (ms)'] < 1500)),:]

        print('Silence filtered. Previous Length: ', len(df_word_classes_duration), '/ Filtered: ', len(df_word_classes_sum_filtered_time))

        #Other(leer) weglassen, wenn Zeitspanne kleiner als 1500 ms (0:00:01.500000)
        df_word_classes_sum_filtered_other = df_word_classes_sum_filtered_time.loc[~((df_word_classes_sum_filtered_time['Silence'] == '') &
                                                                                    (df_word_classes_sum_filtered_time['Music'] == '') &
                                                                                    (df_word_classes_sum_filtered_time['Speech'] == '') &
                                                                                    (df_word_classes_sum_filtered_time['Applause'] == '') &
                                                                                    (df_word_classes_sum_filtered_time['Duration (ms)'] < 1500)),:]

        print('Other filtered. Previous Length: ', len(df_word_classes_sum_filtered_time), 'Filtered:', len(df_word_classes_sum_filtered_other))

        #gleiche Klassen zusammenfassen und Dauer anpassen
        df_word_classes_with_silence = self.find_class_shifts(df_word_classes_sum_filtered_other)
        df_word_classes_with_silence2 = df_word_classes_with_silence.drop(['Duration', 'Duration (ms)'], axis=1)
        df_word_classes_with_silence_duration = self.add_duration_between_timecodes(df_word_classes_with_silence2)

        #create excel
        df_word_classes_with_silence_duration.to_excel(os.path.join(self.folder_yamnet_analysis, f'_3_Summary_Music_Speech_Applause_Silence.xlsx'))
        print(f'_3_Summary_Music_Speech_Applause_Silence.xlsx created.')

        return df_word_classes_with_silence_duration

    #main function
    def remove_silence(self, df_word_classes_with_silence_duration):
        #Silence komplett filtern
        df_word_classes_without_silence = df_word_classes_with_silence_duration.loc[~((df_word_classes_with_silence_duration['Silence'] != '') &
                                                                                        (df_word_classes_with_silence_duration['Music'] == '') &
                                                                                        (df_word_classes_with_silence_duration['Speech'] == '') &
                                                                                        (df_word_classes_with_silence_duration['Applause'] == '')),:]

        df_word_classes_without_silence2 = df_word_classes_without_silence.drop('Silence', axis=1)

        print('Silence removed. Previous Length:', len(df_word_classes_with_silence_duration), '/ Filtered:', len(df_word_classes_without_silence2))

        #gleiche Klassen zusammenfassen und Dauer anpassen
        df_word_classes_without_silence3 = self.find_class_shifts(df_word_classes_without_silence2)
        df_word_classes_without_silence4 = self.add_duration_between_timecodes(df_word_classes_without_silence3)

        #create excel
        df_word_classes_without_silence4.to_excel(os.path.join(self.folder_yamnet_analysis, f'_4_Summary_Music_Speech_Other.xlsx'))
        print(f'_4_Summary_Music_Speech.xlsx created.')

        return df_word_classes_without_silence4

    #main function
    def remove_other(self, df_word_classes_without_silence4):
        #Other komplett filtern
        df_word_classes_without_other = df_word_classes_without_silence4.loc[~((df_word_classes_without_silence4['Music'] == '') &
                                                                                (df_word_classes_without_silence4['Speech'] == '') &
                                                                                (df_word_classes_without_silence4['Applause'] == '')),:]

        print('Other removed. Previous Length:', len(df_word_classes_without_silence4), '/ Filtered:', len(df_word_classes_without_other))

        #gleiche Klassen zusammenfassen und Dauer anpassen
        df_word_classes_without_other2 = self.find_class_shifts(df_word_classes_without_other)
        df_word_classes_without_other3 = self.add_duration_between_timecodes(df_word_classes_without_other2)

        #create excel
        df_word_classes_without_other3.to_excel(os.path.join(self.folder_yamnet_analysis, f'_5_Summary_Music_Speech.xlsx'))
        print(f'_5_Summary_Music_Speech.xlsx created.')

        return df_word_classes_without_other3
    
    #main function
    def remove_music_speech_under_3s(self, df_word_classes_without_other3):
        #Musik und Sprache unter 3s filtern
        df_word_classes_filtered = df_word_classes_without_other3.loc[~((df_word_classes_without_other3['Duration (ms)'] < 3000)),:]

        print('Music and Speech under 3s removed. Previous Length:', len(df_word_classes_without_other3), '/ Filtered:', len(df_word_classes_filtered))

        #gleiche Klassen zusammenfassen und Dauer anpassen
        df_word_classes_filtered2 = self.find_class_shifts(df_word_classes_filtered)
        df_word_classes_filtered3 = self.add_duration_between_timecodes(df_word_classes_filtered2)

        #create excel
        df_word_classes_filtered3.to_excel(os.path.join(self.sub_folder_yamnet, f'{self.name_audiofile_single}_6_Summary_Music_Speech_filtered.xlsx'))
        print(f'_6_Summary_Music_Speech_filtered.xlsx created.')

        return df_word_classes_filtered3
    
    def get_timecodes_for_transcript(self, df_word_classes_filtered3):

        timecodes_start_list = df_word_classes_filtered3['Timecode'].to_list()
        timecodes_end_list = timecodes_start_list[1:]
        file_duration = (len(self.wav_data)/self.sample_rate)*1000
        delta = timedelta(milliseconds=file_duration)
        timecodes_end_list.append(str(delta))
        df_new = df_word_classes_filtered3.replace('', np.nan)
        music_speech = df_new['Speech'].fillna(df_new['Music'])
        music_speech_list = music_speech.to_list()

        return timecodes_start_list, timecodes_end_list, music_speech_list

        



    


    
   

        