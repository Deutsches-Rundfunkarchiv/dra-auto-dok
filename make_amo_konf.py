from datetime import datetime
import librosa
from time import gmtime
from time import strftime
from scipy.io.wavfile import read as read_wav
import pandas
import fleep
from pydub import AudioSegment  
from mutagen.wave import WAVE


class make_amo_konf():
    """Measures audio file to create file Konfektionierung"""

    def __init__(self, hfdb_client, source_audio_files_ordner):
        """Args:
            hfdb_client(function): Zeep-based function for calling HFDB-API
            ak_refs_list(list): List of HFDB-IDs of AKs, that should be attached to the new AMOs and Konfs.
            source_audio_files_ordner(str - path): Path to the original audio files
            konf_audioraum_liste(list): List of defined Audioraum-Entrys for single Audios.
            lese_abspiel_input(list): Input on Lese- und Abspielgeschwindigkeit coming completely from User.
            """
        self.hfdb_client = hfdb_client[0]
        self.instance = hfdb_client[1] 
        self.source_audio_files_ordner = source_audio_files_ordner

    def get_lese_abspielgeschwindigkeit(self, excel_file, lese_abspiel_vorgabe):
        """Makes full entry for Lese- und Abspielgeschwindigkeit for HFDB
        
        Args:
            excel_file(str): Path to excel_File with possible Lese- und Abspielgeschwindigkeiten
        
        Returns:
            leseabspielgeschwindgkeit (dict): Ready to use object to insert into HFDB structure
        """
        user_choice = lese_abspiel_vorgabe
        df = pandas.read_excel(excel_file)
        wert = df['kurzbezeichnung']
        langbezeichnung = df['langbezeichnung']
        normid = df['normId']

        index_list = list(langbezeichnung).index(user_choice)
        if langbezeichnung[index_list] == 'Kein Eintrag' or 'Eintrag' in langbezeichnung[index_list]:
            leseabspielgeschwindigkeit = None
        else:
            leseabspielgeschwindigkeit = {
                'kurzbezeichnung': wert[index_list],
                'langbezeichnung': langbezeichnung[index_list],
                'normId': normid[index_list]
            }

        return(leseabspielgeschwindigkeit)
    
    def get_sampling_rate(self, excel_file, audiofile):## Not needed and implemented right now
        """Measures Sample rate fully automated from original source file
        
        Args:
            excel_file (str): Path to excel file where available sample rate entries are stored.
            audiofile (str): Path to audiofile that should be measured

        Returns:
            samplingrate_entry(dict): Ready to use in HFDB entry part for sampling rate.
        """
        
        df = pandas.read_excel(excel_file)
        wert = df['Wert']
        norm_id = df['norm_id']
        sampling_rate = librosa.get_samplerate(audiofile)
        sampling_rate = int(sampling_rate)/1000
        sampling_rate = round(sampling_rate, 1)
        norm_ids = list(norm_id)
        werte = list(wert)

        index = werte.index(round(sampling_rate, 0))
        norm_id = norm_ids[index]

        samplingrate_entry = {
                            'kurzbezeichnung': sampling_rate,
                            'langbezeichnung': f'{sampling_rate} kHz',
                            'normId': norm_id
                        }
        return samplingrate_entry
    
    #Vollautomatisierte Lösung
    #def get_audioraumdarstellung(self, audiofile):
     #   audio = AudioSegment.from_file(file=audiofile)  
      #  channels = audio.channels
       # if channels == 1:
          #  kurzbez = 100
           # langbez = 'Mono'
           # norm_id = 'http://hfdb.ard.de/normdb/Wert?id=1072'
        #elif channels == 2:
          #  kurzbez = 200
          #  langbez = 'Stereo'
          #  norm_id = 'https://normdb.ivz.cn.ard.de/wert/1073'
 
       # audioRaumdarstellung = {
                      #  'kurzbezeichnung': kurzbez,
                      #  'langbezeichnung': langbez,
                      #  'normId': norm_id
                   # }
       # return(audioRaumdarstellung)
    
    #Teilautomatisierte Lösung
    def get_audioraumdarstellung(self, excel_file, audioraum_vorgabe): #Not needed  right now, will be set manually for whole Audio Batch in advance and then be open for correction on single audio level later.
        """Creates Audioraumdarstellung entry for HFDB based on suggestions
        
        Args:
            excel_file(str): Path to excel file with posssible entries for Audioraumdarstellung.
            audioraum_vorgabe(str): Vorgabe for Audioraumdarstellung based on Measurement and User Interface correction.
        
        Returns:
            audioRaumdarstellung(dict): Ready to use Audioraumdarstellung entry for HFDB.
        """
        df = pandas.read_excel(excel_file)
        werte = df['kurzbez']
        norm_ids = df['norm_id']
        langnamen = df['langbez']  
        
        index = list(langnamen).index(audioraum_vorgabe)
        kurzbez = str(werte[index])
        langbez = langnamen[index]
        norm_id = norm_ids[index]
 
        audioRaumdarstellung = {
                        'kurzbezeichnung': kurzbez,
                        'langbezeichnung': langbez,
                        'normId': norm_id
                    }
        return(audioRaumdarstellung)

    def get_file_format(self, audiofile):## Not needed and implemented right now
        """Defines format of file such as wav, mp3... fully automatically
        
        Args:
            audiofile(str): Path to audiofile

        Returns:
            file_extension(str): Short file extension, such as "wav" or "mp3" for file
            file_format(str): Longer string for file format entry
        
        """
        with open(audiofile, "rb") as file:
            info = fleep.get(file.read(128))
        file_extension = info.extension[0]
        file_format = info.mime[0]

        return(file_extension, file_format)

    def get_file_length(self, audiofile):
        """Gets File Length by measuring file
        
        Args:
            audiofile(str): Path to audiofile

        Returns:
        hours, minutes, seconds (int): Measured time durance of file seperated in hours, minutes and seconds
        """
        if self.source_audio_files_ordner in audiofile:
            audio_file = AudioSegment.from_file(audiofile)
        else:
            audio_file = AudioSegment.from_file(f'{self.source_audio_files_ordner}\\{audiofile}')
        duration = audio_file.duration_seconds
        #time_format = str(datetime.timedelta(seconds=duration))
        #Alternative Librosa-Lösung - funktioniert nur leider nicht mehr zumindest auf mp3s
        #duration_seconds = librosa.get_duration(filename=audiofile)
        time_format = strftime("%H:%M:%S", gmtime(duration))
        hours = int(time_format.split(':')[0])
        minutes = int(time_format.split(':')[1])
        seconds = int(time_format.split(':')[2])
        # Result: '00:02:05'
        return(hours, minutes, seconds)
    
    def get_file_quantisierung(self, excel_file, audiofile): ## Not needed and implemented right now
        """Gets file Quantisierung by measuring it
        
        Args:
            excel_file(str): Path to excel file with possible database entries
            audiofile(str): Path to audiofile for which Quantisierung is measured

        Returns:
            quantisierung(dict): Ready to use database entry for HFDB for Quantisierungs entry
        """
        
        df = pandas.read_excel(excel_file)
        werte = df['Kurzname']
        norm_ids = df['norm_id']
        langnamen = df['Langname']
        if audiofile.endswith('mp3'):
            sound = AudioSegment.from_mp3(audiofile)
            sound.export(f'{audiofile}.wav', format="wav")
            audiofile = f'{audiofile}.wav'
        audio = WAVE(audiofile)
        bit_size = audio.info.bits_per_sample

        index = list(werte).index(bit_size)
        kurzbez = werte[index]
        langbez = langnamen[index]
        norm_id = norm_ids[index]

        quantisierung= {
                            'kurzbezeichnung': kurzbez,
                            'langbezeichnung': langbez,
                            'normId': str(norm_id)
                        }
        return(quantisierung)

    def get_datenrate(self, excel_file, audiofile):## Not needed and implemented right now
        """ Measures data rate in kb/s for audiofile given
        
        Args:
            excel_file(str): Path to excel file with given categories for data rate
            audiofile(str): Path to audiofile that is measured

        Returns:
            datenrate(dict): Ready to use datenrate entry for hfdb
        
        """
        
        
        df = pandas.read_excel(excel_file)
        werte = df['Kurzname']
        norm_ids = df['norm_id']
        langnamen = df['Langname']
        if audiofile.endswith('mp3'):
            audiofile = f'{audiofile}.wav'
        audio = WAVE(audiofile)
        main_info = audio.info.pprint()
        main_info = main_info.split(',')
        datenrate = main_info[0].split('@')[1]
        datenrate = datenrate.replace(' bps','')
        datenrate = int(datenrate)/1000
        datenrate = int(datenrate)

        index = list(werte).index(datenrate)
        kurzbez = werte[index]
        langbez = langnamen[index]
        norm_id = norm_ids[index]

        datenrate =  {
                            'kurzbezeichnung': kurzbez,
                            'langbezeichnung': langbez,
                            'normId': norm_id
                        }
        return(datenrate)

    def create_amo_gesamtkonf(self, AK_Ref, audiofile, audioraum_single, lese_abspielgeschwindigkeit_single, dauer_uebernehmen):
        """Creates an AMO with Gesamtkonfektionierung based on Input-Data from measuring file
        
        Args:
            AK_Ref (str): ID of reference AK, that the AMO and Konf should be linked to. 
            audiofile (str): Path to audiofile, that is base for measurements
            audioraum_Single (): Whole audioraum entry prepared for hfdb-entry
            lese_abspielgeschwindigkeit_single(): SIngle entry fpr lese und abspielgeschwindigkeit
            dauer_uebernehmen(bool): Statement if Dauer should be measured form file or not and be left empty

        Returns:
            amo_id(str): Numeric ID of new created AMO in HFDB.
        """
        file_length = self.get_file_length(audiofile)
        #sampling_rate = self.get_sampling_rate('sampling_rates_norm_db.xlsx', audiofile)
        audioraumdarstellung = audioraum_single #self.get_audioraumdarstellung(audiofile)
        leseabspielgeschwindigkeit = lese_abspielgeschwindigkeit_single
        #quantisierung = self.get_file_quantisierung('bit_size_norm_db_ids.xlsx', audiofile)
        #print('DEBUG AMO Konf')
        #print('Audioraumdarstellung:', audioraumdarstellung)
        #quantisierung = self.get_file_quantisierung('bit_size_norm_db_ids.xlsx', audiofile)
                                                    
        #datenrate = self.get_datenrate('datenrate_norm_db_ids.xlsx', audiofile)
        #dateiformat = self.get_file_format(audiofile)[0]#return(file_extension, file_format)
        #datenrate = self.get_datenrate('datenrate_norm_db_ids.xlsx', audiofile)
        #dateiformat = self.get_file_format(audiofile)[0]#return(file_extension, file_format)
        if dauer_uebernehmen == True:
            dauer = {
                    'hour': file_length[0],
                    'millis': 0,
                    'minute': file_length[1],
                    'second': file_length[2]
                            }
        else:
            dauer = None
        
        amo_with_konf = {
        'erfassungDatum': {
            'day': datetime.today().strftime('%d'),
            'month': datetime.today().strftime('%m'),
            'year': datetime.today().strftime('%Y')
        },
        'erfassungDokumentar': {
            'kurzName': 'DRA-Skript',
            'langName': 'DRA-Skript'
        },
        
        #Gesamtkonfektionierung Start
        'gesamtkonfektionierung': {
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

                        'audioKreationRef': AK_Ref,

                        'booklet': False,
                        'codierung': {
                        'byteDarstellung': None,
                        'datenrate': None,#datenrate,
                        'datenrate': None,#datenrate,
                        'datenreduktion': None,
                        'kanalzahl': None,
                        'leseAbspielgeschwindigkeit': leseabspielgeschwindigkeit,

                        'audioRaumdarstellung': audioraumdarstellung,      

                        'quantisierung': None,#quantisierung,
                        'quantisierung': None,#quantisierung,
                        'rauschunterdrueckung': None,
                        'samplingrate': None,#sampling_rate
                        'samplingrate': None,#sampling_rate
                        
                    },

                        'gesamtAbschnitt': {
                            'bisLokalisierung': None,
                            'dauer': dauer,
                            'ende': None,
                            'name': None,
                            'start': None,
                            'vonLokalisierung': None
                        },

                        'textbeilage': False,
                    },
    
        #Gesamtkonfektionierung Ende
        'label': {
                    'bemerkung': None,
                    'gvl': False,
                    'labelcode': 'X150',
                    'name': 'DRA Babelsberg',
                    'normId': 'http://hfdb.ard.de/normdb/Label?id=1360',
                    'verwendungsbeschraenkung': None,
                    'onlineRecht': None
                },
        'medium': {
                    'abmessung':None,
                    'dateiformat': None,#dateiformat,
                    'dateiformat': None,#dateiformat,
                    'fabrikat': None,
                    'formatversion': None,
                    'mimeType': None,
                    'suffix': None,
                    'traegersystem': {
                    'kurzbezeichnung': 'BAND',
                    'langbezeichnung': 'Band',
                    'normId': 'http://hfdb.ard.de/normdb/Wert?id=232'
                }
                },
        'promotion': False,
        'veroeffentlichungsfirma': {
                    'name': 'Deutsches Rundfunkarchiv',
                    'namenszusatz': None,
                    'normIdInstitution': None,
                    'normIdName': None,
                    'gvl': None
                },
        'veroeffentlichungslabel': 'DRA Babelsberg',
        'wiedergabedauer': {
                    'hour': file_length[0],
                    'millis': -1,
                    'minute': file_length[1],
                    'second': file_length[2]
             
        }}
        print(amo_with_konf)
        #Da audioraumdarstellung nicht übernommen wird aus unbekanntem Grund, wird sie hier noch mal extra hinzugefügt
        print('Start Audioraumdarstellung ergänzen')
        amo_id = self.hfdb_client.service.insertAMO(amo_with_konf)
        amo = self.hfdb_client.service.getAMO(amo_id)
        gesamtkonf = amo.gesamtkonfektionierungRef
        konf = self.hfdb_client.service.getKonf(gesamtkonf)
        konf.audioRaumdarstellung = audioraumdarstellung
        print(konf.audioRaumdarstellung)
        self.hfdb_client.service.updateKonf(konf)

        return(amo_id, gesamtkonf)
    
    def create_einzelkonf(self, AK_Ref, audiofile, audioraum_single, lese_abspielgeschwindigkeit_single, refAMO):
        """Creates an AMO with Gesamtkonfektionierung based on Input-Data from measuring file
        
        Args:
            AK_Ref (str): ID of reference AK, that the AMO and Konf should be linked to. 
            audiofile (str): Path to audiofile, that is base for measurements
            audioraum_single (json_like): Whole audioraum entry prepared for hfdb-entry
            lese_abspielgeschwindigkeit_single (json_like): Single entry for lese und abspielgeschwindigkeit
            refAMO (varies): Could be full AMO Dataset or just AMO ID which depends on the kind of whole-data-structure (Geflechtstruktur) we are dealing with.

        Returns:
            konf_id(str): URI of new created Konfektionierung in HFDB.
        """
        file_length = self.get_file_length(audiofile)
        #sampling_rate = self.get_sampling_rate('sampling_rates_norm_db.xlsx', audiofile)
        audioraumdarstellung = audioraum_single #self.get_audioraumdarstellung(audiofile)
        leseabspielgeschwindigkeit = lese_abspielgeschwindigkeit_single
        #quantisierung = self.get_file_quantisierung('bit_size_norm_db_ids.xlsx', audiofile)
        #print('DEBUG AMO Konf')
        #print('Audioraumdarstellung:', audioraumdarstellung)
        #quantisierung = self.get_file_quantisierung('bit_size_norm_db_ids.xlsx', audiofile)
                                                    
        #datenrate = self.get_datenrate('datenrate_norm_db_ids.xlsx', audiofile)
        #dateiformat = self.get_file_format(audiofile)[0]#return(file_extension, file_format)
        #datenrate = self.get_datenrate('datenrate_norm_db_ids.xlsx', audiofile)
        #dateiformat = self.get_file_format(audiofile)[0]#return(file_extension, file_format)
        
        konf_new = {
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

                        'audioKreationRef': AK_Ref,

                        'booklet': False,
                        'codierung': {
                        'byteDarstellung': None,
                        'datenrate': None,#datenrate,
                    
                        'datenreduktion': None,
                        'kanalzahl': None,
                        'leseAbspielgeschwindigkeit': leseabspielgeschwindigkeit,

                        'audioRaumdarstellung': audioraumdarstellung,      

                        'quantisierung': None,#quantisierung,
                      
                        'rauschunterdrueckung': None,
                        'samplingrate': None,#sampling_rate
                       
                        
                    },

                        'gesamtAbschnitt': {
                            'bisLokalisierung': None,
                            'dauer': {
                                'hour': file_length[0],
                                'millis': 0,
                                'minute': file_length[1],
                                'second': file_length[2]
                            },
                            'ende': None,
                            'name': None,
                            'start': None,
                            'vonLokalisierung': None
                        },

                        'textbeilage': False,
                    }
        
        #Da Daten zum AMO unterschiedlich übergeben werden je nach Geflechtstruktur, hier einmal gucken, ob AMO-ID übergeben wurde oder komplettes AMO!
        if type(refAMO) == str:
            amo_ref_id = refAMO
        else:
            amo_ref_id = refAMO.hfdbId

        konf_id = self.hfdb_client.service.insertKonf(konf_new, amo_ref_id)
        #Da audioraumdarstellung nicht übernommen wird aus unbekanntem Grund, wird sie hier noch mal extra hinzugefügt
        print('Start Audioraumdarstellung ergänzen')
        konf = self.hfdb_client.service.getKonf(konf_id)
        konf.audioRaumdarstellung = audioraumdarstellung
        print(konf.audioRaumdarstellung)
        self.hfdb_client.service.updateKonf(konf)

        return(konf_id)
    
    def create_einzelkonf_v3(self, AK_Ref, audiofile, audioraum_single, lese_abspielgeschwindigkeit_single, refAMO): #Version für Geflecht-Fall3
        """Creates an AMO with Gesamtkonfektionierung based on Input-Data from measuring file
        
        Args:
            AK_Ref (str): ID of reference AK, that the AMO and Konf should be linked to. 
            audiofile (str): Path to audiofile, that is base for measurements
            audioraum_single (json_like): Whole audioraum entry prepared for hfdb-entry
            lese_abspielgeschwindigkeit_single (json_like): Single entry for lese und abspielgeschwindigkeit
            refAMO (varies): Could be full AMO Dataset or just AMO ID which depends on the kind of whole-data-structure (Geflechtstruktur) we are dealing with.

        Returns:
            konf_id(str): URI of new created Konfektionierung in HFDB.
        """
        file_length = self.get_file_length(audiofile)
        #sampling_rate = self.get_sampling_rate('sampling_rates_norm_db.xlsx', audiofile)
        audioraumdarstellung = audioraum_single #self.get_audioraumdarstellung(audiofile)
        leseabspielgeschwindigkeit = lese_abspielgeschwindigkeit_single
        #quantisierung = self.get_file_quantisierung('bit_size_norm_db_ids.xlsx', audiofile)
        #print('DEBUG AMO Konf')
        #print('Audioraumdarstellung:', audioraumdarstellung)
        #quantisierung = self.get_file_quantisierung('bit_size_norm_db_ids.xlsx', audiofile)
                                                    
        #datenrate = self.get_datenrate('datenrate_norm_db_ids.xlsx', audiofile)
        #dateiformat = self.get_file_format(audiofile)[0]#return(file_extension, file_format)
        #datenrate = self.get_datenrate('datenrate_norm_db_ids.xlsx', audiofile)
        #dateiformat = self.get_file_format(audiofile)[0]#return(file_extension, file_format)
        
        konf_new = {
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

                        'audioKreation': AK_Ref,

                        'booklet': False,
                        'codierung': {
                        'byteDarstellung': None,
                        'datenrate': None,#datenrate,
                    
                        'datenreduktion': None,
                        'kanalzahl': None,
                        'leseAbspielgeschwindigkeit': leseabspielgeschwindigkeit,

                        'audioRaumdarstellung': audioraumdarstellung,      

                        'quantisierung': None,#quantisierung,
                      
                        'rauschunterdrueckung': None,
                        'samplingrate': None,#sampling_rate
                       
                        
                    },

                        'gesamtAbschnitt': {
                            'bisLokalisierung': None,
                            'dauer': {
                                'hour': file_length[0],
                                'millis': 0,
                                'minute': file_length[1],
                                'second': file_length[2]
                            },
                            'ende': None,
                            'name': None,
                            'start': None,
                            'vonLokalisierung': None
                        },

                        'textbeilage': False,
                    }
        
        #Da Daten zum AMO unterschiedlich übergeben werden je nach Geflechtstruktur, hier einmal gucken, ob AMO-ID übergeben wurde oder komplettes AMO!
        if type(refAMO) == str:
            amo_ref_id = refAMO
        else:
            amo_ref_id = refAMO.hfdbId

        konf_id = self.hfdb_client.service.insertKonf(konf_new, amo_ref_id)
        #Da audioraumdarstellung nicht übernommen wird aus unbekanntem Grund, wird sie hier noch mal extra hinzugefügt
        print('Start Audioraumdarstellung ergänzen')
        konf = self.hfdb_client.service.getKonf(konf_id)
        konf.audioRaumdarstellung = audioraumdarstellung
        print(konf.audioRaumdarstellung)
        self.hfdb_client.service.updateKonf(konf)

        return(konf_id)        
    def create_amos_konfs_for_ak(self, structure_status, audiofile, ak_ref, konf_audioraum, lese_abspiel_input, konf_komp_audioraum, lese_abspielgeschwindigkeit_komp, ak_komp_id, refAMO = None):
        """Function that brings together Measurements with existing aks to create konfs and amos
        
        Args:
            structure_status(str): Status which kind of structure the user choose for integrating this dataset.
            audiofile(str): Path to source audiofile
            ak_ref(str): URI of AK belonging to this dataset
            konf_audioraum(str): Vorgabe for Audioraumdarstellung based on Measurement and User Interface correction.
            lese_abspiel_input(str): Input to "Lese- und Abspielgeschwindigkeit"
            konf_komp_audioraum
            lese_abspielgeschwindigkeit_komp
            ak_komp_id
            refAMO = None

        Returns:
            amo_single(str): ID of created AMO
            konf(str): ID of created Konf
            ak_korpus(str): ID of korpus AK, that could have been created already before this function and just passed through or could have been created within this function as part of the Konf
        """
        ak_korpus = ak_ref
        #try:
            #urheber = ak_korpus.urheber
            #print('DEBUG URHEBER KOMPILATION')
            #print(urheber)
        #except AttributeError:
           # pass
        if structure_status == 'new_komp_no_ki':
             audio_raum_output_komp = self.get_audioraumdarstellung('Excel_Lists_entities\\audioraumdarstellung_norm_ids.xlsx', konf_komp_audioraum)
             lese_abspielgeschwindigkeit_output_komp = self.get_lese_abspielgeschwindigkeit('lesegeschwindigkeit_norm_db_ids.xlsx', lese_abspielgeschwindigkeit_komp)

             audio_raum_output_korpus = self.get_audioraumdarstellung('Excel_Lists_entities\\audioraumdarstellung_norm_ids.xlsx', konf_audioraum)
             lese_abspielgeschwindigkeit_output_korpus = self.get_lese_abspielgeschwindigkeit('Excel_Lists_entities\\lesegeschwindigkeit_norm_db_ids.xlsx', lese_abspiel_input)


        audioraum = konf_audioraum
        lese_abspielgeschwindigkeit = lese_abspiel_input
        ak = ak_ref
        #try:
           # urheber = ak.urheber
           # print('DEBUG URHEBER KOMPILATION2')
           # print(urheber)
        #except AttributeError:
            #pass
        
        self.source_audio_files_ordner        
        
        
        audiofile_fullpath = f'{self.source_audio_files_ordner}//{audiofile}'
        
        #print('AK Nummer', i)
        #print('Audioraum:', audioraum)
        audioraum_vorlage = audioraum
        audio_raum_output = self.get_audioraumdarstellung('Excel_Lists_entities\\audioraumdarstellung_norm_ids.xlsx', audioraum_vorlage)
        lese_abspielgeschwindigkeit_vorlage = lese_abspielgeschwindigkeit
        lese_abspielgeschwindigkeit_output = self.get_lese_abspielgeschwindigkeit('Excel_Lists_entities\\lesegeschwindigkeit_norm_db_ids.xlsx', lese_abspielgeschwindigkeit_vorlage)
            #print(audio_raum_output)
            #print('AMO Damage Control')
            #print('AK-List:', ak_list[i])
            #print('Audiofiles List Fullpath', audiofiles_list_fullpath[i])
            #print('audio_raum_output:', audio_raum_output)
        if structure_status == 'new_korpus' or structure_status == 'new_komp': #v1 #v2
            amo_single, konf = self.create_amo_gesamtkonf(ak, audiofile_fullpath, audio_raum_output, lese_abspielgeschwindigkeit_output, True)

        if structure_status == 'add_to_vorhandene_komp': #v4
            konf = self.create_einzelkonf_v3(ak, audiofile, audio_raum_output, lese_abspielgeschwindigkeit_output, refAMO)
            amo_single = None
            konf_all = self.hfdb_client.service.getKonf(konf)
            ak_korpus = konf_all.audioKreationRef

            #Urheber nachträglich noch wieder  hinzufügen
            #ak_new = self.hfdb_client.service.getAK(ak_korpus)
            #ak_new.urheber = urheber
            #ak_new.hfdbId = ak_new.hfdbId.split('&version=')[0]
            #self.hfdb_client.service.updateAK(ak_new)


        if structure_status == 'new_komp_no_ki': #V3

            amo_komp, konf_komp = self.create_amo_gesamtkonf(ak_komp_id, audiofile_fullpath, audio_raum_output_komp, lese_abspielgeschwindigkeit_output_komp, False)

            #Konf-Korpus und damit auch gleich AK Korpus erstellen
            konf_korpus = self.create_einzelkonf_v3(ak, audiofile_fullpath, audio_raum_output_korpus, lese_abspielgeschwindigkeit_output_korpus, amo_komp)
         
            amo_single = amo_komp
            konf = konf_korpus
            #Wir müssen in diesem Fall noch die AK_ID raus bekommen der Einzel-Korpus-AK, da diese erst hier mit der Einzelkonfektionierung angelegt wurde, diese übergeben wir mit als Return
            ak_komp_fertig = self.hfdb_client.service.getAK(ak_komp_id)
            ak_korpus = ak_komp_fertig.subKreationRef[0]

            #Urheber nachträglich noch wieder  hinzufügen
            #ak_new = self.hfdb_client.service.getAK(ak_korpus)
            #ak_new.urheber = urheber
            #ak_new.hfdbId = ak_new.hfdbId.split('&version=')[0]
            #self.hfdb_client.service.updateAK(ak_new)

        return(amo_single, konf, ak_korpus)