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
		
	def filter_builds_for_platform(self, build):
		computedMinMacOsVersion = build['attributes']['computedMinMacOsVersion']
		minOsVersion = build['attributes']['minOsVersion']
		computedMinVisionOsVersion = build['attributes']['computedMinVisionOsVersion']
		# print(f"computedMinMacOsVersion: {computedMinMacOsVersion}")
		# print(f"minOsVersion: {minOsVersion}")
		# print(f"computedMinVisionOsVersion: {computedMinVisionOsVersion}")
		if self.platform == 'visionos' and computedMinVisionOsVersion == None:
			return True
		if self.platform == 'ios' and computedMinVisionOsVersion != None:
			return True

		return False
		
	def uploadNotes(self, app_id, token, whats_new, build_number, platform):		
		# Create Header
		HEAD = {
		   'Authorization': 'Bearer ' + token
		}
		
		# URLS
		BASE_URL = 'https://api.appstoreconnect.apple.com/v1/'
		
		# Find builds
		versionId = ""
		versionIdCounter = 0
		while versionId == "" and versionIdCounter < 100:
		
			print("---Finding Build---")
			URL = BASE_URL + 'builds?filter[app]=' + app_id + '&filter[version]=' + build_number
			r = requests.get(URL, params={}, headers=HEAD)
			try:
				
				data = r.json()['data']
				data = list(filter(self.filter_builds_for_platform, data))
				
				if len(data) > 0:
					versionId = data[0]['id']
					print(f"found versionId: {versionId}")
					
			except Exception as e:
				print(f"Error: {e}")
				time.sleep(60) #wait for 60 seconds
				
			versionIdCounter += 1
		
		# Find localizations
		localizationId = ""
		localizationIdCounter = 0
		while localizationId == "" and localizationIdCounter < 100:
		
			print("---Finding Localizations---")
			URL = BASE_URL + 'builds/' + versionId + '/betaBuildLocalizations'
			r = requests.get(URL, params={}, headers=HEAD)
			try:
				localizationId = r.json()['data'][0]['id']
			except Exception as e:
				print(f"Error: {e}")
				time.sleep(60) #wait for 60 seconds
				
			localizationIdCounter += 1
		
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
	
	platform = os.getenv('PLATFORM', 'ios')
	
	print(f"Starting for build: {build_number}")

	service = UploadTestFlightReleaseNotes()
	service.platform = platform
	token = service.generateToken(issuer_id, key_id, private_key)
	reason = service.uploadNotes(app_id, token, whats_new, build_number, platform)
	
	print(reason)

if __name__ == "__main__":
	main()
