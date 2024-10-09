#Insert configurations such as passwords and Credentials etc here
Google_API_ID = 
google_bucket_name =  #Bucket at Google Cloud for temporarly uploading Audiofiles for direct multimodal processing with Gemini

#Wort-Musik-Sendungs-Bestimmung - Threshholds
threshold_music = 
threshold_speech = 

#Sicherheitszertifikat für NDB, wird benötigt weil sonst Proxy dazwischen funkt
path_ndb_proxy_certificate = 

temp_ordner_default = "" #Default Path for saving Files temporarily - optional

wsdl_path1 =  #Path to WSDL-File for HFDB-Authentication HFDB-Prod
wsdl_path2 =  #Path to WSDL-File for HFDB-Authentication  HFDB-Kons

ref_ak_1 = #Vorhandenes AK Objekt, aus dem die Struktur bestimmter Objektteile als Muster herangezogen wird. Used for Urheber, Mitwirkende and Titel, so ref_ak should have good and clean entries in these data points.
ref_ak_2 = #Vorhandenes AK Objekt, aus dem die Struktur bestimmter Objektteile als Muster herangezogen wird. Used for Orte, Zusammenfassunge, Gattungen and general AK structure