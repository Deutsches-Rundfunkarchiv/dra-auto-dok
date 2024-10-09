import pandas as pd
from Levenshtein import ratio, distance
class compare_with_ndb_vocabulary_persons():
    """ Loads vocabulary from source list of NDB-vocabulary, sorts it and compares it with Entities given. Corrects entities that are written wrong."""
    def __init__(self, list_reference, lists_reference_sorted = False):
        """Inputs:
            list_reference(excel-file-path): Path to Excel File that contains vocabulary in given format
            lists_reference_sorted(excel-file-path): Path to sorted excel list, that is ready to be used for comparison
            """
        self.list_reference = list_reference
        self.list_reference_sorted = lists_reference_sorted
        
        if self.list_reference_sorted == False or self.list_reference_sorted == None:
            self.proper_list = self.make_proper_lists()
        else:
            self.proper_list = self.load_proper_list()
        
    def read_source_list(self):
        """Reads Source List

        Returns:
            source(pandas object): Pandas table object of source list"""
        source = pd.read_excel(self.list_reference)

        return(source)

    def read_source_list_detail(self):
        """Splits source list to single lists. Returns these lists
        
        Returns:
            person_id (str): NDB-Person ID
            nachname_person (str): Family name of person
            vorname_person (str): First name of person
            namenszusatz (str): Name Additions such as "von"
            ist_hauptname_person (bool): States if this name is the main name for the person
            name_ids_person (str): Name Ids for this specific person
        """

        source_file_ndb = self.read_source_list()
        person_id = source_file_ndb['Person_ID']
        nachname_person = source_file_ndb['Nachname']
        vorname_person = source_file_ndb['Vorname']
        namenszusatz_person = source_file_ndb['Namenszusatz']
        ist_hauptname_person = source_file_ndb['Ist_Hauptname']
        name_ids_person = source_file_ndb['Name_IDs']
        
        return(person_id, nachname_person, vorname_person, namenszusatz_person, ist_hauptname_person, name_ids_person)
    
    def compare_direct_with_proper_list(self, input_to_compare):
        """Compares sentences directly with proper list without Levensthein - only exact matches count
        
        Args:
            input_to_compare(str): Single Name input that should be compared to whole input list

        Returns:
            nachname(str): Nachname der Person
            vorname(str): Vorname der Person
            person_id(str): NDB-ID der Person, wenn gefunden durch Abgleich.
        """
        
        ref_lists_all = self.proper_list
        name_list_ref = ref_lists_all[0]
        #print(name_list_ref)
        found = False
        final_index = None
        while found == False:
            for i in range(len(name_list_ref)):
                if input_to_compare in name_list_ref[i]:
                    final_index = i
                    found = True
                    break
            break

        if found == True:
            person_id = ref_lists_all[1][final_index]
            list_uebersicht_position = list(ref_lists_all[2]).index(person_id)
            vorname = ref_lists_all[3][list_uebersicht_position]
            nachname = ref_lists_all[4][list_uebersicht_position]
        else:
            split_input = input_to_compare.split(' ')
            nachname = split_input[len(split_input)-1]
            vorname = input_to_compare.replace(nachname, '')
            person_id = None

        return(nachname, vorname, person_id)        

    def make_proper_lists(self):
        """Splits different versions of names into single name entries and combines them with other useful data from source. Returns data lists ready for comparison with entities
        
        Returns:
            sentences (list): Combination of all names of a person as one string for complete comparison of whole term.
            person_id_found (list): 
            person_id (list): Person ID from norm Database
            vornamen_person (list): First name of person
            nachnamen_person (list): Last name of Person
        """
        sentences = []
        person_id_found = []
        is_hauptname_sentence = []
        name_id_sentence = []
       
        source_list = self.read_source_list_detail()
        vornamen_person = source_list[2]
        nachnamen_person = source_list[1]
        person_id = source_list[0]
        ist_hauptname_person = source_list[4]
        name_ids_person = source_list[5]
        print('Make proper List')
        for n in range(len(vornamen_person)):
            print(vornamen_person[n], nachnamen_person[n])
            vorname_person_single = vornamen_person[n].replace('[','')
            vorname_person_single = vorname_person_single.replace(']','')
            vorname_person_single = vorname_person_single.replace("'","")
            
            vorname_list = vorname_person_single.split(',')
            nachname_person_single = nachnamen_person[n].replace('[','')
            nachname_person_single = nachname_person_single.replace(']','')
            nachname_person_single = nachname_person_single.replace("'","")
            
            nachname_list = nachname_person_single.split(',')
            for v in range(len(vorname_list)):
                if v < len(nachname_list) and nachname_list[v] != 'None' and nachname_list[v] != None and nachname_list[v] != ' None' and nachname_list[v] != 'None ':
                    nachname_new = nachname_list[v]
                    if len(nachname_new) >0 and nachname_new[0] == ' ':
                        #print('found nach')
                        nachname_new = nachname_new[1:]
                        sentences.append(nachname_new)
                        person_id_found.append(person_id[n])
                        #is_hauptname_sentence.append()
                    
                    if vorname_list[v] != None:
                        vorname_new = vorname_list[v]
                        if len(vorname_new)>0 and vorname_new[0] == ' ':
                            vorname_new = vorname_new[1:]
                            sentences.append(f'{vorname_new} {nachname_new}')
                            person_id_found.append(person_id[n])
                            
                        if len(vorname_new)>0 and f'{vorname_new} {nachname_new}' not in sentences:
                            sentences.append(f'{vorname_new} {nachname_new}')
                            person_id_found.append(person_id[n])

        print('Done with making proper List')               
        return(sentences, person_id_found, person_id, vornamen_person, nachnamen_person)
    
    def load_proper_list(self):
        """Since making a proper list from original list always takes half an hour, this is a shortcut to loading a list from disk from excel file
        
        Returns:
            sentences (list): Combination of all names of a person as one string for complete comparison of whole term.
            person_id_found (list): 
            person_id (list): Person ID from norm Database
            vornamen_person (list): First name of person
            nachnamen_person (list): Last name of Person    
        
        """
        source_file = self.list_reference_sorted

        for i in range(len(source_file)):
        #Lese die Excel-Quelldatei mit Pandas aus und definiere die beiden Spalten als Quell-Listen und baue daraus einen Dataframe, um damit weiter zu arbeiten.
            df = pd.read_excel(source_file[i])
            try:
                sentences = df['sentences']
                person_id_found = df['person_id_found']
            except:
                person_id = df['person_id']
                vornamen_person = df['vornamen_person']
                nachnamen_person = df['nachnamen_person']
        return(sentences, person_id_found, person_id, vornamen_person, nachnamen_person)
    
    def find_hauptname_from_person_id(self, person_id_search):
        """Find the Hauptname of a person based on the person id"""
        source_list = self.read_source_list_detail()
        vornamen_person = source_list[2]
        nachnamen_person = source_list[1]
        person_id = source_list[0]
        ist_hauptname_person = source_list[4]
        name_ids_person = source_list[5]
        
        index_name = list(person_id).index(person_id_search)
        #Weil Listen in Excel-Listen nicht als Listen erkannt werden, müssen wir sie per Split wieder zu Listen machen.
        ist_hauptname_status_list = ist_hauptname_person[index_name].replace("[",'')
        ist_hauptname_status_list = ist_hauptname_status_list.replace("]",'')
        ist_hauptname_status_list = ist_hauptname_status_list.split(", ")

        #Selbes mit der Liste eines Namenseintrags in der NDB-Excel-Spiegelung
        vornamen_single_list =  vornamen_person[index_name].replace("['",'')
        vornamen_single_list = vornamen_single_list.replace("']",'')
        vornamen_single_list = vornamen_single_list.split("', ")

        nachnamen_single_list =  nachnamen_person[index_name].replace("['",'')
        nachnamen_single_list = nachnamen_single_list.replace("']",'')
        nachnamen_single_list = nachnamen_single_list.split("', ")

        name_id_haupt_single_list =  name_ids_person[index_name].replace("['",'')
        name_id_haupt_single_list = name_id_haupt_single_list.replace("']",'')
        name_id_haupt_single_list = name_id_haupt_single_list.split("', ")
        hauptname_index = 0
        
        for i in range(len(ist_hauptname_status_list)):
            if 'True' in ist_hauptname_status_list[i] or ist_hauptname_status_list[i] == True:
                
                hauptname_index = i
                
                break
        
        vorname_haupt = vornamen_single_list[hauptname_index]
        vorname_haupt = vorname_haupt.replace("'", "")
        print(vorname_haupt)
        nachname_haupt = nachnamen_single_list[hauptname_index]
        nachname_haupt = nachname_haupt.replace("'", "")
        print(nachname_haupt)
        name_id_haupt = name_id_haupt_single_list[hauptname_index]
        name_id_haupt = name_id_haupt.replace("'", "")
        print(name_id_haupt)

        return(vorname_haupt, nachname_haupt, name_id_haupt)

    def get_lowest_distance_ratio(self, input, reference):
        """Levenstein-Distance Util for calculating Distance ratio for a list of possible best matches and finding best match
        Args:
            input (list): list of words that are possible best matches for a reference word
            reference (str): Word that is checked for best similar word.

        Returns:
            final_ref(str): Best matching word
            lowest_distance (int): Distance_ratio of best matching word.
        """
        lowest_distance = 0
        referenced_id = 0
        for i in range(len(reference)):
            distance_single = ratio(input,reference[i])
            if distance_single >lowest_distance:
                lowest_distance = distance_single
                referenced_id = i
        final_ref = reference[referenced_id]

        return (final_ref, lowest_distance)
    
    def get_lowest_distance_absolute (self, input, reference):
        """levenstein-Distance Util for calculation absolute distance for a list of possible best matches and finding best match
        
        Args:
            input (list): list of words that are possible best matches for a reference word
            reference (str): Word that is checked for best similar word.

        Returns:
            final_ref(str): Best matching word
            lowest_distance (int): Distance_ratio of best matching word.
        """
        lowest_distance = 1000
        referenced_id = 0
        for i in range(len(reference)):
            distance_single = distance(input,reference[i])
            if distance_single <lowest_distance:
                lowest_distance = distance_single
                referenced_id = i
        final_ref = reference[referenced_id]
        return (final_ref, lowest_distance)
    
    def compare_and_replace_vocab(self, entitaeten_wort_list, entitaeten_arten_list):
        """Compares Vocabulary with reference database and makes a replacement list for words that are supposed to be written wrong
        
        Args:
            entitaeten_wort_list(list): List of Entities found from text
            entitaeten_arten_list(list): List of kinds of these entities (Persons, Locations etc.)

        Returns:
            list_war (list): List of words that should be replaced
            list_wird (list): List of replacements for words from list_war.
        
        """
        input_vocab = self.proper_list
        sentences = input_vocab[0]
        person_id_found = input_vocab[1]
        person_id = input_vocab[2]
        vorname_person = input_vocab[3]
        nachname_person = input_vocab[4]
        person_id_matched = []
        nachname_matched = []
        vorname_matched = []
        nachname_ersetzen_zusatz = []
        person_id_verified_names = []
        list_war = []
        list_wird = []
        
        for e in range(len(entitaeten_wort_list)):
            list_zwischen_war = []
            list_zwischen_wird = []

            found_replacement = False
            for f in range(len(entitaeten_arten_list[e])):
                
                if entitaeten_arten_list[e][f] == 'PER':
                    
                    similar_word1 = self.get_lowest_distance_ratio (entitaeten_wort_list[e][f], sentences)
                    similar_word2 = self.get_lowest_distance_absolute (entitaeten_wort_list[e][f], sentences)
                    if similar_word1[1] > 0.6 and similar_word2[1]<5 and similar_word1[0] == similar_word2[0]:
                        #list_zwischen_war.append(entitaeten_wort_list_2[e][f])
                        #list_zwischen_wird.append(similar_word1[0])
                        print(entitaeten_wort_list[e][f])
                        print(similar_word1[0])
                        found_replacement = True
                        print(person_id_found)
                        print(sentences)
                        person_id_gefunden = person_id_found[list(sentences).index(similar_word1[0])]
                        #print(person_id_found)
                        person_id_matched.append(person_id_found[list(sentences).index(similar_word1[0])])
                        

                        for i in range(len(person_id)):
                            if person_id[i] == person_id_gefunden:
                                index_ndb = i
                                print(i)
                                
                        nachname_matched.append(nachname_person[index_ndb])
                        nachname_person_single = nachname_person[index_ndb]
                        print(nachname_person_single)
                        vorname_matched.append(vorname_person[index_ndb])
                        vorname_person_single = vorname_person[index_ndb]

                        #Check ob Vorname und Nachname im Textextrakt enthalten ist, dann nehmen wir die Person als korrekt an.  
                        verified_name = False  
                        vorname_enthalten = False
                        nachname_enthalten = False
                        nachname_verifiziert = False
                        nachname_person_single = nachname_person_single.split(',')
                        for o in range(len(nachname_person_single)):
                            nachname_person_single[o] = nachname_person_single[o].replace(" '","")
                            nachname_person_single[o] = nachname_person_single[o].replace("'","")
                            nachname_person_single[o] = nachname_person_single[o].replace("[","")
                            nachname_person_single[o] = nachname_person_single[o].replace("]","")

                        vorname_person_single = vorname_person_single.split(',')
                        for g in range(len(vorname_person_single)):
                            vorname_person_single[g] = vorname_person_single[g].replace(" '","")
                            vorname_person_single[g] = vorname_person_single[g].replace("'","")
                            vorname_person_single[g] = vorname_person_single[g].replace("[","")
                            vorname_person_single[g] = vorname_person_single[g].replace("]","")

                        for v in range(len(nachname_person_single)):
                            print(nachname_person_single[v])
                            if nachname_person_single[v] in similar_word1[0]:
                                nachname_index = similar_word1[0].find(nachname_person_single[v])
                                nachname_enthalten = True
                                nachname_verifiziert = nachname_person_single[v]
                                print(nachname_verifiziert)
                        for n in range(len(vorname_person_single)):
                            if vorname_person_single[n] in similar_word1[0]:
                                vorname_index = similar_word1[0].find(vorname_person_single[n])
                                if vorname_index != nachname_index:
                                    vorname_enthalten = True
                                    vorname_verifiziert = vorname_person_single[v]
                                    print(vorname_verifiziert)

                        if vorname_enthalten == True and nachname_enthalten == True:
                            verified_name = True
                            nachname_ersetzen_zusatz.append(nachname_verifiziert)
                            print('Nachname zum Ersetzen:', nachname_verifiziert)
                            person_id_verified_names.append(person_id_gefunden)
                            print(person_id_gefunden)
                            list_zwischen_war.append(entitaeten_wort_list[e][f])
                            list_zwischen_wird.append(similar_word1[0])
                        
                        print('Name verifiziert = ', verified_name)



                        print('_____________')
            list_war.append(list_zwischen_war)
            list_wird.append(list_zwischen_wird)

            #Make a unique list from the Nachnamen to replace
        unique_nachnamen_ersetzen = []
        person_id_verified_names_unique = []
        for n in range(len(nachname_ersetzen_zusatz)):
            if nachname_ersetzen_zusatz[n] not in unique_nachnamen_ersetzen:
                unique_nachnamen_ersetzen.append(nachname_ersetzen_zusatz[n])
                person_id_verified_names_unique.append(person_id_verified_names[n])

        #Für die verifizierten Nachnamen ebenfalls die Ähnlichkeiten zu vorkommenden Entitäten laut Spacy prüfen und bei gefundenen Matches an die war-Ist Listen anhängen
        if len(unique_nachnamen_ersetzen)>0:
            for e in range(len(entitaeten_wort_list)):
                #list_zwischen_war = []
                #list_zwischen_wird = []

                found_replacement = False
                for f in range(len(entitaeten_arten_list[e])):
                    
                    if entitaeten_arten_list[e][f] == 'PER':
                        
                        similar_word1 = self.get_lowest_distance_ratio (entitaeten_wort_list[e][f], unique_nachnamen_ersetzen)
                        similar_word2 = self.get_lowest_distance_absolute (entitaeten_wort_list[e][f], unique_nachnamen_ersetzen)
                        if similar_word1[1] > 0.8 and similar_word2[1]<4 and similar_word1[0] == similar_word2[0]:
                            #list_zwischen_war.append(entitaeten_wort_list_2[e][f])
                            #list_zwischen_wird.append(similar_word1[0])
                            print(entitaeten_wort_list[e][f])
                            print(similar_word1[0])
                            found_replacement = True
                            list_war[e].append(entitaeten_wort_list[e][f])
                            list_wird[e].append(similar_word1[0])
                            print('_________________')
        
        return(list_war, list_wird)
    
    def make_new_text_with_replacements (self, text_input, entitaeten_wort_list, entitaeten_arten_list):
        """Corrects text input by finding replacements for certain words from NDB
        
        Args:
            text_input(list): List of text input from whisper
            entitaeten_wort_list(list): List of words that spacy identifies as entities. Ist passed on to other functions above
            entitaeten_arten_list(list): List of entity sorts that spacy found for entities above.

        Returns:
            text_input(list): Original text input for control purposes as list
            text_new_list(list): New text with replacements implemented.
        
        """
        text_new_list = []
        replacements_pre_processing = self.compare_and_replace_vocab(entitaeten_wort_list, entitaeten_arten_list)
        list_war = replacements_pre_processing[0]
        list_wird = replacements_pre_processing[1]
        for i in range(len(text_input)):
            text_output = text_input[i]
            
            for j in range(len(list_war)):
                for k in range(len(list_war[j])):
                    if list_war[j][k] in text_input[i]:
                        text_output = text_output.replace(list_war[j][k], list_wird[j][k])
                        text_output = text_output.replace(' s ', "'s ")
                        text_output = text_output.replace(' ,',',')
                        text_output = text_output.replace('  ',' ')
                                 
            text_new_list.append(text_output)

        return(text_input, text_new_list)
    
