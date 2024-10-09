import requests
from config import path_ndb_proxy_certificate
from thefuzz import fuzz
from thefuzz import process

class norm_db_entity_linking():
     
    def __init__(self):
        """
        Args:
            certificate (str): Path to SSL-Certificate on local disk
        """
        self.certificate = path_ndb_proxy_certificate
        self.session = requests.session()
        self.session.trust_env = False
          

    def make_name_suggestions_from_LLM_suggestions (self, name_to_find, ki_text):
        """Makes suggestions for normDB Person entries
        Args:
            name_to_find(str): Name of Person suggested by LLM
            ki_text(str): Description text we get for person from LLM

        Returns:
            person_id_list (list): Person-IDs of suggests from normDB 
            name_id_list (list): Name-IDs of suggests from normDB 
            name_list (list): Names of suggests from normDB 
            vorname_list (list): First Names of suggests from normDB 
            lebenstage_list (list): Life Dates of suggests from normDB 
            link_ndb_list (list): Links to single ndb entries of suggests
            normierungsstatus_list (list): Normierungsstatus of  suggests from NDB
            steckbrief_list (list): Short abstract about persons for suggests
        
        
        """
        abfrage = name_to_find
        steckbrief_list = []
        person_id_list = []
        name_id_list = []
        name_list = []
        vorname_list = []
        lebenstage_list = []
        link_ndb_list = []
        normierungsstatus_list = []
                   
        url = f'https://normdb.ivz.cn.ard.de/normdbrs_person/V2/service/Personen/VorschlaegeErweitert?suchtext={abfrage}&anzahl=1000&schnellsuchModus=true'
        response = self.session.get(url, verify=self.certificate)
        json = response.json() 

        #Sortierungsalgorithmus
        while len(person_id_list) <20: #max Länge Liste = 20 Einträge für Vorschläge, danach aufhören zu suchen
            #Add N.N. Eintrag at the top of the List "manually" if N.N. applies
            if abfrage == "N.N." or abfrage == "N. N." or abfrage == "NN" or "N." in abfrage:
                steckbrief_list.append(None)
                person_id_list.append("person-1224646")
                name_id_list.append("personName-2886969")
                name_list.append('N. N.')
                vorname_list.append(None)
                lebenstage_list.append(None)
                link_ndb_list.append("https://normdb.ivz.cn.ard.de/person/1224646")
                normierungsstatus_list.append("PSGP")

            for i in range(len(json)):
                if json[i]['istHauptname'] == True and json[i]['normierungsstatus']['kurzName'] == 'IND': #Zunächst nach Hauptnamen und höchstem Normierungsstatus suchen
                    found_funktion = False
                    berufe_funktionen = json[i]['berufeFunktionen']
                    for f in range(len(berufe_funktionen)):
                        if found_funktion == False and berufe_funktionen[f] != None and berufe_funktionen[f].lower() in ki_text.lower(): #Erste Einträge = Höchste Stati + Beruf kommt in KI-Text vor
                            found_funktion == True
                            steckbrief_list.append(json[i]['steckbrief'])
                            person_id_list.append(json[i]['personId'])
                            name_id_list.append(json[i]['nameId'])
                            name_list.append(json[i]['name'])
                            vorname_list.append(json[i]['vorname'])
                            if json[i]['beginnDatum'] != None and int(json[i]['beginnDatum']['tag']) != 0 and json[i]['endeDatum'] != None and int(json[i]['endeDatum']['tag']) != 0:
                                lebenstage_list.append(f'{json[i]['beginnDatum']['tag']}.{json[i]['beginnDatum']['monat']}.{json[i]['beginnDatum']['jahr']} - {json[i]['endeDatum']['tag']}.{json[i]['endeDatum']['monat']}.{json[i]['endeDatum']['jahr']}')
                            elif json[i]['beginnDatum'] != None and int(json[i]['beginnDatum']['tag']) != 0:
                                lebenstage_list.append(f'{json[i]['beginnDatum']['tag']}.{json[i]['beginnDatum']['monat']}.{json[i]['beginnDatum']['jahr']} - ?')
                            elif json[i]['endeDatum'] != None and int(json[i]['endeDatum']['tag']) != 0:
                                lebenstage_list.append(f'? - {json[i]['endeDatum']['tag']}.{json[i]['endeDatum']['monat']}.{json[i]['endeDatum']['jahr']} - ?')
                            else:
                                lebenstage_list.append(None)
                            
                            link_ndb_list.append(json[i]['permalink'])
                            normierungsstatus_list.append(json[i]['normierungsstatus']['kurzName'])
                if len(person_id_list) >= 20:
                    break

            for i in range(len(json)):
                if json[i]['istHauptname'] == False and json[i]['normierungsstatus']['kurzName'] == 'IND': #Dann nach Nebennamen und höchstem Normierungsstatus suchen
                    found_funktion = False
                    berufe_funktionen = json[i]['berufeFunktionen']
                    for f in range(len(berufe_funktionen)):
                        if found_funktion == False and berufe_funktionen[f].lower() in ki_text.lower(): #Erste Einträge = Beruf kommt in KI-Text vor
                            found_funktion == True
                            steckbrief_list.append(json[i]['steckbrief'])
                            person_id_list.append(json[i]['personId'])
                            name_id_list.append(json[i]['nameId'])
                            name_list.append(json[i]['name'])
                            vorname_list.append(json[i]['vorname'])
                            if json[i]['beginnDatum'] != None and int(json[i]['beginnDatum']['tag']) != 0 and json[i]['endeDatum'] != None and int(json[i]['endeDatum']['tag']) != 0:
                                lebenstage_list.append(f'{json[i]['beginnDatum']['tag']}.{json[i]['beginnDatum']['monat']}.{json[i]['beginnDatum']['jahr']} - {json[i]['endeDatum']['tag']}.{json[i]['endeDatum']['monat']}.{json[i]['endeDatum']['jahr']}')
                            elif json[i]['beginnDatum'] != None and int(json[i]['beginnDatum']['tag']) != 0:
                                lebenstage_list.append(f'{json[i]['beginnDatum']['tag']}.{json[i]['beginnDatum']['monat']}.{json[i]['beginnDatum']['jahr']} - ?')
                            elif json[i]['endeDatum'] != None and int(json[i]['endeDatum']['tag']) != 0:
                                lebenstage_list.append(f'? - {json[i]['endeDatum']['tag']}.{json[i]['endeDatum']['monat']}.{json[i]['endeDatum']['jahr']} - ?')
                            else:
                                lebenstage_list.append(None)
                            
                            link_ndb_list.append(json[i]['permalink'])
                            normierungsstatus_list.append(json[i]['normierungsstatus']['kurzName'])

                if len(person_id_list) >= 20:
                    break

            for i in range(len(json)):
                if json[i]['istHauptname'] == True and json[i]['normierungsstatus']['kurzName'] == 'PSGP': #Dann nach Hauptnamen und zweithöchstem Normierungsstatus suchen
                    found_funktion = False
                    berufe_funktionen = json[i]['berufeFunktionen']
                    for f in range(len(berufe_funktionen)):
                        if found_funktion == False and berufe_funktionen[f].lower() in ki_text.lower(): #Erste Einträge = Beruf kommt in KI-Text vor
                            found_funktion == True
                            steckbrief_list.append(json[i]['steckbrief'])
                            person_id_list.append(json[i]['personId'])
                            name_id_list.append(json[i]['nameId'])
                            name_list.append(json[i]['name'])
                            vorname_list.append(json[i]['vorname'])
                            if json[i]['beginnDatum'] != None and int(json[i]['beginnDatum']['tag']) != 0 and json[i]['endeDatum'] != None and int(json[i]['endeDatum']['tag']) != 0:
                                lebenstage_list.append(f'{json[i]['beginnDatum']['tag']}.{json[i]['beginnDatum']['monat']}.{json[i]['beginnDatum']['jahr']} - {json[i]['endeDatum']['tag']}.{json[i]['endeDatum']['monat']}.{json[i]['endeDatum']['jahr']}')
                            elif json[i]['beginnDatum'] != None and int(json[i]['beginnDatum']['tag']) != 0:
                                lebenstage_list.append(f'{json[i]['beginnDatum']['tag']}.{json[i]['beginnDatum']['monat']}.{json[i]['beginnDatum']['jahr']} - ?')
                            elif json[i]['endeDatum'] != None and int(json[i]['endeDatum']['tag']) != 0:
                                lebenstage_list.append(f'? - {json[i]['endeDatum']['tag']}.{json[i]['endeDatum']['monat']}.{json[i]['endeDatum']['jahr']} - ?')
                            else:
                                lebenstage_list.append(None)
                            
                            link_ndb_list.append(json[i]['permalink'])
                            normierungsstatus_list.append(json[i]['normierungsstatus']['kurzName'])
                if len(person_id_list) >= 20:
                    break

            for i in range(len(json)):
                if json[i]['istHauptname'] == False and json[i]['normierungsstatus']['kurzName'] == 'PSGP': #Dann nach Nebennamen und zweithöchstem Normierungsstatus suchen
                    found_funktion = False
                    berufe_funktionen = json[i]['berufeFunktionen']
                    for f in range(len(berufe_funktionen)):
                        if found_funktion == False and berufe_funktionen[f].lower() in ki_text.lower(): #Erste Einträge = Beruf kommt in KI-Text vor
                            found_funktion == True
                            steckbrief_list.append(json[i]['steckbrief'])
                            person_id_list.append(json[i]['personId'])
                            name_id_list.append(json[i]['nameId'])
                            name_list.append(json[i]['name'])
                            vorname_list.append(json[i]['vorname'])
                            if json[i]['beginnDatum'] != None and int(json[i]['beginnDatum']['tag']) != 0 and json[i]['endeDatum'] != None and int(json[i]['endeDatum']['tag']) != 0:
                                lebenstage_list.append(f'{json[i]['beginnDatum']['tag']}.{json[i]['beginnDatum']['monat']}.{json[i]['beginnDatum']['jahr']} - {json[i]['endeDatum']['tag']}.{json[i]['endeDatum']['monat']}.{json[i]['endeDatum']['jahr']}')
                            elif json[i]['beginnDatum'] != None and int(json[i]['beginnDatum']['tag']) != 0:
                                lebenstage_list.append(f'{json[i]['beginnDatum']['tag']}.{json[i]['beginnDatum']['monat']}.{json[i]['beginnDatum']['jahr']} - ?')
                            elif json[i]['endeDatum'] != None and int(json[i]['endeDatum']['tag']) != 0:
                                lebenstage_list.append(f'? - {json[i]['endeDatum']['tag']}.{json[i]['endeDatum']['monat']}.{json[i]['endeDatum']['jahr']} - ?')
                            else:
                                lebenstage_list.append(None)
                            
                            link_ndb_list.append(json[i]['permalink'])
                            normierungsstatus_list.append(json[i]['normierungsstatus']['kurzName'])

                if len(person_id_list) >= 20:
                    break

            for i in range(len(json)):
                if json[i]['istHauptname'] == True and json[i]['normierungsstatus']['kurzName'] == 'NMGP': #Dann nach Hauptnamen und dritthöchstem Normierungsstatus suchen
                    found_funktion = False
                    berufe_funktionen = json[i]['berufeFunktionen']
                    for f in range(len(berufe_funktionen)):
                        if found_funktion == False and berufe_funktionen[f].lower() in ki_text.lower(): #Erste Einträge = Beruf kommt in KI-Text vor
                            found_funktion == True
                            steckbrief_list.append(json[i]['steckbrief'])
                            person_id_list.append(json[i]['personId'])
                            name_id_list.append(json[i]['nameId'])
                            name_list.append(json[i]['name'])
                            vorname_list.append(json[i]['vorname'])
                            if json[i]['beginnDatum'] != None and int(json[i]['beginnDatum']['tag']) != 0 and json[i]['endeDatum'] != None and int(json[i]['endeDatum']['tag']) != 0:
                                lebenstage_list.append(f'{json[i]['beginnDatum']['tag']}.{json[i]['beginnDatum']['monat']}.{json[i]['beginnDatum']['jahr']} - {json[i]['endeDatum']['tag']}.{json[i]['endeDatum']['monat']}.{json[i]['endeDatum']['jahr']}')
                            elif json[i]['beginnDatum'] != None and int(json[i]['beginnDatum']['tag']) != 0:
                                lebenstage_list.append(f'{json[i]['beginnDatum']['tag']}.{json[i]['beginnDatum']['monat']}.{json[i]['beginnDatum']['jahr']} - ?')
                            elif json[i]['endeDatum'] != None and int(json[i]['endeDatum']['tag']) != 0:
                                lebenstage_list.append(f'? - {json[i]['endeDatum']['tag']}.{json[i]['endeDatum']['monat']}.{json[i]['endeDatum']['jahr']} - ?')
                            else:
                                lebenstage_list.append(None)
                            
                            link_ndb_list.append(json[i]['permalink'])
                            normierungsstatus_list.append(json[i]['normierungsstatus']['kurzName'])

                if len(person_id_list) >= 20:
                    break

            for i in range(len(json)):
                if json[i]['istHauptname'] == False and json[i]['normierungsstatus']['kurzName'] == 'NMGP': #Dann nach Nebennamen und dritthöchstem Normierungsstatus suchen
                    found_funktion = False
                    berufe_funktionen = json[i]['berufeFunktionen']
                    for f in range(len(berufe_funktionen)):
                        if found_funktion == False and berufe_funktionen[f].lower() in ki_text.lower(): #Erste Einträge = Beruf kommt in KI-Text vor
                            found_funktion == True
                            steckbrief_list.append(json[i]['steckbrief'])
                            person_id_list.append(json[i]['personId'])
                            name_id_list.append(json[i]['nameId'])
                            name_list.append(json[i]['name'])
                            vorname_list.append(json[i]['vorname'])
                            if json[i]['beginnDatum'] != None and int(json[i]['beginnDatum']['tag']) != 0 and json[i]['endeDatum'] != None and int(json[i]['endeDatum']['tag']) != 0:
                                lebenstage_list.append(f'{json[i]['beginnDatum']['tag']}.{json[i]['beginnDatum']['monat']}.{json[i]['beginnDatum']['jahr']} - {json[i]['endeDatum']['tag']}.{json[i]['endeDatum']['monat']}.{json[i]['endeDatum']['jahr']}')
                            elif json[i]['beginnDatum'] != None and int(json[i]['beginnDatum']['tag']) != 0:
                                lebenstage_list.append(f'{json[i]['beginnDatum']['tag']}.{json[i]['beginnDatum']['monat']}.{json[i]['beginnDatum']['jahr']} - ?')
                            elif json[i]['endeDatum'] != None and int(json[i]['endeDatum']['tag']) != 0:
                                lebenstage_list.append(f'? - {json[i]['endeDatum']['tag']}.{json[i]['endeDatum']['monat']}.{json[i]['endeDatum']['jahr']} - ?')
                            else:
                                lebenstage_list.append(None)
                            
                            link_ndb_list.append(json[i]['permalink'])
                            normierungsstatus_list.append(json[i]['normierungsstatus']['kurzName'])

                if len(person_id_list) >= 20:
                    break
                        
            for i in range(len(json)):
                #Dann nach höchstem Normierungsstatus suchen, bei dem aber BEruf nicht in KI-Beschreibung gefunden
                if json[i]['normierungsstatus']['kurzName'] == 'IND':
                    steckbrief_list.append(json[i]['steckbrief'])
                    person_id_list.append(json[i]['personId'])
                    name_id_list.append(json[i]['nameId'])
                    name_list.append(json[i]['name'])
                    vorname_list.append(json[i]['vorname'])
                    if json[i]['beginnDatum'] != None and int(json[i]['beginnDatum']['tag']) != 0 and json[i]['endeDatum'] != None and int(json[i]['endeDatum']['tag']) != 0:
                        lebenstage_list.append(f'{json[i]['beginnDatum']['tag']}.{json[i]['beginnDatum']['monat']}.{json[i]['beginnDatum']['jahr']} - {json[i]['endeDatum']['tag']}.{json[i]['endeDatum']['monat']}.{json[i]['endeDatum']['jahr']}')
                    elif json[i]['beginnDatum'] != None and int(json[i]['beginnDatum']['tag']) != 0:
                        lebenstage_list.append(f'{json[i]['beginnDatum']['tag']}.{json[i]['beginnDatum']['monat']}.{json[i]['beginnDatum']['jahr']} - ?')
                    elif json[i]['endeDatum'] != None and int(json[i]['endeDatum']['tag']) != 0:
                        lebenstage_list.append(f'? - {json[i]['endeDatum']['tag']}.{json[i]['endeDatum']['monat']}.{json[i]['endeDatum']['jahr']} - ?')
                    else:
                        lebenstage_list.append(None)
                                
                    link_ndb_list.append(json[i]['permalink'])
                    normierungsstatus_list.append(json[i]['normierungsstatus']['kurzName'])

                    if len(person_id_list) >= 20:
                        break
            for i in range(len(json)):
                #Dann nach zweithöchstem Normierungsstatus suchen, wo Beruf nicht in KI-Text gefunden wurde.
                if json[i]['normierungsstatus']['kurzName'] == 'PSGP':
                    steckbrief_list.append(json[i]['steckbrief'])
                    person_id_list.append(json[i]['personId'])
                    name_id_list.append(json[i]['nameId'])
                    name_list.append(json[i]['name'])
                    vorname_list.append(json[i]['vorname'])
                    if json[i]['beginnDatum'] != None and int(json[i]['beginnDatum']['tag']) != 0 and json[i]['endeDatum'] != None and int(json[i]['endeDatum']['tag']) != 0:
                        lebenstage_list.append(f'{json[i]['beginnDatum']['tag']}.{json[i]['beginnDatum']['monat']}.{json[i]['beginnDatum']['jahr']} - {json[i]['endeDatum']['tag']}.{json[i]['endeDatum']['monat']}.{json[i]['endeDatum']['jahr']}')
                    elif json[i]['beginnDatum'] != None and int(json[i]['beginnDatum']['tag']) != 0:
                        lebenstage_list.append(f'{json[i]['beginnDatum']['tag']}.{json[i]['beginnDatum']['monat']}.{json[i]['beginnDatum']['jahr']} - ?')
                    elif json[i]['endeDatum'] != None and int(json[i]['endeDatum']['tag']) != 0:
                        lebenstage_list.append(f'? - {json[i]['endeDatum']['tag']}.{json[i]['endeDatum']['monat']}.{json[i]['endeDatum']['jahr']} - ?')
                    else:
                        lebenstage_list.append(None)
                                
                    link_ndb_list.append(json[i]['permalink'])
                    normierungsstatus_list.append(json[i]['normierungsstatus']['kurzName'])

                    if len(person_id_list) >= 20:
                        break
            
            for i in range(len(json)):
                #Dann nach dritthöchstem Normierungsstatus suchen, wo Beruf nicht in KI-Text gefunden wurde.
                if json[i]['normierungsstatus']['kurzName'] == 'NMGP':
                    steckbrief_list.append(json[i]['steckbrief'])
                    person_id_list.append(json[i]['personId'])
                    name_id_list.append(json[i]['nameId'])
                    name_list.append(json[i]['name'])
                    vorname_list.append(json[i]['vorname'])
                    if json[i]['beginnDatum'] != None and int(json[i]['beginnDatum']['tag']) != 0 and json[i]['endeDatum'] != None and int(json[i]['endeDatum']['tag']) != 0:
                        lebenstage_list.append(f'{json[i]['beginnDatum']['tag']}.{json[i]['beginnDatum']['monat']}.{json[i]['beginnDatum']['jahr']} - {json[i]['endeDatum']['tag']}.{json[i]['endeDatum']['monat']}.{json[i]['endeDatum']['jahr']}')
                    elif json[i]['beginnDatum'] != None and int(json[i]['beginnDatum']['tag']) != 0:
                        lebenstage_list.append(f'{json[i]['beginnDatum']['tag']}.{json[i]['beginnDatum']['monat']}.{json[i]['beginnDatum']['jahr']} - ?')
                    elif json[i]['endeDatum'] != None and int(json[i]['endeDatum']['tag']) != 0:
                        lebenstage_list.append(f'? - {json[i]['endeDatum']['tag']}.{json[i]['endeDatum']['monat']}.{json[i]['endeDatum']['jahr']} - ?')
                    else:
                        lebenstage_list.append(None)
                                
                    link_ndb_list.append(json[i]['permalink'])
                    normierungsstatus_list.append(json[i]['normierungsstatus']['kurzName'])

                    if len(person_id_list) >= 20:
                        break

            for i in range(len(json)):
                #Wenn jetzt immer noch keine 20 Einträge gefunden wurden, dann mit den restlichen Ergebnissen auffüllen
                if json[i]['personId'] not in person_id_list:
                    steckbrief_list.append(json[i]['steckbrief'])
                    person_id_list.append(json[i]['personId'])
                    name_id_list.append(json[i]['nameId'])
                    name_list.append(json[i]['name'])
                    vorname_list.append(json[i]['vorname'])
                    if json[i]['beginnDatum'] != None and int(json[i]['beginnDatum']['tag']) != 0 and json[i]['endeDatum'] != None and int(json[i]['endeDatum']['tag']) != 0:
                        lebenstage_list.append(f'{json[i]['beginnDatum']['tag']}.{json[i]['beginnDatum']['monat']}.{json[i]['beginnDatum']['jahr']} - {json[i]['endeDatum']['tag']}.{json[i]['endeDatum']['monat']}.{json[i]['endeDatum']['jahr']}')
                    elif json[i]['beginnDatum'] != None and int(json[i]['beginnDatum']['tag']) != 0:
                        lebenstage_list.append(f'{json[i]['beginnDatum']['tag']}.{json[i]['beginnDatum']['monat']}.{json[i]['beginnDatum']['jahr']} - ?')
                    elif json[i]['endeDatum'] != None and int(json[i]['endeDatum']['tag']) != 0:
                        lebenstage_list.append(f'? - {json[i]['endeDatum']['tag']}.{json[i]['endeDatum']['monat']}.{json[i]['endeDatum']['jahr']} - ?')
                    else:
                        lebenstage_list.append(None)
                                    
                    link_ndb_list.append(json[i]['permalink'])
                    normierungsstatus_list.append(json[i]['normierungsstatus']['kurzName'])

                    if len(person_id_list) >= 20:
                        break
            break
        
        #Auf Wunsch der Anwender den Normierungsstatus ausschreiben
        for n in range(len(normierungsstatus_list)):
            if normierungsstatus_list[n] == 'IND':
                normierungsstatus_list[n] = 'Individuum geprüft'
            elif normierungsstatus_list[n] == 'PSGP':
                normierungsstatus_list[n] = 'Person geprüft'
            elif normierungsstatus_list[n] == 'NMGP':
                normierungsstatus_list[n] = 'Name geprüft'
        
        return person_id_list, name_id_list, name_list, vorname_list, lebenstage_list, link_ndb_list, normierungsstatus_list, steckbrief_list
    
    def create_permalink_vokabel(self, vok_id):
        """Util to create permalink from Vok-ID
        
        Args:
            vok_id (str): Single ID of Vokabel
        
        Returns:
            permalink (str): Permanent link to entity website at NormDatenbank Web. 
        
        """

        permalink = f'https://normdb.ivz.cn.ard.de/vokabel/{vok_id}'

        return(permalink)

    def make_orte_suggestions_from_LLM_suggestions (self, ort_to_find):
        """Makes suggestions for normDB Person entries
        Args:
            ort_to_find(str): Name of Ort suggested by LLM
        
        Returns:
            vokabel_name_id_list (list): Orte Name-IDs of suggests from normDB
            name_list (list): Orte Names of suggests from normDB 
            name_zusatz_list (list): List of posssible Orte Name additions for all suggests.
            permalinks_ndb_list (list): Links to single ndb entries of suggests
            norm_status_list (list): Normierungsstatus of  suggests from NDB
            vokabel_name_id_list (list): Orte Name-IDs of suggests from normDB
            pfade_ort_list (list): Hierarchiepfade for Orte suggests.
        
        """
        abfrage = ort_to_find
        vokabel_id_list = []
        vokabel_name_id_list = []
        name_list = []
        name_zusatz_list = []
        permalinks_ndb_list = []
        norm_status_list = []

        url = f'https://normdb.ivz.cn.ard.de/normdbrs_vokabel/V2/service/VokabelVorschlaege?suchString={abfrage}&vokabularIds=1&trunkierungsModus=2&anzahl=100'
        response = self.session.get(url, verify=self.certificate)

        json = response.json() 
        json_list_vollstaendig = []
        pfade_ort_list = []
        score_thefuzz_list = []
        if len(json) == 0:#Wenn keine Ergebnisse für SUchbegriff gefunden wurde, dann teile Suchbegriff an Leerzeichen auf und suche einzelne Teile.
            abfrage = abfrage.split(' ')
            for a in range(len(abfrage)):
                url = f'https://normdb.ivz.cn.ard.de/normdbrs_vokabel/V2/service/VokabelVorschlaege?suchString={abfrage[a]}&vokabularIds=1&trunkierungsModus=2&anzahl=100'
                response = self.session.get(url, verify=self.certificate)
                json_teil = response.json()
                for t in range(len(json_teil)):
                    json.append(json_teil[t])

        for v in range(len(json)):
            vok_id = json[v]['vokabelId']
            vok_id_number = vok_id.split('-')[1]
            url_abfrage_detail_data = f'https://normdb.ivz.cn.ard.de/normdbrs_vokabel/V2/service/Vokabel/{vok_id_number}'
            response_detail = self.session.get(url_abfrage_detail_data, verify=self.certificate)
            json_detail = response_detail.json() 
            
            list_scores_zwischen = []
            for j in range(len(json_detail['vokabelNamen'])):
                ratio = fuzz.ratio(json_detail['vokabelNamen'][j]['vokabelName'],ort_to_find)
                #print(json_detail['vokabelNamen'][j]['vokabelName'], ratio)
                list_scores_zwischen.append(ratio)
            list_scores_zwischen.sort(reverse = True)
            #print(json_detail['vokabelNamen'][0]['vokabelName'], list_scores_zwischen[0])
            score_thefuzz_list.append(list_scores_zwischen[0])
            #print('******************')

            json_list_vollstaendig.append(json_detail)
                 
  
        # Python program to sort values of first list based on second list
        
        a = list(set(score_thefuzz_list))
        a.sort(reverse = True)
        list_sorted_scores_json = []
        for i in a:
            for j in range(0, len(score_thefuzz_list)):
                if(score_thefuzz_list[j] == i):
                    list_sorted_scores_json.append(json_list_vollstaendig[j])
        #print(list_sorted_scores_json)

        while len(name_list) <20:#20 Ergebnisse sollen angezeigt werden, wir nehmen die 20 mit dem höchsten Score - erst abgestimmte, dann den Rest!
            for i in range(len(list_sorted_scores_json)): 
                
                if list_sorted_scores_json[i]['status']['kurzName'] == 'ABG' and list_sorted_scores_json[i]['zugelassen'] == True and list_sorted_scores_json[i]['vokabelId'] not in vokabel_id_list:
                    norm_status_list.append('ABG')
                    vokabel_id_list.append(list_sorted_scores_json[i]['vokabelId'])
                    permalinks_ndb_list.append(list_sorted_scores_json[i]['permalink'])
                    for v in range(len(list_sorted_scores_json[i]['vokabelNamen'])):
                        if list_sorted_scores_json[i]['vokabelNamen'][v]['istHauptname'] == True:
                            name_list.append(list_sorted_scores_json[i]['vokabelNamen'][v]['vokabelName'])
                            vokabel_name_id_list.append(list_sorted_scores_json[i]['vokabelNamen'][v]['vokabelNameId'])
                            name_zusatz_list.append(list_sorted_scores_json[i]['vokabelNamen'][v]['vokabelNameZusatz'])
                            break
                if len(name_list) >=20:
                    break
            if len(name_list) <20:
                for i in range(len(list_sorted_scores_json)): 
                    
                    if json_detail['status']['kurzName'] != 'ABG' and list_sorted_scores_json[i]['zugelassen'] == True and list_sorted_scores_json[i]['vokabelId'] not in vokabel_id_list:
                        norm_status_list.append(json_detail['status']['kurzName'])
                        vokabel_id_list.append(list_sorted_scores_json[i]['vokabelId'])
                        permalinks_ndb_list.append(list_sorted_scores_json[i]['permalink'])
                        for v in range(len(list_sorted_scores_json[i]['vokabelNamen'])):
                            if list_sorted_scores_json[i]['vokabelNamen'][v]['istHauptname'] == True:
                                name_list.append(list_sorted_scores_json[i]['vokabelNamen'][v]['vokabelName'])
                                vokabel_name_id_list.append(list_sorted_scores_json[i]['vokabelNamen'][v]['vokabelNameId'])
                                name_zusatz_list.append(list_sorted_scores_json[i]['vokabelNamen'][v]['vokabelNameZusatz'])
                                break
                    if len(name_list) >=20:
                        break        

            break

                           

        #Hierarchiepfade für Ergebnisliste abfragen
        for n in range(len(name_list)):
            vok_id = vokabel_id_list[n].split('-')[1]
        
            url_abfrage_pfad_vok = f'https://normdb.ivz.cn.ard.de/normdbrs_vokabel/V2/service/Vokabel/{vok_id}/HierarchiePfad'
            response_pfad = self.session.get(url_abfrage_pfad_vok, verify=self.certificate)
                
            pfade_ort_list.append(response_pfad.text)


            

        return vokabel_name_id_list, name_list, name_zusatz_list, permalinks_ndb_list, norm_status_list, vokabel_name_id_list, pfade_ort_list

    def make_institutionen_suggestions_from_LLM_suggestions (self, inst_to_find):
        """Makes suggestions for normDB Institutionen entries
            
            Args:
                inst_to_find(str): Name of Ort suggested by LLM

            Returns:
                inst_name_id_list (list): Name IDs of institutions suggests
                inst_name_list (list): Names of institutions suggests
                namenszusatz_list (list): Names additions of institutions suggests
                inst_id_list (list): IDs of institutions suggests
                inst_norm_status_list (list): Normierungsstatus of suggests for institutions.
                inst_permalink_list (list): List of permalinks for suggests 
                
                
            """
        print('DEBUG Institutionen Input:', inst_to_find)
        inst_name_list = []
        inst_id_list = []
        inst_norm_status_list = []
        inst_permalink_list = []
        inst_name_id_list = []
        namenszusatz_list = []

        url = f'https://normdb.ivz.cn.ard.de/normdbrs_institution/V2/service/Institutionen/Vorschlaege?suchtext={inst_to_find}&anzahl=100'
        response = self.session.get(url, verify=self.certificate)

        json = response.json() 

        if len(json) == 0:#Wenn keine Ergebnisse für SUchbegriff gefunden wurde, dann teile Suchbegriff an Leerzeichen auf und suche einzelne Teile.
            abfrage = inst_to_find.split(' ')
            for a in range(len(abfrage)):
                url = f'https://normdb.ivz.cn.ard.de/normdbrs_institution/V2/service/Institutionen/Vorschlaege?suchtext={inst_to_find[a]}&anzahl=100'
                json_teil = response.json()
                for t in range(len(json_teil)):
                    json.append(json_teil[t])

        while len(inst_name_list) <20:
            for v in range(len(json)):
                if json[v]['normierungsstatus'] != None:
                   
                    if json[v]['normierungsstatus']['kurzName'] == 'INSIN':
                        inst_name = json[v]['name']
                        inst_name_list.append(inst_name)
                        inst_name_id = json[v]['nameId']
                        inst_name_id_list.append(inst_name_id)
                        namenszusatz = json[v]['namenszusatz']
                        namenszusatz_list.append(namenszusatz)
                        institutionen_id = json[v]['institutionId']
                        inst_id_list.append(institutionen_id)
                        inst_norm_status = json[v]['normierungsstatus']['langName']
                        inst_norm_status_list.append(inst_norm_status)
                        inst_permalink = json[v]['permalink']
                        inst_permalink_list.append(inst_permalink)
                if len(inst_name_list)>=20:
                    break
            for v in range(len(json)):
                if json[v]['normierungsstatus'] != None:
                    if json[v]['normierungsstatus']['kurzName'] == 'INSGP':
                        inst_name = json[v]['name']
                        inst_name_list.append(inst_name)
                        inst_name_id = json[v]['nameId']
                        inst_name_id_list.append(inst_name_id)
                        namenszusatz = json[v]['namenszusatz']
                        namenszusatz_list.append(namenszusatz)
                        institutionen_id = json[v]['institutionId']
                        inst_id_list.append(institutionen_id)
                        inst_norm_status = json[v]['normierungsstatus']['langName']
                        inst_norm_status_list.append(inst_norm_status)
                        inst_permalink = json[v]['permalink']
                        inst_permalink_list.append(inst_permalink)
                if len(inst_name_list)>=20:
                    break

            for v in range(len(json)):
                if json[v]['normierungsstatus'] != None:
                    if json[v]['normierungsstatus']['kurzName'] == 'NMGP':
                        inst_name = json[v]['name']
                        inst_name_list.append(inst_name)
                        inst_name_id = json[v]['nameId']
                        inst_name_id_list.append(inst_name_id)
                        namenszusatz = json[v]['namenszusatz']
                        namenszusatz_list.append(namenszusatz)
                        institutionen_id = json[v]['institutionId']
                        inst_id_list.append(institutionen_id)
                        inst_norm_status = json[v]['normierungsstatus']['langName']
                        inst_norm_status_list.append(inst_norm_status)
                        inst_permalink = json[v]['permalink']
                        inst_permalink_list.append(inst_permalink)
                if len(inst_name_list)>=20:
                    break

            for v in range(len(json)):
                if json[v]['normierungsstatus'] != None:
                    if json[v]['normierungsstatus']['kurzName'] == 'NMUP':
                        inst_name = json[v]['name']
                        inst_name_list.append(inst_name)
                        inst_name_id = json[v]['nameId']
                        inst_name_id_list.append(inst_name_id)
                        namenszusatz = json[v]['namenszusatz']
                        namenszusatz_list.append(namenszusatz)
                        institutionen_id = json[v]['institutionId']
                        inst_id_list.append(institutionen_id)
                        inst_norm_status = json[v]['normierungsstatus']['langName']
                        inst_norm_status_list.append(inst_norm_status)
                        inst_permalink = json[v]['permalink']
                        inst_permalink_list.append(inst_permalink)
                if len(inst_name_list)>=20:
                    break
            
            for v in range(len(json)):
                if json[v]['normierungsstatus'] != None:
                    if json[v]['name']not in inst_name_list:
                        inst_name = json[v]['name']
                        inst_name_list.append(inst_name)
                        inst_name_id = json[v]['nameId']
                        inst_name_id_list.append(inst_name_id)
                        namenszusatz = json[v]['namenszusatz']
                        namenszusatz_list.append(namenszusatz)
                        institutionen_id = json[v]['institutionId']
                        inst_id_list.append(institutionen_id)
                        inst_norm_status = json[v]['normierungsstatus']['langName']
                        inst_norm_status_list.append(inst_norm_status)
                        inst_permalink = json[v]['permalink']
                        inst_permalink_list.append(inst_permalink)
                if len(inst_name_list)>=20:
                    break
            break

        return inst_name_id_list, inst_name_list, namenszusatz_list, inst_id_list, inst_norm_status_list, inst_permalink_list


    def suggest_ndb_sprachen(self, sprache_search):
        """Makes suggestions for normDB Sprachen entries
        Args:
            sprache_search(str): Name of Sprache suggested by LLM

        Returns:
            vokabel_ids (list): Vok-IDs of suggestions for possible spoken languages in audio
            vokabel_namen (list): Names of Vokabeln of possible languages spoken
            vokabel_zusaetze (list): vacabulary additions occuring with possible languages spoken in audio
            vokabel_teilbereiche (list): Vocabulary categories for suggests
            vokabel_eltern_namen (list): Parent Names of suggests for languages
            vokabel_namen_ids (list): IDs of names of suggests for languages
                        
        """
        print('DEBUG Sprache Input:', sprache_search)
        vokabel_ids = []
        vokabel_namen = []
        vokabel_namen_ids = []
        vokabel_zusaetze = []
        vokabel_teilbereiche = []
        vokabel_eltern_namen = []

        url_01 = f'https://normdb.ivz.cn.ard.de/normdbrs_vokabel/V2/service/VokabelVorschlaege?suchString={sprache_search}&vokabularIds=3&teilbereichIds=3&nurZugelasseneVokabeln=true&trunkierungsModus=3&anzahl=20'
        response = self.session.get(url_01, verify=self.certificate)
        print(response)
        json = response.json() 
        if len(json) >0:
            for j in range(len(json)):
                if json[j]['vokabelTeilbereich'] == 'Standard Sprachen':
                    vokabel_ids.append(json[j]['vokabelId'])
                    vokabel_namen.append(json[j]['vokabelName'])
                    vokabel_namen_ids.append(json[j]['vokabelNameId'])
                    if json[j]['vokabelNameZusatz'] == 'null':
                        vokabel_zusaetze.append(None)
                    else:
                        vokabel_zusaetze.append(json[j]['vokabelNameZusatz'])
                    vokabel_teilbereiche.append(json[j]['vokabelTeilbereich'])
                    vokabel_eltern_namen.append(json[j]['elternName'])
            for j in range(len(json)):
                if json[j]['vokabelTeilbereich'] != 'Standard Sprachen':
                    vokabel_ids.append(json[j]['vokabelId'])
                    vokabel_namen.append(json[j]['vokabelName'])
                    vokabel_namen_ids.append(json[j]['vokabelNameId'])
                    if json[j]['vokabelNameZusatz'] == 'null':
                        vokabel_zusaetze.append(None)
                    else:
                        vokabel_zusaetze.append(json[j]['vokabelNameZusatz'])
                    vokabel_teilbereiche.append(json[j]['vokabelTeilbereich'])
                    vokabel_eltern_namen.append(json[j]['elternName'])


        else:
            url_02 = f'https://normdbhotfix.ivz.cn.ard.de/normdbrs_vokabel/V2/service/VokabelVorschlaege?suchString=suchString={sprache_search}&vokabularIds=3&teilbereichIds=3&nurZugelasseneVokabeln=true&trunkierungsModus=2&anzahl=20'

            response = self.session.get(url_02, verify=self.certificate)

            json = response.json() 
            if len(json) >0:
                for j in range(len(json)):
                    if json[j]['vokabelTeilbereich'] == 'Standard Sprachen':
                        vokabel_ids.append(json[j]['vokabelId'])
                        vokabel_namen.append(json[j]['vokabelName'])
                        vokabel_namen_ids.append(json[j]['vokabelNameId'])
                        if json[j]['vokabelNameZusatz'] == 'null':
                            vokabel_zusaetze.append(None)
                        else:
                            vokabel_zusaetze.append(json[j]['vokabelNameZusatz'])
                        vokabel_teilbereiche.append(json[j]['vokabelTeilbereich'])
                        vokabel_eltern_namen.append(json[j]['elternName'])
                for j in range(len(json)):
                    if json[j]['vokabelTeilbereich'] != 'Standard Sprachen':
                        vokabel_ids.append(json[j]['vokabelId'])
                        vokabel_namen.append(json[j]['vokabelName'])
                        vokabel_namen_ids.append(json[j]['vokabelNameId'])
                        if json[j]['vokabelNameZusatz'] == 'null':
                            vokabel_zusaetze.append(None)
                        else:
                            vokabel_zusaetze.append(json[j]['vokabelNameZusatz'])
                        vokabel_teilbereiche.append(json[j]['vokabelTeilbereich'])
                        vokabel_eltern_namen.append(json[j]['elternName'])

        return vokabel_ids, vokabel_namen, vokabel_zusaetze, vokabel_teilbereiche, vokabel_eltern_namen, vokabel_namen_ids   

    def set_vokabel_vorschlaege (self, tag_single):
        """Gets normDB-Vokabel-Vorschläge from LLM-created suggestions and sorts them based on NDB-request result
        
        Args:
            tag_single(str): Single tag suggested by LLM for audio transcript.

        Returns:
            tag_word (list): List of words from NDB that could be tags for HFDB entry
            vok_ids (list): List of vocabulary IDs for tags suggested.
            name_vok_ids (list): Vocabulary IDs of suggests.
            zugeordnete_klassen_name (list): Name of Klasse that is linked to tag
            zugeordnete_klassen_ids (list): ID of Klasse that is linked to tag
            zugeordnete_klassen_name_ids (list): Name IDs of suggests for Klassen linked to tags
            vokabel_typ (str): Type of Vokabel

        """

        """Basisregeln:
        Wenn Begriff als Klasse gefunden (VokTeilbereich):
        Begriff übernehmen

        Wenn Begriff als Synonym zu Klasse gefunden (vokTeilbereich):
        Haupt-Deskriptor übernehmen (DeskriptorName)

        Wenn Begriff in vokTeilbereich als Sachdeskriptor ausgegeben:
        Über API /service/Vokabel/{id}/Zuordnungen die zugeordnete Klasse ausgeben lassen und beide gemeinsam anlegen

        Wenn Begriff als Synonym zu Sachdeskriptor gefunden: 
        Haupt-Deskriptor übernehmen und zusammen mit zugeordneter Klasse ausgeben

        Wenn Begriff in vokTeilbereich als Freier Sachdeskriptor ausgegeben:
        Freien Sachdeskriptor übernehmen und über API /service/Vokabeln/MatchingSachklassifikation Klassenvorschläge ausgeben lassen - diese vorgeschlagenen Klassen der Claudia zur Auswahl als Dropdown anzeigen. FSD und Klasse gemeinsam übernehmen.

        Wenn kein Match mit Vokabel:
        Begriffe nicht als Klasse/Deskriptor ausgeben, sondern als "Tags" in HFDB vorschlagen

        - Alle Begriffe (Klassen, (Freien) Sachdeskriptoren und Tags) mit ihrer Kategorie (KL, SD, FSD, Tag) kennzeichnen. Insgesamt alles "nur" als Vorschlag zur Auswahl anzeigen.
        """  

        tag_word = []
        vok_ids = []
        name_vok_ids = []
        zugeordnete_klassen_name = []
        zugeordnete_klassen_ids = []
        zugeordnete_klassen_name_ids = []
        vokabel_typ = []


        url_01 = f'https://normdb.ivz.cn.ard.de/normdbrs_vokabel/V2/service/VokabelVorschlaege?suchString={tag_single}&vokabularIds=310&nurZugelasseneVokabeln=true&trunkierungsModus=3&anzahl=20'
        response = self.session.get(url_01, verify=self.certificate)

        json = response.json() 
        if len(json) == 0: 
            tag_word.append(tag_single)
        else:
            for i in range(len(json)):
                if json[i]['vokabelNameTyp'] == 'Synonym':
                    #Zunächst prüfen, ob wir Synonyme haben. Dann auf die Haupt-Vokabel switchen, diese abrufen und an die Haupt-json dran hängen, die dann anschließend anylysiert wird.
                    tag_single_new = json[i]['vokabelName']
                    url_alt = f'https://normdb.ivz.cn.ard.de/normdbrs_vokabel/V2/service/VokabelVorschlaege?suchString={tag_single_new}&vokabularIds=310&nurZugelasseneVokabeln=true&trunkierungsModus=3&anzahl=20'
                    response_alt = self.session.get(url_alt, verify=self.certificate)
                    json_alt = response_alt.json()
                    for j in range(len(json_alt)):
                        json.append(json_alt[j])
                
            for i in range(len(json)):
                if json[i]['vokabelNameTyp'] == "Deskriptor":
                    if json[i]['vokabelTeilbereich'] == "Sachdeskriptoren" and json[i]['vokabelNameTyp'] != 'Synonym':
                        vokid = json[i]['vokabelId']
                        vok_ids.append(vokid)
                        name_vok_ids.append(json[i]['vokabelNameId'])
                        tag_word.append(json[i]['vokabelName'])
                        vokabel_typ.append(json[i]['vokabelTeilbereich'])
                        zuordnung_vokabel_url_abruf = f'https://normdb.ivz.cn.ard.de/normdbrs_vokabel/V2/service/Vokabel/{vokid}/Zuordnungen'
                        response_detail_vok = self.session.get(zuordnung_vokabel_url_abruf, verify=self.certificate)

                        json_detail_vok = response_detail_vok.json() 
                        for j in range(len(json_detail_vok['zuordnungen'])):
                            if json_detail_vok['zuordnungen'][j]['vokabelTeilbereich'] == 'Klassen':
                                zugeordnete_klassen_name.append(json_detail_vok['zuordnungen'][j]['vokabelName'])
                                zugeordnete_klassen_ids.append(json_detail_vok['zuordnungen'][j]['vokabelId'])
                                zugeordnete_klassen_name_ids.append(json_detail_vok['zuordnungen'][j]['vokabelNameId'])
                    
                    elif json[i]['vokabelTeilbereich'] == "Freie Sachdeskriptoren":
                        vokid = json[i]['vokabelId']
                        vok_ids.append(vokid)
                        name_vok_ids.append(json[i]['vokabelNameId'])
                        tag_word.append(json[i]['vokabelName'])
                        vokabel_typ.append(json[i]['vokabelTeilbereich'])
                        passende_klassen_abruf_url = f'https://normdb.ivz.cn.ard.de/normdbrs_vokabel/V2/service/Vokabeln/MatchingSachklassifikation?keywords={json[i]['vokabelName']}&useWikidata=true'
                        with requests.sessions.Session() as session:
                            session.auth = ("awolff", "hugoegonbalder87")
                            session.trust_env = False
                            response_detail_klassen = session.post(passende_klassen_abruf_url, verify=self.certificate)
                            print('DEBUG LOGIN NDB:', response_detail_klassen)
                        json_detail_klassen = response_detail_klassen.json()
                        print('DEBUG Entity Linking  Rückgabe:', json_detail_klassen)
                        for k in range(len(json_detail_klassen)):
                            zugeordnete_klassen_name.append(json_detail_klassen[k]["vokabelName"])
                            zugeordnete_klassen_ids.append(json_detail_klassen[k]["vokabelId"])

                    elif json[i]['vokabelTeilbereich'] == "Klassen":
                        tag_word.append(json[i]["vokabelName"])
                        vok_ids.append(json[i]["vokabelId"])
                        name_vok_ids.append(json[i]["vokabelNameId"])
                        vokabel_typ.append(json[i]['vokabelTeilbereich'])

        #if len(tag_word) == 0:
         #   tag_word.append(tag_single)

        print('DEBUG Norm-DB-Rückgabe:', tag_word, vok_ids, name_vok_ids, zugeordnete_klassen_name,zugeordnete_klassen_ids, vokabel_typ)

        return tag_word, vok_ids, name_vok_ids, zugeordnete_klassen_name,zugeordnete_klassen_ids, zugeordnete_klassen_name_ids, vokabel_typ







