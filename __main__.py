import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from make_only_speech_file import make_audio_with_only_speech
from whisper_transcription_tools import transcribe_with_whisper
from spacy_ner import perform_spacy_analysis
from entity_correction_ndb_utilities import compare_with_ndb_vocabulary_persons
import ui_tools
from llm_processing_google import process_text_with_gemini
from make_ak_entry import make_proper_ak
from utils import call_hfdb
from process_media_with_gemini_ai_multimodal import work_with_gemini
from  make_amo_konf import make_amo_konf
from ui_geflecht_struktur import ak_geflecht_menu
from make_amo_konf import make_amo_konf
from make_abo import make_abo
from config import wsdl_path1, wsdl_path2, google_bucket_name, ref_ak_1, ref_ak_2


import pandas
import PySimpleGUI as sg


from datetime import datetime
import pickle #Kann Daten aus Python direkt als Bytes-artige Datei verpacken, die dann auch wieder aufgerufen und direkt weiterverwendet werden kann. Eignet sich sehr gut für Backups
#source_audio_files_ordner,list_files_filtered, transcripts_list
#print = sg.Print
import warnings
warnings.filterwarnings('ignore')
wsdl_path1 = wsdl_path1
wsdl_path2 = wsdl_path2
bucket_name_google = google_bucket_name
gattungen_source_list = 'Excel_Lists_entities\\gattungen_names.xlsx'
def __main__():
    #Gemini von Google ansprechen
    api_basic = process_text_with_gemini()
    api_basic_multimodal = work_with_gemini()
    client_hfdb = call_hfdb(wsdl_path1, wsdl_path2)
    #Für Benamsung von Backup-Files einmal das aktuelle Datum formatieren
    date = str(datetime.now())
    date = date.replace(':','-')
    date = date.replace('.','-')

    transcripts_list = []
    start_times_list = []#for audio_player
    transcripts_original_list_list = [] #for audio_player
    speech_files = [] #for audio_player
    values_to_start = ui_tools.entry()
    abo_start = values_to_start["ANR_erste"]
    print(values_to_start)
    if values_to_start['pickle-path'] != '':
        with open(values_to_start['pickle-path'], 'rb') as handle:
            data = pickle.load(handle)
        
        transcripts_list = data[2]
        source_audio_files_ordner = data[0]
        list_files_filtered = data[1]
        transcripts_original_list_list = data[3]
        start_times_list = data[4]
        speech_files = data[5]
        multimodal_data = data[6]
        temp_dir = data[7]
        audioraum_darstellung_global_suggest = data[8]

    else:
        data = []
        source_audio_files_ordner = values_to_start['path']
        temp_dir = values_to_start['temp_path']
        audioraum_darstellung_global_suggest = values_to_start['audioraum_darstellung_global_suggest']
        #abo_start = values_to_start["ANR_erste"]
        
        if '"' in source_audio_files_ordner or "'" in source_audio_files_ordner:
            source_audio_files_ordner = source_audio_files_ordner.replace('"', '')
            source_audio_files_ordner = source_audio_files_ordner.replace("'", '')
        
        sample_size = values_to_start['sample_size']
        
        list_files = os.listdir(source_audio_files_ordner)
      
        #Only use files that end with mp3 or wav
        list_files_filtered = []
        for file in list_files:
            if file.endswith('wav') or file.endswith('mp3'):
                list_files_filtered.append(file)
        
        if sample_size == '':
            sample_size = None
        elif len(sample_size) <3:
            sample_size = f'{sample_size}000'
            sample_size = int(sample_size)
        else:
            sample_size = int(sample_size)

        for j in range(len(list_files_filtered)):
            print(j)
            print('Transskript',j+1,' von ',len(list_files_filtered), 'wird erstellt')
        #name_file = source_audio_files_ordner.split("Zeitfunk")
            name_file = list_files_filtered[j]
            name_file = f'{source_audio_files_ordner}//{name_file}'
            print(name_file)
            
            print('Start Making Speech-Only-File')
            #Create Sub-Dir for YAMnet-Files
            dir_current = os.listdir(source_audio_files_ordner)
            if 'yamnet_files' not in dir_current:
                print('Yamnet-dir erstellen!')
                os.mkdir(f'{source_audio_files_ordner}//yamnet_files')
            sub_folder_yamnet = f'{source_audio_files_ordner}//yamnet_files'

            if sample_size == None:
                print(name_file)
                speech_file = make_audio_with_only_speech(name_file, temp_dir, sub_folder_yamnet, f'{date}temp{j}').make_file_only_speech()
            else:
                speech_file = make_audio_with_only_speech(name_file, temp_dir, sub_folder_yamnet, f'{date}temp{j}', sample_size).make_file_only_speech()
            speech_files.append(speech_file)
            print('Done Making Speech-Only-File')
            print('Loading Whisper Model')
            whisper_model = transcribe_with_whisper("large-v3")
            print('Start Whisper-Transcription')
            transcription_pure = whisper_model.make_transcription(speech_file)
            print('Done with Whisper-Transcription')
            transcription_sorted = whisper_model.split_json_to_lists(transcription_pure)
            text_sorted = transcription_sorted[0]
            start_sorted = transcription_sorted[1]
            start_times_list.append(start_sorted)#for audio_player
    
            end_sorted = transcription_sorted[2]
            no_speech_prob_sorted = transcription_sorted[3]
            print('Start SpaCy Analysis')
            spacy_ner = perform_spacy_analysis().perform_on_text_list(text_sorted)
            spacy_word_recognized = spacy_ner[0]
            spacy_word_art = spacy_ner[1]
            print('Done with SpaCy Analysis')
            print('Start with NDB-Comparison and Replacements (may take a while....)')
            text_source_ndb_replacements = compare_with_ndb_vocabulary_persons("Excel_Lists_entities\\NDB_Names_0224.xlsx",["Excel_Lists_entities\\sorted_list_260224_person_id_vornamen_nachnamen.xlsx", "Excel_Lists_entities\\sorted_list_260224_sentences_person_id.xlsx"]).make_new_text_with_replacements(text_sorted, spacy_word_recognized, spacy_word_art)
            print('Done with NDB-Comparison and Replacements')
            transcripts_original_list_list.append(text_source_ndb_replacements[1]) #for audio_player
            text_whole = api_basic.make_whole_text(text_source_ndb_replacements[1])
            transcripts_list.append(text_whole)
        
        multimodal_data = api_basic_multimodal.get_info_from_audios (bucket_name_google, list_files_filtered, source_audio_files_ordner,gattungen_source_list) #all data that is created by multimodal model

    transcripts_list_corrected = []
    for k in range(len(transcripts_list)):
        text_whole1 = transcripts_list[k] #ui_tools.text_correction(transcripts_list[k]) = Version mit Korrekturfenster - wird nicht benötigt aktuell
        transcripts_list_corrected.append(text_whole1)

    #Write Pickle File with Transscripts that then can be opened from disk to avoid re-transscripting
    if source_audio_files_ordner != None:

        package = [source_audio_files_ordner,list_files_filtered, transcripts_list, transcripts_original_list_list, start_times_list, speech_files, multimodal_data, temp_dir, audioraum_darstellung_global_suggest]

        #Compare existing pickle_files and only write new one if content is different

        dirlist = os.listdir(source_audio_files_ordner)
        write_new_pickle = True
        if 'backup_zwischen' not in values_to_start['pickle-path']: #Wenn es sich nicht um eine Teil-Pickle handelt, von der geladen wurde, weil dann definitiv schon eine Gesamt-Pickle existieren muss.
            write_new_pickle = False
        else:
            for file in dirlist:
                if file.endswith('.pickle'):
                    with open(f'{source_audio_files_ordner}\\{file}', 'rb') as handle:
                        data1 = pickle.load(handle)
                        
                    if data1 == package:
                        print('DEBUG Pickle: Found Existing Pickle!')
                        write_new_pickle =False
                        break

        if write_new_pickle == True:
            print('DEBUG Pickle: Write new Pickle!')
            with open(f'{source_audio_files_ordner}\\{date}_backup_auto_dok_transcripts.pickle', 'wb') as handle:
                pickle.dump(package, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    #LLM-Pipeline
    path_ref_ndb_person_list_source = "Excel_Lists_entities\\NDB_Names_0224.xlsx"
    path_ref_ndb_person_list_sorted = ["Excel_Lists_entities\\sorted_list_260224_person_id_vornamen_nachnamen.xlsx","Excel_Lists_entities\\sorted_list_260224_sentences_person_id.xlsx"]
    path_ref_ndb_orte_list_source = "Excel_Lists_entities\\NDB_Geo_180324.xlsx"
    path_ref_ndb_orte_list_sorted = None
    
    text_whole1 = transcripts_list_corrected
    #print('New_Text:', text_whole1)
    #print('Debug Area')
    #print(source_audio_files_ordner)
    ak_maker = make_proper_ak(ref_ak_1, ref_ak_2, client_hfdb)
    konf_amo_maker = make_amo_konf(client_hfdb, source_audio_files_ordner)
    abo_maker = make_abo(abo_start, client_hfdb)

    #Listen erstellen oder übernehmen
   
    if len(data) > 9: #Wenn es sich um eine Zwischenspeicherung handelt, die über pickle geladen wurde
            all_aks = data[9]
            all_amos = data[10]
            all_konfs = data[11]
            all_abos = data[12]
            all_anrs = data[13]
            all_files = data[14]
            print('All Aks:', all_aks)
    else:
        all_aks = []
        all_amos = []
        all_konfs = []
        all_abos = []
        all_anrs = []
        all_files = []

    calc_number = 0 #ABO Fortzählungsnummer

    #Make Ordner für Pickle des aktuellen Stands
    try:
        os.mkdir(f'{source_audio_files_ordner}\\Pickle_Backups')
    except FileExistsError:
        pass
    
    #Calculate starting point for correct file_naming
    starting_point = 0
    if 'backup_zwischen' in values_to_start['pickle-path']:
        starting_point = len(all_aks)
        print('Starting_Point:', starting_point)
    for t in range(len(list_files_filtered)):
        status_geflecht_final, ak_id_kompilation_aktuell, kompilationstyp = ak_geflecht_menu(source_audio_files_ordner, list_files_filtered[t])
        

        print('list_files_filtered:', list_files_filtered)
        if status_geflecht_final != None:#Wenn beim Geflecht nicht "Nicht in HFDB übernehmen" gedrückt wurde
            #Create AKs (außer bei V3) und bei Kompilationen auch schon AMOs
            ak_single_new, konf_audioraum, lese_abspielgeschwindigkeit, AMO_komp_id, konf_komp_audioraum, lese_abspielgeschwindigkeit_audioraum, ak_komp_id = ak_maker.main_ak_maker(ak_id_kompilation_aktuell, status_geflecht_final, transcripts_original_list_list[t], multimodal_data[0][t], source_audio_files_ordner, speech_files[t], "Excel_Lists_entities\\beteiligte_funktionen_norm_db.xlsx", "Excel_Lists_entities\\beteiligte_funktionen_urheber_norm_db.xlsx", start_times_list[t], list_files_filtered[t], audioraum_darstellung_global_suggest, kompilationstyp)
            
            #Create restliche AMOs und Konfektionierungen
            if ak_single_new != False: #Wenn in Anlegemaske nicht "Nicht in HFDB übernehmen" gedrückt wurde
                amo_id, konf_id, ak_korpus_id = konf_amo_maker.create_amos_konfs_for_ak(status_geflecht_final, list_files_filtered[t], ak_single_new, konf_audioraum, lese_abspielgeschwindigkeit, konf_komp_audioraum, lese_abspielgeschwindigkeit_audioraum, ak_komp_id, AMO_komp_id)

                #Create ABOs
                if amo_id != None:
                    abo_id, anr = abo_maker.create_abo(calc_number, amo_id)
                    calc_number +=1
                else:
                    print('Kein neues AMO, keine neue ANR und kein neues ABO)')
                    abo_id = 'Bereits vorhanden'
                    anr = 'Bereits vorhanden'

                #Schreibe Listen mit den einzelnen Entitäts-IDs auf Korpus-Ebene (wo Korpus nicht angelegt (V2), nehme Kompilations-AK-ID)
                all_aks.append(ak_korpus_id)
                all_amos.append(amo_id)
                all_konfs.append(konf_id)
                all_abos.append(abo_id)
                all_anrs.append(anr)
                all_files.append(list_files_filtered[t])

                #Schreibe Zwischen-Pickle mit aktuellem Stand der noch anzulegenden Audios und Excel-Liste mit bereits angelegten Daten
                
                package1 = [source_audio_files_ordner, list_files_filtered[(t+1):], transcripts_list[(t+1):], transcripts_original_list_list[(t+1):], start_times_list[(t+1):], speech_files[(t+1):], [multimodal_data[0][(t+1):]], temp_dir, audioraum_darstellung_global_suggest, all_aks, all_amos, all_konfs, all_abos, all_anrs, all_files]
                print('PACKAGE all Aks:', package1[9])
                print('t:', t)
                print('len(ListFilesFiltered):', len(list_files_filtered))
                with open(f'{source_audio_files_ordner}\\Pickle_Backups\\backup_zwischen_{t+1+starting_point}_von_{len(list_files_filtered)+starting_point}.pickle', 'wb') as handle:
                    pickle.dump(package1, handle, protocol=pickle.HIGHEST_PROTOCOL)

                df_zu_schreiben = pandas.DataFrame({'Neue AKs':all_aks,
                                        'Neue AMOs': all_amos,
                                        'Konfs': all_konfs,
                                        'ABOs': all_abos,
                                        'ANRs':  all_anrs,
                                        'Source_File': all_files}) 
    
                df_zu_schreiben.to_excel(f'{source_audio_files_ordner}\\Pickle_Backups\\DRA_auto_dok_ergebnis_ak_uebersicht_{t+1+starting_point}_von_{len(list_files_filtered)+starting_point}.xlsx')
                print('Pfad Übersicht1:', f'{source_audio_files_ordner}\\Pickle_Backups\\DRA_auto_dok_ergebnis_ak_uebersicht_{t+1+starting_point}_von_{len(list_files_filtered)+starting_point}.xlsx')

    df_zu_schreiben = pandas.DataFrame({'Neue AKs':all_aks,
                                        'Neue AMOs': all_amos,
                                        'Konfs': all_konfs,
                                        'ABOs': all_abos,
                                        'ANRs':  all_anrs,
                                        'Source_File': all_files}) 
    try:
        df_zu_schreiben.to_excel(f'{source_audio_files_ordner}\\{date}_DRA_auto_dok_ergebnis_ak_uebersicht.xlsx')
        print('Pfad Übersicht1:', f'{source_audio_files_ordner}\\{date}_DRA_auto_dok_ergebnis_ak_uebersicht.xlsx')
    except:
        df_zu_schreiben.to_excel(f'{date}_DRA_auto_dok_ergebnis_ak_uebersicht.xlsx')
        print('Pfad Übersicht2:', f'{date}_DRA_auto_dok_ergebnis_ak_uebersicht.xlsx')

    ui_tools.information_window(f'Glückwunsch, es wurden {len(all_aks)} neue AK(s) erstellt', f'Neue AKs: {all_aks}')

if __name__ == "__main__": 
    __main__()