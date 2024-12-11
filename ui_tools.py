import PySimpleGUI as sg
import os.path
import pandas
import pickle
from config import temp_ordner_default

def entry(path_pickle_anr = 'path_pickle_last_anr.pickle'):
        """Defines and creates general setting window
        
        Args:
                path_pickle_anr(str): Path to pickle-file where last Archivnummer used is saved. Defines Archivnummer that is starting point for counting up with every new dataset coming in from there. Last used Archivnummer is saved in the pickle-file again.  

        Returns:
                values_passed(list): Complete Values coming from frontend. Contains File Paths for Backup Pickles, File Paths for source audios, Sample-Sizes, ANR-Starting Numbers etc.
        
        """
        #default_anr = 'ZBW21352'
        #Read Kompilations AK from Pickle
        with open(path_pickle_anr, 'rb') as handle:
                default_anr = pickle.load(handle)

        df_audioraum = pandas.read_excel('Excel_Lists_entities\\audioraumdarstellung_norm_ids.xlsx')
        reference_audioraumdarstellung = df_audioraum['langbez']

        layout = [[sg.Text('Willkommen zum DRA-Auto-Dokumentar')],
                [sg.Text('Gib den Pfad zum Ordner mit den zu prozessierenden Files ein')],
                [sg.In(size=(150, 1), enable_events=True, key="path"),
                sg.FolderBrowse(),],
                [sg.Text('ODER: Gib den Pfad zu einer Pickle-Datei mit gespeicherten Transkripten ein')],
                [sg.In(size=(150, 1), enable_events=True, key="pickle-path"),
                sg.FileBrowse(),],
                 
                 [
                sg.Text('Sample_Size in bit eingeben. Gebe nichts ein und es wird der Default-Wert 16 bit übernommen'),
                sg.In(size=(25, 1), enable_events=True, key="sample_size"),
            
                ]
                ,
                [
                sg.Text('Gib den Pfad zu einem Verzeichnis auf der Festplatte ein, wo Dateien temporär automatisch gespeichert werden können.')],
                [
                sg.In(size=(150, 1), enable_events=True, default_text = temp_ordner_default, key="temp_path"),
                sg.FolderBrowse(),
                ]
                ,
                [
                sg.Text('Globale Werte für alle Audiofiles festlegen.', pad=(5, (50, 10)), background_color = 'black', font=('Arial Bold', 20), key=('globale_werte_ueberschrift'))],
                [
                sg.Text('Audioraumdarstellung festlegen (kann auf Einzelfile-Ebene später korrigiert werden)', key=('audioraum_ueberschrift'))],
                [
                sg.Combo(list(reference_audioraumdarstellung), size=(25, 1), font=('Arial Bold', 10), default_value = 'Mono', expand_x=False, enable_events=True,  readonly=False, key=('audioraum_darstellung_global_suggest'))],
                [
                sg.Text('Erste ANR bestimmen, die angelegt werden soll', key=('ANR_ueberschrift'))],
                [sg.In(size=(75, 1), default_text = default_anr, enable_events=True, key="ANR_erste")],
                
                
                [
                sg.Button("OK"), sg.Button("Cancel")
            
                ]
                                       
                ]

        # Create the Window
        window = sg.Window('DRA-Auto-Dokumentar', layout, size=(1300, 500), resizable=True)
        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'OK': # if user closes window or clicks cancel

                values_passed = values
                
                break
            
            elif event == "pickle-path":
                if values["pickle-path"] != '':
                        window[('audioraum_darstellung_global_suggest')].update(disabled=True)
                        #window[("ANR_erste")].update(disabled=True)
                        #window[('globale_werte_ueberschrift')].update(disabled=True)
                        #window[('audioraum_ueberschrift')].update(disabled=True)
                if values["pickle-path"] == '':
                        window[('audioraum_darstellung_global_suggest')].update(disabled=False)
                        #window[("ANR_erste")].update(disabled=False)
                        #window[('globale_werte_ueberschrift')].update(disabled=False)
                        #window[('audioraum_ueberschrift')].update(disabled=False)
                 
            elif event == "Cancel":
                values_passed = None
                break

            
        window.close()
        return(values_passed)

#def text_correction(text_input):
       # """NOT USED RIGHT NOW: MAY BE DELETED. Window for correction of transcript before Metadate is extracted from transcript."""
       # l1 = sg.Text('Transcription Text - Mache hier Korrekturen, wenn gewünscht', font=('Arial Bold', 15), expand_x=True, justification='center')
       # t1 = sg.Multiline(text_input, enable_events=True, key='-INPUT-', expand_x=True, expand_y=True, justification='left')
        #b1 = sg.Button('Ok', key='-OK-', font=('Arial Bold', 20))
        #b2 = sg.Button('Exit', font=('Arial Bold', 20))
        #layout = [[l1], [t1], [b1, b2]]
        #window = sg.Window('Transkriptionskontrolle', layout, size=(1500, 1000))
       # while True:
        #        event, values = window.read()
                
        #        if event == sg.WIN_CLOSED or event == 'Exit':
        #                break
        #        elif event == '-OK-':
        #                return_values = values
        #                break
                
        #window.close()
        #return(return_values)

