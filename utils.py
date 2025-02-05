import ui_tools as ui
import urllib3
from zeep.transports import Transport
from zeep import Client
from requests.auth import HTTPBasicAuth
from requests import Session

def call_hfdb(wsdl_path1 = None, wsdl_path2 = None):
    """Handler for Calls to HFDB-API, can call both HFDB1 (Prod) and HFDB2 (Kons)
    
    Args:
        wsdl_path1(str): Path to WSDL for HFDB Prod. Defaults to None if WSDL can be downloaded from Standard Path
        wsdl_path2(str): Path to WSDL for HFDB Kons. Defaults to None if WSDL can be downloaded from Standard Path

    Returns:
        client(HFDB-Instance): Wrapper for HFDB-API Calls and HFDB-API functionality
        instance(str): Defines which HFDB instance is called.
    
    """
    credentials = None
    authenticated = False
    while authenticated == False:
        try:
            credentials = ui.authenticate('An HFDB authentifizieren')
            instanz = credentials['drahfdb2']
            if instanz == True:
                instance = 'drahfdb2'
            else: 
                instance = 'drahfdb1'
            instance = instance
            username = credentials['username']
            password = credentials['password']
            
            # use drahfdb1 for prod, drahfdb2 for kons, drahfdbfor test
            if instance == 'drahfdb1':
                wsdl = wsdl_path1
                password = password
            else:
                wsdl = wsdl_path2
                password = password
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            session = Session()
            session.auth = HTTPBasicAuth(username, password)
            session.trust_env = False
            session.verify = False
            transport = Transport(session=session)
            client = Client(wsdl=wsdl, transport=transport)
            client.service.getAK(f'http://hfdb.ard.de/{instance}/AudioKreation?id=4954916')
            authenticated = True
            
        except:
            if credentials == 'Exit':
                break
            else:
                ui.information_window('Noch mal versuchen?', 'Authentifizierung fehlgeschlagen!')
    return(client, instance)

def split_name(full_name):
    """
    Teilt einen Namensstring in Vor- und Nachnamen auf.

    Args:
        full_name (str): Der vollständige Name als String.

    Returns:
        tuple: Ein Tupel bestehend aus Vorname und Nachname.
    """
    if full_name != 'N.N.':
        name_parts = full_name.split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:])
        else:
            first_name = full_name
            last_name = ''
    else:
        first_name = ''
        last_name = 'N.N.'
    
    return first_name, last_name

