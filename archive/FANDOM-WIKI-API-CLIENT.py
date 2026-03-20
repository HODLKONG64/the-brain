import requests
from requests_oauthlib import OAuth1

class FandomWikiAPI:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.auth = OAuth1(consumer_key, consumer_secret, access_token, access_token_secret)
        self.base_url = 'https://gkniftyheads.fandom.com/api.php'

    def query(self, params):
        try:
            response = requests.get(self.base_url, params=params, auth=self.auth)
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'An error occurred: {err}')  

# Example usage (Replace these with real credentials):
# wiki_api = FandomWikiAPI('consumer_key', 'consumer_secret', 'access_token', 'access_token_secret')
# result = wiki_api.query({'action': 'query', 'format': 'json'})
# print(result)