def authenticate(text_intro):
        """Authentication Window. Checks if User Credentials can be used to authenticate with HFDB-API.
        
        Args:
                text_intro(str): Information Text for Authentication window ("Welcome...")

        Returns:
                return_values(list): Values coming from Authentication Window, for example login-data used for authentication at API and writing data into HFDB with name of user and information which instance of HFDB to call.
        
        """
        l1 = sg.Text(text_intro, font=('Arial Bold', 15), expand_x=False, justification='left')
        l2 = sg.Text('Username', font=('Arial Bold', 15), expand_x=False, justification='left')
        i1 = sg.In(size=(50, 1), enable_events=True, key="username")
        l3 = sg.Text('Password', font=('Arial Bold', 15), expand_x=False, justification='left')
        i2 = sg.In(size=(50, 1), enable_events=True, key="password", password_char='*')
        l4 = sg.Text('HFDB-Instanz (drahfdb1 für Prod, drahfdb2 für Kons)', font=('Arial Bold', 15), expand_x=True, justification='left')
        r11 = sg.Radio("drahfdb2", "hfdb_radio", key = "drahfdb2", default=True, font=('Arial Bold', 15))
        r12 = sg.Radio("drahfdb1", "hfdb_radio", key = "drahfdb1", default=False, font=('Arial Bold', 15))
        b1 = sg.Button('Ok', key='-OK-', font=('Arial Bold', 20))
        b2 = sg.Button('Exit', font=('Arial Bold', 20))
        layout = [[l1], [l4,r11,r12], [l2,i1], [l3,i2], [b1, b2]]

        window = sg.Window('Authentifizierung', layout)
        
        while True:
                event, values = window.read()
                
                if event == sg.WIN_CLOSED or event == 'Exit':
                        print(event)
                        print ('Exit Event')
                        window.close()
                        return_values = 'Exit'
                        break
                elif event == '-OK-':
                        return_values = values
                        break
                
        window.close()
        return(return_values)

#def entity_correction(text_input, description_text):
        #l1 = sg.Text(description_text, font=('Arial Bold', 15), expand_x=False, justification='center')
        #t1 = sg.Multiline(text_input, enable_events=True, key='-INPUT-', expand_x=True, expand_y=True, justification='left')
        #b1 = sg.Button('Ok', key='-OK-', font=('Arial Bold', 20))
       # b2 = sg.Button('Exit', font=('Arial Bold', 20))
        #layout = [[l1], [t1], [b1, b2]]
        #window = sg.Window('Transkriptionskontrolle', layout,size=(1000, 1000))
        #while True:
                #event, values = window.read()
                
                #if event == sg.WIN_CLOSED or event == 'Exit':
                        #break
                #elif event == '-OK-':
                       # return_values = values
                       # break
                
        #window.close()
        #return(return_values)

def information_window(information_text, header_text):
        """Simple information window with individual text and without interaction except for "ok"-button and no value output
        
        Args:
                information_text(str): Main Text for window
                header_text(str): Header text for window
        """
        heading = [sg.Text(header_text)]
        list_lines = [heading]
        list_lines.append([sg.Text(information_text)])
        list_lines.append([sg.Button("Ok", key='-OK-')])
        layout = [list_lines]
        # Create the Window
        window = sg.Window('AK created!', layout)

        while True:
            event, values = window.read()
            if event == '-OK-' or sg.WIN_CLOSED: # if user closes window or clicks cancel
                
                break
        window.close()

