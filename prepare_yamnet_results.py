import os
import pandas

from mutagen.wave import WAVE
from datetime import timedelta

class prepare_results():
    """Import yamnet analysis and prepare results in Excel."""

    def __init__(self, folder_yamnet_analysis, excel_yamnet_analysis):
        """ Prepares YAMnet-Analysis results for using them for creating speech-only audio-file
        
        Args:
            folder_yamnet_analysis(str): Path to Folder, where yamnet_analysis results are  saved. Should be standardized for example in temp folder.
            excel_yamnet_analysis(str): Name of the excel which is the YAMnet-final-analysis, that should be stored at folder_yamnet_analysis path
        
        """
        self.folder_yamnet_analysis = folder_yamnet_analysis
        self.excel_yamnet_analysis = excel_yamnet_analysis

        self.load_yamnet_analysis()

    def load_yamnet_analysis(self):
        """Loads YAMnet-Analysis results as dataframe and returns dataframe for further processing
        
        Returns:
            df_yamnet_analysis(Dataframe): Dataframe with YAMnet Analysis results.
        """
        
        df_yamnet_analysis = pandas.read_excel(os.path.join(self.folder_yamnet_analysis, 'yamnet_files', self.excel_yamnet_analysis))
        
        self.df_yamnet_analysis = df_yamnet_analysis

        print('Yamnet Analysis loaded.')
        return df_yamnet_analysis

    def get_total_duration(self, folder_audiofiles, id):
        """Gets total duration of speech-only file
        
        Args:
            folder_audiofiles(str): String of location where yamnet audio files are stored
            id(str): Name of original audiofile for naming YAMnet-File.

        Returns:
            ms_total(int): Length of YAMnet-audiofile in milliseconds
            str(delta_gesamt)(str): Length of YAMnet-Audiofile in seconds as string.

        """
        audio = WAVE(os.path.join(f'{folder_audiofiles}\\yamnet_files', f"{id}_yamnet.wav"))
        ms_total = audio.info.length*1000
        delta_gesamt = timedelta(seconds=round(audio.info.length))
        
        return ms_total, str(delta_gesamt)

    def get_total_duration_music(self):
        """Returns total duration of music in given audio found with YAMnet
        
        Returns:
            ms_music(int):  Raw data of how much music is in audiofile in milliseconds
            str(min_music): String data of amount of music in audiofile in milliseconds
        """

        df_music = self.df_yamnet_analysis.loc[(self.df_yamnet_analysis['Music'] == 'MUSIC') | (self.df_yamnet_analysis['Music'] == 'music')]
        ms_music = df_music['Duration (ms)'].sum()
        min_music = timedelta(milliseconds=round(ms_music))
        
        return ms_music, str(min_music)

    def get_total_duration_speech(self):
        """Returns total duration of speech in given audio found with YAMnet
        
        Returns:
            ms_speechc(int):  Raw data of how much speech is in audiofile in milliseconds
            str(min_speech): String data of amount of speech in audiofile in milliseconds
        """
        df_speech = self.df_yamnet_analysis.loc[(self.df_yamnet_analysis['Speech'] == 'SPEECH') | (self.df_yamnet_analysis['Speech'] == 'speech')]
        ms_speech = df_speech['Duration (ms)'].sum()
        min_speech = timedelta(milliseconds=round(ms_speech))
        
        return ms_speech, str(min_speech)
    
    def get_percentage(self, folder_audiofiles, id):
        """Returns percentages of how much of audio is music and how much is speech. Note: Sum must not be 100 percent since there can be other audio signals that are neither music nor speech.
        
        Args:
            folder_audiofiles(str): Path to folder where audiofiles are stored.
            id(str): Name of original audio file input for naming overview files.

        Returns:
            percentage_music(int): Percentage of music in original audio
            percentage_speech(int): Percentage of speech in original audio
        """
        ms_music, music_duration = self.get_total_duration_music()
        ms_speech, speech_duration = self.get_total_duration_speech()
        ms_total_duration, total_duration = self.get_total_duration(folder_audiofiles, id)

        percentage_music = round((ms_music / ms_total_duration)*100, 2)
        percentage_speech = round((ms_speech / ms_total_duration)*100, 2)

        return percentage_music, percentage_speech

    def get_number_shifts(self):
        """Returns number of changes between music, speech and other audio content in audio
        
        Returns:
            number_shifts per audio(int): Tells how often there is a change between audio types within the main audio (music to speech etc.)
        
        """
        number_shifts = len(self.df_yamnet_analysis)-1

        return number_shifts

    def get_all_results(self, folder_audiofiles, id):
        """Loads all needed results for further processing  and for creating a speech-only-file and wraps them to one single list

        Args:
           folder_audiofiles(str): Path to folder where audiofiles are stored
           id (str): Name of original audiofile - needed for naming files to be created and finding them again later.
        
        Returns:
            results_list(list): List of all results needed for creating a speech-only file, which are: id, total_duration, music_duration, percentage_music, speech_duration, percentage_speech, number_shifts, music_speech_list, duration_shifts, timecodes_shifts

        """

        ms_total_duration, total_duration = self.get_total_duration(folder_audiofiles, id)
        ms_music, music_duration = self.get_total_duration_music()
        ms_speech, speech_duration = self.get_total_duration_speech()
        percentage_music, percentage_speech = self.get_percentage(folder_audiofiles, id)
        number_shifts = self.get_number_shifts()

        music_speech = self.df_yamnet_analysis['Speech'].fillna(self.df_yamnet_analysis['Music'])
        music_speech_list = music_speech.to_list()
        duration_shifts = self.df_yamnet_analysis['Duration'].to_list()
        timecodes_shifts = self.df_yamnet_analysis['Timecode'].to_list()

        results_list = [id, total_duration, music_duration, percentage_music, speech_duration, percentage_speech, number_shifts, music_speech_list, duration_shifts, timecodes_shifts]

        return results_list

    

