import vertexai
from vertexai.language_models import TextGenerationModel
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models
import pandas as pd
import time
import config
import json
from vertexai.preview.generative_models import (
    Content,
    FunctionDeclaration,
    GenerativeModel,
    Part,
    Tool,
)
  
class process_text_with_gemini():

    def __init__(self, project_id_google = config.Google_API_ID):
        """
        Args:
            project_id_google(str): Google-Project_id for specific project for billing purposes - Defaults to general test_project

        """
        self.project_id = project_id_google
    
    def generate(self, questions, max_output_tokens= 8192, temperature = 0, location="europe-west4", model = "gemini-1.5-pro-001"):
        """General Google Gemini requests handler. Handles requests and returns answers from LLM-API. Defines parameters for requests. Returns answers in json-format
        Args:
            questions (str): Request to LLM in written form like "Tell my something about..."
            max_output_tokens (int): Maximum tokens that output can have. Can be regulated by Google API as well. Defaults to .... a lot.
            temperature (int): Defines how creative the LLM is supposed to be. Defaults to 0 for not creative at all (stick exactly to what you are told to do)
            location (str): Defines Google region that should be used for requests. Defaults to "europe-west4" for Niederlande.
            model (str): Gemini-Model that should be used for requests. 

        Returns:
            responses_all(list): Raw version of all responses that are returned by the LLM
        
        """
        vertexai.init(project=self.project_id, location=location)
        model = GenerativeModel(model)
        responses = model.generate_content(
            questions,
            generation_config={
                "max_output_tokens": max_output_tokens,
                "temperature": temperature,
                "top_p": 1,
                "response_mime_type": "application/json"
            },
            safety_settings={
                generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            },
            stream=True,
        )
        responses_all = []
        for response in responses:
            responses_all.append(response.text)
        joiner = ''
        responses_all = joiner.join(responses_all)
        #print('DEBUG GOOGLE RESPONSE')
        #print(responses_all)
        return(responses_all)
    
    def generate_free_text(self, questions, max_output_tokens= 10000, temperature = 0, location="europe-west4", model = "gemini-1.5-flash"):
        """General Google Gemini requests handler. Handles requests and returns answers from LLM-API. Defines parameters for requests. Returns answers in free text format
        Args:
            questions (str): Request to LLM in written form like "Tell my something about..."
            max_output_tokens (int): Maximum tokens that output can have. Can be regulated by Google API as well. Defaults to 10000.
            temperature (int): Defines how creative the LLM is supposed to be. Defaults to 0 for not creative at all (stick exactly to what you are told to do)
            location (str): Defines Google region that should be used for requests. Defaults to "europe-west4" for Niederlande.
            model (str): Gemini-Model that should be used for requests. 

        Returns:
            responses_all(list): Raw version of all responses that are returned by the LLM
        
        """
        vertexai.init(project=self.project_id, location=location)
        model = GenerativeModel(model)
        responses = model.generate_content(
            questions,
            generation_config={
                "max_output_tokens": max_output_tokens,
                "temperature": temperature,
                "top_p": 1
            },
            safety_settings={
                generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            },
            stream=True,
        )
        responses_all = []
        for response in responses:
            responses_all.append(response.text)
        joiner = ''
        responses_all = joiner.join(responses_all)
        #print('DEBUG GOOGLE RESPONSE')
        #print(responses_all)
        return(responses_all)
    
    def make_whole_text(self, text_input_list):
        """Makes a string out of lists of text
        
        Args:
            text_input_list(list): Text input as list that should be converted to single string.

        Returns:
            text_whole(str): Whole text as one single string
        
        """
        joiner = ' '
        text_whole = joiner.join(text_input_list)

        return(text_whole)
    
    def set_zusammenfassung(self, text_input, temperature = 0, max_output = 8192, location = "europe-west4"):
        """LLM-request for extracting important persons from source transcript
        Args:
            text_input (str): Source transcript given to the LLM with fixed prompt.
            temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
            max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 100000.
            location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
            
        Returns:
            zfassung(str): Zusammenfassung of transcript given.
        
        """
        schema = """{"zusammenfassung": str}"""
        prompt_text_combined = f"""
                Erstelle eine neutral formulierte Zusammenfassung für dieses Transkript eines Radiobeitrags: {text_input}
                Using this JSON schema: {schema}
                """
        #prompt_text_combined = f"""Erstelle eine neutral formulierte Zusammenfassung für dieses Transkript eines Radiobeitrags: {text_input}. Nutze dieses json-Schema: zusammenfassung = {'zusammenfassung': str}"""

        #Handler for possible API timeouts
        got_response = False
        while got_response == False:
            try:
                response = self.generate(prompt_text_combined,max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(e, '2')
                time.sleep(60)
                        
                        #response = self.generate(prompt_text_combined,max_output, temperature, location)

        #Convert to json and read result
        zfassung = ''
        try:
            json_zfassung = json.loads(response)
            zfassung = json_zfassung['zusammenfassung']
        except:
            pass
        return(zfassung)
    
    def set_schlagworte(self, text_input, temperature = 0, max_output = 1000, location = "europe-west4"):
        """LLM-request for getting Schlagworte for Transcript
        Args:
            text_input (str): Source transcript given to the LLM with fixed prompt.
            temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
            max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 1000.
            location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
            
        Returns:
            tags_list(list): List of Tags
        
        """
        schema = """[{"Schlagwort": str}]"""
        
        prompt_text_combined = f"""Gib eine Liste von maximal 10 kurzen und prägnanten Schlagworten für einen Datenbankeintrag zu einem Audio mit diesem Transkript aus: {text_input}, Using this JSON schema: {schema}"""
        got_response = False
        while got_response == False:
            try:
                response = self.generate(prompt_text_combined,max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(e, '2')
                time.sleep(60)
                        
                        #response = self.generate(prompt_text_combined,max_output, temperature, location)
        #Convert to json and read result
        try:
            json_tags = json.loads(response)
            tags = json_tags
            tags_list = []
            for i in range(len(tags)):
                try:
                    tags_list.append(tags[i]['Schlagwort'])
                except:
                    pass
        except:
            tags_list = []

        return(tags_list)
    
    def set_ueberschrift(self, text_input, temperature = 0, max_output = 1000, location = "europe-west4"):
        """LLM-request for extracting important persons from source transcript
        Args:
            text_input (str): Source transcript given to the LLM with fixed prompt.
            temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
            max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 1000.
            location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
            
        Returns:
            ueberschrift(str): Heading of database entry to suggest
        
        """
        schema = """{"ueberschrift": str}"""
        prompt_text_combined = f"""Erstelle einen passenden Titel für einen Archiveintrag zu diesem Transkript eines Radiobeitrags: {text_input}, Mache keine Vorschläge, sondern gib den besten Vorschlag direkt aus! Keine Erklärungen, nur den reinen Vorschlag!
        Using this json-Schema: {schema}
        """
        
        got_response = False
        while got_response == False:
            try:
                response = self.generate(prompt_text_combined,max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(e, '2')
                time.sleep(60)
                        
                        #response = self.generate(prompt_text_combined,max_output, temperature, location)

        #Decode json-Schema
        json_ueberschrift = json.loads(response)
        ueberschrift = json_ueberschrift['ueberschrift']
        return(ueberschrift)

    def make_proper_list_from_persons(self, persons_raw):
        """Decodes json output from LLM and handles possible wrong json formats
        Args:
            persons_raw(json): Raw json-output from LLM.
        
        Returns:
            person_list(list): List of person names extracted from Transcript
            beschreibung_list(list): List ob descriptions for persons in person_list extracted from transcript
        
        """
        persons_raw_json = persons_raw
        person_list = []
        beschreibung_list = []

        #Decode Json
        try:
            json_personen = json.loads(persons_raw_json)
            personen_all_data = json_personen

            try:
                for i in range(len(personen_all_data)):
                    person_list.append(personen_all_data[i]["person_found"]['person_name'])
                    beschreibung_list.append(personen_all_data[i]["person_found"]['person_beschreibung'])
            except:
                person_list = ['ERROR json Ausgabe']
                beschreibung_list = ['ERROR json Ausgabe']
        except:
            person_list = []
            beschreibung_list = []

        return(person_list, beschreibung_list)
    
    def load_roles_possible(self, excel_source):
        """Handler for excel input for possible roles of persons
        
        Args:
            excel_source(str): Filepath of source document where possible roles are stored

        Returns:
            langbez_gefiltert(list): List of roles that can appear realistically in the given context as defined in excel source.
        
        """
        #Lese die Excel-Quelldatei mit Pandas aus und definiere die beiden Spalten als Quell-Listen und baue daraus einen Dataframe, um damit weiter zu arbeiten.
        df = pd.read_excel(excel_source)
        langbez = df['Langbezeichnung']
        realistisch = df['realistische_auswahl_vorkommende_personen']
        
        langbez_gefiltert = []

        for i in range(len(langbez)):
            if 'ja' in realistisch[i].lower():
                langbez_gefiltert.append(langbez[i])

        return (langbez_gefiltert)            
    
    def find_persons(self, text_input, temperature = 0, max_output = 2048, location = "europe-west4"):
        """LLM-request for extracting important persons from source transcript
        Args:
            text_input (str): Source transcript given to the LLM with fixed prompt.
            temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
            max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 2048.
            location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
            
        Returns:
            response(json): The LLMs response in json format
        
        """
        schema = """[{"person_found": {person_name: str, person_beschreibung: str}}]"""
        prompt_text_combined = ['Welche mit Namen (Vorname und Nachname oder nur Vorname oder nur Nachname) genannten Personen nehmen in diesem Text eine bedeutende Rolle ein?', f'Text: {text_input}', 'Wie werden diese Personen in diesem Text beschrieben?', 'Nenne die Personen als Liste, so wie sie im Text genannt werden, in folgendem Format: **- Person: Beschreibung', 'Nenne nur solche Personen, die auch mit Vor- oder Nachnamen vertreten sind.', 'Nenne jede Person nur einmal.', f'Nutze dieses json-Schema: {schema}']
        got_response = False
        while got_response == False:
            try:
                response = self.generate(prompt_text_combined,max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(e, '2')
                time.sleep(60)
                
                #response = self.generate(prompt_text_combined,max_output, temperature, location)

        return(response)
    
    def is_person_speaker_or_topic(self, text_input, person, temperature = 0, max_output = 2048, location = "europe-west4"):
        """Defines if a person speaks within an audio or if he or she ist just topic
        
        Args:
                text_input (str): Source transcript given to the LLM with fixed prompt.
                temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
                max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 1000.
                location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
                
            Returns:
                response(json): The LLMs response in json format
            
            """
        
        schema = """{"person": {"person_name": str, "person_rolle": str}}"""
        prompt_text_combined = [f'Spricht die Person {person} in dem Audio zu dem dieses Transkript gehört selbst oder wird über sie gesprochen?', f'Wenn die Person {person}, im Transkript selber spricht, dann ist die Antwort "Sprecher", sonst ist die Antwort "Thema".', f'Text: {text_input}', 'Nur eine der beiden Antwortmöglichkeiten ausgeben, keine weiteren Erklärungen!', f'Beziehe Dich nur auf die Person mit dem Namen {person}.', f'Nutze dieses json-Schema: {schema}']
        got_response = False
        while got_response == False:
            try:
                response = self.generate(prompt_text_combined,max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(str(e), '1')
                
                #Umgehung für Fehler "Content has no parts - ggf. dem später noch mal nachgehen"
                if "Content" in str(e):
                    print('Umgehung Contentfehler')
                    response = 'Es wird über die Person gesprochen'
                    got_response = True
                time.sleep(60)
                #response = self.generate(prompt_text_combined,max_output, temperature, location)
       
        #Decode Json
        json_thema_topic = response
        thema_topic_list = json.loads(json_thema_topic)
        personenrolle = thema_topic_list['person']['person_rolle']
        return(personenrolle)
    
    def is_person_urheber(self, text_input, person, temperature = 0, max_output = 2048, location = "europe-west4"):
        """Defines if a person is handled as an "Urheber" of the audio.
        
        Args:
                text_input (str): Source transcript given to the LLM with fixed prompt.
                temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
                max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 2048.
                location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
                
            Returns:
                response(json): The LLMs response in json format
            
            """
        schema = """{"person": {"person_name": str, "is_person_urheber": bool}}"""
        prompt_text_combined = [f'Ist {person} in dem Audio zu dem dieses Transkript gehört auch als Urheber des Audios zu sehen?', f'Text: {text_input}', 'Antwort: "Ja" oder "Nein"', 'Hinweis: Urheber in unserem Sinne sind: Arrangeure, Autoren, Textdichter, Bearbeiter, Herausgeber, Kommentatoren, Komponisten, Berichterstatter, Mitarbeiter an einer Reportage oder Übersetzer.', 'Personen mit anderen Rollen im Text sind keine Urheber!', f'Using this json-Schema: {schema}']
        got_response = False
        while got_response == False:
            try:
                response = self.generate(prompt_text_combined,max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(str(e), '1')
                
                #Umgehung für Fehler "Content has no parts - ggf. dem später noch mal nachgehen"
                if "Content" in str(e):
                    print('Umgehung Contentfehler')
                    response = 'Es wird über die Person gesprochen'
                    got_response = True
                time.sleep(60)
                #response = self.generate(prompt_text_combined,max_output, temperature, location)
      
        #Decode Json
        try:
            json_is_urheber = response
            urheber_list = json.loads(json_is_urheber)
            is_urheber = urheber_list['person']["is_person_urheber"]
        except:
            is_urheber = 'Nein'
        return(is_urheber)
    
    
    def find_person_roles(self, text_input, list_roles_possible, person_found, temperature = 0, max_output = 2048, location = "europe-west4"):
        """LLM-request for finding the roles of persons
        Args:
            text_input (str): Source transcript given to the LLM with fixed prompt.
            list_roles_possible(list): A list of roles the LLM can choose from.
            person_found(str): Person extracted from text that we want to set the role for.
            temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
            max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 2048.
            location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
            
        Returns:
            response(json): The LLMs response in json format
        
        """
        got_response = False
        while got_response == False:
            try:
                schema = """{"person": {"person_name": str, "person_rolle": str}}"""
                prompt_text_combined = [f'Welche Rolle nimmt {person_found} im Text ein?', f'Text: {text_input}', f'Wähle eine Rolle aus folgender Liste: {list_roles_possible}', f'Using this json-Schema: {schema}']
                response = self.generate(prompt_text_combined ,max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(e, '3')
                time.sleep(60)
                #response = self.generate(prompt_text_combined,max_output, temperature, location)

        #Decode-Json
        json_rolle = response
        rolle_list = json.loads(json_rolle)
        rolle = rolle_list['person']["person_rolle"]
        
        return(rolle)
    
    def make_roles_list(self, text_input, list_persons, excel_source):
        """Process json raw outputs to make them lists of roles

        Args:
            text_input(str): Full text of transcript
            list_persons(str): Person names that we want to know the roles of.
            excel_source(str): Excel Source for possible roles - is loaded via excel source handler
        
        Returns:
            list_roles_final_llm(list): List of roles according to llm for persons given as input.

        
        """
        list_roles_final_llm = []
        list_roles_possible = self.load_roles_possible(excel_source)

        for i in range(len(list_persons)):
            person_role = self.find_person_roles(text_input, list_roles_possible, list_persons[i])
            print(person_role)
            #person_role_split = person_role.split('**')[1]
            role_found = False
            try:
                for i in range(len(list_roles_possible)):
                    if list_roles_possible[i] in person_role:
                        list_roles_final_llm.append(list_roles_possible[i])
                        role_found = True
                        break
                if role_found == False:
                    for i in range(len(list_roles_possible)):
                        if list_roles_possible[i] in person_role:
                            list_roles_final_llm.append(list_roles_possible[i])
                            role_found = True
                            break
                if role_found == False:        
                    list_roles_final_llm.append(None)
            except TypeError:
                list_roles_final_llm.append(None)
        
        return(list_roles_final_llm)
        
    def make_proper_list_from_orte(self, orte_raw):
        """Makes proper Orte list from raw json places output
        
        Args:
            orte_raw (json): Raw json-Output for Orte from LLM

        Returns:
            orte_list (list): List of names for places (Orte) extracted from transcript by LLM
            orte_beschreibungen (list): List of descriptions of places as given by LLM.
        
        """
        orte_list = []
        orte_beschreibungen = []
        if "None" not in orte_raw:
            orte_raw_lines = json.loads(orte_raw)
            print(orte_raw_lines)
            try:
                for i in range(len(orte_raw_lines['ort'])):
                    if orte_raw_lines['ort'][i]["ort_name"]!= None:
                        orte_list.append(orte_raw_lines['ort'][i]["ort_name"])
                        orte_beschreibungen.append(orte_raw_lines['ort'][i]["ort_kontext"])
            except KeyError:
                try:
                    for i in range(len(orte_raw_lines['orte'])):
                        if orte_raw_lines['orte'][i]["ort_name"]!= None:
                            orte_list.append(orte_raw_lines['orte'][i]["ort_name"])
                            orte_beschreibungen.append(orte_raw_lines['orte'][i]["ort_kontext"])
                except KeyError:
                    orte_list = []
                    orte_beschreibungen = []
                    try:
                        if orte_raw_lines['ort']["ort_name"] != None:
                            orte_list.append(orte_raw_lines['ort']["ort_name"])
                            orte_beschreibungen.append(orte_raw_lines['ort']["ort_kontext"])
                    except:
                        orte_list = []
                        orte_beschreibungen = []

            
        return(orte_list, orte_beschreibungen)
    
    def make_proper_list_from_institutionen(self, inst_raw):
        """Extracts information about institutions from json-LLM-Outputs
        
        Args:
            inst_raw(json): Raw json-Output for institutions from LLM

        Returns:
            inst_list(list): List of single institution names
        
        """
        if "None" not in inst_raw:
            try:
                inst_raw_lines = json.loads(inst_raw)
                inst_list = []

                try:
                    for i in range(len(inst_raw_lines['Institution'])):
                        inst_list.append(inst_raw_lines['Institution'][i]["institution_name"])
                except KeyError:
                    inst_list = []
                    
                    if inst_raw_lines['Institution']["institution_name"] != None:
                        inst_list.append(inst_raw_lines['Institution']["institution_name"])
            
                if isinstance(inst_list[0], list):
                    inst_list = inst_list[0]             
            except:
                inst_list = [inst_raw]
        else:
            inst_list = []
            
                
        print('DEBUG_Return_LLM_Proper_list_inst', inst_list)   
        return(inst_list)
    
    def make_proper_list_from_ereignis(self, ereignis_raw):
        """Creates useable data for Ereignisse from LLM raw json-Output
        
        Args:
            ereignis_raw(json): Raw json-output from LLM

        Returns:
            ereignis_list(list): List of single Ereignisse extracted from json
        
        """
        if "None" not in ereignis_raw:
            try:
                ereignis_raw_lines = json.loads(ereignis_raw)
                ereignis_list = []
                print('DEBUG EREIGNIS:', ereignis_raw_lines)
                try:
                    for i in range(len(ereignis_raw_lines)):
                        ereignis_list.append(ereignis_raw_lines[i]['ereignis']["ereignis_bezeichnung"])
                except  KeyError:
                    try:
                        for i in range(len(ereignis_raw_lines['ereignis'])):
                            ereignis_list.append(ereignis_raw_lines['ereignis'][i]["ereignis_bezeichnung"])
                    except:
                        try:
                            for i in range(len(ereignis_raw_lines['ereignis'])):
                                ereignis_list.append(ereignis_raw_lines['ereignis']["ereignis_bezeichnung"])
                        except:
                            for i in range(len(ereignis_raw_lines['ereignisse'])):
                                ereignis_list.append(ereignis_raw_lines['ereignisse'][i]['ereignis']["ereignis_bezeichnung"])
            except:
                ereignis_list = [] 

        else:
            ereignis_list = []    
        return(ereignis_list)
    
    def make_proper_list_from_sprache(self, sprache_raw):
        """Creates useable data from raw json LLM output for Sprache
        
        Args:
            sprache_raw(json): Raw json-output from LLM for languages

        Returns:
            sprache_list(list): Useable list for further processing of languages extrated by LLM.
        
        """
        if "None" not in sprache_raw:
            sprache_raw_lines = json.loads(sprache_raw)
            sprache_list = []

            for i in range(len(sprache_raw_lines)):
                try:
                    if sprache_raw_lines[i]['sprache'] not in sprache_list:
                        sprache_list.append(sprache_raw_lines[i]['sprache'])
                except KeyError:
                    for s in range(len(sprache_raw_lines['sprache'])):
                        if sprache_raw_lines['sprache'][s] not in sprache_list:
                            sprache_list.append(sprache_raw_lines['sprache'][s])

        return(sprache_list)
        
    def set_thema_ort(self, text_input, temperature = 0, max_output = 2048, location = "europe-west4"):
        """Defines places that are important in the source transcript
        
        Args:
            text_input (str): Source transcript given to the LLM with fixed prompt.
            temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
            max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 1000.
            location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
                
        Returns:
            response(json): The LLMs response in json format
            
            """
        schema = """{"ort": {"ort_name": str, "ort_kontext": str}}"""
        prompt_text_combined = [f'Welche Orte nehmen in diesem Text eine bedeutende Rolle ein?:  {text_input}?', 'Nenne die Orte als Liste', 'Nenne nur Orte im geographischen Sinne, keine Institutionen!', 'Gib auch als kurze Zusammenfassung in einem Satz den Kontext an, in dem der Ort genannt wird', 'Gib nur für die Aussage des Textes wirklich bedeutende und spezielle Orte an','Jeder Ort sollte nur einmal in der Liste vorkommen!' f'Nutze dieses json-Schema: {schema}']
        got_response = False
        while got_response == False:
            try:
                response = self.generate(prompt_text_combined,max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(e, '4')
                time.sleep(60)
                if "Content" in str(e):
                    response = 'Keine Zusatz-Info'
                    got_response = True
                #response = self.generate(prompt_text_combined,max_output, temperature, location)

        return(response)
    
    
    def set_thema_institution(self, text_input, temperature = 0, max_output = 2048, location = "europe-west4"):
        """Defines institutions
        
        Args:
            text_input (str): Source transcript given to the LLM with fixed prompt.
            temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
            max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 1000.
            location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
                
        Returns:
            response(json): The LLMs response in json format
            
            """
        schema = """{"Institution": {"institution_name": str}}"""
        prompt_text_combined = [f'Gibt es Institutionen, die in diesem Text eine bedeutende Rolle einnehmen?:  {text_input}?', 'Wenn ja, nenne die Institutionen so wie sie im Text genannt werden', 'Institutionen können öffentliche Einrichtungen sein, Firmen, und Ähnliches, die einen Eigennamen haben. Wenn keine relevanten Institutionen vorkommen, gib "None" aus! Keine allgemeinen Begriffe nennen wie "Clubs" oder "Dörfer"! Diese sind keine Institutionen!', f'Nutze dieses json-Schema: {schema}']
        got_response = False
        while got_response == False:
            try:
                response = self.generate(prompt_text_combined,max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(e, '4')
                time.sleep(60)
                if "Content" in str(e):
                    response = 'Keine Zusatz-Info'
                    got_response = True

        return(response)
    
    def set_thema_ereignis(self, text_input, temperature = 0, max_output = 2048, location = "europe-west4"):
        """Defines "Ereignisse" that are important within the transcript
        
        Args:
            text_input (str): Source transcript given to the LLM with fixed prompt.
            temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
            max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 1000.
            location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
                
        Returns:
            response(json): The LLMs response in json format
            
            """
        schema = """[{"ereignis": {"ereignis_bezeichnung": str}}, {"ereignis": {"ereignis_bezeichnung": str}}]"""
        prompt_text_combined = [f'Gibt es historisch bedeutsame Ereignisse, die in diesem Text eine bedeutende Rolle einnehmen?:  {text_input}?', 'Wenn ja, nenne die Ereignisse als Stichwort-Liste, so wie sie im Text genannt werden, in folgendem Format: - Ereignis', 'Ereignisse sind besondere Vorkommnisse, Jubiläen, Geburtstage, etc. die für die Allgemeinheit bedeutsam sind und im Text genannt werden. Wenn kein historisch bedeutsames Ereignis im Text vorkommt, gib "None" aus!', f'Using this json-Schema: {schema}']
        got_response = False
        while got_response == False:
            try:
                response = self.generate(prompt_text_combined,max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(e, '4')
                time.sleep(60)
                if "Content" in str(e):
                    response = 'Keine Zusatz-Info'
                    got_response = True
                #response = self.generate(prompt_text_combined,max_output, temperature, location)

        return(response)
    
    def get_beschreibung_ort(self, text_input, ort_extracted, temperature = 0, max_output = 2048, location = "europe-west4"):

        """Defines description for single Ort
        
        Args:
            text_input (str): Source transcript given to the LLM with fixed prompt.
            ort_extracted(str): Single Ort that was extracted in previous step.
            temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
            max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 1000.
            location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
                
        Returns:
            response(json): The LLMs response in json format
            
            """
        schema = """{"ort": {"ort_name": str, "ort_beschreibung": str}}"""
        prompt_text_combined = [f'In welchem Kontext taucht der Ort {ort_extracted} in folgendem Text auf?', f'Text: {text_input}', 'Antworte in einem Satz!', f'Nutze dieses json-Schema: {schema}']
        got_response = False
        while got_response == False:
            try:
                response = self.generate(prompt_text_combined,max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(str(e), '5')
                time.sleep(60)

                if "Content" in str(e):
                    response = 'Keine Zusatz-Info'
                    got_response = True
                #response = self.generate(prompt_text_combined,max_output, temperature, location)

        #Decode Json
        json_beschreibung_ort = json.loads(response)
        ort = json_beschreibung_ort['ort']['ort_beschreibung']
        return(ort)
    
    def get_beschreibung_institution(self, text_input, inst_extracted, temperature = 0, max_output = 2048, location = "europe-west4"):

        """Defines description text for Institution
        
        Args:
            text_input (str): Source transcript given to the LLM with fixed prompt.
            inst_extracted(str): Single institution that was extracted in previous step.
            temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
            max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 1000.
            location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
                
        Returns:
            response(json): The LLMs response in json format
            
            """
        schema = """{"institution": {"institution_name": str, "institution_beschreibung": str}}"""
        prompt_text_combined = [f'In welchem Kontext taucht diese Institution {inst_extracted} in folgendem Text auf?', f'Text: {text_input}', 'Antworte in einem Satz!', f'Using this json-Schema: {schema}']
        got_response = False
        while got_response == False:
            try:
                response = self.generate(prompt_text_combined,max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(str(e), '5')
                time.sleep(60)

                if "Content" in str(e):
                    response = 'Keine Zusatz-Info'
                    got_response = True
                #response = self.generate(prompt_text_combined,max_output, temperature, location)
        #Decode Json
        json_beschreibung_institution = json.loads(response)
        beschreibung_inst = json_beschreibung_institution['institution']['institution_beschreibung']
        return(beschreibung_inst)
        
    def get_beschreibung_ereignis(self, text_input, ereignis_extracted, temperature = 0, max_output = 2048, location = "europe-west4"):

        """Defines Description text for Ereignis
        
        Args:
            text_input (str): Source transcript given to the LLM with fixed prompt.
            ereignis_extracted(str): Single Ereignis that was extracted in previous step.
            temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
            max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 1000.
            location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
                
        Returns:
            response(json): The LLMs response in json format
            
            """
        schema = """{"ereignis": {"ereignis_name": str, "ereignis_beschreibung": str}}"""
        prompt_text_combined = [f'In welchem Kontext wird dieses Ereignis "{ereignis_extracted}" in folgendem Text genannt?', f'Text: {text_input}', 'Antworte in einem Satz!', f'Using this json-Schema: {schema}']
        got_response = False
        while got_response == False:
            try:
                response = self.generate(prompt_text_combined,max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(str(e), '5')
                time.sleep(60)

                if "Content" in str(e):
                    response = 'Keine Zusatz-Info'
                    got_response = True
                #response = self.generate(prompt_text_combined,max_output, temperature, location)
        
        #Decode Json
        json_beschreibung_ereignis = json.loads(response)
        beschreibung_ereignis = json_beschreibung_ereignis['ereignis']['ereignis_beschreibung']
        return(beschreibung_ereignis)
    
    def get_tag_realisierung(self, text_input, temperature = 0, max_output = 2048, location = "europe-west4"):

        """Defines date for Ereignis
        
        Args:
            text_input (str): Source transcript given to the LLM with fixed prompt.
            temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
            max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 1000.
            location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
                
        Returns:
            response(json): The LLMs response in json format
            
            """
        schema = """{"realisierung": {"realisierung_tag": int, "realisierung_monat": int, "realisierung_jahr": int, "realisierung_zusatz": str}}"""
        prompt_text_combined = [f'An welchem Datum wurde die Aufnahme zu dem Audio zu diesem Transkript vermutlich gemacht oder an welchem Datum hat sie angefangen?', f'Text: {text_input}', 'Wenn Du das Datum nicht genau ermitteln kannst, dann gib als "realisierung_zusatz" "ca", "vor" oder "nach" aus, wobei diese Angaben sich auf das ausgegebene Datum beziehen. Sonst gib als "realisierung_zusatz" None aus. Antworte nur mit dem Datum in folgendem Format: TT.MM.JJJJ! Wenn Du aus dem Text kein Datum ermitteln kannst, gib "None" aus! Wenn Du für das vorgegebene Format für einen Teil des Datums keinen Wert ermitteln kannst, gib dafür "0" aus. Wenn Du zum Beispiel keinen Tag ermitteln kannst, dafür aber Jahr und Monat, gib das Datum in folgendem Format aus: 00.MM.JJJJ! Wenn Du zum Beispiel kein Jahr ermitteln kannst, dafür aber Monat und Tag, gib das Datum in folgendem Format aus: TT.MM.0000!', f'Using this json-Schema: {schema}']
        got_response = False
        while got_response == False:
            try:
                response = self.generate(prompt_text_combined,max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(str(e), '5')
                time.sleep(60)

                if "Content" in str(e):
                    response = 'Keine Zusatz-Info'
                    got_response = True
                #response = self.generate(prompt_text_combined,max_output, temperature, location)

        #Decode Json
        try:
            json_realisierung_tag = json.loads(response)
            realisierung_tag = json_realisierung_tag['realisierung']['realisierung_tag']
            realisierung_monat = json_realisierung_tag['realisierung']['realisierung_monat']
            realisierung_jahr = json_realisierung_tag['realisierung']['realisierung_jahr']
            realisierung_zusatz = json_realisierung_tag['realisierung']['realisierung_zusatz']
        except:
            realisierung_tag = 0
            realisierung_monat = 0
            realisierung_jahr = 0
            realisierung_zusatz = None
        return(realisierung_tag, realisierung_monat, realisierung_jahr, realisierung_zusatz)
    
    def get_tag_realisierung_ende(self, text_input, temperature = 0, max_output = 2048, location = "europe-west4"):

        """Defines date for Ereignis
        
        Args:
            text_input (str): Source transcript given to the LLM with fixed prompt.
            temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
            max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 1000.
            location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
                
        Returns:
            response(json): The LLMs response in json format
            
            """
        schema = """{"realisierung": {"realisierung_tag": int, "realisierung_monat": int, "realisierung_jahr": int, "realisierung_zusatz": str}}"""
        prompt_text_combined = [f'Wurde das Audio zu diesem Transkript vermutlich an mehreren Tagen aufgenommen? Wenn ja, wann endete die Aufnahme?', f'Transkript: {text_input}', 'Wenn Du das Datum nicht genau ermitteln kannst, dann gib als "realisierung_zusatz" "ca", "vor" oder "nach" aus, wobei diese Angaben sich auf das ausgegebene Datum beziehen. Sonst gib als "realisierung_zusatz" None aus. Antworte nur mit dem Datum in folgendem Format: TT.MM.JJJJ! Wenn Du aus dem Text kein Datum ermitteln kannst oder das Audio nur an einem Tag aufgenommen wurde, gib "None" aus! Wenn Du für das vorgegebene Format für einen Teil des Datums keinen Wert ermitteln kannst, gib dafür "0" aus. Wenn Du zum Beispiel keinen Tag ermitteln kannst, dafür aber Jahr und Monat, gib das Datum in folgendem Format aus: 00.MM.JJJJ! Wenn Du zum Beispiel kein Jahr ermitteln kannst, dafür aber Monat und Tag, gib das Datum in folgendem Format aus: TT.MM.0000!', f'Using this json-Schema: {schema}']
        got_response = False
        while got_response == False:
            try:
                response = self.generate(prompt_text_combined,max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(str(e), '5')
                time.sleep(60)

                if "Content" in str(e):
                    response = 'Keine Zusatz-Info'
                    got_response = True
                #response = self.generate(prompt_text_combined,max_output, temperature, location)

        #Decode Json
        try:
            json_realisierung_tag = json.loads(response)
            realisierung_tag = json_realisierung_tag['realisierung']['realisierung_tag']
            realisierung_monat = json_realisierung_tag['realisierung']['realisierung_monat']
            realisierung_jahr = json_realisierung_tag['realisierung']['realisierung_jahr']
            realisierung_zusatz = json_realisierung_tag['realisierung']['realisierung_zusatz']
        except:
            realisierung_tag = 0
            realisierung_monat = 0
            realisierung_jahr = 0
            realisierung_zusatz = 'None'
        return(realisierung_tag, realisierung_monat, realisierung_jahr, realisierung_zusatz)

    def get_realisierung_tag_context(self, text_input, ereignis_anfang_datum, ereignis_ende_datum, temperature = 0, max_output = 2048, location = "europe-west4"):

        """Defines Description text for Ereignis
        
        Args:
            text_input (str): Source transcript given to the LLM with fixed prompt.
            ereignis_extracted(str): Single Ereignis that was extracted in previous step.
            temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
            ereignis_anfang_datum(str): Date of Ereignis Start extracted by LLM in format DD.MM.TT
            ereignis_ende_datum(str): Date of Ereignis End extracted by LLM in format DD
            max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 1000.
            location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
                
        Returns:
            response(json): The LLMs response in json format
            
            """
        schema = """{"ereignis_datum": {"ereignis_datum_beschreibung": str}"""
        prompt_text_combined = [f'Wie stehen diese beiden Datums-Angaben mit dem Text im Verhältnis? Was haben diese Datumsangaben mit dem Text zu tun? Bei dem Text handelt es sich um ein Transkript eines Radiobeitrags oder ähnlichen Audios. Datum 1: {ereignis_anfang_datum}, Datum 2: {ereignis_ende_datum}', f'Text: {text_input}', 'Antworte kurz und prägnant!', f'Using this json-Schema: {schema}']
        got_response = False
        while got_response == False:
            try:
                response = self.generate(prompt_text_combined,max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(str(e), '5')
                time.sleep(60)

                if "Content" in str(e):
                    response = 'Keine Zusatz-Info'
                    got_response = True
                #response = self.generate(prompt_text_combined,max_output, temperature, location)
        
        #Decode Json
        json_beschreibung_realisierung = json.loads(response)
        beschreibung_realisierung_datum = json_beschreibung_realisierung['ereignis_datum']['ereignis_datum_beschreibung']
        return(beschreibung_realisierung_datum)
    
    def get_ort_realisierung(self, text_input, temperature = 0, max_output = 2048, location = "europe-west4"):

        """Defines date for Ereignis
        
        Args:
            text_input (str): Source transcript given to the LLM with fixed prompt.
            temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
            max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 1000.
            location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
                
        Returns:
            response(json): The LLMs response in json format
            
            """
        schema = """{"orte": [{"ort": str, ort_kontext: str}, {"ort": str, ort_kontext: str}]}"""
        prompt_text_combined = [f'An welchem Ort oder welchen Orten wurde diese Radioaufnahme gemacht. Gib jeden Ort nur einmal aus. Antworte nur mit einem Ort, wenn dieser klar aus dem Transkript ersichtlich ist. Es muss sich auch eindeutig um den Ort handeln, wo das Audio aufgenommen wurde!', 'Ein Ort, der nur erwähnt wurde im Transkript, aber keinen Bezug zum Aufnahmeort des Audios hat, soll nicht ausgegeben werden!', f'Transkript: {text_input}', 'Gib zusätzlich auch den Kontext des Ortes an, in dem er im Transkript vorkommt in einem kurzen, prägnanten Satz.', 'Wenn Du den Ort aus dem Transkript nicht ermitteln kannst, gib "None" aus!', 'Hinweis: Wenn es sich um eine Studioaufnahme handelt, ist der Ort aus dem Transkript meist nicht zu ermitteln!', f'Using this json-Schema: {schema}']
        got_response = False
        while got_response == False:
            try:
                response = self.generate(prompt_text_combined,max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(str(e), '5')
                time.sleep(60)

                if "Content" in str(e):
                    response = 'Keine Zusatz-Info'
                    got_response = True
                #response = self.generate(prompt_text_combined,max_output, temperature, location)

        #Decode Json
        orte_list = []
        kontext_list = []
        try:
            json_realisierung_ort = json.loads(response)

            print('DEBUG Realisierung Ort roh Response:', json_realisierung_ort)
            realisierung_ort_alle = json_realisierung_ort['orte']
            for r in range(len(realisierung_ort_alle)):
                orte_list.append(realisierung_ort_alle[r]['ort'])
                kontext_list.append(realisierung_ort_alle[r]['ort_kontext'])

        except:
            ()
        
        print('DEBUG Realisierung Ort ready Response Orte:', orte_list)
        print('DEBUG Realisierung Ort ready Response Kontext:', kontext_list)
        return(orte_list, kontext_list)
    
    def get_tag_ereignis(self, text_input, ereignis_extracted, temperature = 0, max_output = 2048, location = "europe-west4"):

        """Defines date for Ereignis
        
        Args:
            text_input (str): Source transcript given to the LLM with fixed prompt.
            ereignis_extracted(str): Single Ereignis that was extracted in previous step.
            temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
            max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 1000.
            location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
                
        Returns:
            response(json): The LLMs response in json format
            
            """
        schema = """{"ereignis": {"ereignis_name": str, "ereignis_tag": int, "ereignis_monat": int, "ereignis_jahr": int}}"""
        prompt_text_combined = [f'An welchem Datum fand folgendes Ereignis laut Text statt oder an welchem Datum hat es angefangen: "{ereignis_extracted}"?', f'Text: {text_input}', 'Antworte nur mit dem Datum in folgendem Format: TT.MM.JJJJ! Wenn Du aus dem Text kein Datum ermitteln kannst, gib "None" aus! Wenn Du für das vorgegebene Format für einen Teil des Datums keinen Wert ermitteln kannst, gib dafür "0" aus. Wenn Du zum Beispiel keinen Tag ermitteln kannst, dafür aber Jahr und Monat, gib das Datum in folgendem Format aus: 00.MM.JJJJ! Wenn Du zum Beispiel kein Jahr ermitteln kannst, dafür aber Monat und Tag, gib das Datum in folgendem Format aus: TT.MM.0000!', f'Using this json-Schema: {schema}']
        got_response = False
        while got_response == False:
            try:
                response = self.generate(prompt_text_combined,max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(str(e), '5')
                time.sleep(60)

                if "Content" in str(e):
                    response = 'Keine Zusatz-Info'
                    got_response = True
                #response = self.generate(prompt_text_combined,max_output, temperature, location)

        #Decode Json
        try:
            json_beschreibung_ereignis = json.loads(response)
            ereignis_tag = json_beschreibung_ereignis['ereignis']['ereignis_tag']
            ereignis_monat = json_beschreibung_ereignis['ereignis']['ereignis_monat']
            ereignis_jahr = json_beschreibung_ereignis['ereignis']['ereignis_jahr']
        except:
            ereignis_tag = 0
            ereignis_monat = 0
            ereignis_jahr = 0
        return(ereignis_tag, ereignis_monat, ereignis_jahr)
    
    def get_tag_ereignis_ende(self, text_input, ereignis_extracted, temperature = 0, max_output = 2048, location = "europe-west4"):

        """Defines date for Ereignis
        
        Args:
            text_input (str): Source transcript given to the LLM with fixed prompt.
            ereignis_extracted(str): Single Ereignis that was extracted in previous step.
            temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
            max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 1000.
            location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
                
        Returns:
            response(json): The LLMs response in json format
            
            """
        schema = """{"ereignis": {"ereignis_name": str, "ereignis_tag": int, "ereignis_monat": int, "ereignis_jahr": int}}"""
        prompt_text_combined = [f'An welchem Datum ist folgendes Ereignis zuende gegangen: "{ereignis_extracted}"?', f'Text: {text_input}', 'Antworte nur mit dem Datum in folgendem Format: TT.MM.JJJJ! Wenn Du aus dem Text kein End-Datum für das genannte Ereignis ermitteln kannst, gib "None" aus! Wenn Du für das vorgegebene Format für einen Teil des Datums keinen Wert ermitteln kannst, gib dafür "0" aus. Wenn Du zum Beispiel keinen Tag ermitteln kannst, dafür aber Jahr und Monat, gib das Datum in folgendem Format aus: 00.MM.JJJJ! Wenn Du zum Beispiel kein Jahr ermitteln kannst, dafür aber Monat und Tag, gib das Datum in folgendem Format aus: TT.MM.0000!', f'Using this json-Schema: {schema}']
        got_response = False
        while got_response == False:
            try:
                response = self.generate(prompt_text_combined,max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(str(e), '5')
                time.sleep(60)

                if "Content" in str(e):
                    response = 'Keine Zusatz-Info'
                    got_response = True
                #response = self.generate(prompt_text_combined,max_output, temperature, location)

        #Decode Json
        try:
            json_beschreibung_ereignis = json.loads(response)
            ereignis_tag_ende = json_beschreibung_ereignis['ereignis']['ereignis_tag']
            ereignis_monat_ende = json_beschreibung_ereignis['ereignis']['ereignis_monat']
            ereignis_jahr_ende = json_beschreibung_ereignis['ereignis']['ereignis_jahr']
        except:
            ereignis_tag_ende = 0
            ereignis_monat_ende = 0
            ereignis_jahr_ende = 0
        return(ereignis_tag_ende, ereignis_monat_ende, ereignis_jahr_ende)
    
    def set_sprache(self, text_input, temperature = 0, max_output = 1000, location = "europe-west4"):
        """LLM-request for getting Sprachen for Transcript
        Args:
            text_input (str): Source transcript given to the LLM with fixed prompt.
            temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
            max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 1000.
            location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
            
        Returns:
            response(json): The LLMs response in json format
        
        """
        schema = """[{"sprache": str}]"""
        prompt_text_combined = f"Welche Sprachen werden in diesem Transkript eines Radiobeitrags gesprochen?: {text_input}, 'Nenne die gesprochenen Sprachen als Liste in jeweils einem Wort: - Sprache, 'Using this json-Schema: {schema}'"
        got_response = False
        while got_response == False:
            try:
                response = self.generate(prompt_text_combined, max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(e, '2')
                time.sleep(60)
          
        return(response)

    def ask_karin(self, transcript, question, temperature = 0, max_output = 1000, location = "europe-west4"):
        """Open LLM request with free text output
        Args:
            transcript (str): Source transcript given to the LLM as part of question.
            question(str): Question that is asked to the LLM about the content of the transcript
            temperature (float): Sets the creativeness of the model. The less, the more similar are two answers to the same prompt. Can be set between 0 and 1, 0 being the least creative. Defaults to 0.
            max_output (int): Maximum number of tokens (~ number of words) of the LLMs response. Defaults to 1000.
            location(str): Location of the Google server the request should be sent to, defaults to europe-west4 for Netherlands
            
        Returns:
            response(str): The LLMs response
        
        """
        prompt_text_combined = f"Antworte auf folgende Frage nur mit Informationen, die Du im Transkript findest: {question}, Transkript: {transcript}"
        got_response = False
        while got_response == False:
            try:
                response = self.generate_free_text(prompt_text_combined, max_output, temperature, location)
                got_response = True
            except Exception as e: 
                print(e, '2')
                time.sleep(60)
          
        return(response)

