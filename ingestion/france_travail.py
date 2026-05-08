import requests 
import os
from dotenv import load_dotenv
import psycopg2
import json
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

def store_offres(offres, conn):
	cursor = conn.cursor()
	for offre in offres["resultats"]:
		id = offre.get("id")
		intitule = offre.get("intitule")
		description = offre.get("description")
		date_creation = offre.get("dateCreation")
		lieu_libelle = offre.get("lieuTravail", {}).get("libelle")
		code_postal = offre.get("lieuTravail", {}).get("codePostal")
		entreprise_nom = offre.get("entreprise", {}).get("nom")
		type_contrat = offre.get("typeContrat")
		salaire_libelle = offre.get("salaire", {}).get("libelle")
		raw_json = json.dumps(offre)
		cursor.execute("""
			INSERT INTO offres (id, intitule, description, date_creation, lieu_libelle, code_postal, entreprise_nom, type_contrat, salaire_libelle, raw_json)
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			ON CONFLICT (id) DO NOTHING
		""", (id, intitule, description, date_creation, lieu_libelle, code_postal, entreprise_nom, type_contrat, salaire_libelle, raw_json))
	conn.commit()

if __name__ == "__main__":
	token = get_access_token()
	offres = fetch_offres(token)
	conn = psycopg2.connect(
		host=os.getenv("DB_HOST"),
		port=os.getenv("DB_PORT"),
		dbname=os.getenv("DB_NAME"),
		user=os.getenv("DB_USER"),
		password=os.getenv("DB_PASSWORD")
	)
	store_offres(offres, conn)
	print("offres stockées avec succès")
	conn.close()
	