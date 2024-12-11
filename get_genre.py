from prepare_yamnet_results import prepare_results
from config import threshold_music, threshold_speech

class get_genre():
    """Defines Genre for Audio based on YAMnet-Analysis"""

    def __init__(self, path_temp_folder, name_filtered_excel, folder_main_audio, name_main_audio):
        """
        Args:
            path_temp_folder (str): File path to folder, where temp files can be stored automatically as defined in the second screen of the tool or in the config file.
            name_filtered_excel (str): File name of excel that is source for data about musical and non-musical components.
            folder_main_audio (str): Folder path where main audio source is saved (audio that is processed with this tool and that we want to extract metadata from)
            name_main_audio (str): file name of main audio file that is stored in folder_main_audio
        """
        self.path_temp_folder = path_temp_folder
        self.name_filtered_excel = name_filtered_excel
        self.folder_main_audio = folder_main_audio
        self.name_main_audio = name_main_audio
        results_peparer = self.load_yamnet_analysis()
        self.percentages_music_speech = results_peparer.get_percentage(self.folder_main_audio, self.name_main_audio)


    def load_yamnet_analysis(self):
        """Utility for loading external results preparer, that are made by yamnet-class"""
        results_preparer = prepare_results(self.path_temp_folder, self.name_filtered_excel)


        return(results_preparer)
    
    def define_status(self, threshold_speech = threshold_speech, threshold_music = threshold_music):
        """Decides weather audio is defined as "Wort", "Musik" or "Wort/Musik"
            Args:
                threshold_speech (int): YAMNet threshhold that decides if audio part is defined as speech, defaults to value from config-file
                threshold_music (int): YAMnet threshhold that decides if audio part is defined as music, defaults to value from config-file

            Returns:
                status(str): Can be "Wort", "Musik" and "Wort / Musik" based on the percentages of music and speech found in previous processings.
        
        """
        percentages_music = self.percentages_music_speech[0]
        percentages_speech = self.percentages_music_speech[1]

        if int(percentages_music) >int(threshold_music):
            status = "Musik"
        
        elif int(percentages_speech) >int(threshold_speech):
            status = "Wort"

        else:
            status = "Wort / Musik"

        return (status)
    
    def make_ak_part_genre(self, status_raw):
        """Makes HFDB-ready entry part from define_status decision
        Args:
            status_raw (str): Raw status the is decided by define_status def. Can be "Musik", "Wort" or "Wort / Musik"

        Returns:
            entry_ak (json): json-entry as part of final database entry for HFDB.
        """
        if status_raw == "Musik":
            entry_ak = {
                'kurzbezeichnung': 'MSK',
                'langbezeichnung': 'Musik',
                'normId': 'http://hfdb.ard.de/normdb/Wert?id=1114'
            }

        elif status_raw == "Wort":
            entry_ak =  {
                'kurzbezeichnung': 'WRT',
                'langbezeichnung': 'Wort',
                'normId': 'http://hfdb.ard.de/normdb/Wert?id=1115'
            }
        
        elif status_raw == "Wort / Musik":
            entry_ak = {
                'kurzbezeichnung': 'WRM',
                'langbezeichnung': 'Wort / Musik',
                'normId': 'http://hfdb.ard.de/normdb/Wert?id=1117'
            }

        return(entry_ak)

    