class compare_with_ndb_vocabulary_orte(compare_with_ndb_vocabulary_persons):

    def make_proper_lists(self):
        """Makes one whole list with all possible names from Orte_Liste and their name and their IDs and the main entity they belong to
        
        Returns:
            namen_main_list (list): List of strings, that contains all possible names that belong to one single geographical entity.
            namen_main_vok_ids (list): List of vocabulary IDs that belong to the single names from the namen_main_list.
            namen_main_name_ids (list): ID of the main name of the geographical entity.
            hauptname_all  (list): The main name of the geographical entity.
            hauptname_name_id_all (list): The id of the main name of the geographical entity.
        """

        df = pd.read_excel(self.list_reference)
        hauptnamen = df['Hauptname']
        hauptnamen_ids = df['ID_Untergeordnet']
        sonstige_namen = df['Sonstige_Namen']
        hauptname_name_ids = df['Hauptname_name_Ids']
        weitere_namen_name_ids = df['weitere_Namen_Name_IDs']

        namen_main_list = list(hauptnamen)
        namen_main_vok_ids = list(hauptnamen_ids)
        namen_main_name_ids = list(hauptname_name_ids)
        hauptname_all = list(hauptnamen)
        hauptname_name_id_all = list(namen_main_name_ids)

        for i in range(len(sonstige_namen)):
            if sonstige_namen[i] != '[]':
                sonstige_namen_all_single = sonstige_namen[i].split("', '")
                sonstige_namen_ids_single = weitere_namen_name_ids[i].split("', '")
                for j in range(len(sonstige_namen_all_single)):
                    sonstige_namen_all_single[j] = sonstige_namen_all_single[j].replace("['",'')
                    sonstige_namen_all_single[j] = sonstige_namen_all_single[j].replace("']",'')
                    sonstige_namen_all_single[j] = sonstige_namen_all_single[j].replace("']",'')
                    sonstige_namen_all_single[j] = sonstige_namen_all_single[j].replace("'",'')
                    sonstige_namen_ids_single[j] = sonstige_namen_ids_single[j].replace("['",'')
                    sonstige_namen_ids_single[j] = sonstige_namen_ids_single[j].replace("']",'')
                    sonstige_namen_ids_single[j] = sonstige_namen_ids_single[j].replace("']",'')
                    sonstige_namen_ids_single[j] = sonstige_namen_ids_single[j].replace("'",'')
                    hauptname_single = hauptnamen[i]
                    hauptname_id_single = hauptname_name_ids[i]
                    namen_main_list.append(sonstige_namen_all_single[j])
                    namen_main_vok_ids.append(hauptname_id_single)
                    namen_main_name_ids.append(sonstige_namen_ids_single[j])
                    hauptname_all.append(hauptname_single)
                    hauptname_name_id_all.append(hauptname_id_single)

        #Inhalte sollten als Liste abgelegt sein, Spalten für das Excel müssen exakt gleiche Länge (=Anzahl an Items) haben
 
        df_zu_schreiben = pd.DataFrame({
            'Name_to_Match': namen_main_list, 
            'Vok_ID': namen_main_vok_ids, 
            'Name_ID': namen_main_name_ids, 
            'Hauptname_Uebergreifend': hauptname_all,
            'Hauptname_Name_ID_uebergreifend': hauptname_name_id_all
            
            }) 
        df_zu_schreiben.to_excel(f'Excel_Lists_Entities\\Backup_Proper_List_themaOrt.xlsx')
        #print (df_zu_schreiben)

        return(namen_main_list, namen_main_vok_ids, namen_main_name_ids, hauptname_all, hauptname_name_id_all)
    
    
    def compare_direct_with_proper_list(self, input_to_compare):
        """Compares sentences directly with proper list without Levensthein - only exact matches count
        
        Args:
            input_to_compare(str): Single Name input that should be compared to whole input list

        Returns:
            name_ort(str): Name des Ortes nach Abgleich
            vok_id_ort(str): Vokabel-ID des Ortes
            name_id_ort(str): Name_ID des Ortes
        """
        #self.get_lowest_distance_absolute (self, input, reference)
        print(input_to_compare)
        ref_lists_all = self.proper_list
        namen_main_list = list(ref_lists_all[0])
        namen_main_vok_ids = list(ref_lists_all[1])
        namen_main_name_ids = list(ref_lists_all[2])
        
        for n in range(len(namen_main_list)):
            namen_main_list[n] = str(namen_main_list[n])
        levensthein_dist = 1000
        chosen_name_id = None
        lv_dist = self.get_lowest_distance_absolute (input_to_compare, namen_main_list)
        print(lv_dist[1])
        if lv_dist[1] < levensthein_dist:
            levensthein_dist = lv_dist[1]
            chosen_name_id = namen_main_list.index(lv_dist[0])
        
        if int(levensthein_dist) <4:
            chosen_name_final = chosen_name_id
            print(chosen_name_id)
        else:
            chosen_name_final = None

        if chosen_name_final == None:
            namen_return = None
            vok_id_return = None
            name_id_return = None
        else:
            namen_return = namen_main_list[chosen_name_final]
            vok_id_return = namen_main_vok_ids[chosen_name_final]
            name_id_return = namen_main_name_ids[chosen_name_final]
        print(namen_return, vok_id_return, name_id_return)
        return(namen_return, vok_id_return, name_id_return)

    def load_proper_list(self):
        """Since making a proper list from original list always takes half an hour, this is a shortcut to loading a list from disk from excel file
        
        Returns:
            namen_main_list (list): List of strings, that contains all possible names that belong to one single geographical entity.
            namen_main_vok_ids (list): List of vocabulary IDs that belong to the single names from the namen_main_list.
            namen_main_name_ids (list): ID of the main name of the geographical entity.
            hauptname_all  (list): The main name of the geographical entity.
            hauptname_name_id_all (list): The id of the main name of the geographical entity.
        """
        source_file = self.list_reference_sorted

        
        #Lese die Excel-Quelldatei mit Pandas aus und definiere die beiden Spalten als Quell-Listen und baue daraus einen Dataframe, um damit weiter zu arbeiten.
        df = pd.read_excel(source_file)
        namen_main_list = df['Name_to_Match'] 
        namen_main_vok_ids = df['Vok_ID'] 
        namen_main_name_ids = df['Name_ID'] 
        hauptname_all = df['Hauptname_Uebergreifend']
        hauptname_name_id_all = df['Hauptname_Name_ID_uebergreifend']
        
        return(namen_main_list, namen_main_vok_ids, namen_main_name_ids, hauptname_all, hauptname_name_id_all)
