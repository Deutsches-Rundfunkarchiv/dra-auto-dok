#Class for Working with Google Gemini 1.5 and multimodal Files. Upload Audios, Videos or Photos or PDF Files.... and ask questions about them directly

#Note: Service-Account at Google Cloud needed. Must be created in Google Cloud Console online. Service-Account Credentials json must be saved locally from Google Cloud Console.

# Umgebungsvariable "GOOGLE_APPLICATION_CREDENTIALS" muss angelegt werden und auf Pfad der json-Datei zeigen.

#Media Files to be processed with Gemini must be uploaded to Google Cloud first, see def for that below

#Media Files stored have permanent costs, so please use delete function of this class too, after file is processed.

from google.cloud import storage
import vertexai
import vertexai.preview.generative_models as generative_models
from vertexai.generative_models import GenerativeModel, Part
import pandas
import time
from config import Google_API_ID

class work_with_gemini():

    def __init__(self, project_id = Google_API_ID):

        """
        Args:
            project_id (str): Project-ID of Google Project, defaults to config entry
        """
        self.authenticate_implicit_with_adc(project_id)
        self.project_id = project_id

    def authenticate_implicit_with_adc(self, project_id):
        """
        When interacting with Google Cloud Client libraries, the library can auto-detect the
        credentials to use.

        // TODO(Developer):
        //  1. Before running this sample,
        //  set up ADC as described in https://cloud.google.com/docs/authentication/external/set-up-adc
        //  2. Replace the project variable.
        //  3. Make sure that the user account or service account that you are using
        //  has the required permissions. For this sample, you must have "storage.buckets.list".
        Args:
            project_id: The project id of your Google Cloud project.
        """

        # This snippet demonstrates how to list buckets.
        # *NOTE*: Replace the client created below with the client required for your application.
        # Note that the credentials are not specified when constructing the client.
        # Hence, the client library will look for credentials using ADC.
        storage_client = storage.Client(project=project_id)
        buckets = storage_client.list_buckets()
        print("Buckets:")
        for bucket in buckets:
            print(bucket.name)
        print("Listed all storage buckets.")

    def upload_file_to_google_cloud(self, bucket_name, blob_name, path_to_file):
        """Uploads file to certain Google Cloud bucket
        Args:
            bucket_name(str): Name of the Google Cloud Storage Bucket, that file should be stored in, must be part of project defined.
            blob_name(str): Name File should have in Google Cloud Storage Bucket
            path_to_file(str): Filepath of local file, that should be uploaded to Google Cloud Bucket

        Returns:
            gs_url(str): Google Cloud URL like it can be processed by Gemini as media input.

        
        """
        # The ID of your GCS bucket
        # bucket_name = "your-bucket-name"

        # The ID of your new GCS object
        # blob_name = "storage-object-name"

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Mode can be specified as wb/rb for bytes mode.
        # See: https://docs.python.org/3/library/io.html
        blob.upload_from_filename(path_to_file)
        url = blob.public_url
        gs_url = f'gs://{url.split('/', 3)[3]}'

        return gs_url, url
    
    def upload_file_to_google_cloud_public(self, bucket_name, blob_name, path_to_file):
        """Uploads file to certain Google Cloud bucket and makes public available link (for mining platform etc.)
        Args:
            bucket_name(str): Name of the Google Cloud Storage Bucket, that file should be stored in, must be part of project defined.
            blob_name(str): Name File should have in Google Cloud Storage Bucket
            path_to_file(str): Filepath of local file, that should be uploaded to Google Cloud Bucket

        Returns:
            gs_url(str): Google Cloud URL like it can be processed by Gemini as media input.

        
        """
        # The ID of your GCS bucket
        # bucket_name = "your-bucket-name"

        # The ID of your new GCS object
        # blob_name = "storage-object-name"

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Mode can be specified as wb/rb for bytes mode.
        # See: https://docs.python.org/3/library/io.html
        blob.upload_from_filename(path_to_file)
        blob.make_public() #Makes blob publicly available
        url = blob.public_url
        gs_url = f'gs://{url.split('/', 3)[3]}'

        return gs_url, url
    
    def make_prompt_with_media(self, audiofile_gcloud_path, prompt, type = 'audio', file_format = 'wav', location = "europe-west4", model_name="gemini-1.5-pro-preview-0409", max_output_tokens = 8192, temperature = 0):

        """Makes Prompts with Prompt Text and Media for example to Ask questions about an audio. Media must be stored in Google Cloud Bucket
        
        Args:
            audiofile_gcloud_path(str): Google Cloud Path of Media File that should be part of prompt
            prompt(str): Text prompt, for example Question about media file
            type(str): File type, can be "video", audio, etc. - defaults to "audio"
            file_format(str): File format of file, like wav, mpeg etc. - defaults to "wav"
            location(str): Google Cloud Region Name of Cloud Region where Gemini should run, defaults to "europe-west4" (Holland)
            model_name(str): Official Model Name of Gemini Model we want to use, defaults to gemini-1.5-pro-preview-0409

        Returns:
            response_text(str): Text response of Gemini Model to prompt sent.
            
            """

        vertexai.init(project=self.project_id, location=location)

        model = GenerativeModel(model_name= model_name)

        prompt = prompt

        audio_file_uri = audiofile_gcloud_path
        audio_file = Part.from_uri(audio_file_uri, mime_type=f"{type}/{file_format}")

        contents = [audio_file, prompt]
        got_response = False
        while got_response == False:
            try:
                responses = model.generate_content(contents, 
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
                    stream=True,)
                responses_all = []
                for response in responses:
                    responses_all.append(response.text)
                    got_response = True
            except Exception as e: 
                print(e, '2')
                time.sleep(60)
                
        joiner = ''
        responses_all = joiner.join(responses_all)
        return(responses_all)
    
    def delete_file_from_google_cloud(self, bucket_name, blob_name):
        """Deletes File from Google Bucket
        Args:
            bucket_name(str): Plain Name of Google Storage Bucket, z.B. 'gemini_audio_processings'
            blob_name(str): Name of File that was given when it was uploaded as blob-name, z.B. 'zeitfunk_92_whole' - Name of File in Gooogle Storage Bucket without file ending.

        Returns:
            blob_name(str): Name of File that was deleted.
        
        """
        # The ID of your GCS bucket
        # bucket_name = "your-bucket-name"

        # The ID of your new GCS object
        # blob_name = "storage-object-name"

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Mode can be specified as wb/rb for bytes mode.
        # See: https://docs.python.org/3/library/io.html
        blob.delete()

        return f'{blob_name} deleted'
    
    def ask_for_gattung(self, cloud_path_file, gattungen_list):
        """
        Defines Gattungen from Audiofile
        Args:
            cloud_path_file(str): Path in Google Cloud in gs:// format for file that should be processed
            gattungen_list(list): List of possible Gattungen the algorithm chooses from based on YAMnet-Analysis

        Returns:
            response_geordnet(list): Pre-Formatted response from LLM as a list of Gattungen.
        """
    	#Get list of Gattungen from excel list
        df = pandas.read_excel('Excel_Lists_entities\\gattungen_names.xlsx')
        list_gattungen = df['Gattungen_Liste']
        joiner = ', '
        list_gattungen_string = joiner.join(list_gattungen)
        prompt1 = f'Welcher Gattung gehört dieses Audio an? Wähle aus folgenden Möglichkeiten: {list_gattungen_string} - Mehrere Gattungen sind möglich. Nenne in Stichpunkten im Format "Gattung des Audios: Gattung, Gattung, Gattung etc."'

        response = self.make_prompt_with_media(cloud_path_file, prompt1, type = 'audio', file_format = 'wav', location = "europe-west4", model_name="gemini-1.5-flash-001")
        print(response)
        response_geordnet = response.replace('Gattung des Audios: ', '')
        response_geordnet = response.replace('\n', '')
        if ',' in response_geordnet:
            response_geordnet = response.split(", ")
        else:
            response_geordnet = [response_geordnet]

        for i in range(len(response_geordnet)): #if LLM answer is not exactly in Gattungen List, get close match from list
            if response_geordnet[i] not in list_gattungen:
                for j in range(len(list_gattungen)):
                    if list_gattungen[j] in response_geordnet[i]:
                        response_geordnet[i] = list_gattungen[j]
            if ":" in response_geordnet[i]:
                response_geordnet[i] = response_geordnet[i].split(':')[1]


        return(response_geordnet)
    
    def get_info_from_audios(self, bucket_name, audiofiles, path_audiofiles, gattungen_list):
        """Gets infos from speech only audiofiles before they are directly  erased from Google cloud to avoid costs there.
        
        Args:
            bucket_name(str): Name of bucket where audiofiles ares stored on google cloud temporarily
            audiofiles(list): List of auciofiles given to us,
            path_audiofiles(str): Path to temporary storage of                                                                 
            gattungen_list(list): List of possible Gattungen that could occur.
        
        """

        all_infos = []

        gattung_lists = []
        for f in range(len(audiofiles)):
            cloud_path = self.upload_file_to_google_cloud(bucket_name, f'file{f}', f'{path_audiofiles}\\{audiofiles[f]}')
            
            gattung_list = self.ask_for_gattung(cloud_path[0], gattungen_list)
            gattung_lists.append(gattung_list)

            self.delete_file_from_google_cloud(bucket_name, f'file{f}')

        all_infos.append(gattung_lists)

        return(all_infos)

        
