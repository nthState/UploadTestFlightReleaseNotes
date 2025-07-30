import os
import jwt;
import datetime
import sys
import time
import requests
		
class UploadTestFlightReleaseNotes:

	def generateToken(self, issuer_id, key_id, private_key):
		
		current_time = datetime.datetime.now(datetime.timezone.utc)
		unix_timestamp = current_time.timestamp()
		
		exp = unix_timestamp_plus_5_min = unix_timestamp + (10 * 60)  # 10 min * 60 seconds (tokens over 20 minutes are not allowed)
		iss = unix_timestamp_plus_5_min = unix_timestamp + (-1 * 60)  # -1 min * 60 seconds
		
		data = {'aud': 'appstoreconnect-v1',
				'iss': issuer_id,
				'exp': exp,
				'iat': iss}
				
		headers = {'kid': key_id}
		
		encoded_token = jwt.encode(data, private_key, algorithm='ES256', headers=headers)
		
		return encoded_token
		
	def uploadNotes(self, app_id, token, whats_new, build_number):		
		# Create Header
		HEAD = {
		   'Authorization': 'Bearer ' + token
		}
		
		# URLS
		BASE_URL = 'https://api.appstoreconnect.apple.com/v1/'
		
		# Find builds
		versionId = ""
		while versionId == "":
		
			print("---Finding Build---")
			URL = BASE_URL + 'builds?filter[app]=' + app_id + '&filter[version]=' + build_number
			r = requests.get(URL, params={}, headers=HEAD)
			try:
				versionId = r.json()['data'][0]['id']
			except:
				time.sleep(60) #wait for 60 seconds
		
		# Find localizations
		localizationId = ""
		while localizationId == "":
		
			print("---Finding Localizations---")
			URL = BASE_URL + 'builds/' + versionId + '/betaBuildLocalizations'
			r = requests.get(URL, params={}, headers=HEAD)
			try:
				localizationId = r.json()['data'][0]['id']
			except:
				time.sleep(60) #wait for 60 seconds
		
		
		print("---Update What's New---")
		URL = BASE_URL + 'betaBuildLocalizations/' + localizationId
		data = {
			"data": {
				"id": localizationId,
				"type": "betaBuildLocalizations",
				"attributes": {
				"whatsNew": whats_new[:4000] #4000 char limit
				}
			}
		}
		result = requests.patch(URL, json=data, headers=HEAD)
		return result.reason
	

def main():

	issuer_id = os.getenv('ISSUER_ID')
	key_id = os.getenv('KEY_ID')
	private_key = os.getenv('PRIVATE_KEY')
	
	app_id = os.getenv('APP_ID')
	whats_new = os.getenv('WHATS_NEW')
	build_number = os.getenv('BUILD_NUMBER')

	service = UploadTestFlightReleaseNotes()
	token = service.generateToken(issuer_id, key_id, private_key)
	reason = service.uploadNotes(app_id, token, whats_new, build_number)
	
	print(reason)

if __name__ == "__main__":
	main()
