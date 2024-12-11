import PySimpleGUI as sg
from audioplayer import audio_playback
import pickle


def ak_geflecht_menu(path_audiofiles, audiofile_name, path_pickle_last_komp_ak = 'kompilations_ak.pickle'):
    """Vor die AK-Kreation vorgeschaltetes Menü, das steuert wie das Geflecht um die AK ausehen soll
        Args:
            path_audiofiles(str): Path where source audiofiles are stored (from Input at the beginning)
            audiofile_name(str): Name of the original audiofile input
            path_pickle_last_komp_ak(str): ID of the last Kompilations-AK used, defaults to relative standard file path
        
        Returns:
            status_geflecht_final(str): Standardized Geflechtstruktur status for upcoming AK creation
            kompilations_ak(str): ID for Kompilation that new  AK should be part of if applicable.
            komp_typ_weitergabe(str): Defines ststua for Kompilationstyp (like MOIN, KONZ, SEND) 
    
    
    """
    #Read Kompilations AK from Pickle
    with open(path_pickle_last_komp_ak, 'rb') as handle:
            kompilations_ak = pickle.load(handle)
    #Temp for first init:
    #kompilations_ak= '1234567'

    column_1 = []
    list_lines = []
    
    l1_titel = sg.Text('Geflechtstruktur definieren', font=('Arial Bold', 20), background_color = 'black', expand_x=False, justification='center')
    t1_titel = sg.Text(f'Palim!, Palim! Ich bin audiofile {audiofile_name}. Wie möchtest Du mich einordnen?', font=('Arial', 14), expand_x=False, justification='left')

    column_1.append([l1_titel])
    column_1.append([t1_titel])

    #Audioplayer init Gesamtfile
    l2_titel = sg.Text('Noch mal reinhören?',pad=(5, (50, 10)), font=('Arial Bold', 20), background_color = 'black', expand_x=False, justification='center')
    audioplayer1 = audio_playback(f'{path_audiofiles}\\{audiofile_name}')
   
    player_line = [sg.Button("Play", key='Play_File'), sg.Button("Pause", key='Pause_File'), sg.Button("Stop", key='Stop_File')] #, sg.Button("Resume", key='Resume_File')
    slider = [sg.Slider((0, audioplayer1.get_duration()), orientation='horizontal', key='-SL-', enable_events=True, disable_number_display = True, size = (100, 20)), sg.Text(audioplayer1.format_time(0), background_color = 'black', font=('Arial Bold', 20), key='current_time')]
    
    column_1.append([l2_titel])    
    column_1.append(player_line)
    column_1.append(slider)

    #Radiobuttons Struktureinordnung
    l3_titel = sg.Text('Struktur festlegen', font=('Arial Bold', 20), pad=(5, (50, 10)), background_color = 'black', expand_x=False, justification='center')
    layout_struktur = [sg.Radio('Als Korpus anlegen', group_id=1, default=True, key = 'radio_korpus', enable_events=True), sg.Radio('Als Kompilation anlegen', group_id=1, key = 'radio_komp', enable_events=True), sg.Radio('Als KORPUS zu einer Kompilation anlegen', group_id=1, key = 'radio_teil_komp', enable_events=True, )]

    column_1.append([l3_titel])
    column_1.append(layout_struktur)

    #Struktur ok
    #column_1.append([sg.Button("Ok", key='_ok_struktur')])

    #Zweite Ebene wenn Teil einer Kompilation
    layout_struktur_komp_2 = [sg.Radio('Neue Kompilation anlegen', group_id=2, default=True, key = 'radio_neue_komp', visible=False, enable_events=True), sg.Radio('Zu vorhandener Kompilation hinzufügen', group_id=2, key = 'radio_vorhandene_komp', visible = False, enable_events=True)]

    column_1.append(layout_struktur_komp_2)
    #Kompilation 2. Ebene ok
    #column_1.append([sg.Button("Ok", key='_ok_komp_ebene_2', visible = False)])

    #Dritte Ebene wenn zu Vorhandener Kompilation hinzufügen gewählt ist
    column_1.append([sg.Text('ID der Kompilations-AK eingeben, zu der die neue Korpus-AK hinzugefügt werden soll', key = 'ID_AK_komp', visible = False)])
    column_1.append([sg.Input(default_text = kompilations_ak, size=(40, 1), enable_events=True, key="ak_komp_vorhanden", visible = False)])

    #Wenn eine neue Kompilation angelegt wird, noch den Kompilationstyp (Feld "kreationstyp" in der Datenstruktur)
    list_kompilationstypen = ['KONZ Konzert / Öffentliche Veranstaltung', 'MOIN Medienobjektinhalt', 'SEND Sendung']
    column_1.append([sg.Text('Kompilationstyp händisch festlegen', key=('Kompilationstyp_ueberschrift'), visible=False)])
    column_1.append([sg.Combo(list_kompilationstypen, size=(25, 1), font=('Arial Bold', 10), default_value = 'MOIN Medienobjektinhalt', expand_x=False, enable_events=True,  readonly=False, key=('kompilationstyp'), visible=False)])
    
    #Spaltenlayout des Inputs zum Gesamtlayout hinzufügen
    list_lines.append([sg.Column(column_1, scrollable=True, expand_x=True, expand_y=True)]) 
    list_lines.append([sg.Button("Ok", key='_ok_', visible = True), sg.Button("Nicht in HFDB übernehmen", key='hfdb_nein'), sg.Button("Prozess abbrechen", key='Cancel')])
    layout = list_lines
    # Create the Window
    window = sg.Window('Einstellungen HFDB-Geflecht', layout, size=(1100, 700), resizable=True)

    while True:
        event, values = window.read()
            
        #Radiobutton Logik
        if event == 'radio_korpus': 
            window[('radio_neue_komp')].update(visible=False) #Zweite Ebene deaktivieren
            window[('radio_vorhandene_komp')].update(visible=False) #Zweite Ebene deaktivieren
            window[('ID_AK_komp')].update(visible=False) #Dritte Ebene deaktivieren
            window[("ak_komp_vorhanden")].update(visible=False) #Dritte Ebene deaktivieren
            window[('Kompilationstyp_ueberschrift')].update(visible=False) #Kompilationstyp aktivieren
            window[('kompilationstyp')].update(visible=False) #Kompilationstyp aktivieren
        
        if event == 'radio_komp':
            window[('radio_neue_komp')].update(visible=False) #Zweite Ebene deaktivieren
            window[('radio_vorhandene_komp')].update(visible=False) #Zweite Ebene deaktivieren
            window[('ID_AK_komp')].update(visible=False) #Dritte Ebene deaktivieren
            window[("ak_komp_vorhanden")].update(visible=False) #Dritte Ebene deaktivieren
            window[('Kompilationstyp_ueberschrift')].update(visible=True) #Kompilationstyp aktivieren
            window[('kompilationstyp')].update(visible=True) #Kompilationstyp aktivieren

        if event == 'radio_teil_komp':
            #window[('radio_teil_komp')].update() #Radio bestehen lassen in erster Ebene
            window[('radio_neue_komp')].update(visible=True) #Zweite Ebene aktivieren
            window[('radio_vorhandene_komp')].update(visible=True) #Zweite Ebene aktivieren
            window[('ID_AK_komp')].update(visible=False) #Dritte Ebene deaktivieren
            window[("ak_komp_vorhanden")].update(visible=False) #Dritte Ebene deaktivieren
            if values['radio_vorhandene_komp'] == True:
                window[('ID_AK_komp')].update(visible=True) #Dritte Ebene aktivieren
                window[("ak_komp_vorhanden")].update(visible=True) #Dritte Ebene aktivieren
                window[('Kompilationstyp_ueberschrift')].update(visible=False) #Kompilationstyp deaktivieren
                window[('kompilationstyp')].update(visible=False) #Kompilationstyp deaktivieren
            elif values['radio_neue_komp'] == True:
                window[('ID_AK_komp')].update(visible=False) #Dritte Ebene aktivieren
                window[("ak_komp_vorhanden")].update(visible=False) #Dritte Ebene aktivieren
                window[('Kompilationstyp_ueberschrift')].update(visible=True) #Kompilationstyp deaktivieren
                window[('kompilationstyp')].update(visible=True) #Kompilationstyp deaktivieren

        if event == 'radio_vorhandene_komp':
            #window[('radio_vorhandene_komp')].update(default = True) #Radio bestehen lassen in zweiter Ebene
            window[('ID_AK_komp')].update(visible=True) #Dritte Ebene aktivieren
            window[("ak_komp_vorhanden")].update(visible=True) #Dritte Ebene aktivieren
            window[('Kompilationstyp_ueberschrift')].update(visible=False) #Kompilationstyp deaktivieren
            window[('kompilationstyp')].update(visible=False) #Kompilationstyp aktivieren
            
        if event == 'radio_neue_komp':
            window[('ID_AK_komp')].update(visible=False) #Dritte Ebene deaktivieren
            window[("ak_komp_vorhanden")].update(visible=False) #Dritte Ebene deaktivieren
            window[('Kompilationstyp_ueberschrift')].update(visible=True) #Kompilationstyp aktivieren
            window[('kompilationstyp')].update(visible=True) #Kompilationstyp aktivieren


        #Audioplayyer Logik
        if event == 'Play_File': 
            audioplayer1.play_file()
            audioplayer1.scroll_playback_to_second(int(values['-SL-']))
            position = audioplayer1.get_position()
            window['-SL-'].update(value = position)
            window['current_time'].update(audioplayer1.format_time(position))

      
        if event == 'Pause_File': 
            audioplayer1.pause_playback()
            position = audioplayer1.get_position()
            window['-SL-'].update(value = position)
            window['current_time'].update(audioplayer1.format_time(position))


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

        #Wenn fertig
        if event == '_ok_': 
            values_passed = values
            audioplayer1.stop_playback()
            break

        elif event == 'hfdb_nein': 
            values_passed = False
            audioplayer1.stop_playback()
            break

        elif event == sg.WIN_CLOSED or event == "Cancel": # if user closes window or clicks cancel
            audioplayer1.stop_playback()
            values_passed = None
            window.close()
            break

        #Aus den einzelnen Stati einen Endstatus zaubern
    status_geflecht_final = None
    kompilations_ak = None
    komp_typ_weitergabe = None
    if values_passed != False:
        if values_passed['radio_korpus'] == True:
            status_geflecht_final = 'new_korpus' #V1
        elif values_passed['radio_komp'] == True:
            status_geflecht_final = 'new_komp' #V2
        elif values_passed['radio_neue_komp'] == True:
            status_geflecht_final = 'new_komp_no_ki' #V3
        elif values_passed['radio_vorhandene_komp'] == True:
            status_geflecht_final = 'add_to_vorhandene_komp' #V4
    

        #Write current Kompilations-AK to pickle
        kompilations_ak = values_passed['ak_komp_vorhanden']
        with open(path_pickle_last_komp_ak, 'wb') as handle:
                pickle.dump(kompilations_ak, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
        #Define Kompilations-Weitergabe Variable
        kompilationstyp_roh = values_passed['kompilationstyp']

        if kompilationstyp_roh == 'KONZ Konzert / Öffentliche Veranstaltung':
            komp_typ_weitergabe = 'KONZ'

        elif kompilationstyp_roh == 'MOIN Medienobjektinhalt':
            komp_typ_weitergabe = 'MOIN'
        
        elif kompilationstyp_roh == 'SEND Sendung':
            komp_typ_weitergabe = 'SEND'

    window.close()
    return(status_geflecht_final, kompilations_ak, komp_typ_weitergabe)