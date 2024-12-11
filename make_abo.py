from datetime import datetime
import pickle


class make_abo():
    """Class for making ABO"""

    def __init__(self, ref_anr_start_number, hfdb_client):
        """
        Args:
            ref_anr_start_number(str): Start-string from which we shall count upwards for the next ANRs
            hfdb_client: hfdb-client-instance that is needed for talking to HFDB-API
        
        """
        
        self.anr_start_number = ref_anr_start_number
        anr_parts = self.make_base_anr_number()
        self.base_anr_prefix = anr_parts[0]
        self.base_anr_number = anr_parts[1]
        self.hfdb_client = hfdb_client[0]
        self.instance = hfdb_client[1] 

    def make_base_anr_number(self):
        """Calculates right base ABO number from base ABO Number - this is the pure number within the ANR string to start with and calculate up from
        
        Returns:
            prefix(str): Fixed non-numeric prefix of ANR-Number
            base_number(int): Number part of first  ANR  from which we count up from
        
        """
        anr_base = self.anr_start_number
        print('anr_base:', anr_base)
        #example ZNR125785
        found_start_number = False

        number_start_numbers = 0
        #Loop: Springe in Zeichenkette der ANR so lange ein Zeichen weiter bis wir bei einer Zahl angekommen sind
        while found_start_number == False:
            try: 
                int(anr_base[number_start_numbers])
                found_start_number = True
                print('Found Start Number:', number_start_numbers)
            except:
                number_start_numbers = number_start_numbers +1

        prefix = anr_base[0:number_start_numbers]
        base_number = anr_base[number_start_numbers:len(anr_base)]

        return prefix, base_number


    def make_current_anr(self, abo_calc_number):
        """Makes correct current ANR
        
        Args:
            abo_calc_number(str): Number of ABOs we processed since the first one

        Returns:
            current_ANR(str): Curent ANR for current to create ABO
        """
        found_none_zero = False
        checking_point = 0
        print('Base-ANR-number-Loaded:', self.base_anr_number)
        for i in range(len(str(self.base_anr_number))):
                base_anr_number_string = str(self.base_anr_number)
                if base_anr_number_string[i] != '0':
                    found_none_zero == True
                    checking_point = i
                    base_anr_number_new = int(base_anr_number_string[i:len(base_anr_number_string)])
                    break
        print('checking Point:', checking_point)
        print('ANR_Number_Pur:', base_anr_number_new)
        print('Nullen:', checking_point)

        anr_number = base_anr_number_new + abo_calc_number
        if (len(str(anr_number)) > len(str(base_anr_number_new))) and checking_point >0:
            checking_point = checking_point -1

        current_anr = f'{self.base_anr_prefix}{'0'*checking_point}{str(anr_number)}'
        print('ANR fertig:', current_anr)


        return current_anr
    

    def create_abo(self, abo_calc_number, amo_attached, path_pickle_anr = 'path_pickle_last_anr.pickle'):
        """Main ABO class  that creates ABO itself
        Args:
            abo_calc_number(int): The number of the audio coming in (e.g. 2 if it's the second audio of the row)
            amo_attached(str): The URI of the AMO that should be attached  to the AMO.
            path_pickle_anr(str): The Path to a pickle-File where the last ANR used is stored. Defaults to pickle-file within the main library.

        
        """
        ABO_neu = {
            'erfassungDatum': {
                'day': datetime.today().strftime('%d'),
                'month': datetime.today().strftime('%m'),
                'year': datetime.today().strftime('%Y')
            },
            'erfassungDokumentar': {
                'kurzName': 'DRA-Skript',
                'langName': 'DRA-Skript'
            },
            'hfdbId': None,
            
            'quelle': None,
            'workflowSteuerungen': [],
            'externeBeziehungen': [],
            'archivnummer': self.make_current_anr(abo_calc_number),
            'audioMedienobjektRef': amo_attached,
            'aufbewahrungsfrist': None,
            'begleitmaterial': [],
            'bemerkungen': [],
            'beschriftung': None,
            'bestand': {
                'bestandsId': 142811121112,
                'bestandseigner': {
                    'kurzbezeichnung': 'DRA',
                    'langbezeichnung': 'Deutsches Rundfunkarchiv',
                    'normId': 'http://hfdb.ard.de/normdb/Wert?id=4177'
                },
                'bezeichnung': 'Tonträger DRA Babelsberg',
                'kurzbezeichnung': 'BAB',
                'standort': None
            },
            'bestandsobjektErwerb': None,
            'dateiname': None,
            'dateipfad': None,
            'elementAnzahl': None,
            'exemplarAnzahl': None,
            'fremdArchivnummer': None,
            'fremdbestand': None,
            'herkunft': 'Archive Rundfunk der DDR',
            'recht': None,
            'sendefertig': None,
            'server': None,
            'technischeAbnahme': None,
            'technischeBeurteilung': None,
            'url': None,
            'vorhanden': True,
            'zugangsDatum': None,
            'entliehenAnzahl': 0
        }
        
        new_abo = self.hfdb_client.service.insertABO(ABO_neu)
        new_anr = ABO_neu['archivnummer']

        #Write current ANR-Number to pickle
        with open(path_pickle_anr, 'wb') as handle:
            pickle.dump(new_anr, handle, protocol=pickle.HIGHEST_PROTOCOL)

        return new_abo, new_anr
        