import requests
import urllib3
import json
import pandas as pd

# Turn off the warnings about insecure connections
urllib3.disable_warnings()

# Define our own class that handles everything we need it to for get and post requests
class API(object):
   
    def __init__(self):
        # Use this to bypass proxy for internal server
        self.proxies = {'http': None, 'https': None}
        self.host = 'https://<splunk url>:8089'
        self.base = self.host.format(self.search_head)
        self.auth = None
        
    def authenticate(self, username, password):
        self.auth = (username, password)
    
    def _parse_results(self, response):
        try:
            results = json.loads(response.text)
        except json.decoder.JSONDecodeError:
            print(response.text)
            results = {}
        if 'entry' in results:
            df = pd.DataFrame(results['entry'])
        elif 'results' in results:
            df = pd.DataFrame(results['results'])
        elif 'sid' in results:
            df = results['sid']
        elif '_key' in results:
            df = results['_key']
        elif isinstance(results, list):
            try:
                df = pd.DataFrame(results)
            except:
                df = None
        else:
            print('No method for parsing these results:\n{}'.format(results))
            df = None
        return df
    
    def _request(self, method, endpoint, headers=None, data=None, retries=0):
        if self.auth is None:
            raise ValueError("Please provide authentication credentials before trying to interact with the API.")
        
        # Ensure there are not duplicate forward slashes in the end URL
        endpoint = endpoint.lstrip('/')
        url = '{}/{}'.format(self.base, endpoint)
        
        response = requests.request(url=url, 
                                    method=method, 
                                    proxies=self.proxies, 
                                    auth=self.auth, 
                                    verify=False,
                                    headers=headers,
                                    data=data)
        results = self._parse_results(response)          
        return results
    
    def get(self, endpoint, headers=None, data=None):
        return self._request('GET', endpoint, headers, data)
    
    def post(self, endpoint, headers=None, data=None):
        return self._request('POST', endpoint, headers, data)


def connect(cred_file):
    with open(cred_file, 'r') as f:
        creds = json.load(f)
    api = API()
    api.authenticate(creds['username'], creds['password'])
    return api