#OLD Interface Parts from ui_ak_menu, that used to be imported there
#def decision_list(input_list, description_list, description_text, roles_found, reference_roles_list, window_text):
        
        #heading = [sg.Text(description_text)]
        #list_lines = [heading]
        #for i in range(len(input_list)):
               #list_lines.append([
                      #sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-', i), tooltip='Delete this item'),
                      #sg.Input(default_text = input_list[i], size=(25, 1), enable_events=True, key=("input", i)), 
                                  #sg.Combo(list(reference_roles_list), size=(25, 1), font=('Arial Bold', 10), default_value = list(roles_found)[i], expand_x=False, enable_events=True,  readonly=False, key=('combo', i)), 
                                  #sg.Text(description_list[i], font=('Arial Bold', 10), expand_x=False, justification='left', key=('description', i))])
                                  

        #list_lines.append([sg.Text('Weitere hinzufügen (Namen durch Kommas trennen)')])
        #list_lines.append([sg.Input(default_text = '', size=(40, 1), #enable_events=True, key="input_addition")]) 
        #list_lines.append([sg.Text('Rollen für weitere Personen hinzufügen (Bezeichnungen durch Kommas trennen)')])
        #list_lines.append([sg.Input(default_text = '', size=(40, 1), enable_events=True, key="input_roles_addition")])       
        #list_lines.append([sg.Button("In HFDB übernehmen", key='-OK-'), sg.Button("Cancel", key='Cancel')])
        #layout = list_lines

        # Create the Window
       # window = sg.Window(window_text, layout)
        #List of numbers of lines that are flagged for erase so data is not kept for ak creation
        #erase_flagged = []
        # Event Loop to process "events" and get the "values" of the inputs
        #while True:
            #event, values = window.read()
           # if event == '-OK-': 

                #values_passed = values
                
                #break
            
            #elif event[0] == '-DEL-':
                #print(event[1])
               # window[('-DEL-', event[1])].update(visible=False)
               # window[('input', event[1])].update(visible=False)
               # window[('combo', event[1])].update(visible=False)
               # window[('description', event[1])].update(visible=False)
               # erase_flagged.append(int(event[1]))

                                        
            #elif event == sg.WIN_CLOSED or event == "Cancel": # if user closes window or clicks cancel
               # values_passed = None
               # break

            
        #window.close()
        

      #  list_final_entities = []
       # list_final_roles = []
      #  if values_passed != None:
             #   print(values_passed)
             #   additional_values = values_passed["input_addition"]
              #  additional_values = additional_values.split(',')
              #  additional_roles = values_passed["input_roles_addition"]
              #  additional_roles = additional_roles.split(',')
              #  if len(additional_values)>0:
                      # list_final_entities = additional_values
                     #  list_final_roles = additional_roles
                
                #for j in range(len(input_list)):
                       # if values_passed[('input', j)] != '' and values_passed[('input', j)] != ' ' and j not in erase_flagged :
                               # list_final_entities.append(values_passed[('input', j)])
                               # list_final_roles.append(values_passed[('combo', j)]) 

       # else:
              #list_final_entities = None 
              #list_final_roles = None
        #return(list_final_entities, list_final_roles)

#def decision_list_small(input_list, description_list, description_text, window_text):
       # heading = [sg.Text(description_text)]
        #list_lines = [heading]
       # for i in range(len(input_list)):
               #list_lines.append([
                      #sg.B(sg.SYMBOL_X, border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=('-DEL-', i), tooltip='Delete this item'),
                      #sg.Input(default_text = input_list[i], size=(25, 1), enable_events=True, key=("input", i)), 
                                  #sg.Text(description_list[i], font=('Arial Bold', 10), expand_x=False, justification='left', key=('description', i))])
                                  

        #list_lines.append([sg.Text('Weitere hinzufügen (Namen durch Kommas trennen)')])
        #list_lines.append([sg.Input(default_text = '', size=(40, 1), #enable_events=True, key="input_addition")]) 
        #list_lines.append([sg.Button("In HFDB übernehmen", key='-OK-'), sg.Button("Cancel", key='Cancel')])
        #layout = list_lines

        # Create the Window
        #window = sg.Window(window_text, layout)
        #List of numbers of lines that are flagged for erase so data is not kept for ak creation
        #erase_flagged = []
        # Event Loop to process "events" and get the "values" of the inputs
        #while True:
           # event, values = window.read()
            #if event == '-OK-': 

              #  values_passed = values
                
               # break
            
           # elif event[0] == '-DEL-':
               # print(event[1])
               # window[('-DEL-', event[1])].update(visible=False)
               # window[('input', event[1])].update(visible=False)
              #  window[('description', event[1])].update(visible=False)
               # erase_flagged.append(int(event[1]))

                                        
          #  elif event == sg.WIN_CLOSED or event == "Cancel": # if user closes window or clicks cancel
              #  values_passed = None
             #   break

            
       # window.close()
        

       # list_final_entities = []
       # if values_passed != None:
               # print(values_passed)
               # additional_values = values_passed["input_addition"]
              #  additional_values = additional_values.split(',')

               # if len(additional_values)>0:
                      # list_final_entities = additional_values
                
               # for j in range(len(input_list)):
                       # if values_passed[('input', j)] != '' and values_passed[('input', j)] != ' ' and j not in erase_flagged :
                                #list_final_entities.append(values_passed[('input', j)])

        #else:
              #list_final_entities = None 

        #return(list_final_entities)