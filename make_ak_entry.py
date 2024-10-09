import ui_tools as ui
from ui_ak_menu import ui_correction
from entity_correction_ndb_utilities import compare_with_ndb_vocabulary_persons, compare_with_ndb_vocabulary_orte
import pandas
import copy
from llm_processing_google import process_text_with_gemini
from get_genre import get_genre
from norm_db_entity_linking import norm_db_entity_linking
# Schnittstelle ansprechen mit zeep
import urllib3
from copy import deepcopy
from zeep.transports import Transport
from zeep import Client
from requests.auth import HTTPBasicAuth
from requests import Session
import copy
from datetime import datetime
import pickle

class make_proper_ak():
    """Takes found raw data and combines it to proper AK"""

    def __init__(self, ref_ak, ref_ak_2, hfdb_client):
        """
        Args:
            ref_ak(str): URI of reference AK that is used to copy certain elements from it for creating an own new AK. Used for Urheber, Mitwirkende and Titel, so ref_ak should have good and clean entries in these data points.
            ref_ak_2(str): URI of second reference AK, to copy certain elements from it. Used for Orte, Zusammenfassunge, Gattungen and general AK structure
            hfdb_client: HFDB-API-Client Zeep Instance.
        
        
        """
        self.ref_ak = ref_ak
        self.ref_ak_2 = ref_ak_2
        #self.wsdl_path = wsdl_path
        #self.call_hfdb_init = self.call_hfdb()
        self.hfdb_client = hfdb_client[0]
        self.instance = hfdb_client[1]
        self.google_api = process_text_with_gemini()

    def decide_mitwirkende_or_topic(self, transcript):
        """Decides if a person is Mitwirkender or themaPerson
        Args:
            transcript(json or string): Transcript as original json-format or string format.

        Returns:
            persons_mitwirkend (list): Lists of names of persons from class Mitwirkende that take part in transcript text
            persons_mitwirkend_description (list): List of decirptions for persons in persons_mitwirkend
            persons_topics (list): Lists of names of persons from class themaPerson that take part in transcript text
            persons_topics_description (list): List of decirptions for persons in persons_topics

        """
        persons_mitwirkend = []
        persons_mitwirkend_description = []
        persons_topics = []
        persons_topics_description = []
        try:
            transcript = transcript['-INPUT-']
        except TypeError:
            transcript = transcript
        #print(transcript)
        persons = self.google_api.find_persons(transcript)
        #print(persons)
        self.proper_list_persons = self.google_api.make_proper_list_from_persons(persons)
        print('DEBUG PERSONS-LIST_RETURN:', self.proper_list_persons)
        list_persons_raw = self.proper_list_persons[0]
        print(list_persons_raw)
        list_bezeichnungen = self.proper_list_persons[1]
        print(list_bezeichnungen)

        for i in range(len(list_persons_raw)):
            cat_person_raw = self.google_api.is_person_speaker_or_topic(transcript, list_persons_raw[i])
            print('DEBUG PERSON-Rolle-Return:', cat_person_raw)
            if cat_person_raw == 'Thema':
                persons_topics.append(list_persons_raw[i])
                try:
                    persons_topics_description.append(list_bezeichnungen[i])
                except IndexError:
                    persons_topics_description.append(None)
            elif cat_person_raw == 'Sprecher':
                persons_mitwirkend.append(list_persons_raw[i])
                try:
                    persons_mitwirkend_description.append(list_bezeichnungen[i])
                except IndexError:
                    persons_mitwirkend_description.append(None)

        return(persons_mitwirkend, persons_mitwirkend_description, persons_topics, persons_topics_description)
    
    def decide_is_urheber(self, transcript):
        """Decide from Persons Raw List if a person is a Urheber - Persons-List is defined with def decide_mitwirkende_or_topic before this.
        Args:
            transcript(json or string): Transcript as original json-format or string format.
        
        Returns:
            persons_urheber (list): Persons that are recognized as Urheber
            persons_urheber_descriptions (list): LLM-generated descriptions of Urheber

        """
        persons_urheber = []
        persons_urheber_descriptions = []
        try:
            transcript = transcript['-INPUT-']
        except TypeError:
            transcript = transcript

        list_urheber_raw = self.proper_list_persons[0]
        list_bezeichnungen = self.proper_list_persons[1]

        for i in range(len(list_urheber_raw)):
            urheber_yes_no = self.google_api.is_person_urheber(transcript, list_urheber_raw[i])
            if urheber_yes_no == True:
                persons_urheber.append(list_urheber_raw[i])
                try:
                    persons_urheber_descriptions.append(list_bezeichnungen[i])
                except IndexError:
                    persons_urheber_descriptions.append(None)
            elif urheber_yes_no == False:
                pass

        return(persons_urheber, persons_urheber_descriptions)
    
    def make_urheber_suggest(self, transcript, urheber_filtered, urheber_descriptions, path_list_all_entities_available):
        """Make LLM Suggestions for Urheber
        
        Args:
            transcript (str): Original transcript
            urheber_filtered(list): List of urheber that were extracted before.
            urheber_descriptions(list): Descriptions of urheber from urheber_filtered
            path_list_all_entities_available(str): Path to excel with list of possible HFDB roles that urheber could have

        Returns:
            list_persons_raw (list): List of Person Names found.
            list_bezeichnungen (list): List of descriptions from LLM for list_persons_raw
            list_types_entities_given (list): Roles for single persons according to LLM decision
            list(langbez)(list): List of possible roles, that are applicable for person list here.
            ndb_suggests_list(list of lists): Package suggestion data coming from Normdatenbank for list of persons
        
        """
        list_persons_raw = urheber_filtered
        #print(list_persons_raw)
        list_bezeichnungen = urheber_descriptions
        #Norm-DB-Abfrage nach Personen
        norm_db_linker = norm_db_entity_linking()
        ndb_suggests_list = []
        for p in range(len(urheber_filtered)):
            ndb_suggests = norm_db_linker.make_name_suggestions_from_LLM_suggestions(list_persons_raw[p], list_bezeichnungen[p])
            ndb_suggests_list.append(ndb_suggests)

        list_types_entities = pandas.read_excel(path_list_all_entities_available)
        langbez = list_types_entities['Langbezeichnung']
        list_types_entities_given = self.google_api.make_roles_list(transcript, list_persons_raw, 'Excel_Lists_entities\\beteiligte_funktionen_urheber_norm_db.xlsx')

        return(list_persons_raw, list_bezeichnungen, list_types_entities_given, list(langbez), ndb_suggests_list)
    
    def make_urheber_entry(self, liste_urheber_korrigiert, path_list_all_entities_available):
        """Make AK-Entry for Mitwirkende Korrigierte Fassung

        Args:
            liste_urheber_korrigiert (list): List of Urheber coming from frontend, that are chosen by user.
            path_list_all_entities_available (str): Path to source list for NDB data for roles of single Urheber

        Returns:
            list_urheber_hfdb_ready(json_like): json-like object that is part of final HFDB-object and can be injected in those.
        
        """
        
        client = self.hfdb_client
        referenz_ak = client.service.getAK(self.ref_ak)
        urheber_ref = referenz_ak.urheber[0]
        list_types_entities = pandas.read_excel(path_list_all_entities_available)
        t_kurzbez = list_types_entities['Technische Kurzbezeichnung']
        langbez = list_types_entities['Langbezeichnung']
        
        wert_id = list_types_entities['Wert_ID']

        #ndb_comparison_ref = compare_with_ndb_vocabulary(path_ref_ndb_person_list_source, path_ref_ndb_person_list_sorted)

        #proper_name = ndb_comparison_ref.compare_direct_with_proper_list(list_persons_raw)
        #liste_personen_korrigiert = ui.decision_list(list_persons_raw, list_bezeichnungen, 'Korrigiere oder lösche die Personen, die in die HFDB sollen', list_types_entities_given, list(langbez), 'Personen Mitwirkende Import')
        #print('NDB-Comparison')
        #print('NDB-Comparison done!')
        list_urheber_hfdb_ready = []
        if liste_urheber_korrigiert != False:
            
            for j in range(len(liste_urheber_korrigiert[0])):
                if liste_urheber_korrigiert[0][j] != '':
                    urheber_single = copy.deepcopy(urheber_ref)
                    if liste_urheber_korrigiert[0][j][0] != None:
                        person_id = liste_urheber_korrigiert[0][j][0].split('-')[1]
                        urheber_single.person.normIdPerson = f'http://hfdb.ard.de/normdb/Person?id={person_id}'
                    else:
                        person_id = None
                        urheber_single.person.normIdPerson = None

                    if urheber_single.person.normIdPerson != None:
                        
                        urheber_single.person.name = liste_urheber_korrigiert[0][j][2]
                        urheber_single.person.vorname = liste_urheber_korrigiert[0][j][3]
                        person_name_id = liste_urheber_korrigiert[0][j][1].split('-')[1]
                        urheber_single.person.normIdName = f'http://hfdb.ard.de/normdb/PersonenName?id={person_name_id}'
                    else:
                        if len(liste_urheber_korrigiert[0][j][2].split(' '))>1:
                            urheber_single.person.vorname = liste_urheber_korrigiert[0][j][2].split(' ')[0]    
                            urheber_single.person.name = liste_urheber_korrigiert[0][j][2].replace(f'{urheber_single.person.vorname} ', '')
                            urheber_single.person.normIdName = None
                        else:
                            urheber_single.person.vorname = None    
                            urheber_single.person.name = liste_urheber_korrigiert[0][j][2]
                            urheber_single.person.normIdName = None
                    
                    #Geburts und Todesdatum rauswerfen!
                    urheber_single.person.geburtsdatum = None
                    urheber_single.person.todesdatum = None

                    print('Personen korrigiert:', liste_urheber_korrigiert)
                    bezeichnung_funktion_index = list(langbez).index(liste_urheber_korrigiert[1][j])
                    langbezeichnung_funktion = langbez[bezeichnung_funktion_index]
                    kurzbezeichnung_funktion = t_kurzbez[bezeichnung_funktion_index]
                    wert_id_funktion = wert_id[bezeichnung_funktion_index]

                    urheber_single.funktion.kurzbezeichnung = kurzbezeichnung_funktion
                    urheber_single.funktion.langbezeichnung = langbezeichnung_funktion
                    urheber_single.funktion.normId = f'http://hfdb.ard.de/normdb/Wert?id={wert_id_funktion}'
                    list_urheber_hfdb_ready.append(copy.deepcopy(urheber_single))
        else:
            list_urheber_hfdb_ready = False
        
        return(list_urheber_hfdb_ready)


    def make_thema_personen_suggest(self, thema_personen_roh, thema_personen_decriptions_llm, list_urheber_raw):
        """Make LLM Suggestion for themaPersonen
        
        Args:
            thema_personen_roh (list): List of themaPersonen entries from Large Language models - list of their names.
            thema_personen_decriptions_llm (list): List of descriptions for thema_personen_roh entries
            list_urheber_raw (list): List of Urheber from previous Extractions. If person is Urheber, it should not be themaPerson any more

        Returns:
            list_persons_raw (list): List of extracted Person Names without link to Norm-Datenbank
            list_bezeichnungen (list): List of descriptions of persons as extracted by LLM
            ndb_suggests_list (list of lists): List with NDB-Data from comparison with NDB
        """
        #persons = self.google_api.find_persons(transcript)
        #print(persons)
        #proper_list_persons = self.google_api.make_proper_list_from_persons(persons)
        #print(proper_list_persons)
        list_persons_raw = []
        list_bezeichnungen = []
        for i in range(len(thema_personen_roh)):
            if thema_personen_roh[i] != '' and thema_personen_roh[i] not in list_urheber_raw:
                list_persons_raw.append(thema_personen_roh[i])
                list_bezeichnungen.append(thema_personen_decriptions_llm[i])
        #print(list_persons_raw)
        #Norm-DB-Abfrage nach Personen
        norm_db_linker = norm_db_entity_linking()
        ndb_suggests_list = []
        print('DEBUG GEMINI_Rückgabe_themaPers:', list_persons_raw)
        for p in range(len(list_persons_raw)):
            if list_persons_raw[p] != None and "None" not in list_persons_raw[p]:
                print('DEBUG GEMINI_Rückgabe_themaPers:', list_persons_raw[p])
                ndb_suggests = norm_db_linker.make_name_suggestions_from_LLM_suggestions(list_persons_raw[p], list_bezeichnungen[p])
                ndb_suggests_list.append(ndb_suggests)


        return(list_persons_raw, list_bezeichnungen, ndb_suggests_list)

    
    def make_thema_personen_korrigiert_hfdb(self, hfdb_ref, liste_personen_korrigiert):
        """Creates final part of HFDB-Entry
        
        Args:
            hfdb_ref (list): List of themaPersonen entries from Large Language models - list of their names.
            liste_personen_korrigiert (list): List of descriptions for thema_personen_roh entries
            
        Returns:
            list_thema_person_hfdb_ready(json_like): Parts of final HFDB entry for themaPersonen
        
        """
        #liste_personen_korrigiert = ui.decision_list_small(list_persons_raw, list_bezeichnungen, 'Korrigiere oder lösche die Personen, die in die HFDB sollen', 'Thema Person Import')
        #print('Korrigierte Personenliste')
        #print(liste_personen_korrigiert)
        
       # print('ndb_comparison_result')
       # print(ndb_comparison_ref)
        list_thema_person_hfdb_ready = []
        client = self.hfdb_client
        referenz_ak = client.service.getAK(hfdb_ref)
        thema_personen_basic = referenz_ak.themaPersonen[0]

        if liste_personen_korrigiert != False: #Wenn "Nicht in HFDB übernehmen" Button gedrückt wurde, dann ist Wert "False"...
            print('Liste_Roh_korrigiert_Thema_Personen:', liste_personen_korrigiert)
            for j in range(len(liste_personen_korrigiert)):
            # print('Abgleich:', liste_personen_korrigiert[j])
                if liste_personen_korrigiert[j] != '':
                    thema_person_single = copy.deepcopy(thema_personen_basic)
                    proper_name = liste_personen_korrigiert[j][0]
                # print('Proper Name:', proper_name)
                    if proper_name != None:
                        person_id = liste_personen_korrigiert[j][0].split('-')[1]
                        thema_person_single.normIdPerson = f'http://hfdb.ard.de/normdb/Person?id={person_id}'
                    else:
                        person_id = None
                        thema_person_single.normIdPerson = None
                    if thema_person_single.normIdPerson != None:
                                                
                        
                        thema_person_single.name = liste_personen_korrigiert[j][2]
                        thema_person_single.vorname = liste_personen_korrigiert[j][3]
                        person_name_id = liste_personen_korrigiert[j][1].split('-')[1]
                        thema_person_single.normIdName = f'http://hfdb.ard.de/normdb/PersonenName?id={person_name_id}'
                    else:
                        if len(liste_personen_korrigiert[j][2].split(' '))>1:
                            thema_person_single.vorname = liste_personen_korrigiert[j][2].split(' ')[0]
                            thema_person_single.name = liste_personen_korrigiert[j][2].replace(f'{thema_person_single.vorname} ', '')
                            thema_person_single.normIdName = None
                        else:
                            thema_person_single.vorname = None
                            thema_person_single.name = liste_personen_korrigiert[j][2]
                            thema_person_single.normIdName = None


                    list_thema_person_hfdb_ready.append(copy.deepcopy(thema_person_single))
        else:
            list_thema_person_hfdb_ready = False

        return(list_thema_person_hfdb_ready)
    

    def make_mitwirkende_suggest(self, transcript, persons_filtered, persons_descriptions, path_list_all_entities_available):
        """Make LLM Suggestion for Mitwirkende
        Args:
            transcript (str): Original transcript
            persons_filtered(list): List of all persons that were extracted before.
            persons_descriptions(list): Descriptions of persons from persons_filtered
            path_list_all_entities_available(str): Path to excel with list of possible HFDB roles that Mitwirkende could have

        Returns:
            list_persons_raw (list): List of Person Names found.
            list_bezeichnungen (list): List of descriptions from LLM for list_persons_raw
            list_types_entities_given (list): Roles for single persons according to LLM decision
            list(langbez)(list): List of possible roles, that are applicable for person list here.
            ndb_suggests_list(list of lists): Package suggestion data coming from Normdatenbank for list of persons
        """
        #persons = self.google_api.find_persons(transcript)
        #print(persons)
        #proper_list_persons = self.google_api.make_proper_list_from_persons(persons)
        #print(proper_list_persons)
        list_persons_raw = persons_filtered
        print('DEBUG RAW Persons:', list_persons_raw)
        #print(list_persons_raw)
        list_bezeichnungen = persons_descriptions
        #Norm-DB-Abfrage nach Personen
        norm_db_linker = norm_db_entity_linking()
        ndb_suggests_list = []
        for p in range(len(persons_filtered)):
            ndb_suggests = norm_db_linker.make_name_suggestions_from_LLM_suggestions(list_persons_raw[p], list_bezeichnungen[p])
            ndb_suggests_list.append(ndb_suggests)

        list_types_entities = pandas.read_excel(path_list_all_entities_available)
        langbez = list_types_entities['Langbezeichnung']
        list_types_entities_given = self.google_api.make_roles_list(transcript, list_persons_raw, 'Excel_Lists_entities\\beteiligte_funktionen_norm_db.xlsx')
        #'Wenn es gar keine Mitwirkenden gibt, dann adde "N.N." als einzigen Mitwirkenden, denn irgendwer muss ja mitgewirkt haben,'
        if len(list_types_entities_given) == 0:
            list_persons_raw = ['N.N.']
            list_bezeichnungen = ['Keine Bezeichnungen verfügbar']
            list_types_entities_given.append(self.google_api.make_roles_list(transcript, ['N.N.'], 'Excel_Lists_entities\\beteiligte_funktionen_norm_db.xlsx'))
            ndb_suggests_list = [norm_db_linker.make_name_suggestions_from_LLM_suggestions("N.N.", "")]

        return(list_persons_raw, list_bezeichnungen, list_types_entities_given, list(langbez), ndb_suggests_list)
    
    def make_mitwirkende_entry(self, liste_personen_korrigiert, path_list_all_entities_available):
        """Make AK-Entry for Mitwirkende Korrigierte Fassung
        
        Args:
            liste_personen_korrigiert (list): List of Mitwirkende coming from frontend, that are chosen by user.
            path_list_all_entities_available (str): Path to source list for NDB data for roles of single Mitwirkender

        Returns:
            list_mitwirkende_hfdb_ready(json_like): json-like object that is part of final HFDB-object and can be injected in those.
        
        """
        
        client = self.hfdb_client
        referenz_ak = client.service.getAK(self.ref_ak)
        besetzungen_ref = referenz_ak.besetzungen[1]
        list_types_entities = pandas.read_excel(path_list_all_entities_available)
        t_kurzbez = list_types_entities['Technische Kurzbezeichnung']
        langbez = list_types_entities['Langbezeichnung']
        
        wert_id = list_types_entities['Wert_ID']



        #ndb_comparison_ref = compare_with_ndb_vocabulary(path_ref_ndb_person_list_source, path_ref_ndb_person_list_sorted)

        #proper_name = ndb_comparison_ref.compare_direct_with_proper_list(list_persons_raw)
        #liste_personen_korrigiert = ui.decision_list(list_persons_raw, list_bezeichnungen, 'Korrigiere oder lösche die Personen, die in die HFDB sollen', list_types_entities_given, list(langbez), 'Personen Mitwirkende Import')
        #print('NDB-Comparison')
        #print('NDB-Comparison done!')
        list_mitwirkende_hfdb_ready = []
        if liste_personen_korrigiert != False:
            for j in range(len(liste_personen_korrigiert[0])):
                if liste_personen_korrigiert[0][j] != '':
                    besetzung_single = copy.deepcopy(besetzungen_ref)
                    if liste_personen_korrigiert[0][j][0] != None:
                        person_id = liste_personen_korrigiert[0][j][0].split('-')[1]
                        besetzung_single.mitwirkender.person.normIdPerson = f'http://hfdb.ard.de/normdb/Person?id={person_id}'
                    else:
                        person_id = None
                        besetzung_single.mitwirkender.person.normIdPerson = None

                    if besetzung_single.mitwirkender.person.normIdPerson != None:
                        
                        besetzung_single.mitwirkender.person.name = liste_personen_korrigiert[0][j][2]
                        besetzung_single.mitwirkender.person.vorname = liste_personen_korrigiert[0][j][3]
                        person_name_id = liste_personen_korrigiert[0][j][1].split('-')[1]
                        besetzung_single.mitwirkender.person.normIdName = f'http://hfdb.ard.de/normdb/PersonenName?id={person_name_id}'
                    else:
                        if len(liste_personen_korrigiert[0][j][2].split(' ')) > 1:
                            besetzung_single.mitwirkender.person.vorname = liste_personen_korrigiert[0][j][2].split(' ')[0]
                            besetzung_single.mitwirkender.person.name = liste_personen_korrigiert[0][j][2].replace(f'{besetzung_single.mitwirkender.person.vorname} ', '')
                            besetzung_single.mitwirkender.person.normIdName = None
                        else:
                            besetzung_single.mitwirkender.person.vorname = None
                            besetzung_single.mitwirkender.person.name = liste_personen_korrigiert[0][j][2]
                            besetzung_single.mitwirkender.person.normIdName = None

                    
                    print('Personen korrigiert:', liste_personen_korrigiert)
                    try:
                        bezeichnung_funktion_index = list(langbez).index(liste_personen_korrigiert[1][j])
                    except:
                        bezeichnung_funktion_index = 0
                    langbezeichnung_funktion = langbez[bezeichnung_funktion_index]
                    kurzbezeichnung_funktion = t_kurzbez[bezeichnung_funktion_index]
                    wert_id_funktion = wert_id[bezeichnung_funktion_index]

                    besetzung_single.mitwirkender.funktion.kurzbezeichnung = kurzbezeichnung_funktion
                    besetzung_single.mitwirkender.funktion.langbezeichnung = langbezeichnung_funktion
                    besetzung_single.mitwirkender.funktion.normId = f'http://hfdb.ard.de/normdb/Wert?id={wert_id_funktion}'
                    list_mitwirkende_hfdb_ready.append(copy.deepcopy(besetzung_single))
        else:
            list_mitwirkende_hfdb_ready = False

        return(list_mitwirkende_hfdb_ready)
    
    def make_thema_orte_suggest(self, transcript_text):
        """Suggests Orte based on Transcript
        
        Args:
            transcript_text(str): Audio Transcript, that Orte data is extracted from by LLM

        Returns:
            orte_ndb_data(list of lists): Complete datasets for suggestions with NDB data
            orte_beschreibungen(list): List of strings with descriptions for places coming from LLM
            orte_sorted_single[0](list): List of places name strings
        """
        orte_raw = self.google_api.set_thema_ort(transcript_text)
        orte_sorted_single = self.google_api.make_proper_list_from_orte(orte_raw)
        orte_ndb_data = []
        orte_beschreibungen = orte_sorted_single[1]
        linker = norm_db_entity_linking()
        for ort in orte_sorted_single[0]:
            #print('DEBUG ORT AK Maker:', ort)
            normdb_orte_data = linker.make_orte_suggestions_from_LLM_suggestions(ort)
            orte_ndb_data.append(normdb_orte_data)

        return(orte_ndb_data, orte_beschreibungen, orte_sorted_single[0])
    
    def make_orte_entry(self, liste_orte_korrigiert, ref_AK_2):
        """Makes Orte Entry with NDB-Comparison
        
        Args:
            liste_orte_korrigiert (list): List of user-edited places from frontend
            ref_AK_2 (str): URI of reference HFDB entry, that is copied in part to make orte-entries from it.

        Returns:
            orte_list_final(json_like): json-like list ready to be injected into HFDB with Places entries. 
        
        """
        orte_list_final = []
        
        ref_thema_ort = self.hfdb_client.service.getAK(ref_AK_2)
        ref_thema_ort = ref_thema_ort.themaOrte[0]
        
        if liste_orte_korrigiert != False: #Wenn "Nicht in HFDB übernehmen" Knopf gedrückt wird, denn steht hier "False"
            for i in range(len(liste_orte_korrigiert)):
                
                
                new_ort_eintrag = copy.deepcopy(ref_thema_ort)
                new_ort_eintrag.bezeichnung = liste_orte_korrigiert[i][2]
                new_ort_eintrag.normIdName = liste_orte_korrigiert[i][1]
                new_ort_eintrag.normIdVokabel = liste_orte_korrigiert[i][0]
                
                orte_list_final.append(new_ort_eintrag)
        else:
            orte_list_final = False
        
        return(orte_list_final)
    
    def make_ereignis_suggest(self, transcript_text):
        """Suggests Thema Ereignis and its Date
        
        Args:
            transcript_text(str): Audio Transcript, that Orte data is extracted from by LLM

        Returns:
            ereignis_sorted_single (list): List of Strings of Ereignisse to be suggested in frontend
            ereignis_beschreibungen (list): List of descriptions of Ereignisse to be displayed with entries of ereignis_sorted_single
            ereignis_tage (list): List of integers for day entries for date of single Ereignis
            ereignis_monate (list): List of integers for month entries for date of single Ereignis
            ereignis_jahre (list): List of integers for year entries for date of single Ereignis
        
        """
        ereignis_raw = self.google_api.set_thema_ereignis(transcript_text)
        ereignis_sorted_single = self.google_api.make_proper_list_from_ereignis(ereignis_raw)
        ereignis_beschreibungen = []
        ereignis_tage = []
        ereignis_monate = []
        ereignis_jahre = []
        for ereignis in ereignis_sorted_single:
            ereignis_beschreibungen.append(self.google_api.get_beschreibung_ereignis(transcript_text, ereignis))
            ereignis_datum = self.google_api.get_tag_ereignis(transcript_text, ereignis)
            print('DEBUG EREIGNIS DATUM:', ereignis_datum)
            try:
                ereignis_tag = ereignis_datum[0]
                ereignis_month = ereignis_datum[1]
                ereignis_jahr = ereignis_datum[2]
                ereignis_tage.append(ereignis_tag)
                ereignis_monate.append(ereignis_month)
                ereignis_jahre.append(ereignis_jahr)
            except:
                ereignis_tage.append(None)
                ereignis_monate.append(None)
                ereignis_jahre.append(None)
        
        return ereignis_sorted_single, ereignis_beschreibungen, ereignis_tage, ereignis_monate, ereignis_jahre
    
    def make_thema_ereignis_entry(self, ereignis_data_roh):
        """Makes List of Ereignisse and Returns them
        
        Args:
            ereignis_data_roh (list): List of user-corected text data for Ereignis coming from Frontend
        
        Returns:
            ereignis_list (list): List of Ereignis data ready to be injected into HFDB   
        
        """
        ereignis_list = []
        for i in range(len(ereignis_data_roh)):
            ereignis_list.append(ereignis_data_roh[i][0])

        return ereignis_list

    def make_thema_ereignis_datum_entry(self, liste_ereignis_korrigiert):
        """Makes ready entry for themaEreignis
        
        Args:
            liste_ereignis_korrigiert(list): Raw data for Ereignis coming from frontend, that contains date data.

        Returns:
            themaEreignisDatum_list(list): Prepared data ready to be injected into HFDB entry for dates of themaEreignis.
        
        """
        themaEreignisDatum_list = []

        for t in range(len(liste_ereignis_korrigiert)):
            if liste_ereignis_korrigiert[t][1] == '0' or liste_ereignis_korrigiert[t][1] == None or liste_ereignis_korrigiert[t][1] == '' or liste_ereignis_korrigiert[t][1] == '00':
                day_ereignis = 0
            else:
                day_ereignis = liste_ereignis_korrigiert[t][1]

            if liste_ereignis_korrigiert[t][2] == '0' or liste_ereignis_korrigiert[t][2] == None or liste_ereignis_korrigiert[t][2] == '00' or liste_ereignis_korrigiert[t][2] == '':
                month_ereignis = 0
            else:
                month_ereignis = liste_ereignis_korrigiert[t][2]
            
            if liste_ereignis_korrigiert[t][3] == '0' or liste_ereignis_korrigiert[t][3] == None or liste_ereignis_korrigiert[t][3] == '' or liste_ereignis_korrigiert[t][3] == '00' or liste_ereignis_korrigiert[t][3] == '0000' or liste_ereignis_korrigiert[t][3] == 0:
                year_ereignis = None
            else:
                year_ereignis = liste_ereignis_korrigiert[t][3]

            if month_ereignis == 0 and year_ereignis == None:
                thema_ereignis_single_datum = None
            elif year_ereignis == None:
                thema_ereignis_single_datum = None
            else:
                
                thema_ereignis_single_datum = {
                    'beginn': {
                        'day': day_ereignis,
                        'month': month_ereignis,
                        'year': year_ereignis,
                        'datumszusatz': None
                    },
                    'bemerkung': None,
                    'ende': None
                }
            themaEreignisDatum_list.append(thema_ereignis_single_datum)
            print('DEBUG EREIGNIS:', thema_ereignis_single_datum)
        
        return(themaEreignisDatum_list)
        
    def make_thema_institution_suggest(self, transcript_text):
        """Suggests Institutions based on Transcript
        
        Args:
            transcript_text(str): Audio Transcript, that Orte data is extracted from by LLM

        Returns:
            institution_ndb_data(list): List of NDB data suggestions for institutions, that are important part of the source audio
            institution_beschreibungen(list): List of description strings for entries of institutionen_sorted_single coming from LLM
            institutionen_sorted_single(list): List of institution names raw strings
        
        """
        institution_raw = self.google_api.set_thema_institution(transcript_text)
        institutionen_sorted_single = self.google_api.make_proper_list_from_institutionen(institution_raw)
        institution_ndb_data = []
        institution_beschreibungen = []
        linker = norm_db_entity_linking()
        for institution in institutionen_sorted_single:
            
            institution_beschreibungen.append(self.google_api.get_beschreibung_institution(institution, transcript_text))
            norm_institutionen_data = linker.make_institutionen_suggestions_from_LLM_suggestions(institution)
            
            institution_ndb_data.append(norm_institutionen_data)
        
        return (institution_ndb_data, institution_beschreibungen, institutionen_sorted_single)
    
    def make_thema_institution_entry(self, liste_institutionen_korrigiert):
        """Makes ThemaInstitutionen Entry with NDB-Comparison
        
        Args:
            liste_institutionen_korrigiert(list): List of user-corrected institution data coming from frontend

        Returns:
            inst_list_final(list): HFDB-ready entry of institutions as list of json-like objects
        
        """
        inst_list_final = []
        
        ref_thema_inst = {
            'name': 'Europäische Gemeinschaft',
            'namenszusatz': None,
            'normIdInstitution': 'http://hfdb.ard.de/normdb/Institution?id=304624',
            'normIdName': 'http://hfdb.ard.de/normdb/Institutionsname?id=2465094'
        }
        norm_inst_standard_part = ref_thema_inst['normIdInstitution'].split('=')[0]
        norm_name_standard_part = ref_thema_inst['normIdName'].split('=')[0]
        joiner = '='
        if liste_institutionen_korrigiert != False: #Wenn "Nicht in HFDB übernehmen" Knopf gedrückt wird, denn steht hier "False"
            for i in range(len(liste_institutionen_korrigiert)):
                
                new_inst_eintrag = copy.deepcopy(ref_thema_inst)
                
                new_inst_eintrag['name'] = liste_institutionen_korrigiert[i][2]
                
                if liste_institutionen_korrigiert[i][3] != None:
                    new_inst_eintrag['namenszusatz'] = liste_institutionen_korrigiert[i][3]
                else:
                    new_inst_eintrag['namenszusatz'] = None

                if liste_institutionen_korrigiert[i][0] != None:
                    print('DEBUG Institutionen:', liste_institutionen_korrigiert[i])
                    normIdInstitution_number = liste_institutionen_korrigiert[i][1].split('-')[1]
                    new_inst_eintrag['normIdInstitution'] = joiner.join([norm_inst_standard_part, normIdInstitution_number])
                else:
                    new_inst_eintrag['normIdInstitution'] = None

                if liste_institutionen_korrigiert[i][1] != None:
                    normIdName_number = liste_institutionen_korrigiert[i][0].split('-')[1]
                    new_inst_eintrag['normIdName'] = joiner.join([norm_name_standard_part, normIdName_number])
                else:
                    new_inst_eintrag['normIdName'] = None
                
                inst_list_final.append(new_inst_eintrag)
        else:
            inst_list_final = False
        
        return(inst_list_final)
    
    def make_schlagworte_suggest(self, transcript_text):
        """Prepares raw Schlagworte, that then are devided between Klassen und simple Tags. Schlagworte die das LLM vorschlägt, werden danach sortiert ob wir in der ndb dafür Sachdeskriptor-Entsprechungen finden, dann werden sie Deskriptoren, sonst einfache Metatags.
        
        Args:
            transcript_text(str): Audio Transcript, that Orte data is extracted from by LLM

        Returns:
            metatags_suggest(list): List of suggested metatags to be displayed in frontend
            deskriptoren_suggest(list): List of suggested "Deskriptoren" to be displayed in frontend
        
        """
        metatags_suggest = []
        deskriptoren_suggest = []
        liste_tags_roh = self.google_api.set_schlagworte(transcript_text)
        linker = norm_db_entity_linking()
        for t in range(len(liste_tags_roh)):
            ndb_abgleich_results = linker.set_vokabel_vorschlaege(liste_tags_roh[t])
            if len(ndb_abgleich_results[1]) == 0 and len(ndb_abgleich_results[0]) > 0:
                metatags_suggest.append(ndb_abgleich_results[0][0])
            elif len(ndb_abgleich_results[1]) > 0:
                deskriptoren_suggest.append(ndb_abgleich_results)
        
        return(metatags_suggest, deskriptoren_suggest)
    
    def make_deskriptoren_entry(self, deskriptoren_korrigiert):
        """Forms proper Descriptor-and Klasse-Entries for HFDB
        
        Args:
            deskriptoren_korrigiert(list): List of user-corrected "Deskriptoren"  data coming from frontend

        Returns:
            desk_list_final(list): List of json-like objects for "Deskriptoren" ready to be injected in new HFDB entry
            klasse_list_final(list): List of json-like objects for "Klassen" ready to be injected in new HFDB entry

        """
        desk_list_final = []
        klasse_list_final = []
        
        ref_desk = {
            'bezeichnung': 'Kulturförderung',
            'bezeichnungZusatz': None,
            'normIdName': 'http://hfdb.ard.de/normdb/VokabelName?id=91426',
            'normIdVokabel': 'http://hfdb.ard.de/normdb/Vokabel?id=69948',
            'vokabelNameTyp': {
                'kurzbezeichnung': 'DE',
                'langbezeichnung': 'Deskriptor',
                'normId': 'http://hfdb.ard.de/normdb/Wert?id=1159'
            }
        }
        print('DEBUG_MAKE_AK_Desk_Entry Maker:', deskriptoren_korrigiert)
        for i in range(len(deskriptoren_korrigiert)):
            print('DEBUG_MAKE_AK_Desk_Entry Maker:', deskriptoren_korrigiert[i])
            desk_entry = copy.deepcopy(ref_desk)
            desk_entry['bezeichnung'] = deskriptoren_korrigiert[i][0][0]
            norm_id_vok = deskriptoren_korrigiert[i][1][0].split('-')[1]
            norm_id_name = deskriptoren_korrigiert[i][2][0].split('-')[1]
            desk_entry['normIdName'] = f'http://hfdb.ard.de/normdb/VokabelName?id={norm_id_name}'
            desk_entry['normIdVokabel'] = f'http://hfdb.ard.de/normdb/VokabelName?id={norm_id_vok}'
            if 'deskriptor' in deskriptoren_korrigiert[i][3][0].lower():
                desk_list_final.append(desk_entry)
            else:
                klasse_list_final.append(desk_entry)

        return(desk_list_final, klasse_list_final)

    def make_titel_suggest(self, transcript_text):
        """Prepares title from transcript text with LLM
        
        Args:
            transcript_text(str): Transcript text from audio input
        
        Returns:
            ueberschrift_raw(str): Suggest for heading for database entry to be displayed and corrected in frontend
        """
        ueberschrift_raw = self.google_api.set_ueberschrift(transcript_text)
        return(ueberschrift_raw)
    
    def make_titel_korrigiert(self, ueberschrift_korrigiert):
        """Makes AK Part Title from korrigierter Title
        
        Args:
            ueberschrift_korrigiert(str): User-corrected heading coming from frontend
        
        Returns:
            titel(json-like): Final title as json-like object to be part of new HFDB database entry.
        """
        ref_ak= self.hfdb_client.service.getAK(self.ref_ak)
        titel = ref_ak.titel[0]
        titel.text = ueberschrift_korrigiert
        return(titel)
    
    def make_zusammenfassung_suggest(self, transcript_text):
        """Prepares Zusammenfassung from transcript text with LLM
        
        Args:
            transcript_text(str): Transcript text from audio input

        Returns:
            zusammenfassung_raw(str): Suggestion for summary of audio content to be displayed in frontend

        """
        zusammenfassung_raw = self.google_api.set_zusammenfassung(transcript_text)
        return(zusammenfassung_raw)
    
    def make_zusammenfassung_korrigiert_hfdb(self, zusammenfassung_korrigiert):
        """Makes AK-part Zusammenfassung from korrigierte Zusammenfassung
        
        Args:
            zusammenfassung_korrigiert(str): User-corrected summary of audio content coming from frontend

        Returns:
            abstract(json-like): Json-like object ready to be injected into final HFDB entry.
        
        """
        #zusammenfassung_korrigiert = ui.entity_correction(zusammenfassung_raw, 'Korrigiere generierte Zusammenfassung, wenn gewünscht')
        #zusammenfassung_korrigiert = zusammenfassung_korrigiert['-INPUT-']
        #print(zusammenfassung_korrigiert)
        ref_ak= self.hfdb_client.service.getAK(self.ref_ak_2)
        abstract = [ref_ak.deskriptionsText[0]]
        abstract[0].text = zusammenfassung_korrigiert

        return(abstract)    
    
    def make_gattungen_korrigiert_hfdb(self, gattungen_korrigiert):
        """Makes Gattungen entry for HFDB from raw data
        
        Args:
            gattungen_korrigiert(list): List of user-corrected "Gattungen" coming from frontend

        Returns:
            gattungen_final(json-like): List of json-like objects with "Gattungen" entries, ready to be  injected into final HFDB data.
        
        """
        df = pandas.read_excel('Excel_Lists_entities\\gattungen_names.xlsx')
        list_gattungen = list(df['Gattungen_Liste'])
        list_idname = df['normIdName']
        list_idvokabel = df['normIdVokabel']

        ref_ak= self.hfdb_client.service.getAK(self.ref_ak_2)
        gattungen_vorlage = ref_ak.gattung[0]
        gattungen_final = []
        if gattungen_korrigiert != False: #Wenn "Nicht in HFDB übernehmen" grdrückt wurde, dann sind alle Werte == False
            for i in range(len(gattungen_korrigiert)):
                print('Prüfung Gattungen Start', i)
                try:
                    index_gattung = list_gattungen.index(gattungen_korrigiert[i])
                    idname_gattung = list_idname[index_gattung]
                    idname_gattung = idname_gattung.replace("'","")
                    idvokabel_gattung = list_idvokabel[index_gattung]
                    idvokabel_gattung = idvokabel_gattung.replace("'","")
                    gattung_neu = gattungen_vorlage
                    gattung_neu.bezeichnung = gattungen_korrigiert[i]
                    gattung_neu.normIdName = idname_gattung
                    gattung_neu.normIdVokabel = idvokabel_gattung
                    #print(gattung_neu)
                    gattungen_final.append(deepcopy(gattung_neu))
                except ValueError:
                    print('ValueError Pfad')
                    for j in range(len(list_gattungen)):
                        if list_gattungen[j] in gattungen_korrigiert[i]:
                            idname_gattung = list_idname[j]
                            idname_gattung = idname_gattung.replace("'","")
                            idvokabel_gattung = list_idvokabel[j]
                            idvokabel_gattung = idvokabel_gattung.replace("'","")
                            gattung_neu = gattungen_vorlage
                            gattung_neu.bezeichnung = list_gattungen[j]
                            gattung_neu.normIdName = idname_gattung
                            gattung_neu.normIdVokabel = idvokabel_gattung
                            #print(gattung_neu)
                            gattungen_final.append(deepcopy(gattung_neu))
        else:
            gattungen_final = False
        return(gattungen_final)
    
    def make_genre_suggest(self, path_temp_folder, name_filtered_excel, folder_main_audio, name_main_audio):
        """Makes suggestions for Genre entries directly from audio data through special function
        
        Args:
            path_temp_folder(str): Path to folder for temporary saving of files
            name_filtered_excel (str): Name of Excel with data from YAMnet evaluation of audio
            folder_main_audio (str): Path to folder where original audio input ist stored
            name_main_audio (str): File name of original audio input

        Returns:
            status_suggest(str): Final status suggestion to be displayed in frontend

        """

        self.genre_maker = get_genre(path_temp_folder, name_filtered_excel, folder_main_audio, name_main_audio)
        status_suggest = self.genre_maker.define_status()

        return(status_suggest)
    
    def make_genre_korrigiert_hfdb(self, status_raw):
        """Makes full entry for HFDB from frontend data for genre part
        
        Args:
            status_raw(str): User-corrected status coming from frontend

        genre_entry_hfdb(str): Final genre entry ready for HFDB ingest. 
        """
        #print('DEBUG GENRE')
        #print('Status from Maske:', status_raw)
        
        genre_entry_hfdb = self.genre_maker.make_ak_part_genre(status_raw)

        return(genre_entry_hfdb)
    
    def make_sprache_suggest(self, transcript_text):
        """Suggests Sprachen-HFDB-Einträge for Transcrips from LLM
        
        Args:
            transcript_text(str): Transcript of input audio

        Returns:
            sprache_sorted_single(list): Raw name strings of languages occuring in source audio
            sprachen_ndb_data_list(list): NDB-data for sprachen suggested if available to show in frontend
        """
        sprache_suggest = self.google_api.set_sprache(transcript_text)
        sprache_sorted_single = self.google_api.make_proper_list_from_sprache(sprache_suggest) 

        sprachen_ndb_data_list = []
        linker = norm_db_entity_linking()
        for sprache in sprache_sorted_single:
            norm_sprachen_data = linker.suggest_ndb_sprachen(sprache)
            
            sprachen_ndb_data_list.append(norm_sprachen_data)
        
        return(sprache_sorted_single, sprachen_ndb_data_list)
    
    def make_sprache_entry(self, liste_sprachen_korrigiert):
        """Makes ThemaInstitutionen Entry with NDB-Comparison
        
        Args:
            liste_sprachen_korrigiert(list): List of language data after correction by user in frontend.

        Returns:
            sprachen_list_final(list): Final HFDB entry part for languages.
        """
        sprachen_list_final = []
        
        ref_sprachen_entry = {
            'bezeichnung': 'deutsch',
            'bezeichnungZusatz': None,
            'normIdName': 'http://hfdb.ard.de/normdb/VokabelName?id=94',
            'normIdVokabel': 'http://hfdb.ard.de/normdb/Vokabel?id=94',
            'vokabelNameTyp': {
                'kurzbezeichnung': 'DE',
                'langbezeichnung': 'Deskriptor',
                'normId': 'http://hfdb.ard.de/normdb/Wert?id=1159'
            }
        }
        norm_sprache_standard_part = ref_sprachen_entry['normIdVokabel'].split('=')[0]
        norm_name_standard_part = ref_sprachen_entry['normIdName'].split('=')[0]
        joiner = '='
        if liste_sprachen_korrigiert != False: #Wenn "Nicht in HFDB übernehmen" Knopf gedrückt wird, denn steht hier "False"
            for i in range(len(liste_sprachen_korrigiert)):
                
                new_sprache_eintrag = copy.deepcopy(ref_sprachen_entry)
                
                new_sprache_eintrag['bezeichnung'] = liste_sprachen_korrigiert[i][0]
                
                if liste_sprachen_korrigiert[i][1] != None:
                    new_sprache_eintrag['bezeichnungZusatz'] = liste_sprachen_korrigiert[i][1]
                else:
                    new_sprache_eintrag['bezeichnungZusatz'] = None

                if liste_sprachen_korrigiert[i][2] != None:
                    normIdsprache_number = liste_sprachen_korrigiert[i][2].split('-')[1]
                    new_sprache_eintrag['normIdName'] = joiner.join([norm_sprache_standard_part, normIdsprache_number])
                else:
                    new_sprache_eintrag['normIdName'] = None

                if liste_sprachen_korrigiert[i][3] != None:
                    normIdvokabel_number = liste_sprachen_korrigiert[i][3].split('-')[1]
                    new_sprache_eintrag['normIdVokabel'] = joiner.join([norm_name_standard_part, normIdvokabel_number])
                else:
                    new_sprache_eintrag['normIdVokabel'] = None
                
                sprachen_list_final.append(new_sprache_eintrag)
        else:
            sprachen_list_final = False
        
        return(sprachen_list_final)
    
    def make_current_datum_eintrag(self):
        """Returns today's date wherever needed in HFDB-json-format.
        
        Returns:
            current_date(json-like): Json-like object for date entry in HFDB dataset.
        """
        current_date = {
        'day': datetime.today().strftime('%d'),
        'month': datetime.today().strftime('%m'),
        'year': datetime.today().strftime('%Y')
        }
        return(current_date)
    

    def make_ak_suggests_standard(self, transcript, start, urheber_suggest, mitwirkende_suggest, title_suggest, zusammenfassung_suggest, topic_persons, topic_persons_description, ndb_thema_persons_suggest, orte_suggest, institutionen_suggest, ereignis_suggest, audiofile_path, audiofile_name, file_ohne_speech, gattungen_suggest, genre_suggest, sprachen_suggest, schlagworte_suggest, audioraum_darstellung_global_suggest):
        """Standard way of making suggestions and create Control window for entities
        Args:
            transcript(str): Whisper Transcript of Audio
            start(list): List of timecodes that mark the starting points of transcript sections
            urheber_suggest(list): List of  Urheber, suggested by LLM
            mitwirkende_suggest(list): List of Mitwirkende, that is suggested by LLM
            title_suggest(str): Suggestion for AK title
            zusammenfassung_suggest(str): Suggestion for Zusammenfassung for Audio
            topic_persons(list): List for suggestions for Persons in audio
            topic_persons_description(list): List of AI generated descriptions for topics
            ndb_thema_persons_suggest(list): List of  persons that are topic as ndb-alligned data.
            orte_suggests(list): List of Orte data that is suggested
            institutionen_suggest(list): List of possible insitutions to be displayed in frontend
            ereignis_suggest(list): List of possible Ereignisse to be displayed in frontend
            audiofile_path(str): Path to audiofile source path
            audiofile_name(str): Name of audifile including format ending
            file_filtered(Str): Path to audio without music after YAMnet- and VOD-pre-processing
            gattungen_suggest(list): Suggestion for Gattungen data
            genre_suggest(list): Suggestion for genre data 
            sprachen_suggest (list): List of languages  for audio that is suggested to the user in the interface.
            schlagworte_suggest(list): List for tags to suggest for user.
            audioraum_darstellung_global_suggest (json-like): This is set for all AKs at first input window

            returns:
                values_corrected(list): List of correted data based on Transkript and  corrected by user in Frontend.                                                                                                                                                                                                                                                                                                                                 
        """
        ui_main = ui_correction() # Main user interface to correct the data.
        
        values_corrected = ui_main.ak_correction_menu(transcript, start, urheber_suggest[0], urheber_suggest[1], urheber_suggest[2], urheber_suggest[3], urheber_suggest[4], mitwirkende_suggest[0], mitwirkende_suggest[1], mitwirkende_suggest[2], mitwirkende_suggest[3],mitwirkende_suggest[4], title_suggest, zusammenfassung_suggest, topic_persons, topic_persons_description, ndb_thema_persons_suggest, orte_suggest[0], orte_suggest[1], orte_suggest[2], institutionen_suggest, ereignis_suggest, audiofile_path, file_ohne_speech, audiofile_name, gattungen_suggest, genre_suggest, sprachen_suggest[0], sprachen_suggest[1], schlagworte_suggest[0], schlagworte_suggest[1], audioraum_darstellung_global_suggest)

        return values_corrected
    
    def prepare_ak_data_from_raw_data(self, transcript, multimodal_data, audiofile_path, audiofile_name, path_list_all_entities_available, path_list_all_entities_available_urheber):
        """Prepare suggestions from transcripts and multimodal_data. ALl of the returns may be further unpacked in the frontend handlers
        Args:
            transcript(str): Corrected transcript by Whisper with SpaCy entity correction
            multimodal_data(list): Data created directly without transcript processed directly from audio by multimodal model
            audiofile_path(str): Path of source audiofile
            audiofile_name(str): file name of original audio file input
            path_list_all_entities_available(str): Path to excel file with list of available roles for Mitwirkende.
            path_list_all_entities_available_urheber(str): Path to excel file with list of available roles for Urheber.

        Returns:
            gattungen_suggest(list): List of Gattungen to suggest to user
            genre_suggest(str): Suggest for Genre data point
            zusammenfassung_suggest(str): Suggest for summary to show to the user for correction
            title_suggest(str): Suggest for title of dataset to show to user (RHTI)
            orte_suggest(list): List of places data to suggest zu user.
            urheber_suggest(list): List of Urheber to suggest to user
            mitwirkende_suggest(list): List of Mitwirkende to suggest to user
            sprechende(list): List of speakers to suggest to user.
            sprechende_description(list): List of description of speakers to show to user.
            thema_person(list): List of persons that are topics to show to the user
            thema_person_description(list): List of descriptions of people from thema_person list to show to user.
            ndb_thema_persons_suggest(list): NDB data of persons to suggest to user.
            institutionen_suggest(list): List of institutions to show to the user.
            ereignis_suggest(list): List of events to suggest to the user.
            sprachen_suggest(list): List of languages to show to the user
            schlagworte_suggest (list): List of tags to show to the user
        """

        gattungen_suggest = multimodal_data
        genre_suggest = self.make_genre_suggest(audiofile_path, f'{audiofile_path}\\yamnet_files\\{audiofile_name}_6_Summary_Music_Speech_filtered.xlsx', audiofile_path, audiofile_name)

        #if len(transcript)<32000:
            
        sprechende, sprechende_description, topic_persons, topic_persons_description = self.decide_mitwirkende_or_topic(transcript)
        urheber, urheber_description = self.decide_is_urheber(transcript)
        zusammenfassung_suggest = self.make_zusammenfassung_suggest(transcript)
        title_suggest = self.make_titel_suggest(transcript)
        mitwirkende_suggest = self.make_mitwirkende_suggest(transcript, sprechende, sprechende_description, path_list_all_entities_available)
        urheber_suggest = self.make_urheber_suggest(transcript, urheber, urheber_description, path_list_all_entities_available_urheber)
        thema_personen_suggest = self.make_thema_personen_suggest(topic_persons, topic_persons_description, urheber)
        thema_person = thema_personen_suggest[0]
        thema_person_description = thema_personen_suggest[1]
        ndb_thema_persons_suggest = thema_personen_suggest[2]
        orte_suggest = self.make_thema_orte_suggest(transcript)
        institutionen_suggest = self.make_thema_institution_suggest(transcript)
        ereignis_suggest = self.make_ereignis_suggest(transcript)
        sprachen_suggest = self.make_sprache_suggest(transcript)
        schlagworte_suggest = self.make_schlagworte_suggest(transcript)

        #else:
          #  print('Transcript zu lang - wird aufgeteilt')
            #transcript1 = transcript['-INPUT-'][0:20000]
            #transcript2 = transcript['-INPUT-'][20000:len(transcript['-INPUT-'])]
           # sprechende, sprechende_description, topic_persons, topic_persons_description = self.#decide_mitwirkende_or_topic(transcript1)
           # sprechende1, sprechende_description1, topic_persons1, topic_persons_description1 = self.#decide_mitwirkende_or_topic(transcript2)
           # for s in range(len(sprechende1)):
           #     if sprechende1[s] not in sprechende:
           #         sprechende.append(sprechende1[s])
           #         sprechende_description.append(sprechende_description1[s])
           # for t in range(len(topic_persons1)):
            #    if topic_persons1[t] not in topic_persons:
            #            topic_persons.append(topic_persons1[t])
            #            topic_persons_description.append(topic_persons_description1[t])
            #zusammenfassung_suggest1 = self.make_zusammenfassung_suggest(transcript1)
            #zusammenfassung_suggest2 = self.make_zusammenfassung_suggest(transcript2)
            #joiner = ' '
           # zusammenfassung_text_zusammen = joiner.join([zusammenfassung_suggest1, zusammenfassung_suggest2])
           # zusammenfassung_suggest = self.make_zusammenfassung_suggest(zusammenfassung_text_zusammen)
           # title_suggest = self.make_titel_suggest(transcript1)
           # mitwirkende_suggest = self.make_mitwirkende_suggest(transcript1, sprechende, sprechende_description, #path_list_all_entities_available)
           # mitwirkende_suggest2 = self.make_mitwirkende_suggest(transcript2, sprechende1, sprechende_description1, path_list_all_entities_available)
          #      #return(list_persons_raw, list_bezeichnungen, list_types_entities_given, list(langbez))
           # for i in range(len(mitwirkende_suggest2[0])):
             #   if mitwirkende_suggest2[0][i] not in mitwirkende_suggest[0]:
             #       mitwirkende_suggest[0].append(mitwirkende_suggest2[0][i])
            #        mitwirkende_suggest[1].append(mitwirkende_suggest2[1][i])
             #       mitwirkende_suggest[2].append(mitwirkende_suggest2[2][i])
             #       mitwirkende_suggest[3].append(mitwirkende_suggest2[3][i])

           # orte_suggest = self.make_thema_orte_suggest(transcript1)
           # orte_suggest2 = self.make_thema_orte_suggest(transcript2)

           # for ort in orte_suggest2:
               # if ort not in orte_suggest:
                #    orte_suggest.append(ort)

        return(gattungen_suggest, genre_suggest, zusammenfassung_suggest, title_suggest, orte_suggest, urheber_suggest, mitwirkende_suggest, sprechende, sprechende_description, thema_person, thema_person_description, ndb_thema_persons_suggest, institutionen_suggest, ereignis_suggest, sprachen_suggest, schlagworte_suggest)


    def make_ak_v1_v2(self, values_corrected, path_list_all_entities_available, path_list_all_entities_available_urheber, ebene_geflecht, kompilationstyp):
        """Makes AK Entry for first structure version = 'new_korpus' = Audio ist für sich eine AK Korpus  --> Wird auf Korpus-Ebene angelegt.
        
        Args:
            values_corrected(list): Corrected data from correction window ready to be used for ak
            path_ref_ndb_person_list_source (str): Path to current NDB name dump
            path_list_all_entities_available(str): Path to source list for NDB data for roles of single Mitwirkender 
            path_ref_ndb_person_list_sorted(str): Path to pre-processed NDB name dump

        Returns:
            new_ak_id(str): URI of newly created AK
        """
        if values_corrected != False: #Wenn niemand den "Nicht in HFDB übernehmen Knopf gedrückt hat"
            new_ak = self.hfdb_client.service.getAK(self.ref_ak_2)
            new_ak.hfdbId = None
            new_ak.urheber = self.make_urheber_entry(values_corrected[9], path_list_all_entities_available_urheber)
            
            new_ak.besetzungen = self.make_mitwirkende_entry(values_corrected[0],  path_list_all_entities_available)
            new_ak.titel = self.make_titel_korrigiert(values_corrected[3])
            if values_corrected[2] == '': #Wenn Deskriptionstext nicht vorhanden, dann Datum komplett rausnehmen.
                new_ak.deskriptionsText = []
            else:
                new_ak.deskriptionsText = self.make_zusammenfassung_korrigiert_hfdb(values_corrected[2])
            hfdb_ref_topic_persons = f'http://hfdb.ard.de/{self.instance}/AudioKreation?id=4916218'
            new_ak.themaPersonen = self.make_thema_personen_korrigiert_hfdb(hfdb_ref_topic_persons, values_corrected[1])
            new_ak.deskriptor = self.make_deskriptoren_entry(values_corrected[13])[0]
            new_ak.themaOrte = self.make_orte_entry(values_corrected[4], self.ref_ak_2)
            new_ak.themaEreignisse = self.make_thema_ereignis_entry(values_corrected[11])
            new_ak.themaEreignisDatum = self.make_thema_ereignis_datum_entry(values_corrected[11])
            new_ak.themaInstitution = self.make_thema_institution_entry(values_corrected[10])
            new_ak.erfassungDatum = self.make_current_datum_eintrag()
            new_ak.migrationsId = None
            new_ak.bemerkungen = []
            new_ak.gattung = self.make_gattungen_korrigiert_hfdb(values_corrected[5])
            new_ak.genre = self.make_genre_korrigiert_hfdb(values_corrected[7])   
            new_ak.klasse = self.make_deskriptoren_entry(values_corrected[13])[1]
            new_ak.sprachen = self.make_sprache_entry(values_corrected[12])
            new_ak.tags = values_corrected[14]
            #new_ak.urheber = []
            new_ak.audioereignisTyp = None #todo
            new_ak.kollektionen = []
            new_ak.konfektionierungRef = [] #todo
            new_ak.produktionRef = None
            new_ak.ausstrahlungRef = []

            #Ebene Korpus oder Kompilation festlegen, wird über variable "ebene_geflecht" festgelegt.
            if ebene_geflecht == 'korpus':
                new_ak.hierarchieTyp = {
                    'kurzbezeichnung': 'Korpus',
                    'langbezeichnung': 'Korpus',
                    'normId': None
                }
            
            elif ebene_geflecht == 'kompilation':
                new_ak.hierarchieTyp = {
                    'kurzbezeichnung': 'Kompilation',
                    'langbezeichnung': 'Kompilation',
                    'normId': None
                }
                if kompilationstyp == 'KONZ':
                    new_ak.kreationstyp = {
                        'kurzbezeichnung': 'KONZ',
                        'langbezeichnung': 'Konzert / Öffentliche Veranstaltung',
                        'normId': None
                    }

                elif kompilationstyp == 'SEND':
                    new_ak.kreationstyp = {
                        'kurzbezeichnung': 'SEND',
                        'langbezeichnung': 'Sendung',
                        'normId': None
                    }

                elif kompilationstyp == 'MOIN':
                    new_ak.kreationstyp = {
                        'kurzbezeichnung': 'MOIN',
                        'langbezeichnung': 'Medienobjektinhalt',
                        'normId': None
                    }
            #print('DEBUG AK')
            #print(new_ak)
            new_ak_id = self.hfdb_client.service.insertAK(new_ak)
            #Urheber needs to be added after AK exists - Bug in API?
            #new_ak = self.hfdb_client.service.getAK(new_ak_id)
            #new_ak.urheber = self.make_urheber_entry(values_corrected[9], #path_list_all_entities_available_urheber)
            #new_ak.hfdbId = new_ak.hfdbId.split('&version=')[0]
            #self.hfdb_client.service.updateAK(new_ak)

        else:
            new_ak_id = None

        return new_ak_id
    
    
    def make_ak_v4(self, values_corrected, path_list_all_entities_available, path_list_all_entities_available_urheber, superkreation_ID):
        """Makes AK Entry for first structure version = 'new_korpus' = Audio ist für sich eine AK Korpus  --> Wird auf Korpus-Ebene angelegt.
        
        Args:
            values_corrected(list): Corrected data from correction window ready to be used for ak
            path_list_all_entities_available(str): Path to source list for NDB data for roles of single Mitwirkender 
            path_list_all_entities_available_urheber(str): Path to pre-processed NDB name dump
            superkreation_ID(str): String of AK that current AK should be daughter of.

        Returns:
            new_ak(str): String of URI of newly created AK
        """
        if values_corrected != False: #Wenn niemand den "Nicht in HFDB übernehmen Knopf gedrückt hat"
            new_ak = self.hfdb_client.service.getAK(self.ref_ak_2)
            new_ak.hfdbId = None
            new_ak.urheber = self.make_urheber_entry(values_corrected[9], path_list_all_entities_available_urheber)
            #Urheber needs to be added after AK exists - Bug in API?
            new_ak.besetzungen = self.make_mitwirkende_entry(values_corrected[0], path_list_all_entities_available)
            new_ak.titel = self.make_titel_korrigiert(values_corrected[3])
            new_ak.deskriptionsText = self.make_zusammenfassung_korrigiert_hfdb(values_corrected[2])
            hfdb_ref_topic_persons = f'http://hfdb.ard.de/{self.instance}/AudioKreation?id=4916218'
            new_ak.themaPersonen = self.make_thema_personen_korrigiert_hfdb(hfdb_ref_topic_persons, values_corrected[1])
            new_ak.deskriptor = self.make_deskriptoren_entry(values_corrected[13])[0]
            new_ak.themaOrte = self.make_orte_entry(values_corrected[4], self.ref_ak_2)
            new_ak.themaEreignisse = self.make_thema_ereignis_entry(values_corrected[11])
            new_ak.themaEreignisDatum = self.make_thema_ereignis_datum_entry( values_corrected[11])
            new_ak.themaInstitution = self.make_thema_institution_entry(values_corrected[10])
            new_ak.erfassungDatum = self.make_current_datum_eintrag()
            new_ak.migrationsId = None
            new_ak.bemerkungen = []
            new_ak.gattung = self.make_gattungen_korrigiert_hfdb(values_corrected[5])
            new_ak.genre = self.make_genre_korrigiert_hfdb(values_corrected[7])   
            new_ak.klasse = self.make_deskriptoren_entry(values_corrected[13])[1]
            new_ak.sprachen = self.make_sprache_entry(values_corrected[12])
            new_ak.tags = values_corrected[14]
            #new_ak.urheber = []
            new_ak.audioereignisTyp = None #todo
            new_ak.kollektionen = []
            new_ak.konfektionierungRef = [] #todo
            new_ak.produktionRef = None
            new_ak.ausstrahlungRef = []
            new_ak.superKreationRef = [f'http://hfdb.ard.de/drahfdb2/AudioKreation?id={superkreation_ID}']

            #Ebene als Korpus festlegen.
            
            new_ak.hierarchieTyp = {
                'kurzbezeichnung': 'Korpus',
                    'langbezeichnung': 'Korpus',
                    'normId': None
            }
            
            #new_ak_id = self.hfdb_client.service.insertAK(new_ak)
            #Urheber needs to be added after AK exists - Bug in API?
            #new_ak = self.hfdb_client.service.getAK(new_ak_id)
            #new_ak.urheber = self.make_urheber_entry(values_corrected[9], path_list_all_entities_available_urheber)
            #self.hfdb_client.service.updateAK(new_ak)
            #new_ak_fertig = self.hfdb_client.service.getAK(new_ak_id)
            #print(new_ak_fertig)
        else:
            new_ak = False

        return new_ak
    
    def make_ak_v3(self, values_corrected, path_list_all_entities_available,path_list_all_entities_available_urheber, superkreation_ID):
        """Makes AK Entry for other structure Versions for AK-Korpus
        
        Args:
            values_corrected(list): Corrected data from correction window ready to be used for ak
            path_list_all_entities_available(str): Path to source list for NDB data for roles of single Mitwirkender 
            path_list_all_entities_available_urheber(str): Path to pre-processed NDB name dump
            superkreation_ID(str): String of AK that current AK should be daughter of.

        Returns: 
            new_ak (str): URI for newly made AK entry
            urheber (list): Urheber data for further processing

        """
        if values_corrected != False: #Wenn niemand den "Nicht in HFDB übernehmen Knopf gedrückt hat"
            new_ak = self.hfdb_client.service.getAK(self.ref_ak_2)
            new_ak.hfdbId = None
            urheber = self.make_urheber_entry(values_corrected[9], path_list_all_entities_available_urheber)
            print('DEBUG AK_MAKER_03')
            print(urheber)
            #Urheber needs to be added after AK exists - Bug in API?
            new_ak.besetzungen = self.make_mitwirkende_entry(values_corrected[0],  path_list_all_entities_available)
            new_ak.titel = self.make_titel_korrigiert(values_corrected[3])
            new_ak.deskriptionsText = self.make_zusammenfassung_korrigiert_hfdb(values_corrected[2])
            hfdb_ref_topic_persons = f'http://hfdb.ard.de/{self.instance}/AudioKreation?id=4916218'
            new_ak.themaPersonen = self.make_thema_personen_korrigiert_hfdb(hfdb_ref_topic_persons, values_corrected[1])
            new_ak.deskriptor = self.make_deskriptoren_entry(values_corrected[13])[0]
            new_ak.themaOrte = self.make_orte_entry(values_corrected[4], self.ref_ak_2)
            new_ak.themaEreignisse = self.make_thema_ereignis_entry(values_corrected[11])
            new_ak.themaEreignisDatum = self.make_thema_ereignis_datum_entry( values_corrected[11])
            new_ak.themaInstitution = self.make_thema_institution_entry(values_corrected[10])
            new_ak.erfassungDatum = self.make_current_datum_eintrag()
            new_ak.migrationsId = None
            new_ak.bemerkungen = []
            new_ak.gattung = self.make_gattungen_korrigiert_hfdb(values_corrected[5])
            new_ak.genre = self.make_genre_korrigiert_hfdb(values_corrected[7])   
            new_ak.klasse = self.make_deskriptoren_entry(values_corrected[13])[1]
            new_ak.sprachen = self.make_sprache_entry(values_corrected[12])
            new_ak.tags = values_corrected[14]
            #new_ak.urheber = []
            new_ak.audioereignisTyp = None #todo
            new_ak.kollektionen = []
            new_ak.konfektionierungRef = [] #todo
            new_ak.produktionRef = None
            new_ak.ausstrahlungRef = []
            new_ak.superKreationRef = [f'http://hfdb.ard.de/drahfdb2/AudioKreation?id={superkreation_ID}']

            #Ebene als Korpus festlegen.
            
            new_ak.hierarchieTyp = {
                'kurzbezeichnung': 'Korpus',
                    'langbezeichnung': 'Korpus',
                    'normId': None
            }
            
            #new_ak_id = self.hfdb_client.service.insertAK(new_ak)
            #Urheber needs to be added after AK exists - Bug in API?
            #new_ak = self.hfdb_client.service.getAK(new_ak_id)
            #new_ak.urheber = self.make_urheber_entry(values_corrected[9], #path_list_all_entities_available_urheber)
            #self.hfdb_client.service.updateAK(new_ak)

            #new_ak_fertig = self.hfdb_client.service.getAK(new_ak_id)
            #print(new_ak_fertig)

        else: new_ak = False

        return new_ak, urheber
    
    def main_ak_maker(self, ak_id_kompilation_aktuell, status_geflecht_final, transcript, multimodal_data, audiofile_path, file_filtered, path_list_all_entities_available, path_list_all_entities_available_urheber, start, audiofile_name, audioraum_darstellung_global_suggest, kompilationstyp, path_pickle_last_komp_ak = 'kompilations_ak.pickle'):
        """Makes ak based on decisions from structure window
        
        Args:
            ak_id_kompilation_aktuell (str): URI of currently chosen Kompilation
            status_geflecht_final (str): Status that tells how the ai should be levelled  within the HFDB database structure (Kompilation, Korpus etc.)
            transcript (str): Transcript of audio source
            multimodal_data (list): Data directly processed by multimodal LLM currently just used for suggestions for Gattung of audio.
            audiofile_path (str): Path to audiofile of source audio
            file_filtered (str): Path to only speech file pre-processed with YAMnet and VAD.
            path_list_all_entities_available(str): Path to excel file with list of available roles for Mitwirkende.
            path_list_all_entities_available_urheber(str): Path to excel file with list of available roles for Urheber.
            start(list): List of start timecodes of transcript parts
            audiofile_name(str): Name of original source audiofile
            audioraum_darstellung_global_suggest(json-like): This is set for all AKs at first input window for "Audioraumdarstellung"
            kompilationstyp(str): Defines Kompilationstyp if AK is Kompilation (MOIN, SEND, KONZ, etc.)
            path_pickle_last_komp_ak(str): File path where last ak-number is stored, defaults to'kompilations_ak.pickle'
            status_geflecht_final(str): Kind of Geflecht in HFDB that AK should be part of. Defines Ebene that ak is created (Kompilation or Korpus)
            ak_kompilation(str): Latest kompilation ak chosen 
        
        Returns:
            ak_id(str): id of new created ak

        """
        
        #Sonderfall: Neue AK wird als Teil einer neuen Kompilation angelegt, wobei die KI-generierten Daten auf die AK einzahlen und nicht auf die Kompilation, die wiederum eine leere Maske erhält
        if status_geflecht_final == 'new_komp_no_ki':
            gattungen_suggest, genre_suggest, zusammenfassung_suggest, title_suggest, orte_suggest, urheber_suggest, mitwirkende_suggest, sprechende, sprechende_description, topic_persons, topic_persons_description, ndb_thema_persons_suggest, institutionen_suggest, ereignis_suggest, sprachen_suggest, schlagworte_suggest = self.prepare_ak_data_from_raw_data(transcript, multimodal_data, audiofile_path, audiofile_name, path_list_all_entities_available, path_list_all_entities_available_urheber)
            
            values_corrected_komp = self.make_ak_suggests_standard(transcript, start,[[],[],[],[],[]], [[],[],[],[],[]], 'KOMPILATIONS-DATEN HIER SELBST BESTIMMEN', '', [], [], [[],[]], [[],[],[]], [[],[],[]], [[],[],[],[],[]], audiofile_path, audiofile_name, file_filtered, ['Wort'], genre_suggest, [[],[]], [[],[]], audioraum_darstellung_global_suggest)
            
            values_corrected_korpus = self.make_ak_suggests_standard(transcript, start, urheber_suggest, mitwirkende_suggest, title_suggest, zusammenfassung_suggest, topic_persons, topic_persons_description, ndb_thema_persons_suggest, orte_suggest, institutionen_suggest,ereignis_suggest, audiofile_path, audiofile_name, file_filtered, gattungen_suggest, genre_suggest, sprachen_suggest, schlagworte_suggest, audioraum_darstellung_global_suggest)

            values_corrected = values_corrected_korpus
        
        else:
            gattungen_suggest, genre_suggest, zusammenfassung_suggest, title_suggest, orte_suggest, urheber_suggest, mitwirkende_suggest, sprechende, sprechende_description, topic_persons, topic_persons_description, ndb_thema_persons_suggest, institutionen_suggest, ereignis_suggest, sprachen_suggest, schlagworte_suggest = self.prepare_ak_data_from_raw_data(transcript, multimodal_data, audiofile_path, audiofile_name, path_list_all_entities_available, path_list_all_entities_available_urheber)

            values_corrected = self.make_ak_suggests_standard(transcript, start, urheber_suggest, mitwirkende_suggest, title_suggest, zusammenfassung_suggest, topic_persons, topic_persons_description, ndb_thema_persons_suggest, orte_suggest, institutionen_suggest,ereignis_suggest, audiofile_path, audiofile_name, file_filtered, gattungen_suggest, genre_suggest, sprachen_suggest, schlagworte_suggest, audioraum_darstellung_global_suggest)
 
        if values_corrected[0] != False:
            #Konf/Amo-Data to pass on
            konf_audioraum = values_corrected[6]
            lese_abspielgeschwindigkeit = values_corrected[8]
            AMO_komp_id = None
            #Werte, die nur für V3 new_komp_no_ki relevant sind
            konf_komp_audioraum = None
            lese_abspielgeschwindigkeit_komp = 'Kein Eintrag'
            ak_komp_id = None

            if status_geflecht_final == 'new_korpus': #V1
                ak_id = self.make_ak_v1_v2(values_corrected, path_list_all_entities_available,path_list_all_entities_available_urheber, 'korpus', kompilationstyp)
            elif status_geflecht_final == 'new_komp': #V2
                ak_id = self.make_ak_v1_v2(values_corrected,  path_list_all_entities_available, path_list_all_entities_available_urheber, 'kompilation', kompilationstyp)

                ak_komp_id_number = ak_id.split('?id=')[1]
                kompilations_ak = ak_komp_id_number
                with open(path_pickle_last_komp_ak, 'wb') as handle:
                    pickle.dump(kompilations_ak, handle, protocol=pickle.HIGHEST_PROTOCOL)

            elif status_geflecht_final == 'new_komp_no_ki': #V3
                ak_komp_id = self.make_ak_v1_v2(values_corrected_komp,  path_list_all_entities_available, path_list_all_entities_available_urheber, 'kompilation', kompilationstyp)

                ak_komp_id_number = ak_komp_id.split('?id=')[1]
                print('ak_komp_id_number:', ak_komp_id_number)

                #Write new Kompilations-AK to pickle
                kompilations_ak = ak_komp_id_number
                with open(path_pickle_last_komp_ak, 'wb') as handle:
                    pickle.dump(kompilations_ak, handle, protocol=pickle.HIGHEST_PROTOCOL)

                ak_korpus_id, urheber = self.make_ak_v3(values_corrected_korpus,  path_list_all_entities_available,path_list_all_entities_available_urheber, ak_komp_id_number)
                ak_korpus_id.urheber = urheber
                print('DEBUG URHEBER 3')
                print(ak_korpus_id.urheber)

                konf_komp_audioraum = values_corrected_komp[6]
                lese_abspielgeschwindigkeit = values_corrected_komp[8]

                #In diesem Fall ist "ak_id" der gesamte, noch nicht angelegte AK-Inhalt, der in diesem Fall mit der Einzelkonf zusammen erst die Form einer AK annehmen kann, da es sonst Probleme bei der Anlegung (doppelt erstellte AK) gibt.
                ak_id = ak_korpus_id
                print('DEBUG URHEBER 3')
                print(ak_id.urheber)

                ak_komp_nach_korpus = self.hfdb_client.service.getAK(ak_komp_id)

            elif status_geflecht_final == 'add_to_vorhandene_komp': #V4
                ak_id, urheber = self.make_ak_v3(values_corrected,  path_list_all_entities_available,path_list_all_entities_available_urheber, ak_id_kompilation_aktuell)
                ak_id.urheber = urheber
                print('DEBUG URHEBER 4')
                print(ak_id.urheber)
                AK_komp = self.hfdb_client.service.getAK(f'http://hfdb.ard.de/drahfdb2/AudioKreation?id={ak_id_kompilation_aktuell}')
                konf_komp = self.hfdb_client.service.getKonf(AK_komp.konfektionierungRef[0])
                AMO_komp_id = self.hfdb_client.service.getAMO(konf_komp.hfdbId)

                #Weil eigentlich fast alles gleich ist wie bei "new_korpus", ändern wir hier nur nachträglich den HierarchieTyp auf Kompilation
                #ak_new = self.hfdb_client.service.getAK(ak_id)
            # ak_new.hierarchieTyp = {
                #   'kurzbezeichnung': 'Kompilation',
                #  'langbezeichnung': 'Kompilation',
                #  #  'normId': None
            # }
                #self.hfdb_client.service.updateAK(ak_new)
        else:
            ak_id = False
            konf_audioraum = False 
            lese_abspielgeschwindigkeit = False 
            AMO_komp_id = False 
            konf_komp_audioraum = False 
            lese_abspielgeschwindigkeit_komp = False 
            ak_komp_id = False

        return ak_id, konf_audioraum, lese_abspielgeschwindigkeit, AMO_komp_id, konf_komp_audioraum, lese_abspielgeschwindigkeit_komp, ak_komp_id



        
