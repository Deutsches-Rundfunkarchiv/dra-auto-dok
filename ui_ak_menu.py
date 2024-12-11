import PySimpleGUI as sg
import os.path
from audioplayer import audio_playback 
from find_audio_timecodes import find_audio_timecodes
import time
from time import strftime
from time import gmtime
import pandas
from pydub import AudioSegment  
import hyperlink
from IPython.display import HTML
from datetime import datetime
import webbrowser
from llm_processing_google import process_text_with_gemini
from utils import split_name
import threading
import re
from time_converters import convert_milliseconds_to_time_format
from audioplayer_extended import format_transcript, highlight_current_line, transcript_player, update_transcript

#Import Buttons String Variables
from buttons_graphics import refresh_ndb_button, change_input_type_button, add_data_item_button, look_for_name_in_transcript_button, ask_karin_button, send_button
#For Refresh of NDB-Data
from norm_db_entity_linking import norm_db_entity_linking
norm_db_linker = norm_db_entity_linking()

#This is the main menue part of the Auto-Dok-Tool It consists of two sub-parts. The class ui_correction which has all the single elements in it and a sole definition ak_correction_menu, that runs the menue itself and puts the elements from class ui_correction in the right order

class ui_correction():
    """The ui-corection class wraps up all UI elements possible for the ui-correction menue"""
    def __init__(self):
        pass

    def make_day_month_year_lists(self):
        """Makes lists for dropdown-choices for dates
        
        Returns:
            list_day(list): List from 1 to 31 for day choices
            list_month(list): List from 1 to 12 for month choices
            list_year(list): List for year suggestions. Currently starts at 1890 and goes up to todays year automatically. Could be edited if needed in the future.
        """
        list_day = [None]
        list_day.extend(range(1,32))
        list_month = [None]
        list_month.extend(range(1,13))
        list_year = [None]
        list_year.extend(range(1890,datetime.now().year))
        return(list_day, list_month, list_year)

    def empty_column_mitwirkende(self, input_list_mitwirkende, reference_roles_list_mitwirkende, is_combo = False, default_input_freitext = '', default_input_combo = [], description_person = '', audio_starter_list = [], default_hyperlink_to_show = ''):
        """Creates an empty line for UI-Part "Mitwirkende" if user clicks the "add new person to Mitwirkende" (+) button.
        Args:
            input_list_mitwirkende(list): List of "Mitwirkende" Inputs for UI
            reference_roles_list_mitwirkende(list): List of possible Roles the "Mitwirkende" can have
            is_combo(bool): Status if information should be displayed as combo or "Freitext" - defaults to "False" which means information is displayed as "Freitext". Combo is only applicable if  we have information shifted from other Person catagory to Mitwirkender. Thus defaults to False.
            default_input_freitext(str): Default Input of Freitext Feld, defaults to empty.
            default_input_combo(list): Input from NDB if applicable as List of NDB entries.
            description_person(str): Meta Description of Person from LLM, defaults to empty - only used if Data is transfered from other person entry field.
            audio_starter_list(list): List of Audio Starts. Only used if data is transfered from other person entry field. Defaults to empty list
            default_hyperlink_to_show(str): Hyperlink to be displayed if we have NDB-Data. Defaults to None. Only applicable if data is transfered from other Person Entry.

        Returns:
            empty_column_1_x, empty_column_1_y(lists): Wrappers with UI elements for single entry of Mitwirkende.

        """
        #Leere Zeile definieren, für den Fall, dass eine leere Zeile hinzugefügt werden soll
        if reference_roles_list_mitwirkende == []: #Für den Fall, dass gar keine Rollenliste übergeben wurde (z.B. wenn wir eine leere Kompilation anlegen)
            excel = pandas.read_excel('Excel_Lists_entities\\beteiligte_funktionen_norm_db.xlsx')
            bezeichnung = excel['Langbezeichnung']
            reference_roles_list_mitwirkende = bezeichnung
        empty_column_1_x = []
        empty_column_1_y = []
        empty_column_1_x.append(
            sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_mitwirkende', len(input_list_mitwirkende)), tooltip='Delete this item'))
        
        if is_combo == False:
            empty_column_1_x.append(
                sg.Input(default_text = default_input_freitext, size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_mitwirkende_vorname", len(input_list_mitwirkende))))
            empty_column_1_x.append(
                sg.Input(default_text = default_input_freitext, size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_mitwirkende_nachname", len(input_list_mitwirkende))))
            empty_column_1_x.append(
                sg.Combo(default_input_combo, size=(100, 1), font=('Arial Bold', 10), default_value = '', expand_x=False, enable_events=True, visible = False, readonly=False, auto_size_text = True, key=("input_mitwirkende", len(input_list_mitwirkende)))) #unsichtbarer Input, der aktiviert wird, wenn nach Änderung desTextes doch noch Treffer in NDB gefunden werden.
             
            #Show Hyperlink next to Column - Hidden!
            empty_column_1_x.append(sg.Text('', enable_events=True, font=('Arial Bold', 10), key=('URL_mitwirkende', len(input_list_mitwirkende)), visible = False, text_color = 'blue', background_color = 'white'))

        else:
            empty_column_1_x.append(
                sg.Input(default_text = default_input_freitext, size=(25, 1), enable_events=True, readonly=False, visible = False, key=("input_mitwirkende_vorname", len(input_list_mitwirkende))))
            empty_column_1_x.append(
                sg.Input(default_text = default_input_freitext, size=(25, 1), enable_events=True, readonly=False, visible = False, key=("input_mitwirkende_nachname", len(input_list_mitwirkende))))
            empty_column_1_x.append(
                sg.Combo(default_input_combo, size=(100, 1), font=('Arial Bold', 10), default_value = default_input_combo[0], expand_x=False, enable_events=True, visible = True, readonly=False, auto_size_text = True, key=("input_mitwirkende", len(input_list_mitwirkende)))) 
                    
        #Show Hyperlink next to Column - Hidden!
        if default_hyperlink_to_show != '':
            empty_column_1_x.append(sg.Text(default_hyperlink_to_show, enable_events=True, font=('Arial Bold', 10), key=('URL_mitwirkende', len(input_list_mitwirkende)), visible = True, text_color = 'blue', background_color = 'white'))
        
        else:
            empty_column_1_x.append(sg.Text(default_hyperlink_to_show, enable_events=True, font=('Arial Bold', 10), key=('URL_mitwirkende', len(input_list_mitwirkende)), visible = False, text_color = 'blue', background_color = 'white'))

        

        empty_column_1_y.append(#Refresh-NDB-Ergebnis-Button hinzufügen
            sg.Button('', image_data=refresh_ndb_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, pad = ((40, 0), (0, 0)), key=('refresh_ndb_mitwirkende', len(input_list_mitwirkende))))

        empty_column_1_y.append(#Umwandlung Freitext-Feld Button einfügen
            sg.Button('', image_data=change_input_type_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, visible = True, key=('change_input_type_mitwirk', len(input_list_mitwirkende))))

        if is_combo == False:
            empty_column_1_y.append(
                sg.Button('', image_data=look_for_name_in_transcript_button,
                button_color=(sg.theme_background_color(),sg.theme_background_color()),
                border_width=0, visible = True, key=('look_for_name_in_transcript', len(input_list_mitwirkende))))
        else:
            empty_column_1_y.append(
                sg.Button('', image_data=look_for_name_in_transcript_button,
                button_color=(sg.theme_background_color(),sg.theme_background_color()),
                border_width=0, visible = False, key=('look_for_name_in_transcript', len(input_list_mitwirkende))))
        
        empty_column_1_y.append(
            sg.Combo(list(reference_roles_list_mitwirkende), size=(25, 1), font=('Arial Bold', 10), default_value = list(reference_roles_list_mitwirkende)[0], expand_x=False, enable_events=True,  readonly=False, key=('combo_mitwirkende', len(input_list_mitwirkende))))
        empty_column_1_y.append(
            sg.Text(description_person, font=('Arial Bold', 10), expand_x=False, justification='left', visible = True, key=('description_mitwirkende', len(input_list_mitwirkende))))
        
        if len(audio_starter_list) >0:
            empty_column_1_y.append(
                sg.Combo(audio_starter_list, size=(10, 1), font=('Arial Bold', 10), default_value = audio_starter_list[0], visible = True, expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_mitwirkende', len(input_list_mitwirkende))))
            empty_column_1_y.append(
                sg.Button("Play", visible = True, key=('Play_File_mitwirkende', len(input_list_mitwirkende))))
            empty_column_1_y.append(
                sg.Button("Stop", visible = True, key=('Stop_File_mitwirkende', len(input_list_mitwirkende))))

            self.eventlist_mitwirkende.append(('Play_File_mitwirkende', len(input_list_mitwirkende)))
            
            self.eventlist_mitwirkende_stop_file.append(('Stop_File_mitwirkende', len(input_list_mitwirkende)))

        else:
            empty_column_1_y.append(
                sg.Combo(audio_starter_list, size=(10, 1), font=('Arial Bold', 10), default_value = '', visible =False, expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_mitwirkende', len(input_list_mitwirkende))))
            empty_column_1_y.append(
                sg.Button("Play", visible = False, key=('Play_File_mitwirkende', len(input_list_mitwirkende))))
            empty_column_1_y.append(
                sg.Button("Stop", visible = False, key=('Stop_File_mitwirkende', len(input_list_mitwirkende))))
            
        #Button verschieben hinzufügen   
        empty_column_1_y.append(
                sg.Button("Zu Urheber", key=('verschieb_mitwirkende_urheber', len(input_list_mitwirkende))))
        empty_column_1_y.append(
                sg.Button("Zu ThemaPerson", key=('verschieb_mitwirkende_themapers', len(input_list_mitwirkende))))

        #Bemerkungsfeld
        empty_column_1_x.append(sg.Text('Bemerkung:', font=('Arial Bold', 10), expand_x=False, justification='right', pad = ((0, 0),(0, 0)), key=("bemerkung_mitwirkende_text", len(input_list_mitwirkende))))

        empty_column_1_x.append(
            sg.Input(default_text = '', size=(25, 1), enable_events=True, readonly=False, justification='left', visible = True, key=("bemerkung_mitwirkende", len(input_list_mitwirkende))))
        
        return(empty_column_1_x, empty_column_1_y)
    
    def empty_column_urheber(self, input_list_urheber, reference_roles_list_urheber, is_combo = False, default_input_freitext = '', default_input_combo = [], description_person = '', audio_starter_list = [], default_hyperlink_to_show = ''):
        """
        Creates an empty line for UI-Part "Urheber" if user clicks the "add new person to Urheber" (+) button.
        
        Args:
            input_list_urheber(list): List of "Urheber" Inputs for UI
            reference_roles_list_urheber(list): List of possible Roles the "Urheber" can have
            is_combo(bool): Status if information should be displayed as combo or "Freitext" - defaults to "False" which means information is displayed as "Freitext". Combo is only applicable if  we have information shifted from other Person catagory to Urheber. Thus defaults to False.
            default_input_freitext(str): Default Input of Freitext Feld, defaults to empty.
            default_input_combo(list): Input from NDB if applicable as List of NDB entries.
            description_person(str): Meta Description of Person from LLM, defaults to empty - only used if Data is transfered from other person entry field.
            audio_starter_list(list): List of Audio Starts. Only used if data is transfered from other person entry field. Defaults to empty list
            default_hyperlink_to_show(str): Hyperlink to be displayed if we have NDB-Data. Defaults to None. Only applicable if data is transfered from other Person Entry.

        Returns:
            empty_column_1_x, empty_column_1_y(lists): Wrappers with UI elements for single entry of Urheber.

        """
        #Leere Zeile definieren, für den Fall, dass eine leere Zeile hinzugefügt werden soll
        if reference_roles_list_urheber == []: #Für den Fall, dass gar keine Rollenliste übergeben wurde (z.B. wenn wir eine leere Kompilation anlegen)
            excel = pandas.read_excel('Excel_Lists_entities\\beteiligte_funktionen_urheber_norm_db.xlsx')
            bezeichnung = excel['Langbezeichnung']
            reference_roles_list_urheber = bezeichnung
        empty_column_1_x = []
        empty_column_1_y = []

        empty_column_1_x.append(
            sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_urheber', len(input_list_urheber)), tooltip='Delete this item'))
        
        if is_combo == False:
            empty_column_1_x.append(
                sg.Input(default_text = default_input_freitext, size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_urheber_vorname", len(input_list_urheber))))
            empty_column_1_x.append(
                sg.Input(default_text = default_input_freitext, size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_urheber_nachname", len(input_list_urheber))))
            empty_column_1_x.append(
                sg.Combo(default_input_combo, size=(100, 1), font=('Arial Bold', 10), default_value = '', expand_x=False, enable_events=True, visible = False, readonly=False, auto_size_text = True, key=("input_urheber", len(input_list_urheber)))) #unsichtbarer Input, der aktiviert wird, wenn nach Änderung desTextes doch noch Treffer in NDB gefunden werden.
        
            #Show Hyperlink next to Column - Hidden!
            empty_column_1_x.append(sg.Text('', enable_events=True, font=('Arial Bold', 10), key=('URL_urheber', len(input_list_urheber)), visible = False, text_color = 'blue', background_color = 'white'))
        
        else:
            empty_column_1_x.append(
                sg.Input(default_text = default_input_freitext, size=(25, 1), enable_events=True, readonly=False, visible = False, key=("input_urheber_vorname", len(input_list_urheber))))
            empty_column_1_x.append(
                sg.Input(default_text = default_input_freitext, size=(25, 1), enable_events=True, readonly=False, visible = False, key=("input_urheber_nachname", len(input_list_urheber))))
            empty_column_1_x.append(
                sg.Combo(default_input_combo, size=(100, 1), font=('Arial Bold', 10), default_value = default_input_combo[0], expand_x=False, enable_events=True, visible = True, readonly=False, auto_size_text = True, key=("input_urheber", len(input_list_urheber)))) #unsichtbarer Input, der aktiviert wird, wenn nach Änderung desTextes doch noch Treffer in NDB gefunden werden.
        
            #Show Hyperlink next to Column - Hidden!
        if default_hyperlink_to_show != '':
            empty_column_1_x.append(sg.Text(default_hyperlink_to_show, enable_events=True, font=('Arial Bold', 10), key=('URL_urheber', len(input_list_urheber)), visible = True, text_color = 'blue', background_color = 'white'))
        else:
            empty_column_1_x.append(sg.Text(default_hyperlink_to_show, enable_events=True, font=('Arial Bold', 10), key=('URL_urheber', len(input_list_urheber)), visible = False, text_color = 'blue', background_color = 'white'))

        
        empty_column_1_y.append(#Refresh-NDB-Ergebnis-Button hinzufügen
            sg.Button('', image_data=refresh_ndb_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, pad = ((40, 0), (0, 0)), key=('refresh_ndb_urheber', len(input_list_urheber))))

        empty_column_1_y.append(#Umwandlung Freitext-Feld Button einfügen
            sg.Button('', image_data=change_input_type_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, visible = True, key=('change_input_type_urheber', len(input_list_urheber))))
        
        if is_combo == False:
            empty_column_1_y.append(
                sg.Button('', image_data=look_for_name_in_transcript_button,
                button_color=(sg.theme_background_color(),sg.theme_background_color()),
                border_width=0, visible = True, key=('look_for_name_in_transcript_urheber', len(input_list_urheber))))
        else:
            empty_column_1_y.append(
                sg.Button('', image_data=look_for_name_in_transcript_button,
                button_color=(sg.theme_background_color(),sg.theme_background_color()),
                border_width=0, visible = False, key=('look_for_name_in_transcript_urheber', len(input_list_urheber))))
            
        empty_column_1_y.append(
            sg.Combo(list(reference_roles_list_urheber), size=(25, 1), font=('Arial Bold', 10), default_value = list(reference_roles_list_urheber)[0], expand_x=False, enable_events=True,  readonly=False, key=('combo_urheber', len(input_list_urheber))))
        empty_column_1_y.append(
            sg.Text(description_person, font=('Arial Bold', 10), expand_x=False, justification='left', visible = True, key=('description_urheber', len(input_list_urheber))))
        
        if len(audio_starter_list) >0:
            empty_column_1_y.append(
                sg.Combo(audio_starter_list, size=(10, 1), font=('Arial Bold', 10), default_value = audio_starter_list[0], visible =True, expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_urheber', len(input_list_urheber))))
            print('DEBUG URHEBER APPENDIX:', ('audio_starter_urheber', len(input_list_urheber)))
            empty_column_1_y.append(
                sg.Button("Play", visible = True, key=('Play_File_urheber', len(input_list_urheber))))
            empty_column_1_y.append(
                sg.Button("Stop", visible = True, key=('Stop_File_urheber', len(input_list_urheber))))

            self.eventlist_urheber.append(('Play_File_urheber', len(input_list_urheber)))
            
            self.eventlist_urheber_stop_file.append(('Stop_File_urheber', len(input_list_urheber)))
   
        else:
            empty_column_1_y.append(
                sg.Combo(audio_starter_list, size=(10, 1), font=('Arial Bold', 10), default_value = '', visible =False, expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_urheber', len(input_list_urheber))))
            print('DEBUG URHEBER APPENDIX:', ('audio_starter_urheber', len(input_list_urheber)))
            empty_column_1_y.append(
                sg.Button("Play", visible = False, key=('Play_File_urheber', len(input_list_urheber))))
            empty_column_1_y.append(
                sg.Button("Stop", visible = False, key=('Stop_File_urheber', len(input_list_urheber))))
            
        empty_column_1_y.append(
            sg.Button("Zu Mitwirkende", key=('verschieb_urheber_mitwirkende', len(input_list_urheber))))
        empty_column_1_y.append(
            sg.Button("Zu ThemaPerson", key=('verschieb_urheber_themapers', len(input_list_urheber))))
        
        return(empty_column_1_x, empty_column_1_y)

    def empty_column_tpers(self, input_list_tpers, is_combo = False, default_input_freitext = '', default_input_combo = [], description_person = '', audio_starter_list = [], default_hyperlink_to_show = ''):
        """
        Creates an empty line for UI-Part "themaPerson" if user clicks the "add new person to themaPerson (+)" button.

        Args:
            input_list_tpers(list): List of "themaPerson" Inputs for UI
            is_combo(bool): Status if information should be displayed as combo or "Freitext" - defaults to "False" which means information is displayed as "Freitext". Combo is only applicable if we have information shifted from other Person catagory to themaPerson. Thus defaults to False.
            default_input_freitext(str): Default Input of Freitext Feld, defaults to empty.
            default_input_combo(list): Input from NDB if applicable as List of NDB entries. Defaults to empty list.
            description_person(str): Meta Description of Person from LLM, defaults to empty - only used if Data is transfered from other person entry field.
            audio_starter_list(list): List of Audio Starts. Only used if data is transfered from other person entry field. Defaults to empty list
            default_hyperlink_to_show(str): Hyperlink to be displayed if we have NDB-Data. Defaults to None. Only applicable if data is transfered from other Person Entry.

        Returns:
            empty_column_1_x, empty_column_1_y(lists): Wrappers with UI elements for single entry of "themaPerson".

        """
        #Leere Zeile definieren, für den Fall, dass eine leere Zeile hinzugefügt werden soll
        empty_column_1_x = []
        empty_column_1_y = []

        
        empty_column_1_x.append(
            sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_tpers', len(input_list_tpers)), tooltip='Delete this item'))
        
        if is_combo == False:
            empty_column_1_x.append(
                sg.Input(default_text = default_input_freitext, size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_tpers_vorname", len(input_list_tpers))))
            empty_column_1_x.append(
                sg.Input(default_text = default_input_freitext, size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_tpers_nachname", len(input_list_tpers))))
            empty_column_1_x.append(
                sg.Combo(default_input_combo, size=(100, 1), font=('Arial Bold', 10), default_value = '', expand_x=False, enable_events=True, visible = False, readonly=False, auto_size_text = True, key=("input_tpers", len(input_list_tpers)))) #unsichtbarer Input, der aktiviert wird, wenn nach Änderung desTextes doch noch Treffer in NDB gefunden werden.
        
            #Show Hyperlink next to Column - Hidden!
            empty_column_1_x.append(sg.Text('', enable_events=True, font=('Arial Bold', 10), key=('URL_tpers', len(input_list_tpers)), visible = False, text_color = 'blue', background_color = 'white'))

        else:
            empty_column_1_x.append(
                sg.Input(default_text = default_input_freitext, size=(25, 1), enable_events=True, readonly=False, visible = False, key=("input_tpers_vorname", len(input_list_tpers))))
            empty_column_1_x.append(
                sg.Input(default_text = default_input_freitext, size=(25, 1), enable_events=True, readonly=False, visible = False, key=("input_tpers_nachname", len(input_list_tpers))))
            empty_column_1_x.append(
                sg.Combo(default_input_combo, size=(100, 1), font=('Arial Bold', 10), default_value = default_input_combo[0], expand_x=False, enable_events=True, visible = True, readonly=False, auto_size_text = True, key=("input_tpers", len(input_list_tpers)))) #unsichtbarer Input, der aktiviert wird, wenn nach Änderung desTextes doch noch Treffer in NDB gefunden werden.
            
        #Show Hyperlink next to Column - Hidden!
        if default_hyperlink_to_show != '':
            empty_column_1_x.append(sg.Text(default_hyperlink_to_show, enable_events=True, font=('Arial Bold', 10), key=('URL_tpers', len(input_list_tpers)), visible = True, text_color = 'blue', background_color = 'white'))
        else:
            empty_column_1_x.append(sg.Text(default_hyperlink_to_show, enable_events=True, font=('Arial Bold', 10), key=('URL_tpers', len(input_list_tpers)), visible = False, text_color = 'blue', background_color = 'white'))

        empty_column_1_y.append(#Refresh-NDB-Ergebnis-Button hinzufügen
            sg.Button('', image_data=refresh_ndb_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, pad = ((40, 0), (0, 0)), key=('refresh_ndb_tpers', len(input_list_tpers))))

        empty_column_1_y.append(#Umwandlung Freitext-Feld Button einfügen
            sg.Button('', image_data=change_input_type_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, visible = True, key=('change_input_type_tpers',len(input_list_tpers))))

        if is_combo == False:
            empty_column_1_y.append(
                sg.Button('', image_data=look_for_name_in_transcript_button,
                button_color=(sg.theme_background_color(),sg.theme_background_color()),
                border_width=0, visible = True, key=('look_for_name_in_transcript_tpers',len(input_list_tpers))))
            
        else:
            empty_column_1_y.append(
                sg.Button('', image_data=look_for_name_in_transcript_button,
                button_color=(sg.theme_background_color(),sg.theme_background_color()),
                border_width=0, visible = False, key=('look_for_name_in_transcript_tpers',len(input_list_tpers))))
  
        empty_column_1_y.append(
            sg.Text('', font=('Arial Bold', 10), expand_x=False, justification='left', visible = True, key=('description_tpers', len(input_list_tpers))))
        if len(audio_starter_list) >0:
            empty_column_1_y.append(
                sg.Combo(audio_starter_list, size=(10, 1), font=('Arial Bold', 10), default_value = audio_starter_list[0], visible = True, expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_tpers', len(input_list_tpers))))
            empty_column_1_y.append(
                sg.Button("Play", visible = True, key=('Play_File_tpers', len(input_list_tpers))))
            empty_column_1_y.append(
                sg.Button("Stop", visible = True, key=('Stop_File_tpers', len(input_list_tpers))))
            
            self.eventlist_tpers.append(('Play_File_tpers', len(input_list_tpers)))
            
            self.eventlist_tpers_stop_file.append(('Stop_File_tpers', len(input_list_tpers)))

        else:
            empty_column_1_y.append(
                sg.Combo(audio_starter_list, size=(10, 1), font=('Arial Bold', 10), default_value = '', visible =False, expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_tpers', len(input_list_tpers))))
            empty_column_1_y.append(
                sg.Button("Play", visible = False, key=('Play_File_tpers', len(input_list_tpers))))
            empty_column_1_y.append(
                sg.Button("Stop", visible = False, key=('Stop_File_tpers', len(input_list_tpers))))
            
        #Button verschieben hinzufügen   
        empty_column_1_y.append(
                sg.Button("Zu Urheber", key=('verschieb_themapers_urheber', len(input_list_tpers))))
        empty_column_1_y.append(
                sg.Button("Zu Mitwirkende", key=('verschieb_themapers_mitwirkende', len(input_list_tpers))))

        return(empty_column_1_x, empty_column_1_y)

    def empty_column_torte(self, input_list_torte):
        """
        Creates an empty line for UI-Part "themaOrte" if user clicks the "add new Ort" (+) button.

        Args:
            input_list_torte(list): List of "themaOrte" Inputs for UI
            
        Returns:
            empty_column_1_x, empty_column_1_y(lists): Wrappers with UI elements for single entry of "themaOrte".

        """
        #Leere Zeile definieren, für den Fall, dass eine leere Zeile hinzugefügt werden soll
        empty_column_1_x = []
        empty_column_1_y = []
        
        empty_column_1_x.append(
            sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_torte', len(input_list_torte)), tooltip='Delete this item'))
        empty_column_1_x.append(
            sg.Input(default_text = '', size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_torte", len(input_list_torte))))
        empty_column_1_x.append(
            sg.Combo([], size=(100, 1), font=('Arial Bold', 10), default_value = '', expand_x=False, enable_events=True, visible = False, readonly=False, auto_size_text = True, key=("input_torte_alt", len(input_list_torte)))) #unsichtbarer Input, der aktiviert wird, wenn nach Änderung desTextes doch noch Treffer in NDB gefunden werden.

        #Show Hyperlink next to Column - Hidden!
        empty_column_1_x.append(sg.Text('', enable_events=True, font=('Arial Bold', 10), key=('URL_torte', len(input_list_torte)), visible = False, text_color = 'blue', background_color = 'white'))

        empty_column_1_y.append(#Refresh-NDB-Ergebnis-Button hinzufügen
            sg.Button('', image_data=refresh_ndb_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, pad = ((40, 0), (0, 0)), key=('refresh_ndb_torte', len(input_list_torte))))

        empty_column_1_y.append(#Umwandlung Freitext-Feld Button einfügen
            sg.Button('', image_data=change_input_type_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, visible = True, key=('change_input_type_torte',len(input_list_torte))))

        empty_column_1_y.append(
            sg.Button('', image_data=look_for_name_in_transcript_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, visible = True, key=('look_for_name_in_transcript_torte',len(input_list_torte))))
        
        empty_column_1_y.append(
            sg.Text('', font=('Arial Bold', 10), expand_x=False, justification='left', visible = False, key=('description_torte', len(input_list_torte))))
        empty_column_1_y.append(
            sg.Combo([], size=(10, 1), font=('Arial Bold', 10), default_value = '', visible = False, expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_torte', len(input_list_torte))))
        empty_column_1_y.append(
            sg.Button("Play", visible = False, key=('Play_File_torte', len(input_list_torte))))
        empty_column_1_y.append(
            sg.Button("Stop", visible = False, key=('Stop_File_torte', len(input_list_torte))))

        return(empty_column_1_x, empty_column_1_y)
    
    def empty_column_tinst(self, input_list_tinst):
        """
        Creates an empty line for UI-Part "themaInstitution" if user clicks the "add new Institution" (+) button.

        Args:
            input_list_tinst(list): List of "themaInstitution" Inputs for UI
            
        Returns:
            empty_column_1_x, empty_column_1_y(lists): Wrappers with UI elements for single entry of "themaInstitution".

        """
        #Leere Zeile definieren, für den Fall, dass eine leere Zeile hinzugefügt werden soll
        empty_column_1_x = []
        empty_column_1_y = []
        empty_column_1_x.append(
            sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_tinst', len(input_list_tinst)), tooltip='Delete this item'))
        empty_column_1_x.append(
            sg.Input(default_text = '', size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_tinst", len(input_list_tinst))))
        empty_column_1_x.append(
            sg.Combo([], size=(100, 1), font=('Arial Bold', 10), default_value = '', expand_x=False, enable_events=True, visible = False, readonly=False, auto_size_text = True, key=("input_tinst_alt", len(input_list_tinst)))) #unsichtbarer Input, der aktiviert wird, wenn nach Änderung desTextes doch noch Treffer in NDB gefunden werden.
        
        #Show Hyperlink next to Column - Hidden!
        empty_column_1_x.append(sg.Text('', enable_events=True, font=('Arial Bold', 10), key=('URL_tinst', len(input_list_tinst)), visible = False, text_color = 'blue', background_color = 'white'))

        empty_column_1_y.append(#Refresh-NDB-Ergebnis-Button hinzufügen
            sg.Button('', image_data=refresh_ndb_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, pad = ((40, 0), (0, 0)), key=('refresh_ndb_tinst', len(input_list_tinst))))

        empty_column_1_y.append(#Umwandlung Freitext-Feld Button einfügen
            sg.Button('', image_data=change_input_type_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, visible = True, key=('change_input_type_tinst',len(input_list_tinst))))

        empty_column_1_y.append(
            sg.Button('', image_data=look_for_name_in_transcript_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, visible = True, key=('look_for_name_in_transcript_tinst',len(input_list_tinst))))
        
        empty_column_1_y.append(
            sg.Text('', font=('Arial Bold', 10), expand_x=False, justification='left', visible = False, key=('description_tinst', len(input_list_tinst))))
        empty_column_1_y.append(
            sg.Combo([], size=(10, 1), font=('Arial Bold', 10), default_value = '', visible = False, expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_tinst', len(input_list_tinst))))
        empty_column_1_y.append(
            sg.Button("Play", visible = False, key=('Play_File_tinst', len(input_list_tinst))))
        empty_column_1_y.append(
            sg.Button("Stop", visible = False, key=('Stop_File_tinst', len(input_list_tinst))))

        return(empty_column_1_x, empty_column_1_y)
    
    def empty_column_realort(self, realisierung_ort_suggest):
        """
        Creates an empty line for UI-Part "Realisation Ort" if user clicks the "add new Realisation Ort" (+) button.

        Args:
            realisierung_ort_suggest(list): List of Realisation Ort Inputs for UI
            
        Returns:
            empty_column_1_x, empty_column_1_y(lists): Wrappers with UI elements for single entry of "Realisation Ort".

        """
        empty_column_1_x = []
        empty_column_1_y = []

        empty_column_1_x.append(
                sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_realort', len(realisierung_ort_suggest)), tooltip='Delete this item'))
        empty_column_1_x.append(
                    sg.Input(default_text = '', size=(25, 1), enable_events=True, readonly=False, visible = True, key=("realort", len(realisierung_ort_suggest))))
        empty_column_1_x.append(
                    sg.Text('', font=('Arial Bold', 10), expand_x=False, justification='left', key=('realisierung_kontext', len(realisierung_ort_suggest))))
        empty_column_1_y.append(
                    sg.Button('', image_data=look_for_name_in_transcript_button,
                    button_color=(sg.theme_background_color(),sg.theme_background_color()),
                    border_width=0, visible = True, key=('look_for_name_in_transcript_realort', len(realisierung_ort_suggest))))
        empty_column_1_y.append(
            sg.Combo([], size=(10, 1), font=('Arial Bold', 10), default_value = '', visible = False, expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_realort', len(realisierung_ort_suggest))))
        empty_column_1_y.append(
            sg.Button("Play", visible = False, key=('Play_File_realort', len(realisierung_ort_suggest))))
        empty_column_1_y.append(
            sg.Button("Stop", visible = False, key=('Stop_File_realort', len(realisierung_ort_suggest))))
        
        
        
        return(empty_column_1_x, empty_column_1_y)
    
    def empty_column_sprachen(self, input_list_sprachen):
        """
        Creates an empty line for UI-Part "Sprachen" if user clicks the "add new Sprache" (+) button.

        Args:
            input_list_sprachen(list): List of "Sprachen" Inputs for UI
            
        Returns:
            empty_column_1_x, empty_column_1_y(lists): Wrappers with UI elements for single entry of Sprachen.

        """
        #Leere Zeile definieren, für den Fall, dass eine leere Zeile hinzugefügt werden soll
        empty_column_1_x = []
        empty_column_1_y = []
        empty_column_1_x.append(
            sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_sprachen', len(input_list_sprachen)), tooltip='Delete this item'))
        empty_column_1_x.append(
            sg.Input(default_text = '', size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_sprachen", len(input_list_sprachen))))
        empty_column_1_x.append(
            sg.Combo([], size=(100, 1), font=('Arial Bold', 10), default_value = '', expand_x=False, enable_events=True, visible = False, readonly=False, auto_size_text = True, key=("input_sprachen_alt", len(input_list_sprachen)))) #unsichtbarer Input, der aktiviert wird, wenn nach Änderung desTextes doch noch Treffer in NDB gefunden werden.
        empty_column_1_y.append(#Refresh-NDB-Ergebnis-Button hinzufügen
            sg.Button('', image_data=refresh_ndb_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, pad = ((40, 0), (0, 0)), key=('refresh_ndb_sprachen', len(input_list_sprachen))))

        empty_column_1_y.append(#Umwandlung Freitext-Feld Button einfügen
            sg.Button('', image_data=change_input_type_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, visible = True, key=('change_input_type_sprachen',len(input_list_sprachen))))

        return(empty_column_1_x, empty_column_1_y)
    
    def empty_column_tereignis(self, input_list_tereignis):
        #Leere Zeile definieren, für den Fall, dass eine leere Zeile hinzugefügt werden soll
        datelists = self.make_day_month_year_lists()
        empty_column_1_x = []
        empty_column_1_y = []
        empty_column_1_x.append(
            sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_tereignis', len(input_list_tereignis)), tooltip='Delete this item'))

        empty_column_1_x.append(
            sg.Input(default_text = '', size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_tereignis", len(input_list_tereignis))))
            
        empty_column_1_x.append(sg.Text('Datum: ', pad=(5, (0, 0)), background_color = 'black',k=('tereignis_datum_text', len(input_list_tereignis)), font=('Arial Bold', 10)))
            
        empty_column_1_x.append(
            sg.Combo(datelists[0], size=(5, 1), font=('Arial Bold', 10), default_value = 1, expand_x=False, enable_events=True, readonly=False, key=("input_tereignis_tage", len(input_list_tereignis))))

        empty_column_1_x.append(
            sg.Combo(datelists[1], size=(5, 1), font=('Arial Bold', 10), default_value = 1, expand_x=False, enable_events=True, readonly=False, key=("input_tereignis_monate", len(input_list_tereignis))))
            
        empty_column_1_x.append(
            sg.Combo(datelists[2], size=(10, 1), font=('Arial Bold', 10), default_value = 1950, expand_x=False, enable_events=True, readonly=False, key=("input_tereignis_jahre", len(input_list_tereignis))))
        
        empty_column_1_x.append(sg.Text(' bis ', pad=(5, (0, 0)), background_color = 'black',k=('tereignis_datum_text_bis', len(input_list_tereignis)), font=('Arial Bold', 10)))
            
        empty_column_1_x.append(
            sg.Combo(datelists[0], size=(5, 1), font=('Arial Bold', 10), default_value = 1, expand_x=False, enable_events=True, readonly=False, key=("input_tereignis_tage_ende", len(input_list_tereignis))))

        empty_column_1_x.append(
            sg.Combo(datelists[1], size=(5, 1), font=('Arial Bold', 10), default_value = 1, expand_x=False, enable_events=True, readonly=False, key=("input_tereignis_monate_ende", len(input_list_tereignis))))
            
        empty_column_1_x.append(
            sg.Combo(datelists[2], size=(10, 1), font=('Arial Bold', 10), default_value = 1950, expand_x=False, enable_events=True, readonly=False, key=("input_tereignis_jahre_ende", len(input_list_tereignis))))
        
        empty_column_1_y.append(
            sg.Button('', image_data=look_for_name_in_transcript_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, visible = True, pad = ((40, 0), (0, 0)), key=('look_for_name_in_transcript_tereignis',len(input_list_tereignis))))
        
        empty_column_1_y.append(
            sg.Text('', font=('Arial Bold', 10), expand_x=False, justification='left', visible = False, key=('description_tereignis', len(input_list_tereignis))))
        
        empty_column_1_y.append(
            sg.Combo([], size=(10, 1), font=('Arial Bold', 10), default_value = '', visible = False, expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_tereignis', len(input_list_tereignis))))
        empty_column_1_y.append(
            sg.Button("Play", visible = False, key=('Play_File_tereignis', len(input_list_tereignis))))
        empty_column_1_y.append(
            sg.Button("Stop", visible = False, key=('Stop_File_tereignis', len(input_list_tereignis))))

        return(empty_column_1_x, empty_column_1_y)
    
    def empty_column_desk(self, deskriptoren_suggest):
        """Creates an empty line for UI-Part "Deskriptoren" if user clicks the "add new Deskriptor" (+) button.

        Args:
            deskriptoren_suggest(list): List of "Deskriptor" Inputs for UI
            
        Returns:
            empty_column_1_x, empty_column_1_y(lists): Wrappers with UI elements for single entry of Deskriptor.
        """
        #Leere Zeile definieren, für den Fall, dass eine leere Zeile hinzugefügt werden soll
        
        empty_column_1_x = []
        empty_column_1_y = []
        empty_column_1_x.append(
            sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_desk', len(deskriptoren_suggest)), tooltip='Delete this item'))

        empty_column_1_x.append(
            sg.Text('', enable_events=True, font=('Arial Bold', 10), text_color = 'blue', key=('input_desk', len(deskriptoren_suggest)), visible = False, background_color = 'white'))
            
        empty_column_1_x.append(
            sg.Input(default_text = '', size=(25, 1), enable_events=True, visible = True, key=("input_desk_alt", len(deskriptoren_suggest))))
            
        empty_column_1_x.append(
            sg.Text('Zugeordnete Klasse auswählen:', enable_events=False, font=('Arial Bold', 10), text_color = 'blue', visible = False, key=('hinweis_desk_klassen', len(deskriptoren_suggest)), background_color = 'white'))

        empty_column_1_x.append(
            sg.Combo('', size=(50, 1), font=('Arial Bold', 10), default_value = '', expand_x=False, enable_events=True, visible = False, readonly=False, auto_size_text = True, key=("input_desk_klasse_chooser", len(deskriptoren_suggest))))
        
        empty_column_1_y.append(
            sg.Button('', image_data=look_for_name_in_transcript_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, visible = True, pad = ((40, 0), (0, 0)), key=('look_for_name_in_transcript_desk',len(deskriptoren_suggest))))
        
        empty_column_1_y.append(
            sg.Button('', image_data=refresh_ndb_button,
                        button_color=(sg.theme_background_color(),sg.theme_background_color()),
                        border_width=0, pad = ((5, 0), (0, 0)), key=('refresh_ndb_desk', len(deskriptoren_suggest))))
        
        empty_column_1_y.append(
            sg.Button('', image_data=change_input_type_button,
                    button_color=(sg.theme_background_color(),sg.theme_background_color()),
                    border_width=0, visible = True, key=('change_input_type_desk', len(deskriptoren_suggest))))
        
        empty_column_1_y.append(
            sg.Combo([], size=(10, 1), font=('Arial Bold', 10), default_value = '', visible = False, expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_desk', len(deskriptoren_suggest))))
        empty_column_1_y.append(
            sg.Button("Play", visible = False, key=('Play_File_desk', len(deskriptoren_suggest))))
        empty_column_1_y.append(
            sg.Button("Stop", visible = False, key=('Stop_File_desk', len(deskriptoren_suggest))))

        self.eventlist_desk.append(('Play_File_desk', len(deskriptoren_suggest)))

        return(empty_column_1_x, empty_column_1_y)

    def empty_column_tags(self, input_list_tags):
        """Creates an empty line for UI-Part "Tags" if user clicks the "add new Tag" (+) button.

        Args:
            input_list_tags(list): List of "Tags" Inputs for UI
            
        Returns:
            empty_column_1_x, empty_column_1_y(lists): Wrappers with UI elements for single entry of Tag.
        """
        #Leere Zeile definieren, für den Fall, dass eine leere Zeile hinzugefügt werden soll
        empty_column_1_x = []
        empty_column_1_y = []
        empty_column_1_x.append(
            sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_tags', len(input_list_tags)), tooltip='Delete this item'))

        empty_column_1_x.append(
            sg.Input(default_text = '', size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_tags", len(input_list_tags))))
        
        empty_column_1_y.append(
            sg.Button('', image_data=look_for_name_in_transcript_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, visible = True, pad = ((40, 0), (0, 0)), key=('look_for_name_in_transcript_tags',len(input_list_tags))))
        
        empty_column_1_y.append(
            sg.Text('', font=('Arial Bold', 10), expand_x=False, justification='left', visible = False, key=('description_tags', len(input_list_tags))))
        
        empty_column_1_y.append(
            sg.Combo([], size=(10, 1), font=('Arial Bold', 10), default_value = '', visible = False, expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_tags', len(input_list_tags))))
        print('DEBUG Audio Starter Tags Addition', len(input_list_tags))
        empty_column_1_y.append(
            sg.Button("Play", visible = False, key=('Play_File_tags', len(input_list_tags))))
        empty_column_1_y.append(
            sg.Button("Stop", visible = False, key=('Stop_File_tags', len(input_list_tags))))

        return(empty_column_1_x, empty_column_1_y)

    def empty_column_gattung(self, gattungen_suggest, list_gattungen):
        """Adds empty line for additional Gattung entry
        Args:
            gattungen_suggest(list): List of Gattungen suggested by LLM.
            list_gattungen(list): List of Gattungen possible for Dropdown Menue

        Returns:
            column_gattungen(list): Elements wrapper for new default Gattungen line in UI.        
        
        """
        
        column_gattungen=[sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_gatt', len(gattungen_suggest)), tooltip='Delete this item'),
                sg.Combo(list(list_gattungen), size=(25, 1), font=('Arial Bold', 10), default_value = list(gattungen_suggest)[0], expand_x=False, enable_events=True,  readonly=False, key=('combo_gattungen', len(gattungen_suggest)))]
        return(column_gattungen)

    def popup_window(self, transcripts_list, start_sorted, audiofile_path):
        """Defines Popup-Window for individual Transcript Search functionality
        
        Returns:
            window_popup(SimpleGUI Element): Window Element with all functions needed
        
        """
        
        #Audioplayer Such-Version
        column_player1 = []
        column_player2 = []
        column_player3 = []
        column_player4 = []
        self.eventlist_search_player_start = []
        self.eventlist_search_player_end = []
        #heading = [sg.Text('Transkript-Audio-Suche', pad=(5, (50, 10)), background_color = 'black', font=('Arial Bold', 20))]
        audioplayer2 = audio_playback(audiofile_path)

        slider = [sg.Slider((0, audioplayer2.get_duration()), orientation='horizontal', key='-SL-', enable_events=True, disable_number_display = True, size = (100, 20))]
        text_time = [sg.Text(audioplayer2.format_time(0), background_color = 'black', font=('Arial Bold', 20), key='current_time')]

        column_player1.append(
            sg.Input(default_text = '', size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_file_search")))
        column_player1.append(#Umwandlung Freitext-Feld Button einfügen
            sg.Button('', image_data=look_for_name_in_transcript_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, visible = True, key=('look_for_search_in_transcript')))
        column_player2.append(
            sg.Combo([], size=(10, 1), font=('Arial Bold', 10), default_value = '', visible = False, expand_x=False, enable_events=True,  readonly=False, key=f'audio_starter_transcript_search'))
        column_player2.append(
            sg.Button("Play", visible = False, key=f'Play_File_search'))
        column_player2.append(
            sg.Button("Pause", visible = False, key=f'Pause_File_search'))
        column_player2.append(
            sg.Button("Stop", visible = False, key=f'Stop_File_search'))
        column_player2.append(
            sg.Button("Transcript", visible = False, key=f'Transcript_File_search'))
        column_player2.append(
            sg.Button("Gesamtes Transcript", visible = False, key=f'Transcript_File_search_whole'))
        
        column_player2.append(sg.Slider((0, audioplayer2.get_duration()), orientation='horizontal', key='-SL-_search', enable_events=True, disable_number_display = True, size = (50, 20), visible = False))
        
        column_player2.append(
        sg.Text(audioplayer2.format_time(0), background_color = 'black', font=('Arial Bold', 20), key='current_time_search', visible = False))
        
        column_player3.append(sg.Multiline(default_text='', visible = False, size=(200, 5), write_only=True, key = 'transcript_search1'))
        column_player4.append(sg.Multiline(visible = False, size=(200, 300), write_only=True,reroute_cprint=True, key = 'transcript_search2'))
        
        #Popup Window
        layout_popup = []
        layout_popup.append([sg.Column([column_player1], pad = ((0, 0), (10, 0)), key = ('column_search_player_1'), visible = True)])
        layout_popup.append([sg.Column([column_player2], pad = ((0, 0), (10, 0)), key = ('column_search_player_1'), visible = True)])
        layout_popup.append([sg.Column([column_player3], pad = ((0, 0), (10, 0)), key = ('column_search_player_1'), visible = True)])
        layout_popup.append([sg.Column([column_player4], pad = ((0, 0), (10, 0)), key = ('column_search_player_1'), visible = True)])

        layout = layout_popup
        window = sg.Window('Helpers', layout, resizable=True, background_color='DarkSlateGray', keep_on_top=True, border_depth=0.5, finalize = True)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == "Cancel":
                window.close()
                break
                #return None
            if event == 'look_for_search_in_transcript':
                values_name = values[("input_file_search")]
                audio_starts = find_audio_timecodes().find_word_in_transcript(values_name, transcripts_list, start_sorted)
                if len(audio_starts[0]) >0:
                    window[('audio_starter_transcript_search')].update(values = audio_starts[0], value = audio_starts[0][0], visible=True)
                    window[('Play_File_search')].update(visible=True)
                    window[('Pause_File_search')].update(visible=True)
                    window[('Stop_File_search')].update(visible=True)
                    window[('Transcript_File_search')].update(visible=True)
                    window[('Transcript_File_search_whole')].update(visible=True)
                    window[('-SL-_search')].update(visible=True)
                    window[('current_time_search')].update(visible=True)

                    self.eventlist_search_player_start.append('Play_File_search')
                    self.eventlist_search_player_end.append('Stop_File_search')
                    skip_time = values['audio_starter_transcript_search']
                    audioplayer2.scroll_playback_to_second(skip_time)
                    window['-SL-_search'].update(value = skip_time)
                    try:
                        window['current_time_search'].update(audioplayer2.format_time(skip_time))
                    except ValueError:
                        pass
                    
                else:
                    window[('audio_starter_transcript_search')].update(visible=False)
                    window[('Transcript_File_search')].update(visible=False)
                    window[('Play_File_search')].update(visible=False)
                    window[('Pause_File_search')].update(visible=False)
                    window[('Stop_File_search')].update(visible=False)
                    window[('transcript_search1')].update(visible=False)
                    window[('transcript_search2')].update(visible=False)
                    window[('-SL-_search')].update(visible=False)
                    window[('current_time_search')].update(visible=False)
            
            if event == 'audio_starter_transcript_search':
                skip_time = values['audio_starter_transcript_search']
                audioplayer2.scroll_playback_to_second(skip_time)
                window['-SL-_search'].update(value = skip_time)
                window['current_time_search'].update(audioplayer2.format_time(skip_time))

            if event == 'Play_File_search': 
                skip_time = int(values['-SL-_search'])
                print('DEBUG SKIP TIME:', skip_time)
                audioplayer2.play_file()
                audioplayer2.scroll_playback_to_second(skip_time)
            
            if event == 'Stop_File_search': 
                audioplayer2.stop_playback()
                window['-SL-_search'].update(value = 0)
                window['current_time_search'].update(audioplayer2.format_time(0))
            
            if event == 'Pause_File_search': 
                audioplayer2.pause_playback()
                position = audioplayer2.get_position()
                window['-SL-_search'].update(value = position)
                window['current_time_search'].update(audioplayer2.format_time(position))

            if event == '-SL-_search': 
                audioplayer2.scroll_playback_to_second(int(values['-SL-_search']))
                
                window['current_time_search'].update(audioplayer2.format_time(int(values['-SL-_search'])))

            if event == 'Transcript_File_search_whole':
                searchtext = values[("input_file_search")]
                
                #Gesamttranskript in bunt einfügen
                window[('transcript_search2')].update('',visible=False)
                window[('transcript_search2')].update(visible=True)
                
                for t in range(len(transcripts_list)):
                    
                    sg.cprint(f'{strftime("%H:%M:%S", gmtime(start_sorted[t]))}:', font='Arial 12', colors='white on green', end = '')
                    if searchtext.lower() !='' and searchtext.lower() in transcripts_list[t].lower():
                        split_transcript = transcripts_list[t].lower().split(searchtext.lower())
                        for i in range(len(split_transcript)):
                            if i < len(split_transcript)-1:
                                sg.cprint(split_transcript[i], font='Arial 12', end = '')
                            else:
                                sg.cprint(split_transcript[i], font='Arial 12')
                            
                            if len(split_transcript)>1 and i < len(split_transcript)-1:
                                sg.cprint(searchtext, colors='white on red', font='Arial 12 bold', end = '')
                    else:
                        sg.cprint(transcripts_list[t], font='Arial 12')

            #Teilskript
            if event == "Transcript_File_search":
                print('DEBUG PopUp Event Transcript File Search NEW')
                
                print('event_popup_2')
                values_start = values[('audio_starter_transcript_search')]

                #Transkriptausschnitt einfügen
                index_transcript = start_sorted.index(values_start)
                print('index Transcript:', index_transcript)
                list_text = []
                joiner = ' '
                if index_transcript >0:
                    list_text.append(transcripts_list[index_transcript-1])
                                
                    list_text.append(transcripts_list[index_transcript])
                            
                if index_transcript < len(transcripts_list):
                        
                    list_text.append(transcripts_list[index_transcript+1])
                        
                text_gesamt = joiner.join(list_text)

                window[('transcript_search1')].update(value=text_gesamt, visible=True)
                
                print('Contents changed of window')
                    
                #return None
        window.close()
    
    def popup_window_karin(self, transcripts_list): 
        """Defines Popup-Window for interactive AI Helper K.AR.IN
        
        Returns:
            window_popup_karin(SimpleGUI Element): Complete Popup UI element for K.AR.IN functionality.
        """
        #Frage-Antwort Tool
        #Frage  
        processor = process_text_with_gemini()
        print('Open K.AR.IN')
        column1= [sg.Multiline(default_text='Stelle K.AR.IN ("Künstliche ARchiv INtelligenz") eine Frage zum Audio!', size=(60,10), key=('ask_karin_input')), sg.Button('', image_data=send_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, visible = True, key=('ask_karin'))]
            
        column2=[sg.Button('', image_data=ask_karin_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, visible = False, key=('answer_karin')), sg.Multiline(default_text='', size=(60,10), visible = False, key=('ask_karin_output'))]
        
        #Popup Window
        layout_popup = []
        layout_popup.append([sg.Column([column1], pad = ((0, 0), (10, 0)), key = ('column_search_player_1'), visible = True)])
        layout_popup.append([sg.Column([column2], pad = ((0, 0), (10, 0)), key = ('column_search_player_1'), visible = True)])
        
        window_popup_karin = sg.Window('Frag K.AR.IN', layout_popup, size=(600, 400), resizable=True, background_color='DarkSlateGray', keep_on_top=True, border_depth=0.5, finalize = False)

        while True:
            event, values = window_popup_karin.read()
            if event == sg.WIN_CLOSED or event == "Cancel":
                window_popup_karin.close()
                break
            if event == 'ask_karin':#Popup Event
                print('event_popup_3')
                if values[('ask_karin_input')] != '':
                    print('event_popup_4')
                    values_input = values[('ask_karin_input')]
                    joiner = ' '
                    transcript_full = joiner.join(transcripts_list)
                    #print(transcript_full)
                    answer_llm = processor.ask_karin(transcript_full, values_input)
                     
                    window_popup_karin[('answer_karin')].update(visible=True)
                    window_popup_karin[('ask_karin_output')].update(visible=True, value=answer_llm)
        window_popup_karin.close()
        
    
    def popup_window_audioplayer(self, audio_file1, transcript_lines, timecodes, audio_file2): 
        """Defines Popup-Window for Audioplayer of source Audiofile

        Args:
            audiofile_path(str): Path to audiofile of whole audio.
        
        Returns:
            window_popup_audioplayer(SimpleGUI Element): Complete Popup UI element for Audioplayer functionality.
        """
        """column_audioplayer = []
        #Audioplayer init Gesamtfile
        audioplayer1 = audio_playback(audiofile_path)
        heading = [sg.Text('Play File', pad=(5, (50, 10)), background_color = 'black', font=('Arial Bold', 20))]
        player_line = [sg.Button("Play", key='Play_File'), sg.Button("Pause", key='Pause_File'), sg.Button("Stop", key='Stop_File')] #, sg.Button("Resume", key='Resume_File')
        slider = [sg.Slider((0, audioplayer1.get_duration()), orientation='horizontal', key='-SL-', enable_events=True, disable_number_display = True, size = (100, 20))]
        text_time = [sg.Text(audioplayer1.format_time(0), background_color = 'black', font=('Arial Bold', 20), key='current_time')]
        column_audioplayer.append(heading)
        column_audioplayer.append(player_line)
        column_audioplayer.append(slider)
        column_audioplayer.append(text_time)
        
        #Popup Window
        layout_popup = []
        layout_popup.append([sg.Column(column_audioplayer, pad = ((0, 0), (10, 0)), size=(950, 400), expand_x = True, key = ('column_audioplayer_1'), visible = True)])
        
        window_popup_audioplayer = sg.Window('Audioplayer', layout_popup, size=(950, 400), resizable=True, background_color='DarkSlateGray', keep_on_top=True, border_depth=0.5, finalize = False)
        while True:
            event, values = window_popup_audioplayer.read()
            if event == sg.WIN_CLOSED or event == "Cancel":
                window_popup_audioplayer.close()
                break

            if event == 'Play_File': 
                audioplayer1.play_file()
                audioplayer1.scroll_playback_to_second(int(values['-SL-']))
                position = audioplayer1.get_position()
                window_popup_audioplayer['-SL-'].update(value = position)
                window_popup_audioplayer['current_time'].update(audioplayer1.format_time(position))

            if event == 'Pause_File': 
                audioplayer1.pause_playback()
                position = audioplayer1.get_position()
                window_popup_audioplayer['-SL-'].update(value = position)
                window_popup_audioplayer['current_time'].update(audioplayer1.format_time(position))
            
            if event == 'Stop_File': 
                audioplayer1.stop_playback()
                window_popup_audioplayer['-SL-'].update(value = 0)
                window_popup_audioplayer['current_time'].update(audioplayer1.format_time(0))

            if event == '-SL-':
                #print(values['-SL-'])
                #audioplayer1.play_file()
                audioplayer1.scroll_playback_to_second(int(values['-SL-']))
                window_popup_audioplayer['current_time'].update(audioplayer1.format_time(int(values['-SL-'])))
        window_popup_audioplayer.close()"""
              
        transcript_player(audio_file1, transcript_lines, timecodes, audio_file2)

    def main_window(self, transcripts_list, start_sorted, input_list_urheber, description_list_urheber, roles_found_urheber, reference_roles_list_urheber, ndb_urheber_data, input_list_mitwirkende, description_list_mitwirkende, roles_found_mitwirkende, reference_roles_list_mitwirkende, ndb_mitwirkende_data, text_input_titel, zusammenfassung, input_list_tpers, description_list_tpers, ndb_thema_persons_suggest, input_list_torte, description_list_torte, torte_list_llm_original, tinst_suggest_bundle, tereignis_suggest_bundle, audiofiles_path, audiofile, original_file, gattungen_suggest, genre_suggest, sprachen_suggest_original, sprachen_suggest_ndb, metatags_suggest, deskriptoren_suggest, audioraum_darstellung_global_suggest, realisierung_datum_suggest, realisierung_ort_suggest, realisierung_ort_kontext, realisierung_typ_suggest):

        """Main Window Element which contains the standard elements shown when UI-Window appears. Real appearence is flexible and depends on the amount and kind of input data but general structure is always the same.
        
        Args:
            transcripts_list(list): List of transcript parts. Contains whole transcript but devided in parts for combining it with timecodes for audio player.
            start_sorted(list): List of timecodes that define where transcript part from transcript_list starts within the audio-
            input_list_urheber(list): LLM-Suggestions on Urheber
            description_list_urheber(list): Descriptions on single persons from input_list_urheber, coming from LLM
            roles_found_urheber(list): Roles defined for input_list_urheber by LLM  from reference_roles_list_urheber list
            reference_roles_list_urheber(list): List of possible roles that Urheber can have.
            ndb_urheber_data(list): NDB-Suggestions on Urheber based on input_list_urheber as input for NDB search
            input_list_mitwirkende(list): LLM Suggestions on Mitwirkende
            description_list_mitwirkende(list): List of descriptions for Mitwirkende on input_list_mitwirkende generated  by LLM.
            roles_found_mitwirkende(list): Roles defined for input_list_mitwirkende by LLM from reference_roles_list_mitwirkende list
            reference_roles_list_mitwirkende(list): List of possible roles that Mitwirkender can have.
            ndb_mitwirkende_data(list): NDB-Suggestions on Mitwirkender based on input_list_mitwirkende as input for NDB search
            text_input_titel(str): Title for AK entry suggested by LLM
            zusammenfassung(str): Summary for AK entry suggested by LLM
            input_list_tpers(list): List of LLM Suggestions for themaPerson
            description_list_tpers(list): LLM-generated descriptions for persons from input_list_tpers.
            ndb_thema_persons_suggest(list): NDB Suggests for themaPersonen based on input_list_tpers as input for NDB search
            input_list_torte(list): List of LLM Suggestions for themaOrt
            description_list_torte(list): LLM-generated descriptions for Orte from input_list_torte.
            torte_list_llm_original(list): Original unfiltered Orte Output from LLM
            tinst_suggest_bundle(list): LLM suggests for themaInstitution
            tereignis_suggest_bundle(list): LLM suggests for themaEreignis
            audiofiles_path(str): Path to folder where speech only audiofiles are stored.
            audiofile(str): Filename of speech only audiofile
            original_file(str): Path to original input file
            gattungen_suggest(list): List of suggested Gattungen for dataset
            genre_suggest(list): List of suggested Genres for dataset
            sprachen_suggest_original(list): List of LLM-suggested Languages for Dataset
            sprachen_suggest_ndb(list): NDB-Suggests for Languages based on prachen_suggest_original
            metatags_suggest(list): List of suggested Metatags
            deskriptoren_suggest(list): List of suggested Deskriptoren
            audioraum_darstellung_global_suggest(json_like): User-Pre-defined suggestion for Audioraumdarstellung
            realisierung_datum_suggest(list): Suggest for Datum for Realisierungs-Eintrag, that is formatted as list of its contents.
            realisierung_ort_suggest(str): Suggest for Realisierungs-Ort
            realisierung_ort_Kontext(str): Transcription context for Realisierungs-Ort
            realisierung_typ_suggest(str): Suggest for Typ Realisierung

        Returns:
            sg.Window(SimpleGUI Object): General Window for AK-Correction Menue with all elements and data from the Defs input. Can be edited by user.
            audioplayer1(SimpleGUI Object): Audioplayer functionality for original file
            audioplayer2(SimpleGUI Object): Audioplayer functionality for spech-only file for playing certain parts of audio where certain entities occur.
        """
        
        #Gattungen_Liste_auslesen
        #Get list of Gattungen from excel list
        df = pandas.read_excel('Excel_Lists_entities\\gattungen_names.xlsx')
        self.list_gattungen = df['Gattungen_Liste']
        df2 = pandas.read_excel('Excel_Lists_entities\\lesegeschwindigkeit_norm_db_ids.xlsx')
        list_langleseabspielgeschwindigkeit = df2['langbezeichnung']

        #Spalte für Content definieren:
        list_master = []
        column_1 = []
        list_lines = []

        #Top Menu Bar
        menu_def = [['&Assistenten', ['&Stichwortsuche::stichwortsuche', '&Frag K.AR.IN', '&Audioplayer']]]
        column_1.append([sg.MenubarCustom(menu_def)])

        #Überschrift hinzufügen
        l1_titel = sg.Text('RHTI definieren', font=('Arial Bold', 20), background_color = 'black', expand_x=False, justification='center', pad = ((0, 0),(30, 0)))
        t1_titel = sg.Multiline(text_input_titel, enable_events=True, key='input_titel', expand_x=True, expand_y=True, justification='left')
        
        column_1.append([l1_titel])
        column_1.append([t1_titel])
        #column_1.append([])

        #Zusammenfassung hinzufügen
        l1_zusammen = sg.Text('Zusammenfassung definieren', pad=(5, (50, 10)), background_color = 'black', font=('Arial Bold', 20), expand_x=False, justification='center')
        t1_zusammen = sg.Multiline(zusammenfassung, enable_events=True, key='input_zusammen', size = (20,10), expand_x=True, expand_y=True, justification='left')
        
        column_1.append([l1_zusammen])
        column_1.append([t1_zusammen])
        #column_1.append([])
        
        #Mitwirkende Menü
        #General Elements
        heading = sg.Text('Mitwirkende korrigieren', pad=(5, (50, 10)), background_color = 'black', font=('Arial Bold', 20))
        column_1.append([heading])
        
        #column_2 = []
        column_mitwirkende = []
        self.current_input = []
        self.alt_input = []
        self.orig_input = []
        self.final_input_is_original = [] #True = is Original Input Format or 'False' = Final Input is Alternative Input Format
        self.hyperlink_list_mitwirkende = [] #List for Hyperlinks for NDB
        self.current_hyperlink_list_mitwirkende = [] #List for hyperlinks that are currently shown and active
        self.current_hyperlink_mitwirkende = []
        self.mitwirkende_count_original = len(input_list_mitwirkende)
        for i in range(len(input_list_mitwirkende)):
            #Get Timecodes for audioplayer
            audio_starts = find_audio_timecodes().find_word_in_transcript(input_list_mitwirkende[i], transcripts_list, start_sorted)
            print(audio_starts)
            column_1_x = []
            column_1_y = []

            #Für Freitextfelder aufteilen in Vor- und Nachnamensfelder
            first_name, last_name = split_name(input_list_mitwirkende[i])
           
            column_1_x.append(
                    sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_mitwirkende', i), tooltip='Delete this item'))

            #Gegebenen Input verarbeiten
            print('DEBUG N.N. Data:', ndb_mitwirkende_data)
            if ndb_mitwirkende_data[0] == None or len(ndb_mitwirkende_data[i][0])==0: #Wenn beim NDB-Abgleich nichts gefunden wurde für den einzelnen Mitwirkenden oder generell keine Mitwirkenden gefunden wurden und daher "N.N. angelegt werden soll als einzelner Mitwirkender."

                column_1_x.append(
                        sg.Input(default_text = first_name, size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_mitwirkende_vorname", i)))
                column_1_x.append(
                        sg.Input(default_text = input_list_mitwirkende[i], size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_mitwirkende_nachname", i)))
                column_1_x.append(
                    sg.Combo([], size=(100, 1), font=('Arial Bold', 10), default_value = '', expand_x=False, enable_events=True, visible = False, readonly=False, auto_size_text = True, key=("input_mitwirkende", i))) #unsichtbarer Input, der aktiviert wird, wenn nach Änderung desTextes doch noch Treffer in NDB gefunden werden.
                
                #Show Hyperlink next to Column - Hidden!
                column_1_x.append(sg.Text('', enable_events=True, font=('Arial Bold', 10), key=('URL_mitwirkende', i), visible = False, text_color = 'blue', background_color = 'white'))
                
                self.current_input.append('Freitext')
                self.alt_input.append(False)
                self.orig_input.append('Freitext')
                self.final_input_is_original.append(True)  
                self.hyperlink_list_mitwirkende.append(None)  
                self.current_hyperlink_list_mitwirkende.append(None)
                self.current_hyperlink_mitwirkende.append(None)

            else: #Wenn beim NDB-Abgleich etwas gefunden wurde
                list_to_show = []
                print(ndb_mitwirkende_data[i])
                for n in range(len(ndb_mitwirkende_data[i][0])):
                    string_shown = f'{ndb_mitwirkende_data[i][3][n]} | {ndb_mitwirkende_data[i][2][n]} | {ndb_mitwirkende_data[i][4][n]} | {ndb_mitwirkende_data[i][6][n]} | {ndb_mitwirkende_data[i][7][n]} | {(ndb_mitwirkende_data[i][5][n])}'
                    list_to_show.append(string_shown)

                #Add single Hyperlink-Liste to complete Hyperlinks List
                self.hyperlink_list_mitwirkende.append(ndb_mitwirkende_data[i][5])

                column_1_x.append(
                    sg.Combo(list_to_show, size=(100, 1), font=('Arial Bold', 10), default_value = list_to_show[0], expand_x=False, auto_size_text = True, enable_events=True,  readonly=False, key=("input_mitwirkende", i)))
                
                #Unsichtbarer alternativer Input, der  ggf. aktiviert wird unten
                column_1_x.append(
                        sg.Input(default_text = first_name, size=(25, 1), enable_events=True, readonly=False, visible = False, key=("input_mitwirkende_vorname", i)))
                column_1_x.append(
                        sg.Input(default_text = last_name, size=(25, 1), enable_events=True, readonly=False, visible = False, key=("input_mitwirkende_nachname", i)))
                
                #Show Hyperlink next to Column
                column_1_x.append(sg.Text(self.hyperlink_list_mitwirkende[i][0], enable_events=True, font=('Arial Bold', 10), text_color = 'blue', key=('URL_mitwirkende', i), background_color = 'white')) 

                #Add viewable Hyperlink of NDB-Entry
                self.current_hyperlink_list_mitwirkende.append(self.hyperlink_list_mitwirkende[i])
                self.current_hyperlink_mitwirkende.append(self.hyperlink_list_mitwirkende[i][n])

                self.current_input.append('Dropdown')
                self.alt_input.append(False)
                self.orig_input.append('Dropdown')
                self.final_input_is_original.append(True)

            #Bemerkungs-Freitextfeld
            
            column_1_x.append(sg.Text('Bemerkung:', font=('Arial Bold', 10), expand_x=False, justification='left', enable_events=True, pad = ((0, 0),(0, 0)), key=("bemerkung_mitwirkende_text", i)))

            column_1_x.append(
                sg.Input(default_text = '', size=(25, 1), enable_events=True, readonly=False, justification='left', visible = True, key=("bemerkung_mitwirkende", i)))

            column_1_y.append(#Refresh-NDB-Ergebnis-Button hinzufügen
                sg.Button('', image_data=refresh_ndb_button,
                    button_color=(sg.theme_background_color(),sg.theme_background_color()),
                    border_width=0, pad = ((40, 0), (0, 0)), key=('refresh_ndb_mitwirkende', i)))
            
            column_1_y.append(#Umwandlung Freitext-Feld Button einfügen - per Default sichtbar nur wenn wir ein Dropdown-Feld haben
                sg.Button('', image_data=change_input_type_button,
                        button_color=(sg.theme_background_color(),sg.theme_background_color()),
                        border_width=0, visible = True, key=('change_input_type_mitwirk', i)))

            column_1_y.append(
                    sg.Combo(list(reference_roles_list_mitwirkende), size=(25, 1), font=('Arial Bold', 10), default_value = list(roles_found_mitwirkende)[i], expand_x=False, enable_events=True,  readonly=False, key=('combo_mitwirkende', i)))

            if ndb_mitwirkende_data[0] == None or len(ndb_mitwirkende_data[i][0])==0:
                column_1_y.append(
                    sg.Button('', image_data=look_for_name_in_transcript_button,
                    button_color=(sg.theme_background_color(),sg.theme_background_color()),
                    border_width=0, visible = True, key=('look_for_name_in_transcript', i)))
            else:
                column_1_y.append(
                    sg.Button('', image_data=look_for_name_in_transcript_button,
                    button_color=(sg.theme_background_color(),sg.theme_background_color()),
                    border_width=0, visible = False, key=('look_for_name_in_transcript', i)))

            if len(audio_starts[0]) >0:
                column_1_y.append(
                    sg.Combo(audio_starts[0], size=(10, 1), font=('Arial Bold', 10), default_value = audio_starts[0][0], expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_mitwirkende', i)))
                column_1_y.append(
                    sg.Button("Play", key=('Play_File_mitwirkende', i)))
                column_1_y.append(
                    sg.Button("Stop", key=('Stop_File_mitwirkende', i)))
                column_1_y.append(
                    sg.Text(description_list_mitwirkende[i], font=('Arial Bold', 10), expand_x=False, justification='left', key=('description_mitwirkende', i)))
            else:
                column_1_y.append(
                    sg.Text('Not', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('audio_starter_mitwirkende', i)))
                column_1_y.append(
                    sg.Text('Found', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('Play_File_mitwirkende', i)))
                column_1_y.append(
                    sg.Text('in Audio Transcript', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('Stop_File_mitwirkende', i)))
                column_1_y.append(
                    sg.Text(description_list_mitwirkende[i], font=('Arial Bold', 10), expand_x=False, justification='left', key=('description_mitwirkende', i))
                    )
            #Button verschieben hinzufügen   
            column_1_y.append(
                    sg.Button("Zu Urheber", key=('verschieb_mitwirkende_urheber', i)))
            column_1_y.append(
                    sg.Button("Zu ThemaPerson", key=('verschieb_mitwirkende_themapers', i)))
            print('list_x_y')
            #column_1_x.append(sg.Column([column_1_xa], pad = ((0, 0), (10, 0)), key = ('column_mitwirk_x', i), visible = True))
            #column_1_x.append(sg.Column([column_1_xb], pad = ((0, 0), (10, 0)), key = ('column_mitwirk_x', i), visible = True))
            column_mitwirkende.append([sg.Column([column_1_x], pad = ((0, 0), (10, 0)), key = ('column_mitwirk_x', i), visible = True)])
            column_mitwirkende.append([sg.Column([column_1_y], pad = ((0, 0), (0, 0)), key = ('column_mitwirk_y', i), visible = True)])
            
        print('list_mitwirkende')
        column_1.append([sg.Column(column_mitwirkende, pad = ((0, 0), (10, 0)), key = ('column_mitwirk'), visible = True)])

        column_1.append([sg.Button('', image_data=add_data_item_button,
                    button_color=(sg.theme_background_color(),sg.theme_background_color()),
                    border_width=0, pad = ((40, 0), (20, 0)), key=('add_data_mitwirkende'))])
        #column_1.append([sg.Text('Weitere hinzufügen (Namen durch Kommas trennen)')])
        #column_1.append([sg.Input(default_text = '', size=(40, 1), enable_events=True, key="input_addition_mitwirkende")]) 
        #column_1.append([sg.Text('Rollen für weitere Personen hinzufügen (Bezeichnungen durch Kommas trennen)')])
        #column_1.append([sg.Input(default_text = '', size=(40, 1), enable_events=True, key="input_roles_addition_mitwirkende")])
        #column_1.append([])

        self.eventlist_mitwirkende = [] 
        
        for i in range(len(input_list_mitwirkende)):
            self.eventlist_mitwirkende.append(('Play_File_mitwirkende', i)) 
            
        self.eventlist_mitwirkende_stop_file = []       

        for j in range(len(input_list_mitwirkende)):
            self.eventlist_mitwirkende_stop_file.append(('Stop_File_mitwirkende', j))     

        #Urheber-Menü
        #General Elements
        heading = sg.Text('Urheber korrigieren', pad=(5, (50, 10)), background_color = 'black', font=('Arial Bold', 20))
        column_1.append([heading])
        
        #column_2 = []
        column_urheber = []
        self.current_input_urheber = []
        self.alt_input_urheber = []
        self.orig_input_urheber = []
        self.final_input_is_original_urheber = [] #True = is Original Input Format or 'False' = Final Input is Alternative Input Format
        self.urheber_count_original = len(input_list_urheber)
        self.hyperlink_list_urheber = [] #List for Hyperlinks for NDB
        self.current_hyperlink_list_urheber = [] #List for hyperlinks that are currentyl shown and active
        self.current_hyperlink_urheber = []
        for i in range(len(input_list_urheber)):
            #Get Timecodes for audioplayer
            audio_starts = find_audio_timecodes().find_word_in_transcript(input_list_urheber[i], transcripts_list, start_sorted)
            print(audio_starts)
            column_1_x = []
            column_1_y = []

            #Für Freitextfelder aufteilen in Vor- und Nachnamensfelder
            first_name, last_name = split_name(input_list_urheber[i])

            column_1_x.append(
                    sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_urheber', i), tooltip='Delete this item'))

            #Gegebenen Input verarbeiten
            if len(ndb_urheber_data[i][0])==0: #Wenn beim NDB-Abgleich nichts gefunden wurde
                column_1_x.append(
                        sg.Input(default_text = first_name, size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_urheber_vorname", i)))
                column_1_x.append(
                        sg.Input(default_text = last_name, size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_urheber_nachname", i)))
                column_1_x.append(
                    sg.Combo([], size=(100, 1), font=('Arial Bold', 10), default_value = '', expand_x=False, enable_events=True, visible = False, readonly=False, auto_size_text = True, key=("input_urheber", i))) #unsichtbarer Input, der aktiviert wird, wenn nach Änderung desTextes doch noch Treffer in NDB gefunden werden.

                #Show Hyperlink next to Column - Hidden!
                column_1_x.append(sg.Text('', enable_events=True, font=('Arial Bold', 10), key=('URL_urheber', i), visible = False, text_color = 'blue', background_color = 'white'))


                self.current_input_urheber.append('Freitext')
                self.alt_input_urheber.append(False)
                self.orig_input_urheber.append('Freitext')
                self.final_input_is_original_urheber.append(True)  
                self.hyperlink_list_urheber.append(None)  
                self.current_hyperlink_list_urheber.append(None)
                self.current_hyperlink_urheber.append(None)  

            else: #Wenn beim NDB-Abgleich etwas gefunden wurde
                list_to_show = []
                print(ndb_urheber_data[i])
                for n in range(len(ndb_urheber_data[i][0])):
                    string_shown = f'{ndb_urheber_data[i][3][n]} | {ndb_urheber_data[i][2][n]} | {ndb_urheber_data[i][4][n]} | {ndb_urheber_data[i][6][n]} | {ndb_urheber_data[i][7][n]} | {(ndb_urheber_data[i][5][n])}'
                    list_to_show.append(string_shown)

                #Add single Hyperlink-Liste to complete Hyperlinks List
                self.hyperlink_list_urheber.append(ndb_urheber_data[i][5])

                column_1_x.append(
                    sg.Combo(list_to_show, size=(100, 1), font=('Arial Bold', 10), default_value = list_to_show[0], expand_x=False, auto_size_text = True, enable_events=True,  readonly=False, key=("input_urheber", i)))
                
                column_1_x.append(#Unsichtbarer alternativer Input, der  ggf. aktiviert wird unten
                        sg.Input(default_text = first_name, size=(25, 1), enable_events=True, visible = False, key=("input_urheber_vorname", i)))

                column_1_x.append(#Unsichtbarer alternativer Input, der  ggf. aktiviert wird unten
                        sg.Input(default_text = last_name, size=(25, 1), enable_events=True, visible = False, key=("input_urheber_nachname", i)))
                
                #Show Hyperlink next to Column
                column_1_x.append(sg.Text(self.hyperlink_list_urheber[i][0], enable_events=True, font=('Arial Bold', 10), text_color = 'blue', key=('URL_urheber', i), background_color = 'white')) 

                #Add viewable Hyperlink of NDB-Entry
                self.current_hyperlink_list_urheber.append(self.hyperlink_list_urheber[i])
                self.current_hyperlink_urheber.append(self.hyperlink_list_urheber[i][n])

                self.current_input_urheber.append('Dropdown')
                self.alt_input_urheber.append(False)
                self.orig_input_urheber.append('Dropdown')
                self.final_input_is_original_urheber.append(True)

            column_1_y.append(#Refresh-NDB-Ergebnis-Button hinzufügen
                sg.Button('', image_data=refresh_ndb_button,
                    button_color=(sg.theme_background_color(),sg.theme_background_color()),
                    border_width=0, pad = ((40, 0), (0, 0)), key=('refresh_ndb_urheber', i)))
            
            column_1_y.append(#Umwandlung Freitext-Feld Button einfügen - per Default sichtbar nur wenn wir ein Dropdown-Feld haben
                sg.Button('', image_data=change_input_type_button,
                        button_color=(sg.theme_background_color(),sg.theme_background_color()),
                        border_width=0, visible = True, key=('change_input_type_urheber', i)))
            
            if len(ndb_urheber_data[i][0])==0:
                column_1_y.append(
                    sg.Button('', image_data=look_for_name_in_transcript_button,
                    button_color=(sg.theme_background_color(),sg.theme_background_color()),
                    border_width=0, visible = True, key=('look_for_name_in_transcript_urheber', i)))
            else:
                column_1_y.append(
                    sg.Button('', image_data=look_for_name_in_transcript_button,
                    button_color=(sg.theme_background_color(),sg.theme_background_color()),
                    border_width=0, visible = False, key=('look_for_name_in_transcript_urheber', i)))
            
            #Sicher stellen, dass die KI bei den Rollen keinen Mist ausgegeben hat, dann per Default erste Rolle aus Liste anzeigen:
            if list(roles_found_urheber)[i] in list(reference_roles_list_urheber):
                default_rolle = list(roles_found_urheber)[i]
            else:
                default_rolle = list(reference_roles_list_urheber)[0]

            #Rollen-Dropdown:    
            column_1_y.append(
                    sg.Combo(list(reference_roles_list_urheber), size=(25, 1), font=('Arial Bold', 10), default_value = default_rolle, expand_x=False, enable_events=True,  readonly=False, key=('combo_urheber', i)))

            if len(audio_starts[0]) >0:
                column_1_y.append(
                    sg.Combo(audio_starts[0], size=(10, 1), font=('Arial Bold', 10), default_value = audio_starts[0][0], expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_urheber', i)))
                column_1_y.append(
                    sg.Button("Play", key=('Play_File_urheber', i)))
                column_1_y.append(
                    sg.Button("Stop", key=('Stop_File_urheber', i)))
                column_1_y.append(
                    sg.Text(description_list_urheber[i], font=('Arial Bold', 10), expand_x=False, justification='left', key=('description_urheber', i)))
            else:
                column_1_y.append(
                    sg.Text('Not', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('audio_starter_urheber', i)))
                column_1_y.append(
                    sg.Text('Found', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('Play_File_urheber', i)))
                column_1_y.append(
                    sg.Text('in Audio Transcript', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('Stop_File_urheber', i)))
                column_1_y.append(
                    sg.Text(description_list_urheber[i], font=('Arial Bold', 10), expand_x=False, justification='left', key=('description_urheber', i))
                    )
            #Button verschieben hinzufügen    
            column_1_y.append(
                    sg.Button("Zu Mitwirkende", key=('verschieb_urheber_mitwirkende', i)))
            column_1_y.append(
                    sg.Button("Zu ThemaPerson", key=('verschieb_urheber_themapers', i)))
            print('list_x_y')
            #column_1_x.append(sg.Column([column_1_xc], pad = ((0, 0), (10, 0)), key = ('column_urheber_x', i), visible = True))
            #column_1_x.append(sg.Column([column_1_xd], pad = ((0, 0), (10, 0)), key = ('column_urheber_x', i), visible = True))
            column_urheber.append([sg.Column([column_1_x], pad = ((0, 0), (10, 0)), key = ('column_urheber_x', i), visible = True)])
            column_urheber.append([sg.Column([column_1_y], pad = ((0, 0), (0, 0)), key = ('column_urheber_y', i), visible = True)])
            
        print('list_urheber')
        column_1.append([sg.Column(column_urheber, pad = ((0, 0), (10, 0)), key = ('column_urheber'), visible = True)])

        column_1.append([sg.Button('', image_data=add_data_item_button,
                    button_color=(sg.theme_background_color(),sg.theme_background_color()),
                    border_width=0, pad = ((40, 0), (20, 0)), key=('add_data_urheber'))])
        #column_1.append([sg.Text('Weitere hinzufügen (Namen durch Kommas trennen)')])
        #column_1.append([sg.Input(default_text = '', size=(40, 1), enable_events=True, key="input_addition_mitwirkende")]) 
        #column_1.append([sg.Text('Rollen für weitere Personen hinzufügen (Bezeichnungen durch Kommas trennen)')])
        #column_1.append([sg.Input(default_text = '', size=(40, 1), enable_events=True, key="input_roles_addition_mitwirkende")])
        #column_1.append([])

        self.eventlist_urheber = [] 
        
        for i in range(len(input_list_urheber)):
            self.eventlist_urheber.append(('Play_File_urheber', i)) 
            
        self.eventlist_urheber_stop_file = []       

        for j in range(len(input_list_urheber)):
            self.eventlist_urheber_stop_file.append(('Stop_File_urheber', j))     

        #ThemaPersonen hinzufügen
        column_1.append([sg.Text('Thema-Personen korrigieren', pad=(0, (50, 10)), background_color = 'black', font=('Arial Bold', 20))])

        column_tpers = []
        self.current_input_tpers = []
        self.alt_input_tpers = []
        self.orig_input_tpers = []
        self.final_input_is_original_tpers = [] #True = is Original Input Format or 'False' = Final Input is Alternative Input Format
        self.tpers_count_original = len(input_list_tpers)
        self.hyperlink_list_tpers = [] #List for Hyperlinks for NDB
        self.current_hyperlink_list_tpers = [] #List for hyperlinks that are currentyl shown and active
        self.current_hyperlink_tpers = []
        print('DEBUG TPers:', input_list_tpers)
        for i in range(len(input_list_tpers)):
            
            if input_list_tpers[i] != None:
                if len(ndb_thema_persons_suggest[i]) >0:
                    #Get Timecodes for audioplayer
                    audio_starts = find_audio_timecodes().find_word_in_transcript(input_list_tpers[i], transcripts_list, start_sorted)
                    print(audio_starts)
                    column_2_x = []
                    column_2_y = []

                    #Für Freitextfelder aufteilen in Vor- und Nachnamensfelder
                    first_name, last_name = split_name(input_list_tpers[i])
                    #column_2_xa = []
                    #column_2_xb = []

                    column_2_x.append(
                        sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_tpers', i), tooltip='Delete this item'))

                    if len(ndb_thema_persons_suggest[i][0])==0: #Wenn beim NDB-Abgleich nichts gefunden wurde
                        column_2_x.append(sg.Input(default_text = first_name, size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_tpers_vorname", i)))

                        column_2_x.append(sg.Input(default_text = last_name, size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_tpers_nachname", i)))

                        column_2_x.append(
                            sg.Combo([], size=(100, 1), font=('Arial Bold', 10), default_value = '', expand_x=False, enable_events=True, visible = False, readonly=False, auto_size_text = True, key=("input_tpers", i))) #unsichtbarer Input, der aktiviert wird, wenn nach Änderung desTextes doch noch Treffer in NDB gefunden werden.
                        
                        #Show Hyperlink next to Column - Hidden!
                        column_2_x.append(sg.Text('', enable_events=True, font=('Arial Bold', 10), key=('URL_tpers', i), visible = False, text_color = 'blue', background_color = 'white'))

                        self.current_input_tpers.append('Freitext')
                        self.alt_input_tpers.append(False)
                        self.orig_input_tpers.append('Freitext')
                        self.final_input_is_original_tpers.append(True)
                        self.current_hyperlink_list_tpers.append(None)
                        self.current_hyperlink_tpers.append(None)    
                        self.hyperlink_list_tpers.append(None)       

                    else: #Wenn beim NDB-Abgleich etwas gefunden wurde
                        list_to_show_3= []
                        print(ndb_thema_persons_suggest[i])
                        for n in range(len(ndb_thema_persons_suggest[i][0])):
                            string_shown = f'{ndb_thema_persons_suggest[i][3][n]} | {ndb_thema_persons_suggest[i][2][n]} | {ndb_thema_persons_suggest[i][4][n]} | {ndb_thema_persons_suggest[i][6][n]} | {ndb_thema_persons_suggest[i][7][n]} | {(ndb_thema_persons_suggest[i][5][n])}'
                            list_to_show_3.append(string_shown)

                        #Add single Hyperlink-Liste to complete Hyperlinks List
                        self.hyperlink_list_tpers.append(ndb_thema_persons_suggest[i][5])

                        column_2_x.append(
                            sg.Combo(list_to_show_3, size=(100, 1), font=('Arial Bold', 10), default_value = list_to_show_3[0], expand_x=False, enable_events=True, auto_size_text = True, readonly=False, key=('input_tpers', i)))
                        
                        column_2_x.append(#Unsichtbarer alternativer Input, der  ggf. aktiviert wird unten
                                sg.Input(default_text = first_name, size=(25, 1), enable_events=True, visible = False, key=("input_tpers_vorname", i)))
                        
                        column_2_x.append(#Unsichtbarer alternativer Input, der  ggf. aktiviert wird unten
                                sg.Input(default_text = first_name, size=(25, 1), enable_events=True, visible = False, key=("input_tpers_nachname", i)))

                        #Show Hyperlink next to Column
                        column_2_x.append(sg.Text(self.hyperlink_list_tpers[i][0], enable_events=True, font=('Arial Bold', 10), text_color = 'blue', key=('URL_tpers', i), background_color = 'white')) 

                        #Add viewable Hyperlink of NDB-Entry
                        self.current_hyperlink_list_tpers.append(self.hyperlink_list_tpers[i])
                        self.current_hyperlink_tpers.append(self.hyperlink_list_tpers[i][n])

                        self.current_input_tpers.append('Dropdown')
                        self.alt_input_tpers.append(False)
                        self.orig_input_tpers.append('Dropdown')
                        self.final_input_is_original_tpers.append(True)

                    column_2_y.append(#Refresh-NDB-Ergebnis-Button hinzufügen
                        sg.Button('', image_data=refresh_ndb_button,
                            button_color=(sg.theme_background_color(),sg.theme_background_color()),
                            border_width=0, pad = ((40, 0), (0, 0)), key=('refresh_ndb_tpers', i)))
                        
                    column_2_y.append(#Umwandlung Freitext-Feld Button einfügen
                        sg.Button('', image_data=change_input_type_button,
                            button_color=(sg.theme_background_color(),sg.theme_background_color()),
                            border_width=0, visible = True, key=('change_input_type_tpers', i)))
                
                    if len(ndb_thema_persons_suggest[i][0])==0:    
                        column_2_y.append(
                            sg.Button('', image_data=look_for_name_in_transcript_button,
                                button_color=(sg.theme_background_color(),sg.theme_background_color()),
                                border_width=0, visible = True, key=('look_for_name_in_transcript_tpers',i)))
                    else:
                        column_2_y.append(
                            sg.Button('', image_data=look_for_name_in_transcript_button,
                                button_color=(sg.theme_background_color(),sg.theme_background_color()),
                                border_width=0, visible = False, key=('look_for_name_in_transcript_tpers',i)))

                    if len(audio_starts[0]) >0:
                        column_2_y.append( 
                            sg.Combo(audio_starts[0], size=(10, 1), font=('Arial Bold', 10), default_value = audio_starts[0][0], expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_tpers',i)))
                        column_2_y.append(
                            sg.Button("Play", key=('Play_File_tpers', i)))

                        column_2_y.append(   
                            sg.Button("Stop", key=('Stop_File_tpers', i)))
                        
                    else:
                        column_2_y.append(
                            sg.Text('Not', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('audio_starter_tpers',i)))
                        column_2_y.append(    
                            sg.Text('Found', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('Play_File_tpers', i)))
                        column_2_y.append( 
                            sg.Text('in Audio Transcript', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('Stop_File_tpers', i)))
                        
                    
                    column_2_y.append(
                            sg.Text(description_list_tpers[i], font=('Arial Bold', 10), expand_x=False, justification='left', key=('description_tpers', i)))
                    
                    #Button verschieben hinzufügen   
                    column_2_y.append(
                            sg.Button("Zu Urheber", key=('verschieb_themapers_urheber', i)))
                    column_2_y.append(
                            sg.Button("Zu Mitwirkende", key=('verschieb_themapers_mitwirkende', i)))
                    
                    #column_2_x.append(sg.Column([column_2_xa], pad = ((0, 0), (10, 0)), key = ('column_tpers_x', i), visible = True))
                    #column_2_x.append(sg.Column([column_2_xb], pad = ((0, 0), (10, 0)), key = ('column_tpers_x', i), visible = True))

                    column_tpers.append([sg.Column([column_2_x], pad = ((0, 0), (10, 0)), key = ('column_tpers_x', i), visible = True)])
                    column_tpers.append([sg.Column([column_2_y], pad = ((0, 0), (0, 0)), key = ('column_tpers_y', i), visible = True)])  
            else:
                self.current_input_tpers.append(None)
                self.alt_input_tpers.append(None)
                self.orig_input_tpers.append(None)
                self.final_input_is_original_tpers.append(None) #True = is Original Input Format or 'False' = Final Input is Alternative Input Format
                
                self.hyperlink_list_tpers.append(None) #List for Hyperlinks for NDB
                self.current_hyperlink_list_tpers.append(None)
                self.current_hyperlink_tpers.append(None)       
                ndb_thema_persons_suggest.insert(i, None)   

                         

        column_1.append([sg.Column(column_tpers, pad = ((0, 0), (10, 0)), key = ('column_tpers'), visible = True)])

        column_1.append([sg.Button('', image_data=add_data_item_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, pad = ((40, 0), (20, 0)), key=('add_data_tpers'))])
        
        self.eventlist_tpers = [] 
        
        for i in range(len(input_list_tpers)):
            self.eventlist_tpers.append(('Play_File_tpers', i))

        self.eventlist_tpers_stop_file = []       

        for j in range(len(input_list_tpers)):
            self.eventlist_tpers_stop_file.append(('Stop_File_tpers', j))

        #ThemaOrt hinzufügen
        column_1.append([sg.Text('Thema-Ort korrigieren', pad=(5, (50, 10)), background_color = 'black', font=('Arial Bold', 20))])
        column_torte = []
        self.current_input_torte = []
        self.alt_input_torte = []
        self.orig_input_torte = []
        self.final_input_is_original_torte = []
        self.torte_count_original = len(torte_list_llm_original)
        self.hyperlink_list_torte = [] #List for Hyperlinks for NDB
        self.current_hyperlink_list_torte = [] #List for hyperlinks that are currentyl shown and active
        self.current_hyperlink_torte = []
        for i in range(len(torte_list_llm_original)):
            print('DEBUG EInzeleintrag themaORte:', torte_list_llm_original[i])

            #Get Timecodes for audioplayer
            audio_starts = find_audio_timecodes().find_word_in_transcript(torte_list_llm_original[i], transcripts_list, start_sorted)
            
            column_1_x = []
            column_1_y = []
            
            column_1_x.append(
                    sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_torte', i), tooltip='Delete this item'))

            if len(input_list_torte[i][0])==0: #Wenn beim NDB-Abgleich nichts gefunden wurde
                column_1_x.append(
                    sg.Input(default_text = torte_list_llm_original[i], size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_torte", i)))

                column_1_x.append(
                    sg.Combo([], size=(100, 1), font=('Arial Bold', 10), default_value = '', expand_x=False, enable_events=True, visible = False, readonly=False, auto_size_text = True, key=("input_torte_alt", i))) #unsichtbarer Input, der aktiviert wird, wenn nach Änderung desTextes doch noch Treffer in NDB gefunden werden.
                
                #Show Hyperlink next to Column - Hidden!
                column_1_x.append(sg.Text('', enable_events=True, font=('Arial Bold', 10), key=('URL_torte', i), visible = False, text_color = 'blue', background_color = 'white'))

                self.current_input_torte.append('Freitext')
                self.alt_input_torte.append(False)
                self.orig_input_torte.append('Freitext')
                self.final_input_is_original_torte.append(True)
                self.current_hyperlink_list_torte.append(None)
                self.current_hyperlink_torte.append(None)   
                self.hyperlink_list_torte.append(None)

            else: #Wenn beim NDB-Abgleich etwas gefunden wurde
                print('DEBUG TORTE2:', i)
                list_to_show = []
                for n in range(len(input_list_torte[i][0])):
                    string_shown = f'{input_list_torte[i][1][n]} | {input_list_torte[i][2][n]} | {input_list_torte[i][4][n]} | {input_list_torte[i][6][n]} | {input_list_torte[i][3][n]}'
                    
                    list_to_show.append(string_shown)

                #Add single Hyperlink-Liste to complete Hyperlinks List
                self.hyperlink_list_torte.append(input_list_torte[i][3])

                column_1_x.append(
                    sg.Combo(list_to_show, size=(100, 1), font=('Arial Bold', 10), default_value = list_to_show[0], expand_x=False, enable_events=True,  readonly=False, key=("input_torte", i)))

                column_1_x.append(#Unsichtbarer alternativer Input, der  ggf. aktiviert wird unten
                        sg.Input(default_text = torte_list_llm_original[i], size=(25, 1), enable_events=True, visible = False, key=("input_torte_alt", i)))

                #Show Hyperlink next to Column
                column_1_x.append(sg.Text(self.hyperlink_list_torte[i][0], enable_events=True, font=('Arial Bold', 10), text_color = 'blue', key=('URL_torte', i), background_color = 'white')) 

                #Add viewable Hyperlink of NDB-Entry
                self.current_hyperlink_list_torte.append(self.hyperlink_list_torte[i])
                self.current_hyperlink_torte.append(self.hyperlink_list_torte[i][n])

                self.current_input_torte.append('Dropdown')
                self.alt_input_torte.append(False)
                self.orig_input_torte.append('Dropdown')
                self.final_input_is_original_torte.append(True)

            column_1_y.append(#Refresh-NDB-Ergebnis-Button hinzufügen
                sg.Button('', image_data=refresh_ndb_button,
                        button_color=(sg.theme_background_color(),sg.theme_background_color()),
                        border_width=0, pad = ((40, 0), (0, 0)), key=('refresh_ndb_torte', i)))
                
            column_1_y.append(#Umwandlung Freitext-Feld Button einfügen
                sg.Button('', image_data=change_input_type_button,
                    button_color=(sg.theme_background_color(),sg.theme_background_color()),
                    border_width=0, visible = True, key=('change_input_type_torte', i)))
            
            if self.hyperlink_list_torte[i] != None:
                if self.hyperlink_list_torte[i][0] != None and len(self.hyperlink_list_torte[i][0]) == 0:
                    column_1_y.append(
                        sg.Button('', image_data=look_for_name_in_transcript_button,
                            button_color=(sg.theme_background_color(),sg.theme_background_color()),
                            border_width=0, visible = True, key=('look_for_name_in_transcript_torte', i)))
                else:
                    column_1_y.append(
                        sg.Button('', image_data=look_for_name_in_transcript_button,
                            button_color=(sg.theme_background_color(),sg.theme_background_color()),
                            border_width=0, visible = False, key=('look_for_name_in_transcript_torte', i)))
            else:
                column_1_y.append(
                    sg.Button('', image_data=look_for_name_in_transcript_button,
                        button_color=(sg.theme_background_color(),sg.theme_background_color()),
                        border_width=0, visible = False, key=('look_for_name_in_transcript_torte', i)))

            if len(audio_starts[0]) >0:
                column_1_y.append(
                    sg.Combo(audio_starts[0], size=(10, 1), font=('Arial Bold', 10), default_value = audio_starts[0][0], expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_torte', i)))
                column_1_y.append(
                    sg.Button("Play", key=('Play_File_torte', i)))
                column_1_y.append(
                    sg.Button("Stop", key=('Stop_File_torte', i)))
            
            else:
                column_1_y.append(
                    sg.Text('Not', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('audio_starter_torte', i)))
                column_1_y.append(
                    sg.Text('Found', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('Play_File_torte', i)))
                column_1_y.append(
                    sg.Text('in Audio Transcript', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('Stop_File_torte', i)))
            column_1_y.append(
                sg.Text(description_list_torte[i], font=('Arial Bold', 10), expand_x=False, justification='left', key=('description_torte', i))
                    )
            
            #column_1_x.append(sg.Column([column_1_xa], pad = ((0, 0), (10, 0)), key = ('column_torte_x', i), visible = True))
            #column_1_x.append(sg.Column([column_1_xb], pad = ((0, 0), (10, 0)), key = ('column_torte_x', i), visible = True)) 

            column_torte.append([sg.Column([column_1_x], pad = ((0, 0), (10, 0)), key = ('column_torte_x', i), visible = True)])
            column_torte.append([sg.Column([column_1_y], pad = ((0, 0), (0, 0)), key = ('column_torte_y', i), visible = True)])                            

        column_1.append([sg.Column(column_torte, pad = ((0, 0), (10, 0)), key = ('column_torte'), visible = True)])
        column_1.append([sg.Button('', image_data=add_data_item_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, pad = ((40, 0), (20, 0)), key=('add_data_torte'))])

        self.eventlist_torte = [] 
        
        for i in range(len(input_list_torte)):
            self.eventlist_torte.append(('Play_File_torte', i))

        self.eventlist_torte_stop_file = []       

        for j in range(len(input_list_torte)):
            self.eventlist_torte_stop_file.append(('Stop_File_torte', j))
        
        #ThemaInstitutionen hinzufügen
        #Instututionen entpacken
        input_list_tinst_ndb = tinst_suggest_bundle[0]
        description_list_tinst = tinst_suggest_bundle[1]
        tinst_list_llm_original = tinst_suggest_bundle[2]

        #Main Institutionen
        column_1.append([sg.Text('Thema-Institution korrigieren', pad=(5, (50, 10)), background_color = 'black', font=('Arial Bold', 20))])
        column_tinst = []
        self.current_input_tinst = []
        self.alt_input_tinst = []
        self.orig_input_tinst = []
        self.final_input_is_original_tinst = []
        self.tinst_count_original = len(tinst_list_llm_original)
        self.hyperlink_list_tinst = [] #List for Hyperlinks for NDB
        self.current_hyperlink_list_tinst = [] #List for hyperlinks that are currentyl shown and active
        self.current_hyperlink_tinst = []

        for i in range(len(tinst_list_llm_original)):
            #Get Timecodes for audioplayer
            audio_starts = find_audio_timecodes().find_word_in_transcript(tinst_list_llm_original[i], transcripts_list, start_sorted)
            
            column_1_x = []
            column_1_y = []
            column_1_x.append(
                    sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_tinst', i), tooltip='Delete this item'))
            
            if len(input_list_tinst_ndb[i][0])==0: #Wenn beim NDB-Abgleich nichts gefunden wurde
                column_1_x.append(
                        sg.Input(default_text = tinst_list_llm_original[i], size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_tinst", i)))

                column_1_x.append(
                    sg.Combo([], size=(100, 1), font=('Arial Bold', 10), default_value = '', expand_x=False, enable_events=True, visible = False, readonly=False, auto_size_text = True, key=("input_tinst_alt", i))) #unsichtbarer Input, der aktiviert wird, wenn nach Änderung desTextes doch noch Treffer in NDB gefunden werden.
                
                #Show Hyperlink next to Column - Hidden!
                column_1_x.append(sg.Text('', enable_events=True, font=('Arial Bold', 10), key=('URL_tinst', i), visible = False, text_color = 'blue', background_color = 'white'))

                self.current_input_tinst.append('Freitext')
                self.alt_input_tinst.append(False)
                self.orig_input_tinst.append('Freitext')
                self.final_input_is_original_tinst.append(True)
                self.current_hyperlink_list_tinst.append(None)
                self.current_hyperlink_tinst.append(None)   
                self.hyperlink_list_tinst.append(None)

            else: #Wenn beim NDB-Abgleich etwas gefunden wurde
                list_to_show = []
                for n in range(len(input_list_tinst_ndb[i][0])):
                    string_shown = f'{input_list_tinst_ndb[i][1][n]} | {input_list_tinst_ndb[i][2][n]} | {input_list_tinst_ndb[i][3][n]} | {input_list_tinst_ndb[i][4][n]} | {input_list_tinst_ndb[i][5][n]}'
                    
                    list_to_show.append(string_shown)

                #Add single Hyperlink-Liste to complete Hyperlinks List
                self.hyperlink_list_tinst.append(input_list_tinst_ndb[i][5])

                column_1_x.append(
                    sg.Combo(list_to_show, size=(100, 1), font=('Arial Bold', 10), default_value = list_to_show[0], expand_x=False, enable_events=True,  readonly=False, key=("input_tinst", i)))

                column_1_x.append(#Unsichtbarer alternativer Input, der  ggf. aktiviert wird unten
                        sg.Input(default_text = tinst_list_llm_original[i], size=(25, 1), enable_events=True, visible = False, key=("input_tinst_alt", i)))
                
                #Show Hyperlink next to Column
                column_1_x.append(sg.Text(self.hyperlink_list_tinst[i][0], enable_events=True, font=('Arial Bold', 10), text_color = 'blue', key=('URL_tinst', i), background_color = 'white'))
                
                #Add viewable Hyperlink of NDB-Entry
                self.current_hyperlink_list_tinst.append(self.hyperlink_list_tinst[i])
                self.current_hyperlink_tinst.append(self.hyperlink_list_tinst[i][n])

                self.current_input_tinst.append('Dropdown')
                self.alt_input_tinst.append(False)
                self.orig_input_tinst.append('Dropdown')
                self.final_input_is_original_tinst.append(True)

            column_1_y.append(#Refresh-NDB-Ergebnis-Button hinzufügen
                sg.Button('', image_data=refresh_ndb_button,
                        button_color=(sg.theme_background_color(),sg.theme_background_color()),
                        border_width=0, pad = ((40, 0), (0, 0)), key=('refresh_ndb_tinst', i)))
                
            column_1_y.append(#Umwandlung Freitext-Feld Button einfügen
            sg.Button('', image_data=change_input_type_button,
                    button_color=(sg.theme_background_color(),sg.theme_background_color()),
                    border_width=0, visible = True, key=('change_input_type_tinst', i)))
            
            if len(input_list_tinst_ndb[i][0])==0:    
                column_1_y.append(
                    sg.Button('', image_data=look_for_name_in_transcript_button,
                            button_color=(sg.theme_background_color(),sg.theme_background_color()),
                            border_width=0, visible = True, key=('look_for_name_in_transcript_tinst',i)))
            else:
                column_1_y.append(
                    sg.Button('', image_data=look_for_name_in_transcript_button,
                            button_color=(sg.theme_background_color(),sg.theme_background_color()),
                            border_width=0, visible = False, key=('look_for_name_in_transcript_tinst',i)))

            if len(audio_starts[0]) >0:
                column_1_y.append(
                    sg.Combo(audio_starts[0], size=(10, 1), font=('Arial Bold', 10), default_value = audio_starts[0][0], expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_tinst', i)))
                column_1_y.append(
                    sg.Button("Play", key=('Play_File_tinst', i)))
                column_1_y.append(
                    sg.Button("Stop", key=('Stop_File_tinst', i)))
            
            else:
                column_1_y.append(
                    sg.Text('Not', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('audio_starter_tinst', i)))
                column_1_y.append(
                    sg.Text('Found', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('Play_File_tinst', i)))
                column_1_y.append(
                    sg.Text('in Audio Transcript', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('Stop_File_tinst', i)))
            column_1_y.append(
                sg.Text(description_list_tinst[i], font=('Arial Bold', 10), expand_x=False, justification='left', key=('description_tinst', i))
                )
            
            #column_1_x.append(sg.Column([column_1_xa], pad = ((0, 0), (10, 0)), key = ('column_tinst_x', i), visible = True))
            #column_1_x.append(sg.Column([column_1_xb], pad = ((0, 0), (10, 0)), key = ('column_tinst_x', i), visible = True))

            column_tinst.append([sg.Column([column_1_x], pad = ((0, 0), (10, 0)), key = ('column_tinst_x', i), visible = True)])
            column_tinst.append([sg.Column([column_1_y], pad = ((0, 0), (0, 0)), key = ('column_tinst_y', i), visible = True)])   
                                    

        column_1.append([sg.Column(column_tinst, pad = ((0, 0), (10, 0)), key = ('column_tinst'), visible = True)])
        column_1.append([sg.Button('', image_data=add_data_item_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, pad = ((40, 0), (20, 0)), key=('add_data_tinst'))])

        self.eventlist_tinst = [] 
        
        for i in range(len(input_list_tinst_ndb)):
            self.eventlist_tinst.append(('Play_File_tinst', i))

        self.eventlist_tinst_stop_file = []       

        for j in range(len(input_list_tinst_ndb)):
            self.eventlist_tinst_stop_file.append(('Stop_File_tinst', j))

        #ThemaEreignis hinzufügen
        datelists = self.make_day_month_year_lists()
        #Ereignisse entpacken
        tereignis_list_llm_original = tereignis_suggest_bundle[0]
        description_list_tereignis = tereignis_suggest_bundle[1]
        tereignis_list_tage = tereignis_suggest_bundle[2]
        tereignis_list_monate = tereignis_suggest_bundle[3]
        tereignis_list_jahre = tereignis_suggest_bundle[4]
        tereignis_list_tage_ende = tereignis_suggest_bundle[5]
        tereignis_list_monate_ende = tereignis_suggest_bundle[6]
        tereignis_list_jahre_ende = tereignis_suggest_bundle[7]

        self.final_input_is_original_tereignis = []

        #Main Ereignis
        column_1.append([sg.Text('Thema-Ereignis korrigieren', pad=(5, (50, 10)), background_color = 'black', font=('Arial Bold', 20))])
        column_tereignis = []
        
        for i in range(len(tereignis_list_llm_original)):
            #Get Timecodes for audioplayer
            audio_starts = find_audio_timecodes().find_word_in_transcript(tereignis_list_llm_original[i], transcripts_list, start_sorted)
            self.final_input_is_original_tereignis.append(True)
            column_1_x = []
            column_1_y = []
            column_1_x.append(
                    sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_tereignis', i), tooltip='Delete this item'))

            column_1_x.append(
                sg.Input(default_text = tereignis_list_llm_original[i], size=(100, 1), enable_events=True, readonly=False, visible = True, key=("input_tereignis", i)))
            
            column_1_x.append(sg.Text('Datum: ', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('tereignis_datum_text', i)))
            
            column_1_x.append(
                    sg.Combo(datelists[0], size=(5, 1), font=('Arial Bold', 10), default_value = tereignis_list_tage[i], expand_x=False, enable_events=True, readonly=False, key=("input_tereignis_tage", i)))

            column_1_x.append(
                    sg.Combo(datelists[1], size=(5, 1), font=('Arial Bold', 10), default_value = tereignis_list_monate[i], expand_x=False, enable_events=True, readonly=False, key=("input_tereignis_monate", i)))
            
            column_1_x.append(
                    sg.Combo(datelists[2], size=(10, 1), font=('Arial Bold', 10), default_value = tereignis_list_jahre[i], expand_x=False, enable_events=True, readonly=False, key=("input_tereignis_jahre", i)))
            
            column_1_x.append(sg.Text(' bis ', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('tereignis_datum_text_bis', i)))

            column_1_x.append(
                    sg.Combo(datelists[0], size=(5, 1), font=('Arial Bold', 10), default_value = tereignis_list_tage_ende[i], expand_x=False, enable_events=True, readonly=False, key=("input_tereignis_tage_ende", i)))

            column_1_x.append(
                    sg.Combo(datelists[1], size=(5, 1), font=('Arial Bold', 10), default_value = tereignis_list_monate_ende[i], expand_x=False, enable_events=True, readonly=False, key=("input_tereignis_monate_ende", i)))
            
            column_1_x.append(
                    sg.Combo(datelists[2], size=(10, 1), font=('Arial Bold', 10), default_value = tereignis_list_jahre_ende[i], expand_x=False, enable_events=True, readonly=False, key=("input_tereignis_jahre_ende", i)))
            
            column_1_y.append(
                sg.Button('', image_data=look_for_name_in_transcript_button,
                button_color=(sg.theme_background_color(),sg.theme_background_color()),
                border_width=0, visible = True, pad = ((40, 0), (0, 0)), key=('look_for_name_in_transcript_tereignis',i)))


            if len(audio_starts[0]) >0:
                column_1_y.append(
                    sg.Combo(audio_starts[0], size=(10, 1), font=('Arial Bold', 10), default_value = audio_starts[0][0], expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_tereignis', i)))
                column_1_y.append(
                    sg.Button("Play", key=('Play_File_tereignis', i)))
                column_1_y.append(
                    sg.Button("Stop", key=('Stop_File_tereignis', i)))
            
            else:
                column_1_y.append(
                    sg.Combo('', size=(10, 1), font=('Arial Bold', 10), default_value = '', expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_tereignis', i), visible = False))
                column_1_y.append(
                    sg.Button("Play", key=('Play_File_tereignis', i), visible = False))
                column_1_y.append(
                    sg.Button("Stop", key=('Stop_File_tereignis', i), visible = False))
            column_1_y.append(
                sg.Text(description_list_tereignis[i], font=('Arial Bold', 10), expand_x=False, justification='left', key=('description_tereignis', i))
                )

            column_tereignis.append([sg.Column([column_1_x], pad = ((0, 0), (10, 0)), key = ('column_tereignis_x', i), visible = True)])
            column_tereignis.append([sg.Column([column_1_y], pad = ((0, 0), (0, 0)), key = ('column_tereignis_y', i), visible = True)])   
                                    

        column_1.append([sg.Column(column_tereignis, pad = ((0, 0), (10, 0)), key = ('column_tereignis'), visible = True)])
        column_1.append([sg.Button('', image_data=add_data_item_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, pad = ((40, 0), (20, 0)), key=('add_data_tereignis'))])

        self.eventlist_tereignis = [] 
        
        for i in range(len(tereignis_list_llm_original)):
            self.eventlist_tereignis.append(('Play_File_tereignis', i))

        self.eventlist_tereignis_stop_file = []       

        for j in range(len(tereignis_list_llm_original)):
            self.eventlist_tereignis_stop_file.append(('Stop_File_tereignis', j))

        #Realisierungsdatum hinzufügen
        datelists = self.make_day_month_year_lists()
        #Ereignisse entpacken
        try:
            realisierung_tage = realisierung_datum_suggest[0]
            realisierung_monate = realisierung_datum_suggest[1]
            realisierung_jahre = realisierung_datum_suggest[2]
            realisierung_zusatz = realisierung_datum_suggest[3]
            realisierung_ende_tage = realisierung_datum_suggest[4]
            realisierung_ende_monate = realisierung_datum_suggest[5]
            realisierung_ende_jahre = realisierung_datum_suggest[6]
            realisierung_ende_zusatz = realisierung_datum_suggest[7]
            realisierung_datum_kontext = realisierung_datum_suggest[8]
        except IndexError:
            realisierung_tage = None
            realisierung_monate = None
            realisierung_jahre = None
            realisierung_zusatz = None
            realisierung_ende_tage = None
            realisierung_ende_monate = None
            realisierung_ende_jahre = None
            realisierung_ende_zusatz = None
            realisierung_datum_kontext = None

        self.final_input_is_original_realisierung_datum = None

        #Main Ereignis
        column_1.append([sg.Text('Realisierung Datum korrigieren', pad=(5, (50, 10)), background_color = 'black', font=('Arial Bold', 20))])
        column_realdatum = []
        
        column_1_x = []
        column_1_y = []

        column_1_x.append(
            sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_realdatum'), tooltip='Delete this item'))

        column_1_x.append(
            sg.Combo([None, 'circa', 'exakt', 'nach', 'vor'], size=(10, 1), font=('Arial Bold', 10), default_value = realisierung_zusatz, expand_x=False, enable_events=True, readonly=False, key=("input_realdatum_zusatz")))

        column_1_x.append(
            sg.Combo(datelists[0], size=(5, 1), font=('Arial Bold', 10), default_value = realisierung_tage, expand_x=False, enable_events=True, readonly=False, key=("input_realdatum_tage")))

        column_1_x.append(
            sg.Combo(datelists[1], size=(5, 1), font=('Arial Bold', 10), default_value = realisierung_monate, expand_x=False, enable_events=True, readonly=False, key=("input_realdatum_monate")))
            
        column_1_x.append(
            sg.Combo(datelists[2], size=(10, 1), font=('Arial Bold', 10), default_value = realisierung_jahre, expand_x=False, enable_events=True, readonly=False, key=("input_realdatum_jahre")))
            
        column_1_x.append(sg.Text(' bis ', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('realdatum_text_bis')))

        column_1_x.append(
            sg.Combo([None, 'circa', 'exakt', 'nach', 'vor'], size=(10, 1), font=('Arial Bold', 10), default_value = realisierung_ende_zusatz, expand_x=False, enable_events=True, readonly=False, key=("realdatum_ende_zusatz")))

        column_1_x.append(
            sg.Combo(datelists[0], size=(5, 1), font=('Arial Bold', 10), default_value = realisierung_ende_tage, expand_x=False, enable_events=True, readonly=False, key=("realdatum_tage_ende")))

        column_1_x.append(
            sg.Combo(datelists[1], size=(5, 1), font=('Arial Bold', 10), default_value = realisierung_ende_monate, expand_x=False, enable_events=True, readonly=False, key=("realdatum_monate_ende")))
            
        column_1_x.append(
            sg.Combo(datelists[2], size=(10, 1), font=('Arial Bold', 10), default_value = realisierung_ende_jahre, expand_x=False, enable_events=True, readonly=False, key=("realdatum_jahre_ende")))
        
        column_1_y.append(
                sg.Multiline(default_text=realisierung_datum_kontext, size=(100, 3), write_only=True, key=('description_realdatum', i))
                )


        column_realdatum.append([sg.Column([column_1_x, column_1_y], pad = ((10, 0), (10, 0)), key = ('column_realdatum_x'), visible = True)])
                                    

        column_1.append([sg.Column(column_realdatum, pad = ((0, 0), (10, 0)), key = ('column_realdatum'), visible = True)])

        #Realisierung Ort hinzufügen
        column_1.append([sg.Text('Realisierung Ort korrigieren', pad=(5, (50, 10)), background_color = 'black', font=('Arial Bold', 20))])
        column_realort = []

        
        for r in range(len(realisierung_ort_suggest)):
            column_1_x = []
            column_1_y = []
            if realisierung_ort_suggest[r] != None:
                #Get Timecodes for audioplayer
                audio_starts = find_audio_timecodes().find_word_in_transcript(realisierung_ort_suggest[r], transcripts_list, start_sorted)
                
                column_1_x.append(
                    sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_realort', r), tooltip='Delete this item'))
                column_1_x.append(
                        sg.Input(default_text = realisierung_ort_suggest[r], size=(25, 1), enable_events=True, readonly=False, visible = True, key=("realort", r)))
                column_1_x.append(
                        sg.Text(realisierung_ort_kontext[r], font=('Arial Bold', 10), expand_x=False, justification='left', key=('realisierung_kontext', r)))
                column_1_y.append(
                        sg.Button('', image_data=look_for_name_in_transcript_button,
                        button_color=(sg.theme_background_color(),sg.theme_background_color()),
                        border_width=0, visible = True, key=('look_for_name_in_transcript_realort', r)))
                if len(audio_starts[0]) >0:
                    column_1_y.append(
                        sg.Combo(audio_starts[0], size=(10, 1), font=('Arial Bold', 10), default_value = audio_starts[0][0], expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_realort', r)))
                    column_1_y.append(
                        sg.Button("Play", key=('Play_File_realort', r)))
                    column_1_y.append(
                        sg.Button("Stop", key=('Stop_File_realort', r)))
                    
                else:
                    column_1_y.append(
                        sg.Text('Not', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('audio_starter_realort', r)))
                    column_1_y.append(
                        sg.Text('Found', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('Play_File_realort', r)))
                    column_1_y.append(
                        sg.Text('in Audio Transcript', font=('Arial Bold', 10), background_color = 'black', expand_x=False, justification='left', key=('Stop_File_realort', r)))
                
            column_realort.append([sg.Column([column_1_x], pad = ((0, 0), (10, 0)), key = ('column_realort_x', r), visible = True)])
            column_realort.append([sg.Column([column_1_y], pad = ((0, 0), (10, 0)), key = ('column_realort_y', r), visible = True)])

        column_1.append([sg.Column(column_realort, pad = ((0, 0), (10, 0)), key = ('column_realort'), visible = True)])

        column_1.append([sg.Button('', image_data=add_data_item_button,
                    button_color=(sg.theme_background_color(),sg.theme_background_color()),
                    border_width=0, pad = ((40, 0), (20, 0)), key=('add_data_realort'))])

        self.eventlist_realort = [] 
        
        for i in range(len(realisierung_ort_suggest)):
            self.eventlist_realort.append(('Play_File_realort', i))

        self.eventlist_realort_stop_file = []       

        for j in range(len(realisierung_ort_suggest)):
            self.eventlist_realort_stop_file.append(('Stop_File_realort', j))
        
        #Realisierung Typ hinzufügen
        column_1.append([sg.Text('Realisierung Typ korrigieren', pad=(5, (50, 10)), background_color = 'black', font=('Arial Bold', 20))])
        column_realtyp = []
        
        column_1_x = []
        list_realtyp_auswahl = ['None', 'unbekannt', 'Mitschnitt / Sendemitschnitt', 'Studioproduktion', 'Live-Aufnahme', 'Live mit Beifall', 'Live ohne Beifall']
        column_1_x.append(
            sg.Combo(list_realtyp_auswahl, size=(25, 1), font=('Arial Bold', 10), default_value = realisierung_typ_suggest, expand_x=False, enable_events=True,  readonly=False, key=('realtyp')))
        
        column_realtyp.append([sg.Column([column_1_x], pad = ((0, 0), (10, 0)), key = ('column_realtyp_x'), visible = True)])
                                    
        column_1.append([sg.Column(column_realtyp, pad = ((0, 0), (10, 0)), key = ('column_realtyp'), visible = True)])

        #Sprachen hinzufügen
        
        #Main Sprachen
        column_1.append([sg.Text('Sprachen korrigieren', pad=(5, (50, 10)), background_color = 'black', font=('Arial Bold', 20))])
        column_sprachen = []
        self.current_input_sprachen = []
        self.alt_input_sprachen = []
        self.orig_input_sprachen = []
        self.final_input_is_original_sprachen = []
        self.sprachen_count_original = len(sprachen_suggest_original)
        
        for i in range(len(sprachen_suggest_original)):
            column_1_x = []
            column_1_y = []
            column_1_x.append(
                    sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_sprachen', i), tooltip='Delete this item'))
            
            if len(sprachen_suggest_ndb[i][0])==0: #Wenn beim NDB-Abgleich nichts gefunden wurde
                column_1_x.append(
                        sg.Input(default_text = sprachen_suggest_original[i], size=(25, 1), enable_events=True, readonly=False, visible = True, key=("input_sprachen", i)))

                column_1_x.append(
                    sg.Combo([], size=(100, 1), font=('Arial Bold', 10), default_value = '', expand_x=False, enable_events=True, visible = False, readonly=False, auto_size_text = True, key=("input_sprachen_alt", i))) #unsichtbarer Input, der aktiviert wird, wenn nach Änderung desTextes doch noch Treffer in NDB gefunden werden.
                self.current_input_sprachen.append('Freitext')
                self.alt_input_sprachen.append(False)
                self.orig_input_sprachen.append('Freitext')
                self.final_input_is_original_sprachen.append(True)

            else: #Wenn beim NDB-Abgleich etwas gefunden wurde
                list_to_show = []
                print('DEBUG SPRACHEN:', sprachen_suggest_ndb)
                for n in range(len(sprachen_suggest_ndb[i][0])):
                    string_shown = f'{sprachen_suggest_ndb[i][1][n]} | {sprachen_suggest_ndb[i][2][n]} | {sprachen_suggest_ndb[i][3][n]} | {sprachen_suggest_ndb[i][4][n]} | {sprachen_suggest_ndb[i][0][n]}'
                    
                    list_to_show.append(string_shown)

                column_1_x.append(
                    sg.Combo(list_to_show, size=(100, 1), font=('Arial Bold', 10), default_value = list_to_show[0], expand_x=False, enable_events=True,  readonly=False, key=("input_sprachen", i)))

                column_1_x.append(#Unsichtbarer alternativer Input, der  ggf. aktiviert wird unten
                        sg.Input(default_text = sprachen_suggest_original[i], size=(25, 1), enable_events=True, visible = False, key=("input_sprachen_alt", i)))

                self.current_input_sprachen.append('Dropdown')
                self.alt_input_sprachen.append(False)
                self.orig_input_sprachen.append('Dropdown')
                self.final_input_is_original_sprachen.append(True)

            column_1_y.append(#Refresh-NDB-Ergebnis-Button hinzufügen
                sg.Button('', image_data=refresh_ndb_button,
                        button_color=(sg.theme_background_color(),sg.theme_background_color()),
                        border_width=0, pad = ((40, 0), (0, 0)), key=('refresh_ndb_sprachen', i)))
                
            column_1_y.append(#Umwandlung Freitext-Feld Button einfügen
            sg.Button('', image_data=change_input_type_button,
                    button_color=(sg.theme_background_color(),sg.theme_background_color()),
                    border_width=0, visible = True, key=('change_input_type_sprachen', i)))


            column_sprachen.append([sg.Column([column_1_x], pad = ((0, 0), (10, 0)), key = ('column_sprachen_x', i), visible = True)])
            column_sprachen.append([sg.Column([column_1_y], pad = ((0, 0), (0, 0)), key = ('column_sprachen_y', i), visible = True)])   
                                    

        column_1.append([sg.Column(column_sprachen, pad = ((0, 0), (10, 0)), key = ('column_sprachen'), visible = True)])
        column_1.append([sg.Button('', image_data=add_data_item_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, pad = ((40, 0), (20, 0)), key=('add_data_sprachen'))])

        #Despriptoren hinzufügen
        #Deskriptoren entpacken
        print('DEBUG Deskriptoren:', deskriptoren_suggest)
        #Main Deskriptoren
        column_1.append([sg.Text('Deskriptor korrigieren', pad=(5, (50, 10)), background_color = 'black', font=('Arial Bold', 20))])
        column_desk = []
        self.current_input_desk = []
        self.alt_input_desk = []
        self.orig_input_desk = []
        self.final_input_is_original_desk = []
        self.desk_count_original = len(deskriptoren_suggest)
        self.text_input_transcr_search_desk = []
        self.deskriptoren_all_data = []

        for i in range(len(deskriptoren_suggest)):
            #Get Timecodes for audioplayer
            print('DEBUG BEGRIFF SUGGEST:', deskriptoren_suggest[i])
            self.deskriptoren_all_data.append(deskriptoren_suggest[i])
            audio_starts = find_audio_timecodes().find_word_in_transcript(deskriptoren_suggest[i][0][0], transcripts_list, start_sorted)
            self.text_input_transcr_search_desk.append(deskriptoren_suggest[i][0][0])
            
            column_1_x = []
            column_1_y = []
            column_1_x.append(
                    sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_desk', i), tooltip='Delete this item'))
            
            #In diesem Fall gibt es die Unterscheidung "Es wurde etwas in der NDB gefunden und es wurde nichts in der NDB gefunden nicht, da es keine Deskriptoren ohne NDB EIntrag geben darf.
            list_to_show = []
            if len(deskriptoren_suggest[i][3]) == 0 and deskriptoren_suggest[i][6][0] == 'Freie Sachdeskriptoren':
                string_shown_main_data = f'{deskriptoren_suggest[i][0][0]} | {deskriptoren_suggest[i][1][0]} | {deskriptoren_suggest[i][6][0]} | ACHTUNG! Freier Sachdeskriptor ohne zugeordnete Klasse. Über  Plus-Symbol unten Klasse hinzufügen!'
                self.current_input_desk.append('zugeordnete_klasse_keine')
                self.orig_input_desk.append('zugeordnete_klasse_keine')

            elif len(deskriptoren_suggest[i][3]) == 0 and deskriptoren_suggest[i][6][0] != 'Freie Sachdeskriptoren':
                string_shown_main_data = f'{deskriptoren_suggest[i][0][0]} | {deskriptoren_suggest[i][1][0]} | {deskriptoren_suggest[i][6][0]}'
                self.current_input_desk.append('zugeordnete_klasse_keine')
                self.orig_input_desk.append('zugeordnete_klasse_keine')
                           
            elif len(deskriptoren_suggest[i][3]) >1:
                string_shown_main_data = f'{deskriptoren_suggest[i][0][0]} | {deskriptoren_suggest[i][1][0]} | {deskriptoren_suggest[i][6][0]}'
                self.current_input_desk.append('zugeordnete_klasse_flex')
                self.orig_input_desk.append('zugeordnete_klasse_flex')
                
            elif len(deskriptoren_suggest[i][3]) == 1:
                string_shown_main_data = f'{deskriptoren_suggest[i][0][0]} | {deskriptoren_suggest[i][1][0]} | {deskriptoren_suggest[i][6][0]} | zugeordnete Klassen: {deskriptoren_suggest[i][3][0]}/{deskriptoren_suggest[i][4][0]}'
                self.current_input_desk.append('zugeordnete_klasse_fix')
                self.orig_input_desk.append('zugeordnete_klasse_fix')

            column_1_x.append(
                sg.Text(string_shown_main_data, enable_events=True, font=('Arial Bold', 10), text_color = 'blue', key=('input_desk', i), background_color = 'white'))

            column_1_x.append(#Unsichtbarer alternativer Input, der  ggf. aktiviert wird unten
                    sg.Input(default_text = deskriptoren_suggest[i][0], size=(25, 1), enable_events=True, visible = False, key=("input_desk_alt", i)))
                
            if len(deskriptoren_suggest[i][3]) > 1:
                list_to_show = []
                print(deskriptoren_suggest[i][3])
                column_1_x.append(
                sg.Text('Zugeordnete Klasse auswählen:', enable_events=True, font=('Arial Bold', 10), text_color = 'blue', key=('hinweis_desk_klassen', i), background_color = 'white'))
                for n in range(len(deskriptoren_suggest[i][4])):
                    string_shown = f'{deskriptoren_suggest[i][3][n]} | {deskriptoren_suggest[i][4][n]}'
                    list_to_show.append(string_shown)
                
                column_1_x.append(
                    sg.Combo(list_to_show, size=(50, 1), font=('Arial Bold', 10), default_value = list_to_show[0], expand_x=False, enable_events=True, visible = True, readonly=False, auto_size_text = True, key=("input_desk_klasse_chooser", i))) 
                
            else:
                column_1_x.append(
                    sg.Text('Zugeordnete Klasse auswählen:', enable_events=True, font=('Arial Bold', 10), text_color = 'blue', key=('hinweis_desk_klassen', i), visible = False, background_color = 'white'))
                column_1_x.append(
                    sg.Combo(list_to_show, size=(100, 1), font=('Arial Bold', 10), default_value = '', expand_x=False, enable_events=True, visible = False, readonly=False, auto_size_text = True, key=("input_desk_klasse_chooser", i))) 

            
            self.alt_input_desk.append(False)
            
            self.final_input_is_original_desk.append(True)
            column_1_y.append(
                sg.Button('', image_data=look_for_name_in_transcript_button,
                button_color=(sg.theme_background_color(),sg.theme_background_color()),
                border_width=0, visible = True, pad = ((40, 0), (0, 0)), key=('look_for_name_in_transcript_desk', i)))

            column_1_y.append(#Refresh-NDB-Ergebnis-Button hinzufügen
                sg.Button('', image_data=refresh_ndb_button,
                        button_color=(sg.theme_background_color(),sg.theme_background_color()),
                        border_width=0, pad = ((5, 0), (0, 0)), key=('refresh_ndb_desk', i)))
                
            column_1_y.append(#Umwandlung Freitext-Feld Button einfügen
            sg.Button('', image_data=change_input_type_button,
                    button_color=(sg.theme_background_color(),sg.theme_background_color()),
                    border_width=0, visible = True, key=('change_input_type_desk', i)))

            if len(audio_starts[0]) >0:
                column_1_y.append(
                    sg.Combo(audio_starts[0], size=(10, 1), font=('Arial Bold', 10), default_value = audio_starts[0][0], expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_desk', i)))
                column_1_y.append(
                    sg.Button("Play", key=('Play_File_desk', i)))
                column_1_y.append(
                    sg.Button("Stop", key=('Stop_File_desk', i)))
            
            else:
                column_1_y.append(
                    sg.Combo(audio_starts[0], size=(10, 1), font=('Arial Bold', 10), default_value = '', visible = False, expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_desk', i)))
                
                column_1_y.append(
                    sg.Button("Play", key=('Play_File_desk', i), visible = False))
                column_1_y.append(
                    sg.Button("Stop", key=('Stop_File_desk', i), visible = False,))
            
            #column_1_x.append(sg.Column([column_1_xa], pad = ((0, 0), (10, 0)), key = ('column_tinst_x', i), visible = True))
            #column_1_x.append(sg.Column([column_1_xb], pad = ((0, 0), (10, 0)), key = ('column_tinst_x', i), visible = True))

            column_desk.append([sg.Column([column_1_x], pad = ((0, 0), (10, 0)), key = ('column_desk_x', i), visible = True)])
            column_desk.append([sg.Column([column_1_y], pad = ((0, 0), (0, 0)), key = ('column_desk_y', i), visible = True)])   
                                    

        column_1.append([sg.Column(column_desk, pad = ((0, 0), (10, 0)), key = ('column_desk'), visible = True)])
        column_1.append([sg.Button('', image_data=add_data_item_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, pad = ((40, 0), (20, 0)), key=('add_data_desk'))])
        
        self.eventlist_desk = [] 
        
        for i in range(len(deskriptoren_suggest)):
            self.eventlist_desk.append(('Play_File_desk', i))

        self.eventlist_desk_stop_file = []       

        for j in range(len(deskriptoren_suggest)):
            self.eventlist_desk_stop_file.append(('Stop_File_desk', j))

        #Metatags
        tags_llm_original = metatags_suggest
        self.final_input_is_original_tags = []

        #Main Metatags
        column_1.append([sg.Text('Metatags korrigieren', pad=(5, (50, 10)), background_color = 'black', font=('Arial Bold', 20))])
        column_tags = []
        
        for i in range(len(tags_llm_original)):
            #Get Timecodes for audioplayer
            audio_starts = find_audio_timecodes().find_word_in_transcript(tags_llm_original[i], transcripts_list, start_sorted)
            self.final_input_is_original_tags.append(True)
            column_1_x = []
            column_1_y = []
            column_1_x.append(
                    sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_tags', i), tooltip='Delete this item'))

            column_1_x.append(
                sg.Input(default_text = tags_llm_original[i], size=(100, 1), enable_events=True, readonly=False, visible = True, key=("input_tags", i)))
            
            column_1_y.append(
                sg.Button('', image_data=look_for_name_in_transcript_button,
                button_color=(sg.theme_background_color(),sg.theme_background_color()),
                border_width=0, visible = True, pad = ((40, 0), (0, 0)), key=('look_for_name_in_transcript_tags',i)))

            if len(audio_starts[0]) >0:
                column_1_y.append(
                    sg.Combo(audio_starts[0], size=(10, 1), font=('Arial Bold', 10), default_value = audio_starts[0][0], expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_tags', i)))
                column_1_y.append(
                    sg.Button("Play", key=('Play_File_tags', i)))
                column_1_y.append(
                    sg.Button("Stop", key=('Stop_File_tags', i)))
            
            else:
                column_1_y.append(
                    sg.Combo('', size=(10, 1), font=('Arial Bold', 10), default_value = '', expand_x=False, enable_events=True,  readonly=False, key=('audio_starter_tags', i), visible = False))
                column_1_y.append(
                    sg.Button("Play", key=('Play_File_tags', i), visible = False))
                column_1_y.append(
                    sg.Button("Stop", key=('Stop_File_tags', i), visible = False))

            column_tags.append([sg.Column([column_1_x], pad = ((0, 0), (10, 0)), key = ('column_tags_x', i), visible = True)])
            column_tags.append([sg.Column([column_1_y], pad = ((0, 0), (0, 0)), key = ('column_tags_y', i), visible = True)])   
                                    

        column_1.append([sg.Column(column_tags, pad = ((0, 0), (10, 0)), key = ('column_tags'), visible = True)])
        column_1.append([sg.Button('', image_data=add_data_item_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, pad = ((40, 0), (20, 0)), key=('add_data_tags'))])

        self.eventlist_tags = [] 
        
        for i in range(len(tags_llm_original)):
            self.eventlist_tags.append(('Play_File_tags', i))

        self.eventlist_tags_stop_file = []       

        for j in range(len(tags_llm_original)):
            self.eventlist_tags_stop_file.append(('Stop_File_tags', j))

        #Gattungen bearbeiten
        column_1.append([sg.Text('Gattung Audio korrigieren', pad=(5, (50, 10)), background_color = 'black', font=('Arial Bold', 20))])
        column_gattungen = []
        for i in range(len(gattungen_suggest)):
            column_gattungen.append(
                [sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-_gatt', i), tooltip='Delete this item'),
                sg.Combo(list(self.list_gattungen), size=(25, 1), font=('Arial Bold', 10), default_value = list(gattungen_suggest)[i], expand_x=False, enable_events=True,  readonly=False, key=('combo_gattungen', i))])
        column_gattungen = ([sg.Column(column_gattungen, pad = ((0, 0), (10, 0)), key = ('column_gattung'), visible = True)])
        column_1.append(column_gattungen)
        column_1.append([sg.Button('', image_data=add_data_item_button,
            button_color=(sg.theme_background_color(),sg.theme_background_color()),
            border_width=0, pad = ((40, 0), (20, 0)), key=('add_data_gattungen'))])

        #Genre bearbeiten
        list_genre = ['Wort', 'Musik', 'Wort / Musik']
        column_1.append([sg.Text('Genre korrigieren', pad=(5, (50, 10)), background_color = 'black', font=('Arial Bold', 20))])
        column_1.append([
                sg.Combo(list(list_genre), size=(25, 1), font=('Arial Bold', 10), default_value = genre_suggest, expand_x=False, enable_events=True,  readonly=False, key=('combo_genre'))])
        
        #Konf-Audio-Setting that could not entirely be automated
        audioton_suggest = audioraum_darstellung_global_suggest#get_audioraumdarstellung(f'{audiofiles_path}\\{original_file}')

        #Get list of Audioraumdarstellungen from excel list
        df = pandas.read_excel('Excel_Lists_entities\\audioraumdarstellung_norm_ids.xlsx')
        list_langbez = df['langbez']
        #list_kurzbez = df['kurzbez']
        #list_norm_ids = df['norm_id']

        column_1.append([sg.Text('Audioeigenschaften Audiofile korrigieren', pad=(5, (50, 10)), background_color = 'black', font=('Arial Bold', 20))])
        column_1.append(
            [sg.Combo(list(list_langbez), size=(25, 1), font=('Arial Bold', 10), default_value = audioton_suggest, expand_x=False, enable_events=True,  readonly=False, key=('combo_audioton'))])

        #Lese- und Abspielgeschwindigkeit bearbeiten
        column_1.append([sg.Text('Lese- und Abspielgeschwindigkeit eintragen (Nicht KI generiert)', pad=(5, (50, 10)), background_color = 'black', font=('Arial Bold', 20))])
        column_1.append(
            [sg.Combo(list(list_langleseabspielgeschwindigkeit), size=(25, 1), font=('Arial Bold', 10), default_value = 'Kein Eintrag', expand_x=False, enable_events=True,  readonly=False, key=('combo_lese_abspiel'))])
    
        #Audioplayer init Gesamtfile
        audioplayer1 = audio_playback(f'{audiofiles_path}\\{original_file}')
        heading = [sg.Text('Play File', pad=(5, (50, 10)), background_color = 'black', font=('Arial Bold', 20))]
        player_line = [sg.Button("Play", key='Play_File'), sg.Button("Pause", key='Pause_File'), sg.Button("Stop", key='Stop_File')] #, sg.Button("Resume", key='Resume_File')
        slider = [sg.Slider((0, audioplayer1.get_duration()), orientation='horizontal', key='-SL-', enable_events=True, disable_number_display = True), sg.Text(audioplayer1.format_time(0), background_color = 'black', font=('Arial Bold', 20), key='current_time')]
        
        column_1.append(heading)
        column_1.append(player_line)
        column_1.append(slider)
        

        #Audioplayer init Speech Only File
        audioplayer2 = audio_playback(audiofile)
        #column_1.append(heading)
        #column_1.append([sg.Column([column_player1], pad = ((0, 0), (10, 0)), key = ('column_search_player_1'), visible = True)])
        #column_1.append([sg.Column([column_player2], pad = ((0, 0), (10, 0)), key = ('column_search_player_1'), visible = True)])
        #column_1.append([sg.Column([column_player3], pad = ((0, 0), (10, 0)), key = ('column_search_player_1'), visible = True)])
        
        #Add to HFDB Buttons   
        column_1.append([
            sg.Button("In HFDB übernehmen", key='-OK-', size=(20, 2), button_color=('white', 'green')),
            sg.Button("Nicht in HFDB übernehmen", key='hfdb_nein', size=(20, 2), button_color=('white', 'orange')),
            sg.Button("Prozess abbrechen", key='Cancel', size=(20, 2), button_color=('white', 'red'))
        ])
        
        list_lines.append([sg.Column(column_1, scrollable=False, expand_x=True, expand_y=True)])
        list_master.append([sg.Column(list_lines, scrollable=True, expand_x=True, expand_y=True, key='column_1')])
        #Add to HFDB Buttons   
        list_buttons = []
        list_buttons.append([
            sg.Button("In HFDB übernehmen", key='-OK-', size=(20, 2), button_color=('white', 'green')),
            sg.Button("Nicht in HFDB übernehmen", key='hfdb_nein', size=(20, 2), button_color=('white', 'orange')),
            sg.Button("Prozess abbrechen", key='Cancel', size=(20, 2), button_color=('white', 'red'))
        ])
        list_master.append([sg.Column(list_buttons, scrollable=False, expand_x=True, expand_y=True)])
        layout = list_master
        print(layout)
    
        """# Add to HFDB Buttons
        button_layout = [
            sg.Button("In HFDB übernehmen", key='-OK-', size=(20, 2), button_color=('white', 'green')),
            sg.Button("Nicht in HFDB übernehmen", key='hfdb_nein', size=(20, 2), button_color=('white', 'orange')),
            sg.Button("Prozess abbrechen", key='Cancel', size=(20, 2), button_color=('white', 'red'))
        ]
        list_lines.append([sg.Column(column_1, scrollable=True, expand_x=True, expand_y=True)])
        list_lines.append([sg.Column([button_layout], justification='center', element_justification='center', pad=(0, 20))])

        layout = list_lines
        print(layout)"""

        # Create the Window
        return (sg.Window('AK Daten Korrekturfenster', layout, size=(1100, 1000), resizable=True, finalize = True), audioplayer1, audioplayer2)

    def ak_correction_menu(self, transcripts_list, start_sorted, input_list_urheber, description_list_urheber, roles_found_urheber, reference_roles_list_urheber, ndb_urheber_data, input_list_mitwirkende, description_list_mitwirkende, roles_found_mitwirkende, reference_roles_list_mitwirkende, ndb_mitwirkende_data, text_input_titel, zusammenfassung, input_list_tpers, description_list_tpers, ndb_thema_persons_suggest, input_list_torte, description_list_torte, torte_list_llm_original, tinst_suggest_bundle, tereignis_suggest_bundle, audiofiles_path, audiofile, original_file, gattungen_suggest, genre_suggest, sprachen_suggest_original, sprachen_suggest_ndb, metatags_suggest, deskriptoren_suggest, audioraum_darstellung_global_suggest, realisierung_datum_suggest, realisierung_orte_suggest, realisierung_ort_kontext, realisierung_typ_suggest):
        """Wrapper for activating and "playing" UI-AK-Menue and handling interactive elements. Has same inputs as main_window and passes them through to it
        
        Main Window Element which contains the standard elements shown when UI-Window appears. Real appearence is flexible and depends on the amount and kind of input data but general structure is always the same.
        
        Args:
            transcripts_list(list): List of transcript parts. Contains whole transcript but devided in parts for combining it with timecodes for audio player.
            start_sorted(list): List of timecodes that define where transcript part from transcript_list starts within the audio-
            input_list_urheber(list): LLM-Suggestions on Urheber
            description_list_urheber(list): Descriptions on single persons from input_list_urheber, coming from LLM
            roles_found_urheber(list): Roles defined for input_list_urheber by LLM  from reference_roles_list_urheber list
            reference_roles_list_urheber(list): List of possible roles that Urheber can have.
            ndb_urheber_data(list): NDB-Suggestions on Urheber based on input_list_urheber as input for NDB search
            input_list_mitwirkende(list): LLM Suggestions on Mitwirkende
            description_list_mitwirkende(list): List of descriptions for Mitwirkende on input_list_mitwirkende generated  by LLM.
            roles_found_mitwirkende(list): Roles defined for input_list_mitwirkende by LLM from reference_roles_list_mitwirkende list
            reference_roles_list_mitwirkende(list): List of possible roles that Mitwirkender can have.
            ndb_mitwirkende_data(list): NDB-Suggestions on Mitwirkender based on input_list_mitwirkende as input for NDB search
            text_input_titel(str): Title for AK entry suggested by LLM
            zusammenfassung(str): Summary for AK entry suggested by LLM
            input_list_tpers(list): List of LLM Suggestions for themaPerson
            description_list_tpers(list): LLM-generated descriptions for persons from input_list_tpers.
            ndb_thema_persons_suggest(list): NDB Suggests for themaPersonen based on input_list_tpers as input for NDB search
            input_list_torte(list): List of LLM Suggestions for themaOrt
            description_list_torte(list): LLM-generated descriptions for Orte from input_list_torte.
            torte_list_llm_original(list): Original unfiltered Orte Output from LLM
            tinst_suggest_bundle(list): LLM suggests for themaInstitution
            tereignis_suggest_bundle(list): LLM suggests for themaEreignis
            audiofiles_path(str): Path to folder where speech only audiofiles are stored.
            audiofile(str): Filename of speech only audiofile
            original_file(str): Path to original input file
            gattungen_suggest(list): List of suggested Gattungen for dataset
            genre_suggest(list): List of suggested Genres for dataset
            sprachen_suggest_original(list): List of LLM-suggested Languages for Dataset
            sprachen_suggest_ndb(list): NDB-Suggests for Languages based on prachen_suggest_original
            metatags_suggest(list): List of suggested Metatags
            deskriptoren_suggest(list): List of suggested Deskriptoren
            audioraum_darstellung_global_suggest(json_like): User-Pre-defined suggestion for Audioraumdarstellung
            realisierung_datum_suggest(json_like): LLM-Suggestions for Realisierungsdatum
            realisierung_orte_suggest(list): Suggestions forRealisierung-Orte
            realisierung_ort_kontext(list): Context for Realisierung Orte Suggestions from transcript

        Returns:
            list_final_entities_mitwirkende(list): List of Mitwirkende data after correction through interface.
            list_final_entities_tpers(list): List of themaPersonen data after correction through interface
            zusammenfassung_korrigiert(str): Corrected summary
            titel_korrigiert(str): Corrected title
            list_final_entities_torte(list): List of ThemaOrte data after correction through interface by user
            list_final_entities_gattungen(list): List of Gattungen data after correction through interface by user
            konf_audio_gattungen_korrigiert(str): Value for Audioraumdarstellung as set or corrected by the user through interface
            genre_korrigiert(str): Value for Genre as corrected  and  checked by the user through interface.
            lese_abspielgeschwindigkeit(str): Value for Lese- und Abspielgeschwindigkeit as possibly corrected by user through interface.
            list_final_entities_urheber(list): List of Urheber data after correction through interface by user
            list_final_entities_tinst(list): List of Institutionen data after correction through interface by user
            list_final_entities_tereignis(list): List of ThemaEreignis data after correction through interface by user
            list_final_entities_sprachen(list): List of Sprachen data after correction through interface by user
            list_final_entities_desk(list): List of Deskriptoren data after correction through interface by user
            list_final_entities_tags(list): List of (Meta-)Tags data after correction through interface by user
            list_final_entities_realisierungsdatum(list): List of contents of Realisierungsdatum
            list_final_entities_realisierung_orte(str): String with Realisierung Orte
        
        """
        #List of numbers of lines that are flagged for erase so details not kept for ak creation
        erase_flagged_mitwirkende = []
        erase_flagged_urheber = []
        erase_flagged_tpers = []
        erase_flagged_torte = []
        erase_flagged_gatt = []
        erase_flagged_genre = []
        erase_flagged_tinst = []
        erase_flagged_tereignis = []
        erase_flagged_sprachen = []
        erase_flagged_desk = []
        erase_flagged_tags = []
        erase_flagged_realdatum = False
        erase_flagged_realorte = []

        window1 = self.main_window(transcripts_list, start_sorted, input_list_urheber, description_list_urheber, roles_found_urheber, reference_roles_list_urheber, ndb_urheber_data, input_list_mitwirkende, description_list_mitwirkende, roles_found_mitwirkende, reference_roles_list_mitwirkende, ndb_mitwirkende_data, text_input_titel, zusammenfassung, input_list_tpers, description_list_tpers, ndb_thema_persons_suggest, input_list_torte, description_list_torte, torte_list_llm_original, tinst_suggest_bundle, tereignis_suggest_bundle,audiofiles_path, audiofile, original_file, gattungen_suggest, genre_suggest, sprachen_suggest_original, sprachen_suggest_ndb, metatags_suggest, deskriptoren_suggest, audioraum_darstellung_global_suggest, realisierung_datum_suggest, realisierung_orte_suggest, realisierung_ort_kontext, realisierung_typ_suggest)
        audioplayer1 = window1[1]
        audioplayer2 = window1[2]
        window = window1[0]
        #Institutionen entpacken
        input_list_tinst_ndb = tinst_suggest_bundle[0]
        description_list_tinst = tinst_suggest_bundle[1]
        tinst_list_llm_original = tinst_suggest_bundle[2]

        #Ereignisse entpacken
        tereignis_list_llm_original = tereignis_suggest_bundle[0]
        description_list_tereignis = tereignis_suggest_bundle[1]
        tereignis_list_tage = tereignis_suggest_bundle[2]
        tereignis_list_monate = tereignis_suggest_bundle[3]
        tereignis_list_jahre = tereignis_suggest_bundle[4]
        tereignis_list_tage_ende = tereignis_suggest_bundle[5]
        tereignis_list_monate_ende = tereignis_suggest_bundle[6]
        tereignis_list_jahre_ende = tereignis_suggest_bundle[7]
        
        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            
            window, event, values = sg.read_all_windows(timeout = 10000000)
            popup_open_search = False
            if event == sg.WIN_CLOSED or event == "Cancel":
                window.close()
                break
            if event == '-OK-': 
                #event_popup = 'close_me'
                values_passed = values
                audioplayer1.stop_playback()
                try:    
                    window.close()
                except:
                    ()            
                try:
                    window_popup_karin.close()
                except:
                    ()
                try:
                    window_popup_audioplayer.close()
                except:
                    ()
                break

            if event == 'add_data_mitwirkende':
                new_columns = self.empty_column_mitwirkende(input_list_mitwirkende, reference_roles_list_mitwirkende)
                window.extend_layout(window['column_mitwirk'], [new_columns[0]])
                window.extend_layout(window['column_mitwirk'], [new_columns[1]])
                input_list_mitwirkende.append('None')
                description_list_mitwirkende.append('None')
                ndb_mitwirkende_data.append(['','','','','','','',''])
                self.current_input.append('Freitext')
                self.alt_input.append(False)
                self.orig_input.append('Freitext')
                self.final_input_is_original.append(True)
                self.hyperlink_list_mitwirkende.append(None)  
                self.current_hyperlink_list_mitwirkende.append(None)
                self.current_hyperlink_mitwirkende.append(None)
                window.refresh()
                window['column_1'].contents_changed()

            if event == 'add_data_urheber':
                new_columns = self.empty_column_urheber(input_list_urheber, reference_roles_list_urheber)
                window.extend_layout(window['column_urheber'], [new_columns[0]])
                window.extend_layout(window['column_urheber'], [new_columns[1]])
                input_list_urheber.append('None')
                description_list_urheber.append('None')
                ndb_urheber_data.append(['','','','','','','',''])
                self.current_input_urheber.append('Freitext')
                self.alt_input_urheber.append(False)
                self.orig_input_urheber.append('Freitext')
                self.final_input_is_original_urheber.append(True)
                self.hyperlink_list_urheber.append(None)  
                self.current_hyperlink_list_urheber.append(None)
                self.current_hyperlink_urheber.append(None)
                window.refresh()
                window['column_1'].contents_changed()
                
            if event == 'add_data_tpers':
                new_columns = self.empty_column_tpers(input_list_tpers)
                window.extend_layout(window['column_tpers'], [new_columns[0]])
                window.extend_layout(window['column_tpers'], [new_columns[1]])
                input_list_tpers.append('None')
                description_list_tpers.append('None')
                ndb_thema_persons_suggest.append(['','','','','','','',''])
                self.current_input_tpers.append('Freitext')
                self.alt_input_tpers.append(False)
                self.orig_input_tpers.append('Freitext')
                self.final_input_is_original_tpers.append(True)  
                self.hyperlink_list_tpers.append(None)  
                self.current_hyperlink_list_tpers.append(None)
                self.current_hyperlink_tpers.append(None)  
                window.refresh()
                window['column_1'].contents_changed()

            if event == 'add_data_torte':
                new_columns = self.empty_column_torte(torte_list_llm_original)
                window.extend_layout(window['column_torte'], [new_columns[0]])
                window.extend_layout(window['column_torte'], [new_columns[1]])
                torte_list_llm_original.append('None')
                description_list_torte.append('None')
                input_list_torte.append('')
                self.current_input_torte.append('Freitext')
                self.alt_input_torte.append(False)
                self.orig_input_torte.append('Freitext')
                self.final_input_is_original_torte.append(True) 
                self.hyperlink_list_torte.append(None)  
                self.current_hyperlink_list_torte.append(None)
                self.current_hyperlink_torte.append(None)  
                window.refresh()
                window['column_1'].contents_changed()

            if event == 'add_data_tinst':
                new_columns = self.empty_column_tinst(tinst_list_llm_original)
                window.extend_layout(window['column_tinst'], [new_columns[0]])
                window.extend_layout(window['column_tinst'], [new_columns[1]])
                tinst_list_llm_original.append('None')
                description_list_tinst.append('None')
                input_list_tinst_ndb.append('')
                self.current_input_tinst.append('Freitext')
                self.alt_input_tinst.append(False)
                self.orig_input_tinst.append('Freitext')
                self.final_input_is_original_tinst.append(True) 
                self.hyperlink_list_tinst.append(None)  
                self.current_hyperlink_list_tinst.append(None)
                self.current_hyperlink_tinst.append(None)
                window.refresh()
                window['column_1'].contents_changed()

            if event == 'add_data_tereignis':
                new_columns = self.empty_column_tereignis(tereignis_list_llm_original)
                window.extend_layout(window['column_tereignis'], [new_columns[0]])
                window.extend_layout(window['column_tereignis'], [new_columns[1]])
                tereignis_list_llm_original.append('None')
                description_list_tereignis.append('None')
                tereignis_list_tage.append(1)
                tereignis_list_monate.append(1)
                tereignis_list_jahre.append(1950)
                tereignis_list_tage_ende.append(1)
                tereignis_list_monate_ende.append(1)
                tereignis_list_jahre_ende.append(1950)
                self.final_input_is_original_tereignis.append(True) 
                window.refresh()
                window['column_1'].contents_changed()

            if event == 'add_data_sprachen':
                new_columns = self.empty_column_sprachen(sprachen_suggest_original)
                window.extend_layout(window['column_sprachen'], [new_columns[0]])
                window.extend_layout(window['column_sprachen'], [new_columns[1]])
                sprachen_suggest_original.append('None')
                sprachen_suggest_ndb.append('')
                self.current_input_sprachen.append('Freitext')
                self.alt_input_sprachen.append(False)
                self.orig_input_sprachen.append('Freitext')
                self.final_input_is_original_sprachen.append(True) 
                window.refresh()
                window['column_1'].contents_changed()

            if event == 'add_data_realort':
                new_columns = self.empty_column_realort(realisierung_orte_suggest)
                window.extend_layout(window['column_realort'], [new_columns[0]])
                window.extend_layout(window['column_realort'], [new_columns[1]])
                realisierung_orte_suggest.append('')
                window.refresh()
                window['column_1'].contents_changed()

            if event == 'add_data_desk':
                new_columns = self.empty_column_desk(deskriptoren_suggest)
                window.extend_layout(window['column_desk'], [new_columns[0]])
                window.extend_layout(window['column_desk'], [new_columns[1]])
                deskriptoren_suggest.append('None')
                self.current_input_desk.append('Freitext')
                self.alt_input_desk.append(False)
                self.orig_input_desk.append('Freitext')
                self.final_input_is_original_desk.append(True)
                self.text_input_transcr_search_desk.append('')
                self.deskriptoren_all_data.append(None)
                window.refresh()
                window['column_1'].contents_changed()

            if event == 'add_data_tags':
                new_columns = self.empty_column_tags(metatags_suggest)
                window.extend_layout(window['column_tags'], [new_columns[0]])
                window.extend_layout(window['column_tags'], [new_columns[1]])
                metatags_suggest.append('None')
                self.final_input_is_original_tags.append(True)   
                window.refresh()
                window['column_1'].contents_changed()

            if event == 'add_data_gattungen':
                gattungen_list = self.list_gattungen
                new_columns = self.empty_column_gattung(gattungen_suggest, gattungen_list)
                window.extend_layout(window['column_gattung'], [new_columns])
                gattungen_suggest.append('None')
                window.refresh()
                window['column_1'].contents_changed()

            #Verschieben von Personen in andere Personenkategorie
            #Verschieben von Mitwirkende zu Urheber
            if event != None and event[0] == 'verschieb_mitwirkende_urheber':
                input_list_urheber.append(input_list_mitwirkende[event[1]])
                ndb_urheber_data.append(ndb_mitwirkende_data[event[1]])
                self.hyperlink_list_urheber.append(ndb_mitwirkende_data[event[1]][5])
                description_list_urheber.append(description_list_mitwirkende[event[1]])
                self.alt_input_urheber.append(self.alt_input[event[1]])
                self.orig_input_urheber.append(self.orig_input[event[1]])
                self.final_input_is_original_urheber.append(self.final_input_is_original[event[1]])
                self.hyperlink_list_urheber.append(self.hyperlink_list_mitwirkende[event[1]])  
                self.current_hyperlink_list_urheber.append(self.current_hyperlink_list_mitwirkende[event[1]])
                self.current_hyperlink_urheber.append(self.current_hyperlink_mitwirkende[event[1]])
                self.current_input_urheber.append(self.current_input[event[1]])

                print('DEBUG LIST URHEBER INPUT:', input_list_urheber)

                if self.current_input_urheber[-1] == 'Freitext':
                    is_combo_new = False
                    default_input_freitext = input_list_urheber[len(input_list_urheber)-1]
                    default_input_combo = []
                    hyperlink_to_show = ''
                else:
                    is_combo_new = True
                    list_to_show = []
                    
                    for n in range(len(ndb_urheber_data[len(ndb_urheber_data)-1][0])):
                        string_shown = f'{ndb_urheber_data[len(ndb_urheber_data)-1][3][n]} | {ndb_urheber_data[len(ndb_urheber_data)-1][2][n]} | {ndb_urheber_data[len(ndb_urheber_data)-1][4][n]} | {ndb_urheber_data[len(ndb_urheber_data)-1][6][n]} | {ndb_urheber_data[len(ndb_urheber_data)-1][7][n]} | {(ndb_urheber_data[len(ndb_urheber_data)-1][5][n])}'
                        list_to_show.append(string_shown)

                    default_input_freitext = input_list_urheber[-1]
                    default_input_combo = list_to_show
                    hyperlink_to_show = ndb_urheber_data[-1][5][0]
                
                audio_starts_new = find_audio_timecodes().find_word_in_transcript(input_list_urheber[-1], transcripts_list, start_sorted)
                print('DEBUG DESCRIPTION LIST URHEBER:', description_list_urheber)
                print('DEBUG DESCRIPTION LIST URHEBER NUMBER:', description_list_urheber[-1])

                new_columns = self.empty_column_urheber(input_list_urheber[:-1], reference_roles_list_urheber, is_combo = is_combo_new, default_input_freitext = default_input_freitext, default_input_combo = default_input_combo, description_person = description_list_urheber[-1], audio_starter_list = audio_starts_new[0], default_hyperlink_to_show = hyperlink_to_show) #input_urheber muss bis zum vorletzten Eintrag gehen, weil sonst die Zählung der UI-Elemente-Trigger-Werte nicht passt.
                window.extend_layout(window['column_urheber'], [new_columns[0]])
                window.extend_layout(window['column_urheber'], [new_columns[1]])
                
                #Erase Data from Mitwirkende
                window[('-DEL-_mitwirkende', event[1])].update(visible=False)
                window[('input_mitwirkende', event[1])].update(visible=False)
                window[('input_mitwirkende_vorname', event[1])].update(visible=False)
                window[('input_mitwirkende_nachname', event[1])].update(visible=False)
                window[('combo_mitwirkende', event[1])].update(visible=False)
                window[('description_mitwirkende', event[1])].update(visible=False)
                window[('Play_File_mitwirkende',event[1])].update(visible=False)
                window[('Stop_File_mitwirkende', event[1])].update(visible=False)
                window[('audio_starter_mitwirkende', event[1])].update(visible=False)
                window[(f'refresh_ndb_mitwirkende', event[1])].update(visible=False)
                window[('change_input_type_mitwirk', event[1])].update(visible = False)
                window[('URL_mitwirkende', event[1])].update(visible = False)
                window[('verschieb_mitwirkende_urheber', event[1])].update(visible = False)
                window[('verschieb_mitwirkende_themapers', event[1])].update(visible = False)
                window[("bemerkung_mitwirkende_text", event[1])].update(visible = False)
                window[("bemerkung_mitwirkende", event[1])].update(visible = False)
                
                try:
                    window[('look_for_name_in_transcript', event[1])].update(visible = False)
                except:
                    pass
                
                erase_flagged_mitwirkende.append(int(event[1]))   
                window.refresh()
                window['column_1'].contents_changed()                  

            #Verschieben von Mitwirkende zu themaPersonen
            if event != None and event[0] == 'verschieb_mitwirkende_themapers':
                input_list_tpers.append(input_list_mitwirkende[event[1]])
                (ndb_mitwirkende_data[event[1]])
                self.hyperlink_list_tpers.append(ndb_mitwirkende_data[event[1]][5])
                description_list_tpers.append(description_list_mitwirkende[event[1]])
                self.alt_input_tpers.append(self.alt_input[event[1]])
                self.orig_input_tpers.append(self.orig_input[event[1]])
                self.final_input_is_original_tpers.append(self.final_input_is_original[event[1]])
                self.hyperlink_list_tpers.append(self.hyperlink_list_mitwirkende[event[1]])  
                self.current_hyperlink_list_tpers.append(self.current_hyperlink_list_mitwirkende[event[1]])
                self.current_hyperlink_tpers.append(self.current_hyperlink_mitwirkende[event[1]])
                self.current_input_tpers.append(self.current_input[event[1]])

                if self.current_input_tpers[-1] == 'Freitext':
                    is_combo_new = False
                    default_input_freitext = input_list_tpers[-1]
                    default_input_combo = []
                    hyperlink_to_show = ''
                
                else:
                    is_combo_new = True
                    list_to_show = []
                    
                    for n in range(len(ndb_thema_persons_suggest[len(ndb_thema_persons_suggest)-1][0])):
                        string_shown = f'{ndb_thema_persons_suggest[-1][3][n]} | {ndb_thema_persons_suggest[-1][2][n]} | {ndb_thema_persons_suggest[-1][4][n]} | {ndb_thema_persons_suggest[-1][6][n]} | {ndb_thema_persons_suggest[-1][7][n]} | {(ndb_thema_persons_suggest[-1][5][n])}'
                        list_to_show.append(string_shown)

                    default_input_freitext = input_list_tpers[-1]
                    default_input_combo = list_to_show
                    hyperlink_to_show = ndb_thema_persons_suggest[-1][5][0]
                
                audio_starts_new = find_audio_timecodes().find_word_in_transcript(input_list_tpers[-1], transcripts_list, start_sorted)
               
                new_columns = self.empty_column_tpers(input_list_tpers[:-1], is_combo = is_combo_new, default_input_freitext = default_input_freitext, default_input_combo = default_input_combo, description_person = description_list_tpers[-1], audio_starter_list = audio_starts_new[0], default_hyperlink_to_show = hyperlink_to_show) #input_urheber muss bis zum vorletzten Eintrag gehen, weil sonst die Zählung der UI-Elemente-Trigger-Werte nicht passt.
                window.extend_layout(window['column_tpers'], [new_columns[0]])
                window.extend_layout(window['column_tpers'], [new_columns[1]])
                
                #Erase Data from Mitwirkende
                window[('-DEL-_mitwirkende', event[1])].update(visible=False)
                window[('input_mitwirkende', event[1])].update(visible=False)
                window[('input_mitwirkende_vorname', event[1])].update(visible=False)
                window[('input_mitwirkende_nachname', event[1])].update(visible=False)
                window[('combo_mitwirkende', event[1])].update(visible=False)
                window[('description_mitwirkende', event[1])].update(visible=False)
                window[('Play_File_mitwirkende',event[1])].update(visible=False)
                window[('Stop_File_mitwirkende', event[1])].update(visible=False)
                window[('audio_starter_mitwirkende', event[1])].update(visible=False)
                window[(f'refresh_ndb_mitwirkende', event[1])].update(visible=False)
                window[('change_input_type_mitwirk', event[1])].update(visible = False)
                window[('URL_mitwirkende', event[1])].update(visible = False)
                window[('verschieb_mitwirkende_urheber', event[1])].update(visible = False)
                window[('verschieb_mitwirkende_themapers', event[1])].update(visible = False)
                window[('verschieb_mitwirkende_themapers', event[1])].update(visible = False)
                window[("bemerkung_mitwirkende_text", event[1])].update(visible = False)
                window[("bemerkung_mitwirkende", event[1])].update(visible = False)
                try:
                    window[('look_for_name_in_transcript', event[1])].update(visible = False)
                except:
                    pass
                
                erase_flagged_mitwirkende.append(int(event[1])) 
                window.refresh()
                window['column_1'].contents_changed()

            #Verschieben von themaPersonen zu Mitwirkende
            if event != None and event[0] == 'verschieb_themapers_mitwirkende':
                input_list_mitwirkende.append(input_list_tpers[event[1]])
                ndb_mitwirkende_data.append(ndb_thema_persons_suggest[event[1]])
                self.hyperlink_list_mitwirkende.append(ndb_thema_persons_suggest[event[1]][5])
                description_list_mitwirkende.append(description_list_tpers[event[1]])
                self.alt_input.append(self.alt_input_tpers[event[1]])
                self.orig_input.append(self.orig_input_tpers[event[1]])
                self.final_input_is_original.append(self.final_input_is_original_tpers[event[1]])
                self.hyperlink_list_mitwirkende.append(self.hyperlink_list_tpers[event[1]])  
                self.current_hyperlink_list_mitwirkende.append(self.current_hyperlink_list_tpers[event[1]])
                self.current_hyperlink_mitwirkende.append(self.current_hyperlink_tpers[event[1]])
                self.current_input.append(self.current_input_tpers[event[1]])

                if self.current_input[-1] == 'Freitext':
                    is_combo_new = False
                    default_input_freitext = input_list_mitwirkende[-1]
                    default_input_combo = []
                    
                    hyperlink_to_show = ''
                else:
                    is_combo_new = True
                    list_to_show = []
                    
                    for n in range(len(ndb_mitwirkende_data[-1][0])):
                        string_shown = f'{ndb_mitwirkende_data[-1][3][n]} | {ndb_mitwirkende_data[-1][2][n]} | {ndb_mitwirkende_data[-1][4][n]} | {ndb_mitwirkende_data[-1][6][n]} | {ndb_mitwirkende_data[-1][7][n]} | {(ndb_mitwirkende_data[-1][5][n])}'
                        list_to_show.append(string_shown)


                    default_input_freitext = input_list_mitwirkende[-1]
                    default_input_combo = list_to_show
                   
                    print('DEBUG Mitwirkende:', ndb_mitwirkende_data)
                    hyperlink_to_show = ndb_mitwirkende_data[-1][5][0]
                
                audio_starts_new = find_audio_timecodes().find_word_in_transcript(input_list_tpers[-1], transcripts_list, start_sorted)
               
                new_columns = self.empty_column_mitwirkende(input_list_mitwirkende[:-1],reference_roles_list_mitwirkende, is_combo = is_combo_new, default_input_freitext = default_input_freitext, default_input_combo = default_input_combo, description_person = description_list_tpers[-1], audio_starter_list = audio_starts_new[0], default_hyperlink_to_show = hyperlink_to_show) #input_mitwirkende muss bis zum vorletzten Eintrag gehen, weil sonst die Zählung der UI-Elemente-Trigger-Werte nicht passt.
                window.extend_layout(window['column_mitwirk'], [new_columns[0]])
                window.extend_layout(window['column_mitwirk'], [new_columns[1]])
                
                #Erase Data from ThemaPersonen
                window[('-DEL-_tpers', event[1])].update(visible=False)
                window[('input_tpers', event[1])].update(visible=False)
                window[('input_tpers_vorname', event[1])].update(visible=False)
                window[('input_tpers_nachname', event[1])].update(visible=False)
                window[('description_tpers', event[1])].update(visible=False)
                window[('Play_File_tpers',event[1])].update(visible=False)
                window[('Stop_File_tpers', event[1])].update(visible=False)
                window[('audio_starter_tpers', event[1])].update(visible=False)
               
                window[(f'refresh_ndb_tpers', event[1])].update(visible=False)
                window[('change_input_type_tpers', event[1])].update(visible = False)
                window[('URL_tpers', event[1])].update(visible = False)
                window[('verschieb_themapers_urheber', event[1])].update(visible = False)
                window[('verschieb_themapers_mitwirkende', event[1])].update(visible = False)
                try:
                    window[('look_for_name_in_transcript_tpers', event[1])].update(visible = False)
                except:
                    pass
                
                erase_flagged_tpers.append(int(event[1])) 
                window.refresh()
                window['column_1'].contents_changed()

            #Verschieben von ThemaPersonen zu Urheber
            if event != None and event[0] == 'verschieb_themapers_urheber':
                input_list_urheber.append(input_list_tpers[event[1]])
                ndb_urheber_data.append(ndb_thema_persons_suggest[event[1]])
                self.hyperlink_list_urheber.append(ndb_thema_persons_suggest[event[1]][5])
                description_list_urheber.append(description_list_tpers[event[1]])
                self.alt_input_urheber.append(self.alt_input_tpers[event[1]])
                self.orig_input_urheber.append(self.orig_input_tpers[event[1]])
                self.final_input_is_original_urheber.append(self.final_input_is_original_tpers[event[1]])
                self.hyperlink_list_urheber.append(self.hyperlink_list_tpers[event[1]])  
                self.current_hyperlink_list_urheber.append(self.current_hyperlink_list_tpers[event[1]])
                self.current_hyperlink_urheber.append(self.current_hyperlink_tpers[event[1]])
                self.current_input_urheber.append(self.current_input_tpers[event[1]])

                if self.current_input_urheber[-1] == 'Freitext':
                    is_combo_new = False
                    default_input_freitext = input_list_urheber[len(input_list_urheber)-1]
                    default_input_combo = []
                    
                    hyperlink_to_show = ''
                else:
                    is_combo_new = True
                    list_to_show = []
                    
                    for n in range(len(ndb_urheber_data[len(ndb_urheber_data)-1][0])):
                        string_shown = f'{ndb_urheber_data[len(ndb_urheber_data)-1][3][n]} | {ndb_urheber_data[len(ndb_urheber_data)-1][2][n]} | {ndb_urheber_data[len(ndb_urheber_data)-1][4][n]} | {ndb_urheber_data[len(ndb_urheber_data)-1][6][n]} | {ndb_urheber_data[len(ndb_urheber_data)-1][7][n]} | {(ndb_urheber_data[len(ndb_urheber_data)-1][5][n])}'
                        list_to_show.append(string_shown)

                    default_input_freitext = input_list_urheber[-1]
                    default_input_combo = list_to_show
                    
                    print('DEBUG URHEBER NDB DATA:', ndb_urheber_data)
                    hyperlink_to_show = ndb_urheber_data[-1][5][0]
                
                audio_starts_new = find_audio_timecodes().find_word_in_transcript(input_list_urheber[-1], transcripts_list, start_sorted)
                print('DEBUG DESCRIPTION LIST URHEBER:', description_list_urheber)
                print('DEBUG DESCRIPTION LIST URHEBER NUMBER:', description_list_urheber[-1])

                new_columns = self.empty_column_urheber(input_list_urheber[:-1], reference_roles_list_urheber, is_combo = is_combo_new, default_input_freitext = default_input_freitext, default_input_combo = default_input_combo, description_person = description_list_urheber[-1], audio_starter_list = audio_starts_new[0], default_hyperlink_to_show = hyperlink_to_show) #input_urheber muss bis zum vorletzten Eintrag gehen, weil sonst die Zählung der UI-Elemente-Trigger-Werte nicht passt.
                window.extend_layout(window['column_urheber'], [new_columns[0]])
                window.extend_layout(window['column_urheber'], [new_columns[1]])
                
                #Erase Data from Mitwirkende
                window[('-DEL-_tpers', event[1])].update(visible=False)
                window[('input_tpers', event[1])].update(visible=False)
                window[('input_tpers_vorname', event[1])].update(visible=False)
                window[('input_tpers_nachname', event[1])].update(visible=False)
                window[('description_tpers', event[1])].update(visible=False)
                window[('Play_File_tpers',event[1])].update(visible=False)
                window[('Stop_File_tpers', event[1])].update(visible=False)
                window[('audio_starter_tpers', event[1])].update(visible=False)
                window[(f'refresh_ndb_tpers', event[1])].update(visible=False)
                window[('change_input_type_tpers', event[1])].update(visible = False)
                window[('URL_tpers', event[1])].update(visible = False)
                window[('verschieb_themapers_urheber', event[1])].update(visible = False)
                window[('verschieb_themapers_mitwirkende', event[1])].update(visible = False)
                try:
                    window[('look_for_name_in_transcript_tpers', event[1])].update(visible = False)
                except:
                    pass
                
                erase_flagged_tpers.append(int(event[1]))    
                window.refresh()
                window['column_1'].contents_changed()

            #Verschieben von Urheber zu Mitwirkende
            if event != None and event[0] == 'verschieb_urheber_mitwirkende':
                input_list_mitwirkende.append(input_list_urheber[event[1]])
                ndb_mitwirkende_data.append(ndb_urheber_data[event[1]])
                self.hyperlink_list_mitwirkende.append(ndb_urheber_data[event[1]][5])
                description_list_mitwirkende.append(description_list_urheber[event[1]])
                self.alt_input.append(self.alt_input_urheber[event[1]])
                self.orig_input.append(self.orig_input_urheber[event[1]])
                self.final_input_is_original.append(self.final_input_is_original_urheber[event[1]])
                self.hyperlink_list_mitwirkende.append(self.hyperlink_list_urheber[event[1]])  
                self.current_hyperlink_list_mitwirkende.append(self.current_hyperlink_list_urheber[event[1]])
                self.current_hyperlink_mitwirkende.append(self.current_hyperlink_urheber[event[1]])
                self.current_input.append(self.current_input_urheber[event[1]])

                if self.current_input[-1] == 'Freitext':
                    is_combo_new = False
                    default_input_freitext = input_list_urheber[-1]
                    default_input_combo = []
                    
                    hyperlink_to_show = ''
                else:
                    is_combo_new = True
                    list_to_show = []
                    
                    for n in range(len(ndb_mitwirkende_data[-1][0])):
                        string_shown = f'{ndb_mitwirkende_data[-1][3][n]} | {ndb_mitwirkende_data[-1][2][n]} | {ndb_mitwirkende_data[-1][4][n]} | {ndb_mitwirkende_data[-1][6][n]} | {ndb_mitwirkende_data[-1][7][n]} | {(ndb_mitwirkende_data[-1][5][n])}'
                        list_to_show.append(string_shown)


                    default_input_freitext = input_list_mitwirkende[-1]
                    default_input_combo = list_to_show
                    
                    hyperlink_to_show = ndb_mitwirkende_data[-1][5][0]
                
                audio_starts_new = find_audio_timecodes().find_word_in_transcript(input_list_mitwirkende[-1], transcripts_list, start_sorted)
               
                new_columns = self.empty_column_mitwirkende(input_list_mitwirkende[:-1], reference_roles_list_mitwirkende, is_combo = is_combo_new, default_input_freitext = default_input_freitext, default_input_combo = default_input_combo, description_person = description_list_mitwirkende[-1], audio_starter_list = audio_starts_new[0], default_hyperlink_to_show = hyperlink_to_show) #input_urheber muss bis zum vorletzten Eintrag gehen, weil sonst die Zählung der UI-Elemente-Trigger-Werte nicht passt.
                window.extend_layout(window['column_mitwirk'], [new_columns[0]])
                window.extend_layout(window['column_mitwirk'], [new_columns[1]])
                
                #Erase Data from ThemaPersonen
                window[('-DEL-_urheber', event[1])].update(visible=False)
                window[('input_urheber', event[1])].update(visible=False)
                window[('combo_urheber', event[1])].update(visible=False)
                window[('description_urheber', event[1])].update(visible=False)
                window[('Play_File_urheber',event[1])].update(visible=False)
                window[('Stop_File_urheber', event[1])].update(visible=False)
                window[('audio_starter_urheber', event[1])].update(visible=False)
                window[(f'input_urheber', event[1])].update(visible=False)
                window[(f'input_urheber_vorname', event[1])].update(visible=False)
                window[(f'input_urheber_nachname', event[1])].update(visible=False)
                window[(f'refresh_ndb_urheber', event[1])].update(visible=False)
                window[('change_input_type_urheber', event[1])].update(visible = False)
                window[('URL_urheber', event[1])].update(visible = False)
                window[('verschieb_urheber_themapers', event[1])].update(visible = False)
                window[('verschieb_urheber_mitwirkende', event[1])].update(visible = False)
                try:
                    window[('look_for_name_in_transcript_urheber', event[1])].update(visible = False)
                except:
                    pass
                
                erase_flagged_urheber.append(int(event[1])) 
                window.refresh()
                window['column_1'].contents_changed()

            #Verschieben von Urheber zu themaPersonen
            if event != None and event[0] == 'verschieb_urheber_themapers':
                input_list_tpers.append(input_list_urheber[event[1]])
                ndb_thema_persons_suggest.append(ndb_urheber_data[event[1]])
                self.hyperlink_list_tpers.append(ndb_urheber_data[event[1]][5])
                description_list_tpers.append(description_list_urheber[event[1]])
                self.alt_input_tpers.append(self.alt_input_urheber[event[1]])
                self.orig_input_tpers.append(self.orig_input_urheber[event[1]])
                self.final_input_is_original_tpers.append(self.final_input_is_original_urheber[event[1]])
                self.hyperlink_list_tpers.append(self.hyperlink_list_urheber[event[1]])  
                self.current_hyperlink_list_tpers.append(self.current_hyperlink_list_urheber[event[1]])
                self.current_hyperlink_tpers.append(self.current_hyperlink_urheber[event[1]])
                self.current_input_tpers.append(self.current_input_urheber[event[1]])

                if self.current_input_tpers[-1] == 'Freitext':
                    is_combo_new = False
                    default_input_freitext = input_list_tpers[-1]
                    default_input_combo = []
                    
                    hyperlink_to_show = ''
                else:
                    is_combo_new = True
                    list_to_show = []
                    
                    for n in range(len(ndb_thema_persons_suggest[len(ndb_thema_persons_suggest)-1][0])):
                        string_shown = f'{ndb_thema_persons_suggest[-1][3][n]} | {ndb_thema_persons_suggest[-1][2][n]} | {ndb_thema_persons_suggest[-1][4][n]} | {ndb_thema_persons_suggest[-1][6][n]} | {ndb_thema_persons_suggest[-1][7][n]} | {(ndb_thema_persons_suggest[-1][5][n])}'
                        list_to_show.append(string_shown)

                    default_input_freitext = input_list_tpers[-1]
                    default_input_combo = list_to_show
                    
                    hyperlink_to_show = ndb_thema_persons_suggest[-1][5][0]
                
                audio_starts_new = find_audio_timecodes().find_word_in_transcript(input_list_tpers[-1], transcripts_list, start_sorted)
               
                new_columns = self.empty_column_tpers(input_list_tpers[:-1], is_combo = is_combo_new, default_input_freitext = default_input_freitext, default_input_combo = default_input_combo, description_person = description_list_tpers[-1], audio_starter_list = audio_starts_new[0], default_hyperlink_to_show = hyperlink_to_show) #input_tpers muss bis zum vorletzten Eintrag gehen, weil sonst die Zählung der UI-Elemente-Trigger-Werte nicht passt.
                window.extend_layout(window['column_tpers'], [new_columns[0]])
                window.extend_layout(window['column_tpers'], [new_columns[1]])
                
                #Erase Data from Urheber
                window[('-DEL-_urheber', event[1])].update(visible=False)
                window[('input_urheber', event[1])].update(visible=False)
                window[('input_urheber_vorname', event[1])].update(visible=False)
                window[('input_urheber_nachname', event[1])].update(visible=False)
                window[('combo_urheber', event[1])].update(visible=False)
                window[('description_urheber', event[1])].update(visible=False)
                window[('Play_File_urheber',event[1])].update(visible=False)
                window[('Stop_File_urheber', event[1])].update(visible=False)
                window[('audio_starter_urheber', event[1])].update(visible=False)
                window[(f'refresh_ndb_urheber', event[1])].update(visible=False)
                window[('change_input_type_urheber', event[1])].update(visible = False)
                window[('URL_urheber', event[1])].update(visible = False)
                window[('verschieb_urheber_mitwirkende', event[1])].update(visible = False)
                window[('verschieb_urheber_themapers', event[1])].update(visible = False)
                try:
                    window[('look_for_name_in_transcript_urheber', event[1])].update(visible = False)
                except:
                    pass
                erase_flagged_urheber.append(int(event[1])) 
                window.refresh()
                window['column_1'].contents_changed()


            #Reading and Changing Hyperlinks:
            #Mitwirkende
            if event != None and event[0] == "input_mitwirkende":
                
                if self.current_input[event[1]] == 'Dropdown' and event[0] == "input_mitwirkende":
                    current_choice_mitwirkender = values[("input_mitwirkende", event[1])]
                    new_hyperlink = False
                    
                    for n in range(len(self.current_hyperlink_list_mitwirkende[event[1]])):
                        if self.current_hyperlink_list_mitwirkende[event[1]][n] in current_choice_mitwirkender:
                            new_hyperlink = self.current_hyperlink_list_mitwirkende[event[1]][n]
                            self.current_hyperlink_mitwirkende[event[1]] = new_hyperlink
                           
                            window[('URL_mitwirkende', event[1])].update(value = new_hyperlink)
                            break
            #Urheber
            if event != None and event[0] == "input_urheber":
                print('DEBUG Add Urheber Input:', self.current_input_urheber)
                print('DEBUG Add Urheber Input:', event)
                
                if self.current_input_urheber[event[1]] == 'Dropdown' and event[0] == "input_urheber":
                    current_choice_urheber = values[("input_urheber", event[1])]
                    new_hyperlink = False
                    
                    for n in range(len(self.current_hyperlink_list_urheber[event[1]])):
                        if self.current_hyperlink_list_urheber[event[1]][n] in current_choice_urheber:
                            new_hyperlink = self.current_hyperlink_list_urheber[event[1]][n]
                            self.current_hyperlink_urheber[event[1]] = new_hyperlink
                           
                            window[('URL_urheber', event[1])].update(value = new_hyperlink)
                            break

            #ThemaPerson
            if event != None and event[0] == "input_tpers":
                print('DEBUG Add themaPers Input:', self.current_input_tpers)
                print('DEBUG Add themaPers Input:', event)

                if self.current_input_tpers[event[1]] == 'Dropdown' and event[0] == "input_tpers":
                    current_choice_tpers = values[("input_tpers", event[1])]
                    new_hyperlink = False
                    
                    for n in range(len(self.current_hyperlink_list_tpers[event[1]])):
                        if self.current_hyperlink_list_tpers[event[1]][n] in current_choice_tpers:
                            new_hyperlink = self.current_hyperlink_list_tpers[event[1]][n]
                            self.current_hyperlink_tpers[event[1]] = new_hyperlink
                           
                            window[('URL_tpers', event[1])].update(value = new_hyperlink)
                            break
            
            #ThemaOrte
            if event != None and (event[0] == "input_torte" or event[0] == "input_torte_alt"):
                
                if self.current_input_torte[event[1]] == 'Dropdown' and event[0] == "input_torte":
                    current_choice_torte = values[("input_torte", event[1])]
                    new_hyperlink = False
                    
                    for n in range(len(self.current_hyperlink_list_torte[event[1]])):
                        if self.current_hyperlink_list_torte[event[1]][n] in current_choice_torte:
                            new_hyperlink = self.current_hyperlink_list_torte[event[1]][n]
                            self.current_hyperlink_torte[event[1]] = new_hyperlink
                           
                            window[('URL_torte', event[1])].update(value = new_hyperlink)
                            break
                elif self.current_input_torte[event[1]] == 'Dropdown' and event[0] == "input_torte_alt":
                    current_choice_torte = values[("input_torte_alt", event[1])]
                    new_hyperlink = False
                    
                    for n in range(len(self.current_hyperlink_list_torte[event[1]])):
                        if self.current_hyperlink_list_torte[event[1]][n] in current_choice_torte:
                            new_hyperlink = self.current_hyperlink_list_torte[event[1]][n]
                            self.current_hyperlink_torte[event[1]] = new_hyperlink
                            
                            window[('URL_torte', event[1])].update(value = new_hyperlink)
                            break

            #ThemaInstitutionen
            if event != None and (event[0] == "input_tinst" or event[0] == "input_tinst_alt"):
                
                if self.current_input_tinst[event[1]] == 'Dropdown' and event[0] == "input_tinst":
                    current_choice_tinst = values[("input_tinst", event[1])]
                    new_hyperlink = False
                    
                    for n in range(len(self.current_hyperlink_list_tinst[event[1]])):
                        if self.current_hyperlink_list_tinst[event[1]][n] in current_choice_tinst:
                            new_hyperlink = self.current_hyperlink_list_tinst[event[1]][n]
                            self.current_hyperlink_tinst[event[1]] = new_hyperlink
                           
                            window[('URL_tinst', event[1])].update(value = new_hyperlink)
                            break
                elif self.current_input_tinst[event[1]] == 'Dropdown' and event[0] == "input_tinst_alt":
                    current_choice_tinst = values[("input_tinst_alt", event[1])]
                    new_hyperlink = False
                    
                    for n in range(len(self.current_hyperlink_list_tinst[event[1]])):
                        if self.current_hyperlink_list_tinst[event[1]][n] in current_choice_tinst:
                            new_hyperlink = self.current_hyperlink_list_tinst[event[1]][n]
                            self.current_hyperlink_tinst[event[1]] = new_hyperlink
                            
                            window[('URL_tinst', event[1])].update(value = new_hyperlink)
                            break

            #Opening Hyperlinks in Browser:
            #Mitwirkende
            if event != None and event[0] == "URL_mitwirkende":
                print('DEBUG Hyperlink:', self.current_hyperlink_mitwirkende[event[1]])
                url = self.current_hyperlink_mitwirkende[event[1]]
                webbrowser.open(url)

            #Urheber
            if event != None and event[0] == "URL_urheber":
                print('DEBUG Hyperlink:', self.current_hyperlink_urheber[event[1]])
                url = self.current_hyperlink_urheber[event[1]]
                webbrowser.open(url)

            #ThemaPerson
            if event != None and event[0] == "URL_tpers":
                print('DEBUG Hyperlink:', self.current_hyperlink_tpers[event[1]])
                url = self.current_hyperlink_tpers[event[1]]
                webbrowser.open(url)

            #ThemaOrte
            if event != None and event[0] == "URL_torte":
                print('DEBUG Hyperlink:', self.current_hyperlink_torte[event[1]])
                url = self.current_hyperlink_torte[event[1]]
                webbrowser.open(url)

            #ThemaInstitutionen
            if event != None and event[0] == "URL_tinst":
                print('DEBUG Hyperlink:', self.current_hyperlink_tinst[event[1]])
                url = self.current_hyperlink_tinst[event[1]]
                webbrowser.open(url)
                        
            if event != None and event[0] == 'look_for_name_in_transcript_tpers':
                values_name = values[("input_tpers", event[1])]
                audio_starts = find_audio_timecodes().find_word_in_transcript(values_name, transcripts_list, start_sorted)
                if len(audio_starts[0]) >0:
                    print(event[1])
                    window[('audio_starter_tpers', event[1])].update(values = audio_starts[0], value = audio_starts[0][0], visible=True)
                    window[('Play_File_tpers', event[1])].update(visible=True)
                    window[('Stop_File_tpers', event[1])].update(visible=True)
                    if ('Play_File_tpers', event[1]) not in self.eventlist_tpers:
                        self.eventlist_tpers.append(('Play_File_tpers', event[1]))
                        self.eventlist_tpers_stop_file.append(('Stop_File_tpers', event[1]))
                else:
                    window[('audio_starter_tpers', event[1])].update(visible=False)
                    window[('Play_File_tpers', event[1])].update(visible=False)
                    window[('Stop_File_tpers', event[1])].update(visible=False)

            if event != None and event[0] == 'look_for_name_in_transcript_torte':
                values_name = values[("input_torte", event[1])]
                audio_starts = find_audio_timecodes().find_word_in_transcript(values_name, transcripts_list, start_sorted)
                if len(audio_starts[0]) >0:
                    print(event[1])
                    window[('audio_starter_torte', event[1])].update(values = audio_starts[0], value = audio_starts[0][0], visible=True)
                    window[('Play_File_torte', event[1])].update(visible=True)
                    window[('Stop_File_torte', event[1])].update(visible=True)
                    if ('Play_File_torte', event[1]) not in self.eventlist_torte:
                        self.eventlist_torte.append(('Play_File_torte', event[1]))
                        self.eventlist_torte_stop_file.append(('Stop_File_torte', event[1]))
                else:
                    window[('audio_starter_torte', event[1])].update(visible=False)
                    window[('Play_File_torte', event[1])].update(visible=False)
                    window[('Stop_File_torte', event[1])].update(visible=False)

            if event != None and event[0] == 'look_for_name_in_transcript_tinst':
                values_name = values[("input_tinst", event[1])]
                audio_starts = find_audio_timecodes().find_word_in_transcript(values_name, transcripts_list, start_sorted)
                if len(audio_starts[0]) >0:
                    print(event[1])
                    window[('audio_starter_tinst', event[1])].update(values = audio_starts[0], value = audio_starts[0][0], visible=True)
                    window[('Play_File_tinst', event[1])].update(visible=True)
                    window[('Stop_File_tinst', event[1])].update(visible=True)
                    if ('Play_File_tinst', event[1]) not in self.eventlist_tinst:
                        self.eventlist_tinst.append(('Play_File_tinst', event[1]))
                        self.eventlist_tinst_stop_file.append(('Stop_File_tinst', event[1]))
                else:
                    window[('audio_starter_tinst', event[1])].update(visible=False)
                    window[('Play_File_tinst', event[1])].update(visible=False)
                    window[('Stop_File_tinst', event[1])].update(visible=False)

            if event != None and event[0] == 'look_for_name_in_transcript_desk':
                if self.current_input_desk[event[1]] == 'Freitext':
                    searchfor = values[("input_desk_alt", event[1])]
                    if '(' in searchfor:
                        searchfor = searchfor[2:len(searchfor)-3]
                else:
                    searchfor = self.text_input_transcr_search_desk[event[1]]

                print('DEBUG SEARCHFOR2:', searchfor)

                audio_starts = find_audio_timecodes().find_word_in_transcript(searchfor, transcripts_list, start_sorted)
                if len(audio_starts[0]) >0 and deskriptoren_suggest[event[1]][0]!=  '':
                    print(event[1])
                    window[('audio_starter_desk', event[1])].update(values = audio_starts[0], value = audio_starts[0][0], visible=True)
                    window[('Play_File_desk', event[1])].update(visible=True)
                    window[('Stop_File_desk', event[1])].update(visible=True)
                    if ('Play_File_desk', event[1]) not in self.eventlist_tinst:
                        self.eventlist_tinst.append(('Play_Filedesk', event[1]))
                        self.eventlist_tinst_stop_file.append(('Stop_File_desk', event[1]))
                else:
                    window[('audio_starter_desk', event[1])].update(visible=False)
                    window[('Play_File_desk', event[1])].update(visible=False)
                    window[('Stop_File_desk', event[1])].update(visible=False)
               
            if event != None and event[0] == 'look_for_name_in_transcript': #Button for "Mitwirkende"
                values_vorname = values[("input_mitwirkende_vorname", event[1])]
                values_nachname = values[("input_mitwirkende_nachname", event[1])]
                values_name = ' '.join([values_vorname, values_nachname])
                audio_starts = find_audio_timecodes().find_word_in_transcript(values_name, transcripts_list, start_sorted)
                if len(audio_starts[0]) >0:
                    
                    window[('audio_starter_mitwirkende', event[1])].update(values = audio_starts[0], value = audio_starts[0][0], visible=True)
                    print('audio_starter_mitwirkende', event[1], 'triggered')
                    window[('Play_File_mitwirkende', event[1])].update(visible=True)
                    window[('Stop_File_mitwirkende', event[1])].update(visible=True)
                    if ('Play_File_mitwirkende', event[1]) not in self.eventlist_mitwirkende:
                        self.eventlist_mitwirkende.append(('Play_File_mitwirkende', event[1]))
                        self.eventlist_mitwirkende_stop_file.append(('Stop_File_mitwirkende', event[1]))
                else:
                    window[('audio_starter_mitwirkende', event[1])].update(visible=False)
                    window[('Play_File_mitwirkende', event[1])].update(visible=False)
                    window[('Stop_File_mitwirkende', event[1])].update(visible=False)

            if event != None and event[0] == 'look_for_name_in_transcript_urheber': #Button for "Mitwirkende"
                print('DEBUG: Look for Name in Transcript triggered')

                values_name = values[("input_urheber", event[1])]
                print('DEBUG SEARCH Button:', values_name)
                audio_starts = find_audio_timecodes().find_word_in_transcript(values_name, transcripts_list, start_sorted)
                if len(audio_starts[0]) >0:
                    print('DEBUG SEARCH Button 2 Audio Starts:', audio_starts[0])
                    
                    window[('audio_starter_urheber', event[1])].update(values = audio_starts[0], value = audio_starts[0][0], visible=True)
                    
                    window[('Play_File_urheber', event[1])].update(visible=True)
                    window[('Stop_File_urheber', event[1])].update(visible=True)
                    if ('Play_File_urheber', event[1]) not in self.eventlist_urheber:
                        self.eventlist_urheber.append(('Play_File_urheber', event[1]))
                        self.eventlist_urheber_stop_file.append(('Stop_File_urheber', event[1]))
                else:
                    print('DEBUG SEARCH Button 2 No Audio Starts:', audio_starts[0])
                    window[('audio_starter_urheber', event[1])].update(visible=False)
                    window[('Play_File_urheber', event[1])].update(visible=False)
                    window[('Stop_File_urheber', event[1])].update(visible=False)

            if event != None and event[0] == 'look_for_name_in_transcript_tereignis': #Button for "Mitwirkende"

                values_name = values[("input_tereignis", event[1])]
                audio_starts = find_audio_timecodes().find_word_in_transcript(values_name, transcripts_list, start_sorted)
                if len(audio_starts[0]) >0:
                    
                    window[('audio_starter_tereignis', event[1])].update(values = audio_starts[0], value = audio_starts[0][0], visible=True)
                    
                    window[('Play_File_tereignis', event[1])].update(visible=True)
                    window[('Stop_File_tereignis', event[1])].update(visible=True)
                    if ('Play_File_tereignis', event[1]) not in self.eventlist_tereignis:
                        self.eventlist_tereignis.append(('Play_File_tereignis', event[1]))
                        self.eventlist_tereignis_stop_file.append(('Stop_File_tereignis', event[1]))
                else:
                    window[('audio_starter_tereignis', event[1])].update(visible=False)
                    window[('Play_File_tereignis', event[1])].update(visible=False)
                    window[('Stop_File_tereignis', event[1])].update(visible=False)

            
            if event != None and event[0] == 'look_for_name_in_transcript_realort': #Button for "Tags"
                values_name = values[("realort", event[1])]
                audio_starts = find_audio_timecodes().find_word_in_transcript(values_name, transcripts_list, start_sorted)
                if len(audio_starts[0]) >0:
                    try:
                        window[('audio_starter_realort', event[1])].update(values = audio_starts[0], value = audio_starts[0][0], visible=True)
                        
                        window[('Play_File_realort', event[1])].update(visible=True)
                        window[('Stop_File_realort', event[1])].update(visible=True)
                    except TypeError:
                        window[('audio_starter_realort', event[1])].update(values = audio_starts[0], value = audio_starts[0][0], visible=True)
                        
                        window[('Play_File_realort', event[1])].update(visible=True)
                        window[('Stop_File_realort', event[1])].update(visible=True)
                    if ('Play_File_realort', event[1]) not in self.eventlist_tereignis:
                        self.eventlist_realort.append(('Play_File_realort', event[1]))
                        self.eventlist_realort_stop_file.append(('Stop_File_realort', event[1]))
                else:
                    window[('audio_starter_realort', event[1])].update(visible=False)
                    window[('Play_File_realort', event[1])].update(visible=False)
                    window[('Stop_File_realort', event[1])].update(visible=False)

            if event != None and event[0] == 'look_for_name_in_transcript_tags': #Button for "Tags"
                values_name = values[("input_tags", event[1])]
                audio_starts = find_audio_timecodes().find_word_in_transcript(values_name, transcripts_list, start_sorted)
                if len(audio_starts[0]) >0:
                    try:
                        window[('audio_starter_tags', event[1])].update(values = audio_starts[0], value = audio_starts[0][0], visible=True)
                        
                        window[('Play_File_tags', event[1])].update(visible=True)
                        window[('Stop_File_tags', event[1])].update(visible=True)
                    except TypeError:
                        window[('audio_starter_tags', event[1])].update(values = audio_starts[0], value = audio_starts[0][0], visible=True)
                        
                        window[('Play_File_tags', event[1])].update(visible=True)
                        window[('Stop_File_tags', event[1])].update(visible=True)
                    if ('Play_File_tags', event[1]) not in self.eventlist_tereignis:
                        self.eventlist_realort.append(('Play_File_tags', event[1]))
                        self.eventlist_realort_stop_file.append(('Stop_File_tags', event[1]))
                else:
                    window[('audio_starter_tags', event[1])].update(visible=False)
                    window[('Play_File_tags', event[1])].update(visible=False)
                    window[('Stop_File_tags', event[1])].update(visible=False)

            if event == 'look_for_search_in_transcript':
                values_name = values[("input_file_search")]
                audio_starts = find_audio_timecodes().find_word_in_transcript(values_name, transcripts_list, start_sorted)
                if len(audio_starts[0]) >0:
                    window[('audio_starter_transcript_search')].update(values = audio_starts[0], value = audio_starts[0][0], visible=True)
                    window[('Play_File_search')].update(visible=True)
                    window[('Stop_File_search')].update(visible=True)
                    window[('Transcript_File_search')].update(visible=True)
                    self.eventlist_search_player_start.append('Play_File_search')
                    self.eventlist_search_player_end.append('Stop_File_search')
                    
                else:
                    window[('audio_starter_transcript_search')].update(visible=False)
                    window[('Transcript_File_search')].update(visible=False)
                    window[('Play_File_search')].update(visible=False)
                    window[('Stop_File_search')].update(visible=False)
                    window[('transcript_search1')].update(visible=False)
            
            elif event == 'hfdb_nein': 
                values_passed = False
                audioplayer1.stop_playback()
                break
            
            elif event != None and event[0] == '-DEL-_mitwirkende':
                print(event[1])
                window[('-DEL-_mitwirkende', event[1])].update(visible=False)
                window[('input_mitwirkende', event[1])].update(visible=False)
                window[('input_mitwirkende_vorname', event[1])].update(visible=False)
                window[('input_mitwirkende_nachname', event[1])].update(visible=False)
                window[('combo_mitwirkende', event[1])].update(visible=False)
                window[('description_mitwirkende', event[1])].update(visible=False)
                window[('Play_File_mitwirkende',event[1])].update(visible=False)
                window[('Stop_File_mitwirkende', event[1])].update(visible=False)
                window[('audio_starter_mitwirkende', event[1])].update(visible=False)
                window[(f'refresh_ndb_mitwirkende', event[1])].update(visible=False)
                window[('change_input_type_mitwirk', event[1])].update(visible = False)
                window[('URL_mitwirkende', event[1])].update(visible = False)
                window[('verschieb_mitwirkende_urheber', event[1])].update(visible = False)
                window[('verschieb_mitwirkende_themapers', event[1])].update(visible = False)
                window[("bemerkung_mitwirkende_text", event[1])].update(visible = False)
                window[("bemerkung_mitwirkende", event[1])].update(visible = False)
                #if event[1] >= self.mitwirkende_count_original:
                window[('look_for_name_in_transcript', event[1])].update(visible = False)
                
                
                erase_flagged_mitwirkende.append(int(event[1]))
                window.refresh()
                window['column_1'].contents_changed()

            elif event != None and event[0] == '-DEL-_urheber':
                print(event[1])
                window[('-DEL-_urheber', event[1])].update(visible=False)
                window[('input_urheber', event[1])].update(visible=False)
                window[('input_urheber_vorname', event[1])].update(visible=False)
                window[('input_urheber_nachname', event[1])].update(visible=False)
                window[('combo_urheber', event[1])].update(visible=False)
                window[('description_urheber', event[1])].update(visible=False)
                window[('Play_File_urheber',event[1])].update(visible=False)
                window[('Stop_File_urheber', event[1])].update(visible=False)
                window[('audio_starter_urheber', event[1])].update(visible=False)
                #window[(f'input_urheber_alt', event[1])].update(visible=False)
                window[(f'refresh_ndb_urheber', event[1])].update(visible=False)
                window[('change_input_type_urheber', event[1])].update(visible = False)
                window[('URL_urheber', event[1])].update(visible = False)
                window[('verschieb_urheber_mitwirkende', event[1])].update(visible = False)
                window[('verschieb_urheber_themapers', event[1])].update(visible = False)
                #if event[1] >= self.urheber_count_original:
                window[('look_for_name_in_transcript_urheber', event[1])].update(visible = False)
                
                
                erase_flagged_urheber.append(int(event[1]))
                window.refresh()
                window['column_1'].contents_changed()
            
            elif event != None and event[0] == '-DEL-_tpers':
                print(event[1])
                window[('-DEL-_tpers', event[1])].update(visible=False)
                window[('input_tpers', event[1])].update(visible=False)
                window[('input_tpers_vorname', event[1])].update(visible=False)
                window[('input_tpers_nachname', event[1])].update(visible=False)
                window[('description_tpers', event[1])].update(visible=False)
                window[('Play_File_tpers', event[1])].update(visible=False)
                window[('audio_starter_tpers', event[1])].update(visible=False)
                window[('Stop_File_tpers', event[1])].update(visible=False)
                #window[(f'input_tpers_alt', event[1])].update(visible=False)
                window[(f'refresh_ndb_tpers', event[1])].update(visible=False)
                window[('URL_tpers', event[1])].update(visible = False)
                window[('verschieb_themapers_urheber', event[1])].update(visible = False)
                window[('verschieb_themapers_mitwirkende', event[1])].update(visible = False)
                window[('look_for_name_in_transcript_tpers', event[1])].update(visible = False)
                window[('change_input_type_tpers', event[1])].update(visible = False)
                erase_flagged_tpers.append(int(event[1]))
                window.refresh()
                window['column_1'].contents_changed()

            elif event != None and event[0] == '-DEL-_torte':
                print(event[1])
                window[('-DEL-_torte', event[1])].update(visible=False)
                window[('input_torte', event[1])].update(visible=False)
                window[('description_torte', event[1])].update(visible=False)
                window[('Play_File_torte', event[1])].update(visible=False)
                window[('audio_starter_torte', event[1])].update(visible=False)
                window[('Stop_File_torte', event[1])].update(visible=False)
                window[('input_torte_alt', event[1])].update(visible=False)
                window[('refresh_ndb_torte', event[1])].update(visible=False)
                window[('URL_torte', event[1])].update(visible = False)
                #if event[1] >= self.torte_count_original:
                window[('look_for_name_in_transcript_torte', event[1])].update(visible = False)
                
                window[('change_input_type_torte', event[1])].update(visible = False)
                erase_flagged_torte.append(int(event[1]))
                window.refresh()
                window['column_1'].contents_changed()
            
            elif event != None and event[0] == '-DEL-_tinst':
                print(event[1])
                window[('-DEL-_tinst', event[1])].update(visible=False)
                window[('input_tinst', event[1])].update(visible=False)
                window[('description_tinst', event[1])].update(visible=False)
                window[('Play_File_tinst', event[1])].update(visible=False)
                window[('audio_starter_tinst', event[1])].update(visible=False)
                window[('Stop_File_tinst', event[1])].update(visible=False)
                window[('input_tinst_alt', event[1])].update(visible=False)
                window[('refresh_ndb_tinst', event[1])].update(visible=False)
                window[('URL_tinst', event[1])].update(visible = False)
                #if event[1] >= self.tinst_count_original:
                window[('look_for_name_in_transcript_tinst', event[1])].update(visible = False)
                
                window[('change_input_type_tinst', event[1])].update(visible = False)
                erase_flagged_tinst.append(int(event[1]))
                window.refresh()
                window['column_1'].contents_changed()

            elif event != None and event[0] == '-DEL-_tereignis':
                print(event[1])
                window[('-DEL-_tereignis', event[1])].update(visible=False)
                window[('input_tereignis', event[1])].update(visible=False)
                window[('description_tereignis', event[1])].update(visible=False)
                window[('tereignis_datum_text', event[1])].update(visible=False)
                window[('input_tereignis_tage', event[1])].update(visible=False)
                window[('input_tereignis_monate', event[1])].update(visible=False)
                window[('input_tereignis_jahre', event[1])].update(visible=False)
                window[('input_tereignis_tage_ende', event[1])].update(visible=False)
                window[('input_tereignis_monate_ende', event[1])].update(visible=False)
                window[('input_tereignis_jahre_ende', event[1])].update(visible=False)
                window[('Play_File_tereignis', event[1])].update(visible=False)
                window[('audio_starter_tereignis', event[1])].update(visible=False)
                window[('Stop_File_tereignis', event[1])].update(visible=False)
                window[('tereignis_datum_text_bis', event[1])].update(visible=False)
                window[('look_for_name_in_transcript_tereignis', event[1])].update(visible = False)
                erase_flagged_tereignis.append(int(event[1]))
                window.refresh()
                window['column_1'].contents_changed()

            elif event != None and event[0] == '-DEL-_sprachen':
                print(event[1])
                window[('-DEL-_sprachen', event[1])].update(visible=False)
                window[('input_sprachen', event[1])].update(visible=False)
                window[('input_sprachen_alt', event[1])].update(visible=False)
                window[('refresh_ndb_sprachen', event[1])].update(visible=False)
                
                window[('change_input_type_sprachen', event[1])].update(visible = False)
                erase_flagged_sprachen.append(int(event[1]))
                window.refresh()
                window['column_1'].contents_changed()

            elif event != None and event[0] == '-DEL-_desk':
                print(event[1])
                window[('-DEL-_desk', event[1])].update(visible=False)
                window[('input_desk', event[1])].update(visible=False)
                window[('input_desk_alt', event[1])].update(visible=False)
                window[('hinweis_desk_klassen', event[1])].update(visible=False)
                window[('input_desk_klasse_chooser', event[1])].update(visible = False)
                window[('look_for_name_in_transcript_desk', event[1])].update(visible = False)
                window[('refresh_ndb_desk', event[1])].update(visible = False)
                window[('change_input_type_desk', event[1])].update(visible = False)
                window[('audio_starter_desk', event[1])].update(visible = False)
                window[('Play_File_desk', event[1])].update(visible = False)
                window[('Stop_File_desk', event[1])].update(visible = False)
                erase_flagged_desk.append(int(event[1]))
                window.refresh()
                window['column_1'].contents_changed()

            elif event != None and event[0] == '-DEL-_tags':
                print(event[1])
                window[('-DEL-_tags', event[1])].update(visible=False)
                window[('input_tags', event[1])].update(visible=False)
                window[('Play_File_tags', event[1])].update(visible=False)
                window[('audio_starter_tags', event[1])].update(visible=False)
                window[('Stop_File_tags', event[1])].update(visible=False)
                window[('look_for_name_in_transcript_tags', event[1])].update(visible = False)
                erase_flagged_tags.append(int(event[1]))
                window.refresh()
                window['column_1'].contents_changed()
            
            elif event != None and event[0] == '-DEL-_gatt':
                print(event[1])
                window[('-DEL-_gatt', event[1])].update(visible=False)
                window[('combo_gattungen', event[1])].update(visible=False)
                erase_flagged_gatt.append(int(event[1]))
                window.refresh()
                window['column_1'].contents_changed()

            elif event != None and event[0] == '-DEL-_genre':
                print(event[1])
                window[('-DEL-_genre', event[1])].update(visible=False)
                window[('combo_genre', event[1])].update(visible=False)
                erase_flagged_genre.append(int(event[1]))
                window.refresh()
                window['column_1'].contents_changed()

            elif event != None and event == '-DEL-_realdatum':
                
                window[('-DEL-_realdatum')].update(visible=False)
                window[('input_realdatum_tage')].update(visible=False)
                window[('input_realdatum_monate')].update(visible=False)
                window[('input_realdatum_jahre')].update(visible=False)
                window[('realdatum_text_bis')].update(visible=False)
                window[('realdatum_tage_ende')].update(visible=False)
                window[('realdatum_monate_ende')].update(visible=False)
                window[('realdatum_jahre_ende')].update(visible=False)
                window[('input_realdatum_zusatz')].update(visible=False)
                window[('realdatum_ende_zusatz')].update(visible=False)
                window[('description_realdatum')].update(visible=False)
                
                erase_flagged_realdatum = True
                window.refresh()
                window['column_1'].contents_changed()

            elif event != None and event[0] == '-DEL-_realort':
                window[('-DEL-_realort', event[1])].update(visible=False)
                window[('realort', event[1])].update(visible=False)
                window[('realisierung_kontext', event[1])].update(visible=False)
                window[('look_for_name_in_transcript_realort', event[1])].update(visible=False)
                window[('audio_starter_realort', event[1])].update(visible=False)
                window[('Play_File_realort', event[1])].update(visible=False)
                window[('Stop_File_realort', event[1])].update(visible=False)
                
                erase_flagged_realorte.append(event[1])
                window.refresh()
                window['column_1'].contents_changed()

            elif event != None and event[0] == 'refresh_ndb_mitwirkende': 
                #Refresh Mitwirkender Abgleich - löst neue NDB-Suche aus
                values_passed = values
                window[("bemerkung_mitwirkende", event[1])].update(visible = False)
                window[("bemerkung_mitwirkende_text", event[1])].update(visible = False)
                
                window[("input_mitwirkende", event[1])].update(disabled = True)
                index_mitwirkender_refresh = event[1]
                vorname = values_passed[('input_mitwirkende_vorname', index_mitwirkender_refresh)]
                nachname = values_passed[('input_mitwirkende_nachname', index_mitwirkender_refresh)]
                name = ' '.join([vorname, nachname])
                if self.current_input[index_mitwirkender_refresh] == 'Freitext': #Bei Freitextfeld stets mit aktuellem Input des Freitextes suchen
                    new_dropdown_input = norm_db_linker.make_name_suggestions_from_LLM_suggestions(name, description_list_mitwirkende[index_mitwirkender_refresh])
                       
                else: #Sonst mir originalem Input neu suchen in NDB
                    if input_list_mitwirkende[index_mitwirkender_refresh] != 'None':
                        new_dropdown_input = norm_db_linker.make_name_suggestions_from_LLM_suggestions(name, description_list_mitwirkende[index_mitwirkender_refresh])   
                    else:
                        ()         
                
                if len(new_dropdown_input[0])==0: #Wenn beim NDB-Abgleich nichts gefunden wurde
                    if self.orig_input[index_mitwirkender_refresh] == 'Freitext':
                        window[("input_mitwirkende_vorname", event[1])].update(value = values_passed[('input_mitwirkende_vorname', index_mitwirkender_refresh)], disabled = False)
                        window[("input_mitwirkende_nachname", event[1])].update(value = values_passed[('input_mitwirkende_nachname', index_mitwirkender_refresh)], disabled = False)
                        self.final_input_is_original[event[1]] = True
                        
                    elif self.orig_input[index_mitwirkender_refresh] == 'Dropdown':
                        window[("input_mitwirkende", event[1])].update(value = values_passed[('input_mitwirkende', index_mitwirkender_refresh)], visible = True, disabled = False, readonly = False)
                        window[("input_mitwirkende", event[1])].update(visible = False)   
                        self.final_input_is_original[event[1]] = False           

                else: #Wenn beim NDB-Abgleich etwas gefunden wurde
                    list_to_show = []
                    self.current_input[index_mitwirkender_refresh] = 'Dropdown'
                    #Replace Result list global:
                    ndb_mitwirkende_data[index_mitwirkender_refresh] = new_dropdown_input

                    for n in range(len(new_dropdown_input[0])):
                        string_shown = f'{new_dropdown_input[3][n]} | {new_dropdown_input[2][n]} | {new_dropdown_input[4][n]} | {new_dropdown_input[6][n]} | {new_dropdown_input[7][n]} | {(new_dropdown_input[5][n])}'
                        list_to_show.append(string_shown)
                    
                    if self.orig_input[index_mitwirkender_refresh] == 'Dropdown':
                        window[("input_mitwirkende", event[1])].update(values = list_to_show, value = list_to_show[0], disabled = False, visible = True)
                        self.final_input_is_original[event[1]] = True
                        window[("input_mitwirkende_vorname", event[1])].update(visible = False)
                        window[("input_mitwirkende_nachname", event[1])].update(visible = False)
                    
                    elif self.orig_input[index_mitwirkender_refresh] == 'Freitext':
                        window[("input_mitwirkende", event[1])].update(values = list_to_show, value = list_to_show[0], visible = True, disabled = False)
                        window[("input_mitwirkende_vorname", event[1])].update(visible = False)
                        window[("input_mitwirkende_nachname", event[1])].update(visible = False)
                        self.final_input_is_original[event[1]] = False

                    #Edit NDB-Hyperlink
                    self.current_hyperlink_list_mitwirkende[index_mitwirkender_refresh] = new_dropdown_input[5]
                    window[("URL_mitwirkende", index_mitwirkender_refresh)].update(visible = True, value = new_dropdown_input[5][0])   
                    self.current_hyperlink_mitwirkende[index_mitwirkender_refresh] = new_dropdown_input[5][0]
                window[("bemerkung_mitwirkende_text", event[1])].update(visible = True)
                window[("bemerkung_mitwirkende", event[1])].update(visible = True)
                
            
            elif event != None and event[0] == 'change_input_type_mitwirk': #Wenn Button zum ändern des Inputs bei Mitwirkenden gedrückt wurde
                if self.orig_input[event[1]] == 'Freitext' and self.current_input[event[1]] != 'Freitext':
                    self.current_input[event[1]] = 'Freitext'
                    self.alt_input[event[1]] = False
                    window[('input_mitwirkende', event[1])].update(visible=False)
                    window[("input_mitwirkende_vorname", event[1])].update(visible=True, readonly = False) 
                    window[("input_mitwirkende_nachname", event[1])].update(visible=True, readonly = False)   
                    self.final_input_is_original[event[1]] = True
                    window[('URL_mitwirkende', event[1])].update(visible = False)
                    print('Button_state_1')
                elif self.orig_input[event[1]] == 'Freitext' and self.current_input[event[1]] == 'Freitext':
                    self.current_input[event[1]] = 'Freitext'
                    self.alt_input[event[1]] = False 
                    self.final_input_is_original[event[1]] = True
                    window[('URL_mitwirkende', event[1])].update(visible = False)
                    print('Button_state_2')
                elif self.orig_input[event[1]] == 'Dropdown' and self.current_input[event[1]] != 'Dropdown':
                    self.current_input[event[1]] = 'Freitext'
                    self.alt_input[event[1]] = True
                    window[('input_mitwirkende', event[1])].update(visible=False, readonly = False)
                    window[("input_mitwirkende_vorname", event[1])].update(visible=True)  
                    window[("input_mitwirkende_nachname", event[1])].update(visible=True)  
                    self.final_input_is_original[event[1]] = False
                    window[('URL_mitwirkende', event[1])].update(visible = False)
                    print('Button_state_3')
                elif self.orig_input[event[1]] == 'Dropdown' and self.current_input[event[1]] == 'Dropdown':
                    self.current_input[event[1]] = 'Freitext'
                    self.alt_input[event[1]] = True
                    window[('input_mitwirkende', event[1])].update(visible=False, readonly = False)
                    window[("input_mitwirkende_vorname", event[1])].update(visible=True)  
                    window[("input_mitwirkende_nachname", event[1])].update(visible=True) 
                    self.final_input_is_original[event[1]] = True
                    print('Button_state_4')
                    window[('URL_mitwirkende', event[1])].update(visible = False)

            elif event != None and event[0] == 'refresh_ndb_urheber': #Refresh Urheber Abgleich - löst neue NDB-Suche aus
                values_passed = values
                
                window[("input_urheber", event[1])].update(disabled = True)
                index_urheber_refresh = event[1]
                vorname = values_passed[('input_urheber_vorname', index_urheber_refresh)]
                nachname = values_passed[('input_urheber_nachname', index_urheber_refresh)]
                name = ' '.join([vorname, nachname])

                if self.current_input_urheber[index_urheber_refresh] == 'Freitext': #Bei Freitextfeld stets mit aktuellem Input des Freitextes suchen
                    new_dropdown_input = norm_db_linker.make_name_suggestions_from_LLM_suggestions(name, description_list_urheber[index_urheber_refresh])
                             
                        
                else: #Sonst mir originalem Input neu suchen in NDB
                    if input_list_urheber[index_urheber_refresh] != 'None':
                        new_dropdown_input = norm_db_linker.make_name_suggestions_from_LLM_suggestions(input_list_urheber[index_urheber_refresh], description_list_urheber[index_urheber_refresh])   
                    else:
                        ()            
                
                if len(new_dropdown_input[0])==0: #Wenn beim NDB-Abgleich nichts gefunden wurde
                    if self.orig_input_urheber[index_urheber_refresh] == 'Freitext':
                        window[("input_urheber_vorname", event[1])].update(value = values_passed[('input_urheber_vorname', index_urheber_refresh)], disabled = False)
                        window[("input_urheber_nachname", event[1])].update(value = values_passed[('input_urheber_nachname', index_urheber_refresh)], disabled = False)
                        self.final_input_is_original_urheber[event[1]] = True
                        
                    elif self.orig_input_urheber[index_urheber_refresh] == 'Dropdown':
                        window[("input_urheber", event[1])].update(value = values_passed[('input_urheber', index_urheber_refresh)], visible = True, disabled = False, readonly = False)
                        window[("input_urheber", event[1])].update(visible = False)   
                        self.final_input_is_original_urheber[event[1]] = False           

                else: #Wenn beim NDB-Abgleich etwas gefunden wurde
                    list_to_show = []
                    self.current_input_urheber[index_urheber_refresh] = 'Dropdown'
                    #Replace Result list global:
                    ndb_urheber_data[index_urheber_refresh] = new_dropdown_input

                    for n in range(len(new_dropdown_input[0])):
                        string_shown = f'{new_dropdown_input[3][n]} | {new_dropdown_input[2][n]} | {new_dropdown_input[4][n]} | {new_dropdown_input[6][n]} | {new_dropdown_input[7][n]} | {(new_dropdown_input[5][n])}'
                        list_to_show.append(string_shown)
                    
                    if self.orig_input_urheber[index_urheber_refresh] == 'Dropdown':
                        window[("input_urheber", event[1])].update(values = list_to_show, value = list_to_show[0], disabled = False, visible = True)
                        self.final_input_is_original_urheber[event[1]] = True
                        window[("input_urheber_vorname", event[1])].update(visible = False)
                        window[("input_urheber_nachname", event[1])].update(visible = False)
                    
                    elif self.orig_input_urheber[index_urheber_refresh] == 'Freitext':
                        window[("input_urheber", event[1])].update(values = list_to_show, value = list_to_show[0], visible = True, disabled = False)
                        window[("input_urheber_vorname", event[1])].update(visible = False)
                        window[("input_urheber_nachname", event[1])].update(visible = False)
                        self.final_input_is_original_urheber[event[1]] = False

                    #Edit NDB-Hyperlink
                    self.current_hyperlink_list_urheber[index_urheber_refresh] = new_dropdown_input[5]
                    window[("URL_urheber", index_urheber_refresh)].update(visible = True, value = new_dropdown_input[5][0])   
                    self.current_hyperlink_urheber[index_urheber_refresh] = new_dropdown_input[5][0]         
            
            elif event != None and event[0] == 'change_input_type_urheber': #Wenn Button zum ändern des Inputs bei Mitwirkenden gedrückt wurde
                if self.orig_input_urheber[event[1]] == 'Freitext' and self.current_input_urheber[event[1]] != 'Freitext':
                    self.current_input_urheber[event[1]] = 'Freitext'
                    self.alt_input_urheber[event[1]] = False
                    window[('input_urheber', event[1])].update(visible=False)
                    window[("input_urheber_vorname", event[1])].update(visible=True, readonly = False)  
                    window[("input_urheber_nachname", event[1])].update(visible=True, readonly = False)  
                    self.final_input_is_original_urheber[event[1]] = True
                    window[('URL_urheber', event[1])].update(visible = False)
                    print('Button_state_1 Urheber')
                elif self.orig_input_urheber[event[1]] == 'Freitext' and self.current_input_urheber[event[1]] == 'Freitext':
                    self.current_input_urheber[event[1]] = 'Freitext'
                    self.alt_input_urheber[event[1]] = False 
                    self.final_input_is_original_urheber[event[1]] = True
                    window[('URL_urheber', event[1])].update(visible = False)
                    print('Button_state_2 Urheber')
                elif self.orig_input_urheber[event[1]] == 'Dropdown' and self.current_input_urheber[event[1]] != 'Dropdown':
                    self.current_input_urheber[event[1]] = 'Freitext'
                    self.alt_input_urheber[event[1]] = True
                    window[('input_urheber', event[1])].update(visible=True, readonly = False)
                    window[("input_urheber_vorname", event[1])].update(visible=True)  
                    window[("input_urheber_nachname", event[1])].update(visible=True)  
                    self.final_input_is_original_urheber[event[1]] = False
                    window[('URL_urheber', event[1])].update(visible = False)
                    print('Button_state_3 Urheber')
                elif self.orig_input_urheber[event[1]] == 'Dropdown' and self.current_input_urheber[event[1]] == 'Dropdown':
                    self.current_input_urheber[event[1]] = 'Freitext'
                    self.alt_input_urheber[event[1]] = True
                    window[('input_urheber', event[1])].update(visible=False)
                    window[("input_urheber_vorname", event[1])].update(visible=True) 
                    window[("input_urheber_nachname", event[1])].update(visible=True) 
                    self.final_input_is_original_urheber[event[1]] = True
                    window[('URL_urheber', event[1])].update(visible = False)
                    print('Button_state_4 Urheber')

            elif event != None and event[0] == 'refresh_ndb_tpers': #Refresh themaPerson Abgleich - löst neue NDB-Suche aus
                values_passed = values
                
                window[("input_tpers", event[1])].update(disabled = True)
                index_tpers_refresh = event[1]
                vorname = values_passed[('input_tpers_vorname', index_tpers_refresh)]
                nachname = values_passed[('input_tpers_nachname', index_tpers_refresh)]
                name = ' '.join([vorname, nachname])
                print('Current Input_Tpers Liste:', self.current_input_tpers)
                print('Index looked for:', index_tpers_refresh)
                if self.current_input_tpers[index_tpers_refresh] == 'Freitext': #Bei Freitextfeld stets mit aktuellem Input des Freitextes suchen
                        
                    new_dropdown_input = norm_db_linker.make_name_suggestions_from_LLM_suggestions(name, description_list_tpers[index_tpers_refresh])
                        
                else: #Sonst mit originalem Input neu suchen in NDB
                    
                    new_dropdown_input = norm_db_linker.make_name_suggestions_from_LLM_suggestions(input_list_tpers[index_tpers_refresh], description_list_tpers[index_tpers_refresh])               
                
                if len(new_dropdown_input[0])==0: #Wenn beim NDB-Abgleich nichts gefunden wurde
                    if self.orig_input_tpers[index_tpers_refresh] == 'Freitext':
                        window[("input_tpers_vorname", event[1])].update(value = values_passed[('input_tpers_vorname', index_tpers_refresh)], disabled = False)
                        window[("input_tpers_nachname", event[1])].update(value = values_passed[('input_tpers_nachname', index_tpers_refresh)], disabled = False)
                        self.final_input_is_original_tpers[event[1]] = True
                        
                        
                    elif self.orig_input_tpers[index_tpers_refresh] == 'Dropdown':
                        window[("input_tpers", event[1])].update(value = values_passed[('input_tpers', index_tpers_refresh)], visible = True, disabled = False, readonly = False)
                        window[("input_tpers", event[1])].update(visible = False)   
                        self.final_input_is_original_tpers[event[1]] = False       

                else: #Wenn beim NDB-Abgleich etwas gefunden wurde
                    list_to_show = []
                    self.current_input_tpers[index_tpers_refresh] = 'Dropdown'
                    #Replace Result list global:
                    ndb_thema_persons_suggest[index_tpers_refresh] = new_dropdown_input

                    for n in range(len(new_dropdown_input[0])):
                        string_shown = f'{new_dropdown_input[3][n]} | {new_dropdown_input[2][n]} | {new_dropdown_input[4][n]} | {new_dropdown_input[6][n]} | {new_dropdown_input[7][n]} | {(new_dropdown_input[5][n])}'
                        list_to_show.append(string_shown)
                    
                    if self.orig_input_tpers[index_tpers_refresh] == 'Dropdown':
                        window[("input_tpers", event[1])].update(values = list_to_show, value = list_to_show[0], disabled = False, visible = True)
                        self.final_input_is_original_tpers[event[1]] = True
                        window[("input_tpers_vorname", event[1])].update(visible = False)
                        window[("input_tpers_nachname", event[1])].update(visible = False)

                    elif self.orig_input_tpers[index_tpers_refresh] == 'Freitext':
                        
                        window[("input_tpers", event[1])].update(values = list_to_show, value = list_to_show[0], visible = True, disabled = False)
                        window[("input_tpers_vorname", event[1])].update(visible = False)
                        window[("input_tpers_nachname", event[1])].update(visible = False)
                        self.final_input_is_original_tpers[event[1]] = False

                    #Edit NDB-Hyperlink
                    self.current_hyperlink_list_tpers[index_tpers_refresh] = new_dropdown_input[5]
                    window[("URL_tpers", index_tpers_refresh)].update(visible = True, value = new_dropdown_input[5][0])  
                    print('DEBUG HYPERLINK CURRENT TPERS:', self.current_hyperlink_tpers) 
                    print('DEBUG HYPERLINK CURRENT TPERS:', index_tpers_refresh) 
                    print('DEBUG HYPERLINK CURRENT TPERS:', new_dropdown_input)
                    self.current_hyperlink_tpers[index_tpers_refresh] = new_dropdown_input[5][0]

            elif event != None and event[0] == 'change_input_type_tpers': #Wenn Button zum ändern des Inputs bei Mitwirkenden gedrückt wurde
                if self.orig_input_tpers[event[1]] == 'Freitext' and self.current_input_tpers[event[1]] != 'Freitext':
                    self.current_input_tpers[event[1]] = 'Freitext'
                    self.alt_input_tpers[event[1]] = False
                    window[('input_tpers', event[1])].update(visible=False)
                    window[("input_tpers_vorname", event[1])].update(visible=True, readonly = False)
                    window[("input_tpers_nachname", event[1])].update(visible=True, readonly = False)    
                    self.final_input_is_original_tpers[event[1]] = True
                    window[('URL_tpers', event[1])].update(visible = False)
                    print('Button_state_1')
                elif self.orig_input_tpers[event[1]] == 'Freitext' and self.current_input_tpers[event[1]] == 'Freitext':
                    self.current_input_tpers[event[1]] = 'Freitext'
                    self.alt_input_tpers[event[1]] = False 
                    self.final_input_is_original_tpers[event[1]] = True
                    window[('URL_tpers', event[1])].update(visible = False)
                    print('Button_state_2')
                elif self.orig_input_tpers[event[1]] == 'Dropdown' and self.current_input_tpers[event[1]] != 'Dropdown':
                    self.current_input_tpers[event[1]] = 'Freitext'
                    self.alt_input_tpers[event[1]] = True
                    window[('input_tpers', event[1])].update(visible=True, readonly = False)
                    window[("input_tpers_vorname", event[1])].update(visible=True)  
                    window[("input_tpers_nachname", event[1])].update(visible=True)  
                    self.final_input_is_original_tpers[event[1]] = False
                    window[('URL_tpers', event[1])].update(visible = False)
                    print('Button_state_3')
                elif self.orig_input_tpers[event[1]] == 'Dropdown' and self.current_input_tpers[event[1]] == 'Dropdown':
                    self.current_input_tpers[event[1]] = 'Freitext'
                    self.alt_input_tpers[event[1]] = True
                    window[('input_tpers', event[1])].update(visible=False)
                    window[("input_tpers_vorname", event[1])].update(visible=True) 
                    window[("input_tpers_nachname", event[1])].update(visible=True) 
                    self.final_input_is_original_tpers[event[1]] = True
                    print('Button_state_4')  
                    window[('URL_tpers', event[1])].update(visible = False)

            elif event != None and event[0] == 'refresh_ndb_torte': #Refresh themaPerson Abgleich - löst neue NDB-Suche aus
                values_passed = values
                
                window[("input_torte", event[1])].update(disabled = True)
                index_torte_refresh = event[1]
                
                if self.current_input_torte[index_torte_refresh] == 'Freitext': #Bei Freitextfeld stets mit aktuellem Input des Freitextes suchen
                    
                    if self.alt_input_torte[index_torte_refresh] == False: #Wenn es sich hier nicht um den alternativem Input zum Original Input handelt, der ursprünglich ausgeblendet ist
                        
                        new_dropdown_input = norm_db_linker.make_orte_suggestions_from_LLM_suggestions(values_passed[('input_torte', index_torte_refresh)])
                        
                    else: #Wenn das Feld ursprünglich ein Dropdown war und jetzt umgewandelt wurde in ein Freitextfeld
                        
                        new_dropdown_input = norm_db_linker.make_orte_suggestions_from_LLM_suggestions(values_passed[('input_torte_alt', index_torte_refresh)])
                        
                else: #Sonst mit originalem Input neu suchen in NDB
                    
                    new_dropdown_input = norm_db_linker.make_orte_suggestions_from_LLM_suggestions(torte_list_llm_original[index_torte_refresh])               
                
                if len(new_dropdown_input[0])==0: #Wenn beim NDB-Abgleich nichts gefunden wurde
                    if self.orig_input_torte[index_torte_refresh] == 'Freitext':
                        window[("input_torte", event[1])].update(value = values_passed[('input_torte', index_torte_refresh)], disabled = False)
                        self.final_input_is_original_torte[event[1]] = True
                        
                    elif self.orig_input_torte[index_torte_refresh] == 'Dropdown':
                        window[("input_torte_alt", event[1])].update(value = values_passed[('input_torte_alt', index_torte_refresh)], visible = True, disabled = False, readonly = False)
                        window[("input_torte", event[1])].update(visible = False)   
                        self.final_input_is_original_torte[event[1]] = False           

                else: #Wenn beim NDB-Abgleich etwas gefunden wurde
                    list_to_show = []
                    self.current_input_torte[index_torte_refresh] = 'Dropdown'
                    #Replace Result list global:
                    input_list_torte[index_torte_refresh] = new_dropdown_input

                    for n in range(len(new_dropdown_input[0])):
                        string_shown = f'{new_dropdown_input[1][n]} | {new_dropdown_input[2][n]} | {new_dropdown_input[4][n]} | {new_dropdown_input[6][n]} | {new_dropdown_input[3][n]}'
                        list_to_show.append(string_shown)
                    
                    if self.orig_input_torte[index_torte_refresh] == 'Dropdown':
                        window[("input_torte", event[1])].update(values = list_to_show, value = list_to_show[0], disabled = False, visible = True)
                        
                        window[("input_torte_alt", event[1])].update(visible = False)

                    elif self.orig_input_torte[index_torte_refresh] == 'Freitext':
                        
                        window[("input_torte_alt", event[1])].update(values = list_to_show, value = list_to_show[0], visible = True, disabled = False)
                        window[("input_torte", event[1])].update(visible = False)    

                    #Edit NDB-Hyperlink
                    self.current_hyperlink_list_torte[index_torte_refresh] = new_dropdown_input[3]
                    window[("URL_torte", index_torte_refresh)].update(visible = True, value = new_dropdown_input[3][0])   
                    self.current_hyperlink_torte[index_torte_refresh] = new_dropdown_input[3][0]   

            elif event != None and event[0] == 'change_input_type_torte': #Wenn Button zum ändern des Inputs bei Mitwirkenden gedrückt wurde
                if self.orig_input_torte[event[1]] == 'Freitext' and self.current_input_torte[event[1]] != 'Freitext':
                    self.current_input_torte[event[1]] = 'Freitext'
                    self.alt_input_torte[event[1]] = False
                    window[('input_torte_alt', event[1])].update(visible=False)
                    window[("input_torte", event[1])].update(visible=True, readonly = False)  
                    window[('URL_torte', event[1])].update(visible = False)
                    self.final_input_is_original_torte[event[1]] = True
                    print('Button_state_1')
                elif self.orig_input_torte[event[1]] == 'Freitext' and self.current_input_torte[event[1]] == 'Freitext':
                    self.current_input_torte[event[1]] = 'Freitext'
                    self.alt_input_torte[event[1]] = False 
                    self.final_input_is_original_torte[event[1]] = True
                    window[('URL_torte', event[1])].update(visible = False)
                    print('Button_state_2')
                elif self.orig_input_torte[event[1]] == 'Dropdown' and self.current_input_torte[event[1]] != 'Dropdown':
                    self.current_input_torte[event[1]] = 'Freitext'
                    self.alt_input_torte[event[1]] = True
                    window[('input_torte_alt', event[1])].update(visible=True, readonly = False)
                    window[("input_torte", event[1])].update(visible=False)  
                    self.final_input_is_original_torte[event[1]] = False
                    window[('URL_torte', event[1])].update(visible = False)
                    print('Button_state_3')
                elif self.orig_input_torte[event[1]] == 'Dropdown' and self.current_input_torte[event[1]] == 'Dropdown':
                    self.current_input_torte[event[1]] = 'Freitext'
                    self.alt_input_torte[event[1]] = True
                    window[('input_torte_alt', event[1])].update(visible=True)
                    window[("input_torte", event[1])].update(visible=False) 
                    self.final_input_is_original_torte[event[1]] = True
                    window[('URL_torte', event[1])].update(visible = False)
                    print('Button_state_4')     
            
            elif event != None and event[0] == 'refresh_ndb_tinst': #Refresh themaInstitution Abgleich - löst neue NDB-Suche aus
                values_passed = values
                
                window[("input_tinst", event[1])].update(disabled = True)
                index_tinst_refresh = event[1]
                
                if self.current_input_tinst[index_tinst_refresh] == 'Freitext': #Bei Freitextfeld stets mit aktuellem Input des Freitextes suchen
                    
                    if self.alt_input_tinst[index_tinst_refresh] == False: #Wenn es sich hier nicht um den alternativem Input zum Original Input handelt, der ursprünglich ausgeblendet ist
                        
                        new_dropdown_input = norm_db_linker.make_institutionen_suggestions_from_LLM_suggestions(values_passed[('input_tinst', index_tinst_refresh)])
                        
                    else: #Wenn das Feld ursprünglich ein Dropdown war und jetzt umgewandelt wurde in ein Freitextfeld
                        
                        new_dropdown_input = norm_db_linker.make_institutionen_suggestions_from_LLM_suggestions(values_passed[('input_tinst_alt', index_tinst_refresh)])
                        
                else: #Sonst mit originalem Input neu suchen in NDB
                    
                    new_dropdown_input = norm_db_linker.make_institutionen_suggestions_from_LLM_suggestions(tinst_list_llm_original[index_tinst_refresh])               
                
                if len(new_dropdown_input[0])==0: #Wenn beim NDB-Abgleich nichts gefunden wurde
                    if self.orig_input_tinst[index_tinst_refresh] == 'Freitext':
                        window[("input_tinst", event[1])].update(value = values_passed[('input_tinst', index_tinst_refresh)], disabled = False)
                        self.final_input_is_original_tinst[event[1]] = True
                        
                    elif self.orig_input_tinst[index_tinst_refresh] == 'Dropdown':
                        window[("input_tinst_alt", event[1])].update(value = values_passed[('input_tinst_alt', index_tinst_refresh)], visible = True, disabled = False, readonly = False)
                        window[("input_tinst", event[1])].update(visible = False)   
                        self.final_input_is_original_tinst[event[1]] = False           

                else: #Wenn beim NDB-Abgleich etwas gefunden wurde
                    list_to_show = []
                    self.current_input_tinst[index_tinst_refresh] = 'Dropdown'
                    #Replace Result list global:
                    input_list_tinst_ndb[index_tinst_refresh] = new_dropdown_input

                    for n in range(len(new_dropdown_input[0])):
                        string_shown = f'{new_dropdown_input[1][n]} | {new_dropdown_input[2][n]} | {new_dropdown_input[3][n]} | {new_dropdown_input[4][n]} | {new_dropdown_input[5][n]}'
                        list_to_show.append(string_shown)
                    
                    if self.orig_input_tinst[index_tinst_refresh] == 'Dropdown':
                        window[("input_tinst", event[1])].update(values = list_to_show, value = list_to_show[0], disabled = False, visible = True)
                        
                        window[("input_tinst_alt", event[1])].update(visible = False)
                        self.final_input_is_original_tinst[event[1]] = True

                    elif self.orig_input_tinst[index_tinst_refresh] == 'Freitext':
                        
                        window[("input_tinst_alt", event[1])].update(values = list_to_show, value = list_to_show[0], visible = True, disabled = False)
                        window[("input_tinst", event[1])].update(visible = False)
                        self.final_input_is_original_tinst[event[1]] = False  

                    #Edit NDB-Hyperlink
                    self.current_hyperlink_list_tinst[index_tinst_refresh] = new_dropdown_input[5]
                    window[("URL_tinst", index_tinst_refresh)].update(visible = True, value = new_dropdown_input[5][0])   
                    self.current_hyperlink_tinst[index_tinst_refresh] = new_dropdown_input[5][0]     

            elif event != None and event[0] == 'change_input_type_tinst': #Wenn Button zum ändern des Inputs bei Mitwirkenden gedrückt wurde
                if self.orig_input_tinst[event[1]] == 'Freitext' and self.current_input_tinst[event[1]] != 'Freitext':
                    self.current_input_tinst[event[1]] = 'Freitext'
                    self.alt_input_tinst[event[1]] = False
                    window[('input_tinst_alt', event[1])].update(visible=False)
                    window[("input_tinst", event[1])].update(visible=True, readonly = False)  
                    window[('URL_tinst', event[1])].update(visible = False)
                    self.final_input_is_original_tinst[event[1]] = True
                    print('Button_state_1')
                elif self.orig_input_tinst[event[1]] == 'Freitext' and self.current_input_tinst[event[1]] == 'Freitext':
                    self.current_input_tinst[event[1]] = 'Freitext'
                    self.alt_input_tinst[event[1]] = False 
                    window[('URL_tinst', event[1])].update(visible = False)
                    self.final_input_is_original_tinst[event[1]] = True
                    print('Button_state_2')
                elif self.orig_input_tinst[event[1]] == 'Dropdown' and self.current_input_tinst[event[1]] != 'Dropdown':
                    self.current_input_tinst[event[1]] = 'Freitext'
                    self.alt_input_tinst[event[1]] = True
                    window[('input_tinst_alt', event[1])].update(visible=True, readonly = False)
                    window[("input_tinst", event[1])].update(visible=False) 
                    window[('URL_tinst', event[1])].update(visible = False) 
                    self.final_input_is_original_tinst[event[1]] = False
                    print('Button_state_3')
                elif self.orig_input_tinst[event[1]] == 'Dropdown' and self.current_input_tinst[event[1]] == 'Dropdown':
                    self.current_input_tinst[event[1]] = 'Freitext'
                    self.alt_input_tinst[event[1]] = True
                    window[('input_tinst_alt', event[1])].update(visible=True)
                    window[("input_tinst", event[1])].update(visible=False)
                    window[('URL_tinst', event[1])].update(visible = False) 
                    self.final_input_is_original_tinst[event[1]] = True
                    print('Button_state_4')   

            elif event != None and event[0] == 'refresh_ndb_sprachen': #Refresh themaInstitution Abgleich - löst neue NDB-Suche aus
                values_passed = values
                
                window[("input_sprachen", event[1])].update(disabled = True)
                index_sprachen_refresh = event[1]
                
                if self.current_input_sprachen[index_sprachen_refresh] == 'Freitext': #Bei Freitextfeld stets mit aktuellem Input des Freitextes suchen
                    
                    if self.alt_input_sprachen[index_sprachen_refresh] == False: #Wenn es sich hier nicht um den alternativem Input zum Original Input handelt, der ursprünglich ausgeblendet ist
                        
                        new_dropdown_input = norm_db_linker.suggest_ndb_sprachen(values_passed[('input_sprachen', index_sprachen_refresh)])
                        
                    else: #Wenn das Feld ursprünglich ein Dropdown war und jetzt umgewandelt wurde in ein Freitextfeld
                        
                        new_dropdown_input = norm_db_linker.suggest_ndb_sprachen(values_passed[('input_sprachen_alt', index_sprachen_refresh)])
                        
                else: #Sonst mit originalem Input neu suchen in NDB
                    
                    new_dropdown_input = norm_db_linker.suggest_ndb_sprachen(sprachen_suggest_original[index_sprachen_refresh])               
                
                if len(new_dropdown_input[0])==0: #Wenn beim NDB-Abgleich nichts gefunden wurde
                    if self.orig_input_sprachen[index_sprachen_refresh] == 'Freitext':
                        window[("input_sprachen", event[1])].update(value = values_passed[('input_sprachen', index_sprachen_refresh)], disabled = False)
                        self.final_input_is_original_sprachen[event[1]] = True
                        
                    elif self.orig_input_sprachen[index_sprachen_refresh] == 'Dropdown':
                        window[("input_sprachen_alt", event[1])].update(value = values_passed[('input_sprachen_alt', index_sprachen_refresh)], visible = True, disabled = False, readonly = False)
                        window[("input_sprachen", event[1])].update(visible = False)   
                        self.final_input_is_original_sprachen[event[1]] = False           

                else: #Wenn beim NDB-Abgleich etwas gefunden wurde
                    list_to_show = []
                    self.current_input_sprachen[index_sprachen_refresh] = 'Dropdown'
                    #Replace Result list global:
                    sprachen_suggest_ndb[index_sprachen_refresh] = new_dropdown_input

                    for n in range(len(new_dropdown_input[0])):
                        string_shown = f'{new_dropdown_input[1][n]} | {new_dropdown_input[2][n]} | {new_dropdown_input[3][n]} | {new_dropdown_input[4][n]} | {new_dropdown_input[0][n]}'
                        list_to_show.append(string_shown)
                    
                    if self.orig_input_sprachen[index_sprachen_refresh] == 'Dropdown':
                        window[("input_sprachen", event[1])].update(values = list_to_show, value = list_to_show[0], disabled = False, visible = True)
                        
                        window[("input_sprachen_alt", event[1])].update(visible = False)
                        self.final_input_is_original_sprachen[event[1]] = True

                    elif self.orig_input_sprachen[index_sprachen_refresh] == 'Freitext':
                        
                        window[("input_sprachen_alt", event[1])].update(values = list_to_show, value = list_to_show[0], visible = True, disabled = False)
                        window[("input_sprachen", event[1])].update(visible = False)
                        self.final_input_is_original_sprachen[event[1]] = False       

            elif event != None and event[0] == 'change_input_type_sprachen': #Wenn Button zum ändern des Inputs bei Sprachen gedrückt wurde
                if self.orig_input_sprachen[event[1]] == 'Freitext' and self.current_input_sprachen[event[1]] != 'Freitext':
                    self.current_input_sprachen[event[1]] = 'Freitext'
                    self.alt_input_sprachen[event[1]] = False
                    window[('input_sprachen_alt', event[1])].update(visible=False)
                    window[("input_sprachen", event[1])].update(visible=True, readonly = False)  
                    self.final_input_is_original_sprachen[event[1]] = True
                    print('Button_state_1')
                elif self.orig_input_sprachen[event[1]] == 'Freitext' and self.current_input_sprachen[event[1]] == 'Freitext':
                    self.current_input_sprachen[event[1]] = 'Freitext'
                    self.alt_input_sprachen[event[1]] = False 
                    self.final_input_is_original_sprachen[event[1]] = True
                    print('Button_state_2')
                elif self.orig_input_sprachen[event[1]] == 'Dropdown' and self.current_input_sprachen[event[1]] != 'Dropdown':
                    self.current_input_sprachen[event[1]] = 'Freitext'
                    self.alt_input_sprachen[event[1]] = True
                    window[('input_sprachen_alt', event[1])].update(visible=True, readonly = False)
                    window[("input_sprachen", event[1])].update(visible=False)  
                    self.final_input_is_original_sprachen[event[1]] = False
                    print('Button_state_3')
                elif self.orig_input_sprachen[event[1]] == 'Dropdown' and self.current_input_sprachen[event[1]] == 'Dropdown':
                    self.current_input_sprachen[event[1]] = 'Freitext'
                    self.alt_input_sprachen[event[1]] = True
                    window[('input_sprachen_alt', event[1])].update(visible=True)
                    window[("input_sprachen", event[1])].update(visible=False) 
                    self.final_input_is_original_sprachen[event[1]] = True
                    print('Button_state_4')   

            elif event != None and event[0] == 'refresh_ndb_desk': #Refresh Desk - löst neue NDB-Suche aus
                values_passed = values

                index_desk_refresh = event[1]
                                
                if self.current_input_desk[index_desk_refresh] == 'Freitext': #Bei Freitextfeld stets mit aktuellem Input des Freitextes suchen
                    self.text_input_transcr_search_desk[index_desk_refresh] =  values_passed[('input_desk_alt', index_desk_refresh)] 
                    new_dropdown_input = norm_db_linker.set_vokabel_vorschlaege(values_passed[('input_desk_alt', index_desk_refresh)])
                    print('DEBUG New Dropdown Input Desk:', new_dropdown_input)
                    self.deskriptoren_all_data[index_desk_refresh] = new_dropdown_input  
                     
                else: #Sonst mit originalem Input neu suchen in NDB
                    
                    new_dropdown_input = norm_db_linker.set_vokabel_vorschlaege(deskriptoren_suggest[index_desk_refresh][0][0])  
                    self.deskriptoren_all_data[index_desk_refresh] = new_dropdown_input          
                
                if len(new_dropdown_input[1])==0: #Wenn beim NDB-Abgleich nichts gefunden wurde
                    window[("input_desk_alt", event[1])].update(value = values_passed[('input_desk_alt', index_desk_refresh)], disabled = False)
                    self.current_input_desk[index_desk_refresh] = 'Freitext'    

                else: #Wenn beim NDB-Abgleich etwas gefunden wurde
                    list_to_show = []
                    self.text_input_transcr_search_desk[index_desk_refresh] = new_dropdown_input[0][0]
                    if len(new_dropdown_input[3]) == 0 and new_dropdown_input[6][0] == 'Freie Sachdeskriptoren':
                        string_shown_main_data = f'{new_dropdown_input[0][0]} | {new_dropdown_input[1][0]} | {new_dropdown_input[6][0]} | ACHTUNG! Freier Sachdeskriptor ohne zugeordnete Klasse. Über Plus-Symbol unten Klasse hinzufügen!'
                        self.current_input_desk[index_desk_refresh] = 'zugeordnete_klasse_keine'
                        window[('input_desk_alt', event[1])].update(visible=False)
                        window[('input_desk', event[1])].update(visible=True, value = string_shown_main_data)
                        
                    elif len(new_dropdown_input[3]) == 0 and new_dropdown_input[6][0] != 'Freie Sachdeskriptoren':
                        string_shown_main_data = f'{new_dropdown_input[0][0]} | {new_dropdown_input[1][0]} | {new_dropdown_input[6][0]}'
                        self.current_input_desk[index_desk_refresh] = 'zugeordnete_klasse_keine'
                        window[('input_desk_alt', event[1])].update(visible=False)
                        window[('input_desk', event[1])].update(visible=True, value = string_shown_main_data)

                    elif len(new_dropdown_input[3]) >1:
                        string_shown_main_data = f'{new_dropdown_input[0][0]} | {new_dropdown_input[1][0]} | {new_dropdown_input[6][0]}'
                        self.current_input_desk[index_desk_refresh]= 'zugeordnete_klasse_flex'

                        list_to_show = []
                        for n in range(len(new_dropdown_input[4])):
                            string_shown = f'{new_dropdown_input[3][n]} | {new_dropdown_input[4][n]}'
                            list_to_show.append(string_shown)

                        window[('input_desk_alt', event[1])].update(visible=False)
                        window[('input_desk', event[1])].update(visible=True, value = string_shown_main_data)
                        window[('hinweis_desk_klassen', event[1])].update(visible=True)
                        window[("input_desk_klasse_chooser", event[1])].update(visible=True, values = list_to_show, value = list_to_show [0])

                    elif len(new_dropdown_input[3]) == 1:
                        string_shown_main_data = f'{new_dropdown_input[0][0]} | {new_dropdown_input[1][0]} | {new_dropdown_input[6][0]} | zugeordnete Klassen: {new_dropdown_input[3][0]}/{new_dropdown_input[4][0]}'
                        self.current_input_desk[index_desk_refresh]= 'zugeordnete_klasse_fix'
                        window[('input_desk_alt', event[1])].update(visible=False)
                        window[('input_desk', event[1])].update(visible=True, value = string_shown_main_data)   

            elif event != None and event[0] == 'change_input_type_desk': #Wenn Button zum ändern des Inputs bei Deskriptoren gedrückt wurde
                
                self.current_input_desk[event[1]] = 'Freitext'
                window[('input_desk_alt', event[1])].update(visible=True)
                window[("input_desk", event[1])].update(visible=False)  
                window[("hinweis_desk_klassen", event[1])].update(visible=False)
                window[("input_desk_klasse_chooser", event[1])].update(visible=False)   

            if event == 'Play_File': 
                audioplayer1.play_file()
                audioplayer1.scroll_playback_to_second(int(values['-SL-']))
                position = audioplayer1.get_position()
                window['-SL-'].update(value = position)
                window['current_time'].update(audioplayer1.format_time(position))

            #if audioplayer1.is_playing == True: Not working
                #position = audioplayer1.get_position()
                #window['current_time'].update(audioplayer1.format_time(position))
        
            if event == 'Pause_File': 
                audioplayer1.pause_playback()
                position = audioplayer1.get_position()
                window['-SL-'].update(value = position)
                window['current_time'].update(audioplayer1.format_time(position))

            #if event == 'Resume_File': 
            # audioplayer1.resume_playback()

            if event == 'Stop_File': 
                audioplayer1.stop_playback()
                window['-SL-'].update(value = 0)
                window['current_time'].update(audioplayer1.format_time(0))

            if event == '-SL-':
                #print(values['-SL-'])
                #audioplayer1.play_file()
                audioplayer1.scroll_playback_to_second(int(values['-SL-']))
                window['current_time'].update(audioplayer1.format_time(int(values['-SL-'])))
                #audioplayer1.pause_playback()
           
            #Make Audioplayer Play on Ebene der einzelnen Personen, Orte, Mitwirkenden etc.
            if event in self.eventlist_tpers: 
                print(self.eventlist_tpers)
                
                event_index = self.eventlist_tpers.index(event)
                print(event_index)
                skip_time = (values[('audio_starter_tpers', event_index)])
                audioplayer2.play_file()
                audioplayer2.scroll_playback_to_second(skip_time)

            if event in self.eventlist_torte: 
                event_index = self.eventlist_torte.index(event)
                skip_time = (values[('audio_starter_torte', event_index)])
                audioplayer2.play_file()
                audioplayer2.scroll_playback_to_second(skip_time)

            if event in self.eventlist_tinst: 
                event_index = self.eventlist_tinst.index(event)
                skip_time = (values[('audio_starter_tinst', event_index)])
                audioplayer2.play_file()
                audioplayer2.scroll_playback_to_second(skip_time) 

            if event in self.eventlist_realort: 
                event_index = self.eventlist_realort.index(event)
                skip_time = (values[('audio_starter_realort', event_index)])
                audioplayer2.play_file()
                audioplayer2.scroll_playback_to_second(skip_time)   
            
            if event in self.eventlist_mitwirkende: 
                print(event)
                print(self.eventlist_mitwirkende)
                #print('Eventlist_Mitwirkende triggered')
                event_index = self.eventlist_mitwirkende.index(event)
                skip_time = (values[('audio_starter_mitwirkende', event_index)])
                print('DEBUG SKIP-TIME MITWIRKENDE:', skip_time)
                audioplayer2.play_file()
                if skip_time != '':
                   audioplayer2.scroll_playback_to_second(int(float(skip_time)))

            if event in self.eventlist_urheber: 
                print(event)
                print(self.eventlist_urheber)
                #print('Eventlist_Mitwirkende triggered')
                event_index = self.eventlist_urheber.index(event)
                skip_time = (values[('audio_starter_urheber', event_index)])
                print('SKIP-TIME:', skip_time)
                audioplayer2.play_file()
                if skip_time != '':
                   audioplayer2.scroll_playback_to_second(int(float(skip_time)))

            if event in self.eventlist_tereignis: 
                print(event)
                print(self.eventlist_tereignis)
                #print('Eventlist_Mitwirkende triggered')
                event_index = self.eventlist_tereignis.index(event)
                skip_time = (values[('audio_starter_tereignis', event_index)])
                audioplayer2.play_file()
                if skip_time != '':
                   audioplayer2.scroll_playback_to_second(int(float(skip_time)))

            if event in self.eventlist_desk: 
                print(event)
                print(self.eventlist_desk)
                #print('Eventlist_Mitwirkende triggered')
                event_index = self.eventlist_desk.index(event)
                skip_time = (values[('audio_starter_desk', event_index)])
                audioplayer2.play_file()
                if skip_time != '':
                   audioplayer2.scroll_playback_to_second(int(float(skip_time)))

            if event in self.eventlist_tags: 
                print(event)
                print(self.eventlist_tags)
                
                event_index = self.eventlist_tags.index(event)
                skip_time = (values[('audio_starter_tags', event_index)])
                audioplayer2.play_file()
                if skip_time != '':
                   audioplayer2.scroll_playback_to_second(int(float(skip_time)))
            
            #Make Audioplayer stop on Ebene der einzelnen Mitwirkenden, Orte, Personen etc.
            if event in self.eventlist_mitwirkende_stop_file or event in self.eventlist_urheber_stop_file or event == 'Stop_File_search' or event in self.eventlist_desk_stop_file: 
                print('found in Stop Eventlist')
                #event_index = self.eventlist_mitwirkende_stop_file.index(event)
                
                audioplayer2.stop_playback()

            if event in self.eventlist_torte_stop_file or event in self.eventlist_tinst_stop_file or event in self.eventlist_tereignis_stop_file or event in self.eventlist_tags_stop_file or event in self.eventlist_realort_stop_file: 
                print('found in Stop Eventlist')
                #event_index = self.eventlist_torte_stop_file.index(event)
                
                audioplayer2.stop_playback()

            if event in self.eventlist_tpers_stop_file: 
                print('found in Stop Eventlist')
                #event_index = self.eventlist_tpers_stop_file.index(event)
                
                audioplayer2.stop_playback()
                

            #Popups
            if event == 'Stichwortsuche::stichwortsuche':#Popup Event
                window_popup = self.popup_window(transcripts_list, start_sorted, audiofile)
                
            #Ask K.AR.IN
            if event == 'Frag K.AR.IN':#Popup Event
                
                window_popup_karin = self.popup_window_karin(transcripts_list)
                print('event_popup_2')

            #Audioplayer Gesamtfile
            if event == 'Audioplayer':#Popup Event
                
                print('Open Audioplayer')
                window_popup_audioplayer = self.popup_window_audioplayer(audiofile, transcripts_list, start_sorted, f'{audiofiles_path}\\{original_file}')
                print('event_audioplayer_1')
        try:    
            window.close()
        except:
            ()
        try:
            window_popup.close()
        except:
            ()
        
        try:
            window_popup_karin.close()
        except:
            ()
        try:
            window_popup_audioplayer.close()
        except:
            ()
        
        if popup_open_search == True:

            print(values_passed)
        
        if values_passed != False: #Wenn nicht der Button "Nicht in HFDB übernehmen" gedrückt wurde
            
            list_final_entities_mitwirkende = []
            list_final_roles_mitwirkende = []
                        
            for j in range(len(input_list_mitwirkende)):
                if self.current_input[j] == 'Dropdown':
                    try:
                        mitwirkende = values_passed[('input_mitwirkende', j)]
                        vorname = None
                        nachname = None
                        bemerkung = values_passed[("bemerkung_mitwirkende", j)]
                    except TypeError:
                        mitwirkende = ''
                        vorname = ''
                        nachname = ''
                        bemerkung = ''
                else:
                    mitwirkende = ''
                    vorname = values_passed[('input_mitwirkende_vorname', j)]
                    nachname = values_passed[('input_mitwirkende_nachname', j)]
                    bemerkung = values_passed[("bemerkung_mitwirkende", j)]

                list_single_entity_sets_mitwirkende = []
                if vorname != '' and vorname != ' ' and nachname != '' and nachname != ' ' and j not in erase_flagged_mitwirkende:
                    if '|' in mitwirkende:#Wenn wir ein Dropdown-Feld mit NDB-Daten haben
                        raw_data = mitwirkende
                        single_values = raw_data.split('|')
                        #print('Single Values:', single_values)
                        #print('NDB Mitwirkende Data:', ndb_mitwirkende_data)
                        #print('Single Values:', single_values[5])
                        print('DEBUG Mitwirkende Übergabe:', ndb_mitwirkende_data[j][5])
                        print('DEBUG ndb_mitwirkende_data[j]:', ndb_mitwirkende_data[j])
                        index_list_original_ndb_abgleich = ndb_mitwirkende_data[j][5].index(single_values[5].strip())
                        person_id_chosen = ndb_mitwirkende_data[j][0][index_list_original_ndb_abgleich].strip()
                        

                        name_id_chosen = ndb_mitwirkende_data[j][1][index_list_original_ndb_abgleich].strip()
                        

                        name_chosen = ndb_mitwirkende_data[j][2][index_list_original_ndb_abgleich].strip()
                        
                        if ndb_mitwirkende_data[j][3][index_list_original_ndb_abgleich] != None:
                            vorname_chosen = ndb_mitwirkende_data[j][3][index_list_original_ndb_abgleich].strip()
                        else:
                            vorname_chosen = None
                        
                    else:
                        person_id_chosen = None
                        name_id_chosen = None
                        name_chosen = nachname
                        vorname_chosen = vorname


                    list_single_entity_sets_mitwirkende.append(person_id_chosen)
                    list_single_entity_sets_mitwirkende.append(name_id_chosen)
                    list_single_entity_sets_mitwirkende.append(name_chosen)
                    list_single_entity_sets_mitwirkende.append(vorname_chosen)
                    list_single_entity_sets_mitwirkende.append(bemerkung)

                    list_final_entities_mitwirkende.append(list_single_entity_sets_mitwirkende)
                    
                    list_final_roles_mitwirkende.append(values_passed[('combo_mitwirkende', j)]) 

            #Finale Urheber zur Rückgabe an ak-maker erstellen
            list_final_entities_urheber = []
            list_final_roles_urheber = []
                        
            for j in range(len(input_list_urheber)):
                if self.current_input_urheber[j] == True:
                    urheber = values_passed[('input_urheber', j)]
                    vorname = None
                    nachname = None
                else:
                    urheber = ''
                    vorname = values_passed[('input_urheber_vorname', j)]
                    nachname = values_passed[('input_urheber_nachname', j)]
                list_single_entity_sets_urheber = []
                if vorname != '' and vorname != ' ' and nachname != '' and nachname != ' ' and j not in erase_flagged_urheber:
                    if ' | ' in urheber:#Wenn wir ein Dropdown-Feld mit NDB-Daten haben
                        raw_data = urheber
                        single_values = raw_data.split(' | ')
                        #print('Single Values:', single_values)
                        #print('NDB Mitwirkende Data:', ndb_mitwirkende_data)
                        #print('Single Values:', single_values[5])
                        print('DEBUG NDB URHEBER DATA - j:', ndb_urheber_data[j])
                        index_list_original_ndb_abgleich = ndb_urheber_data[j][5].index(single_values[5])
                        person_id_chosen = ndb_urheber_data[j][0][index_list_original_ndb_abgleich]
                        

                        name_id_chosen = ndb_urheber_data[j][1][index_list_original_ndb_abgleich]
                        

                        name_chosen = ndb_urheber_data[j][2][index_list_original_ndb_abgleich]
                        

                        if ndb_urheber_data[j][3][index_list_original_ndb_abgleich] != None:
                            vorname_chosen = ndb_urheber_data[j][3][index_list_original_ndb_abgleich].strip()
                        else:
                            vorname_chosen = None
                        
                    else:
                        person_id_chosen = None
                        name_id_chosen = None
                        name_chosen = nachname
                        vorname_chosen = vorname

                    list_single_entity_sets_urheber.append(person_id_chosen)
                    list_single_entity_sets_urheber.append(name_id_chosen)
                    list_single_entity_sets_urheber.append(name_chosen)
                    list_single_entity_sets_urheber.append(vorname_chosen)

                    list_final_entities_urheber.append(list_single_entity_sets_urheber)
                    list_final_roles_urheber.append(values_passed[('combo_urheber', j)]) 

            
            #ThemaPersonen_additions
            list_final_entities_tpers = []
                        
            for j in range(len(input_list_tpers)):
                if input_list_tpers[j] != None:
                    if self.current_input_tpers[j] == 'Dropdown':
                        tpers = values_passed[('input_tpers', j)]
                        vorname = None
                        nachname = None
                    else:
                        tpers = ''
                        vorname = values_passed[('input_tpers_vorname', j)]
                        nachname = values_passed[('input_tpers_nachname', j)]
                    list_single_entity_sets_tpers = []
                    if vorname != '' and vorname != ' ' and nachname != '' and nachname != ' ' and j not in erase_flagged_tpers:
                        if ' | ' in tpers:#Wenn wir ein Dropdown-Feld mit NDB-Daten haben
                            raw_data = tpers
                            print('raw_data:', raw_data)
                            single_values = raw_data.split(' | ')
                            print('single_values:', single_values)
                            print('DEBUG NDB TPERS DATA - j:', ndb_thema_persons_suggest[j])

                            index_list_original_ndb_abgleich = ndb_thema_persons_suggest[j][5].index(single_values[5])

                            person_id_chosen = ndb_thema_persons_suggest[j][0][index_list_original_ndb_abgleich]
                            

                            name_id_chosen = ndb_thema_persons_suggest[j][1][index_list_original_ndb_abgleich]
                            

                            name_chosen = ndb_thema_persons_suggest[j][2][index_list_original_ndb_abgleich]
                            

                            if ndb_thema_persons_suggest[j][3][index_list_original_ndb_abgleich] != None:
                                vorname_chosen = ndb_thema_persons_suggest[j][3][index_list_original_ndb_abgleich].strip()
                            else:
                                vorname_chosen = None
                            
                        else:
                            person_id_chosen = None
                            name_id_chosen = None
                            name_chosen = nachname
                            vorname_chosen = vorname

                        list_single_entity_sets_tpers.append(person_id_chosen)
                        list_single_entity_sets_tpers.append(name_id_chosen)
                        list_single_entity_sets_tpers.append(name_chosen)
                        list_single_entity_sets_tpers.append(vorname_chosen)

                        list_final_entities_tpers.append(list_single_entity_sets_tpers)
                    
            #ThemaOrte_additions
            list_final_entities_torte = []
                        
            for j in range(len(input_list_torte)):
                if self.final_input_is_original_torte[j] == True:
                    torte = values_passed[('input_torte', j)]
                else:
                    torte = values_passed[('input_torte_alt', j)]
                list_single_entity_sets_torte = []
                if torte != '' and torte != ' ' and j not in erase_flagged_torte:
                    if '|' in torte:#Wenn wir ein Dropdown-Feld mit NDB-Daten haben
                        raw_data = torte
                        #print('raw_data:', raw_data)
                        single_values = raw_data.split('|')
                        print('single_values:', single_values)
                        index_list_original_ndb_abgleich = input_list_torte[j][1].index(single_values[0].strip())
                        vok_id_chosen = input_list_torte[j][0][index_list_original_ndb_abgleich].strip()
                        

                        name_id_chosen = input_list_torte[j][5][index_list_original_ndb_abgleich].strip()
                        

                        name_chosen = input_list_torte[j][1][index_list_original_ndb_abgleich].strip()
                        
                        
                    else:
                        vok_id_chosen = None
                        name_id_chosen = None
                        name_chosen = values_passed[('input_torte', j)]

                    list_single_entity_sets_torte.append(vok_id_chosen)
                    list_single_entity_sets_torte.append(name_id_chosen)
                    list_single_entity_sets_torte.append(name_chosen)

                    list_final_entities_torte.append(list_single_entity_sets_torte)

            #ThemaInstitutionen_additions
            list_final_entities_tinst = []
                        
            for j in range(len(input_list_tinst_ndb)):
                if self.final_input_is_original_tinst[j] == True:
                    tinst = values_passed[('input_tinst', j)]
                else:
                    tinst = values_passed[('input_tinst_alt', j)]
                list_single_entity_sets_tinst = []
                if tinst != '' and tinst != ' ' and j not in erase_flagged_tinst:
                    if ' | ' in tinst:#Wenn wir ein Dropdown-Feld mit NDB-Daten haben
                        raw_data = tinst
                        #print('raw_data:', raw_data)
                        single_values = raw_data.split(' | ')
                        print('single_values_tinst:', single_values)
                        index_list_original_ndb_abgleich = input_list_tinst_ndb[j][1].index(single_values[0])
                        inst_id_chosen = input_list_tinst_ndb[j][3][index_list_original_ndb_abgleich]
                        

                        name_id_chosen = input_list_tinst_ndb[j][0][index_list_original_ndb_abgleich]
                        

                        name_chosen = input_list_tinst_ndb[j][1][index_list_original_ndb_abgleich]

                        name_addition = input_list_tinst_ndb[j][2][index_list_original_ndb_abgleich]
                            
                    else:
                        inst_id_chosen = None
                        name_id_chosen = None
                        name_addition = None
                        name_chosen = values_passed[('input_tinst', j)]
                    #print('DEBUG AUSGABE UI INSTITUTION:', inst_id_chosen, name_id_chosen, name_chosen, name_addition)
                    list_single_entity_sets_tinst.append(inst_id_chosen)
                    list_single_entity_sets_tinst.append(name_id_chosen)
                    list_single_entity_sets_tinst.append(name_chosen)
                    list_single_entity_sets_tinst.append(name_addition)

                    list_final_entities_tinst.append(list_single_entity_sets_tinst)

            #Sprachen_additions
            list_final_entities_sprachen = []
                        
            for j in range(len(sprachen_suggest_ndb)):
                if self.final_input_is_original_sprachen[j] == True:
                    sprachen = values_passed[('input_sprachen', j)]
                else:
                    sprachen = values_passed[('input_sprachen_alt', j)]
                list_single_entity_sets_sprachen = []
                if sprachen != '' and sprachen != ' ' and j not in erase_flagged_sprachen:
                    if ' | ' in sprachen:#Wenn wir ein Dropdown-Feld mit NDB-Daten haben
                        raw_data = sprachen
                        #print('raw_data:', raw_data)
                        single_values = raw_data.split(' | ')
                        print('single_values_sprachen:', single_values)
                        index_list_original_ndb_abgleich = sprachen_suggest_ndb[j][1].index(single_values[0])
                        bezeichnung_chosen = sprachen_suggest_ndb[j][1][index_list_original_ndb_abgleich]
                        

                        bezeichnung_zusatz_chosen = sprachen_suggest_ndb[j][2][index_list_original_ndb_abgleich]
                        

                        norm_id_name_chosen = sprachen_suggest_ndb[j][5][index_list_original_ndb_abgleich]

                        norm_id_vokabel_chosen = sprachen_suggest_ndb[j][0][index_list_original_ndb_abgleich]
                            
                    else:
                        bezeichnung_chosen = None
                        bezeichnung_zusatz_chosen = None
                        norm_id_name_chosen = None
                        norm_id_vokabel_chosen = values_passed[('input_sprache', j)]
                    #print('DEBUG AUSGABE UI INSTITUTION:', inst_id_chosen, name_id_chosen, name_chosen, name_addition)
                    list_single_entity_sets_sprachen.append(bezeichnung_chosen)
                    list_single_entity_sets_sprachen.append(bezeichnung_zusatz_chosen)
                    list_single_entity_sets_sprachen.append(norm_id_name_chosen)
                    list_single_entity_sets_sprachen.append(norm_id_vokabel_chosen)

                    list_final_entities_sprachen.append(list_single_entity_sets_sprachen)

            #ThemaEreignis_additions
            list_final_entities_tereignis = []
                        
            for j in range(len(tereignis_list_llm_original)):
                list_single_entity_sets_tereignis = []
                if tereignis_list_llm_original[j] != '' and tereignis_list_llm_original[j] != ' ' and j not in erase_flagged_tereignis:

                    tereignis_name = values_passed[("input_tereignis", j)]
                    tereignis_day = values_passed[("input_tereignis_tage", j)]
                    tereignis_month = values_passed[("input_tereignis_monate", j)]
                    tereignis_year = values_passed[("input_tereignis_jahre", j)]
                    tereignis_day_ende = values_passed[("input_tereignis_tage_ende", j)]
                    tereignis_month_ende = values_passed[("input_tereignis_monate_ende", j)]
                    tereignis_year_ende = values_passed[("input_tereignis_jahre_ende", j)]

                    list_single_entity_sets_tereignis.append(tereignis_name)
                    list_single_entity_sets_tereignis.append(tereignis_day)
                    list_single_entity_sets_tereignis.append(tereignis_month)
                    list_single_entity_sets_tereignis.append(tereignis_year)
                    list_single_entity_sets_tereignis.append(tereignis_day_ende)
                    list_single_entity_sets_tereignis.append(tereignis_month_ende)
                    list_single_entity_sets_tereignis.append(tereignis_year_ende)

                    list_final_entities_tereignis.append(list_single_entity_sets_tereignis)

            #Realisation_Datum_additions
            list_final_entities_realdatum = []
            if erase_flagged_realdatum == False:
                list_final_entities_realdatum.append(values_passed[("input_realdatum_tage")])
                list_final_entities_realdatum.append(values_passed[("input_realdatum_monate")])
                list_final_entities_realdatum.append(values_passed[("input_realdatum_jahre")])
                list_final_entities_realdatum.append(values_passed[("input_realdatum_zusatz")])
                list_final_entities_realdatum.append(values_passed[("realdatum_tage_ende")])
                list_final_entities_realdatum.append(values_passed[("realdatum_monate_ende")])
                list_final_entities_realdatum.append(values_passed[("realdatum_jahre_ende")])
                list_final_entities_realdatum.append(values_passed[("realdatum_ende_zusatz")])

            #Realisierung Orte
            realorte_list_final = []
            for r in range(len(realisierung_orte_suggest)):
                if r not in erase_flagged_realorte:
                    realisierung_ort = values_passed[("realort", r)]
                    realorte_list_final.append(realisierung_ort)
            
            realorte_string = ', '.join(realorte_list_final)
            realisierung_orte = realorte_string

            #Deskriptoren_Values Passing
            list_final_entities_desk = []
                        
            for j in range(len(self.text_input_transcr_search_desk)):
                list_single_entity_sets_desk = []
                if self.current_input_desk[j] != 'Freitext' and j not in erase_flagged_desk:
                    print('DEBUG DESKRIPTOREN Übergabe:', self.deskriptoren_all_data[j])
                    desk_name = self.deskriptoren_all_data[j][0]
                    desk_vok_id = self.deskriptoren_all_data[j][1]
                    desk_name_id = self.deskriptoren_all_data[j][2]
                    vok_typ = self.deskriptoren_all_data[j][6]

                    list_single_entity_sets_desk.append(desk_name)
                    list_single_entity_sets_desk.append(desk_vok_id)
                    list_single_entity_sets_desk.append(desk_name_id)
                    list_single_entity_sets_desk.append(vok_typ)
                    list_final_entities_desk.append(list_single_entity_sets_desk)

                    if self.current_input_desk == 'zugeordnete_klasse_flex':
                        list_single_entity_sets_desk = []
                        input_additional_desk = values_passed[("input_desk_klasse_chooser", j)]
                        single_values = input_additional_desk.split(' | ')
                        desk_name = single_values[0]
                        desk_vok_id = single_values[1]
                        index_data = self.deskriptoren_all_data[j][4].index(desk_vok_id)
                        desk_name_id = self.deskriptoren_all_data[j][5][index_data]
                        list_single_entity_sets_desk.append(desk_name)
                        list_single_entity_sets_desk.append(desk_vok_id)
                        list_single_entity_sets_desk.append(desk_name_id)
                        list_single_entity_sets_desk.append('klasse')
                        list_final_entities_desk.append(list_single_entity_sets_desk)

                    elif self.current_input_desk == 'zugeordnete_klasse_fix':
                        list_single_entity_sets_desk = []
                        desk_name = self.deskriptoren_all_data[j][3][0]
                        desk_vok_id = self.deskriptoren_all_data[j][4][0]
                        desk_name_id = self.deskriptoren_all_data[j][5][0]
                        
                        list_single_entity_sets_desk.append(desk_name)
                        list_single_entity_sets_desk.append(desk_vok_id)
                        list_single_entity_sets_desk.append(desk_name_id)
                        list_single_entity_sets_desk.append('klasse')
                        list_final_entities_desk.append(list_single_entity_sets_desk)

            #Tags_additions
            list_final_entities_tags = []

            for j in range(len(metatags_suggest)):
                
                tag_single = values_passed[("input_tags", j)]
                if tag_single != '' and tag_single != ' ' and j not in erase_flagged_tags:

                    tag_name = tag_single

                    list_final_entities_tags.append(tag_name)

            #Gattungen additions
            #mitwirkende_additions
            list_final_entities_gattungen = []
                        
            for j in range(len(gattungen_suggest)):
                if values_passed[('combo_gattungen', j)] != '' and values_passed[('combo_gattungen', j)] != ' ' and j not in erase_flagged_gatt:
                    list_final_entities_gattungen.append(values_passed[('combo_gattungen', j)])

            #Other_entities_clean returns
            konf_audio_gattungen_korrigiert = values_passed['combo_audioton']
            zusammenfassung_korrigiert = values_passed['input_zusammen']
            titel_korrigiert = values_passed['input_titel']
            list_final_entities_mitwirkende = [list_final_entities_mitwirkende, list_final_roles_mitwirkende]
            list_final_entities_urheber = [list_final_entities_urheber, list_final_roles_urheber]
            genre_korrigiert = values_passed['combo_genre']
            lese_abspielgeschwindigkeit = values_passed['combo_lese_abspiel']
            realisierung_typ_final_return = values_passed['realtyp']
            
        else: #Wenn Button "Nicht in HFDB übernehmen" gedrückt wurde
            list_final_entities_mitwirkende = False
            list_final_entities_urheber = False
            list_final_entities_tpers = False
            zusammenfassung_korrigiert = False
            titel_korrigiert = False
            list_final_entities_torte = False
            list_final_entities_tinst = False
            list_final_entities_sprachen = False
            konf_audio_gattungen_korrigiert = False
            genre_korrigiert = False
            lese_abspielgeschwindigkeit = False
            list_final_entities_gattungen = False
            list_final_entities_tereignis = False
            list_final_entities_desk = False
            list_final_entities_tags = False
            list_final_entities_realdatum = False
            realisierung_orte = False
            realisierung_typ_final_return = False

        return(list_final_entities_mitwirkende, list_final_entities_tpers, zusammenfassung_korrigiert, titel_korrigiert, list_final_entities_torte, list_final_entities_gattungen, konf_audio_gattungen_korrigiert, genre_korrigiert, lese_abspielgeschwindigkeit, list_final_entities_urheber, list_final_entities_tinst, list_final_entities_tereignis, list_final_entities_sprachen, list_final_entities_desk, list_final_entities_tags,list_final_entities_realdatum, realisierung_orte, realisierung_typ_final_return)



        