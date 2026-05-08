print("hello")
import requests 
import os
from dotenv import load_dotenv
load_dotenv()
CLIENT_ID = os.getenv("FRANCE_TRAVAIL_CLIENT_ID")
CLIENT_SECRET= os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET")
def get_access_token():
	url = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
	params= {"realm" : "/partenaire"}
	data= { "grant_type": "client_credentials",
      		"client_id": CLIENT_ID,
      		"client_secret": CLIENT_SECRET,
      		"scope": "api_offresdemploiv2 o2dsoffre"}

	response = requests.post(url, params=params, data=data)
	return response.json()["access_token"]
def fetch_offres(token):
	url = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
	headers= { "Authorization" : "Bearer "+ token, 
	           "Accept" : "application/json"}
	params= {"motsCles": "data engineer",
		 "range": "0-49"}
	response = requests.get(url, headers=headers, params=params)
	return response.json()
if __name__ == "__main__":
	print("script lancé")
	token = get_access_token()
	print("token obtenu:" , token)
	offres = fetch_offres(token)
	print(offres)