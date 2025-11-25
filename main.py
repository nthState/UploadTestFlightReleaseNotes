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
		
	def uploadNotes(self, app_id, token, whats_new, build_number, platform, attempts):
		HEAD = {'Authorization': f'Bearer {token}'}
		BASE_URL = 'https://api.appstoreconnect.apple.com/v1/'
		
		# --- Find build ---
		versionId = None
		for attempt in range(attempts):
			print(f"---Finding Build (Attempt {attempt+1})---")
			URL = f"{BASE_URL}builds?filter[app]={app_id}&filter[version]={build_number}&filter[preReleaseVersion.platform]={platform}"
			r = requests.get(URL, headers=HEAD)
			
			if not r.ok:
				print(f"Error: {r.status_code} {r.reason}")
				if r.status_code == 404:
					break  # stop early on invalid request
				time.sleep(10)
				continue
			
			data = r.json().get('data', [])
			if data:
				versionId = data[0]['id']
				print(f"Found versionId: {versionId}")
				break
			
			print("Build not found yet, retrying...")
			time.sleep(10)
		
		if not versionId:
			raise RuntimeError("Failed to find versionId after 10 attempts.")
	
		# --- Find localizations ---
		localizationId = None
		for attempt in range(attempts):
			print(f"---Finding Localization (Attempt {attempt+1})---")
			URL = f"{BASE_URL}builds/{versionId}/betaBuildLocalizations"
			r = requests.get(URL, headers=HEAD)
			
			if not r.ok:
				print(f"Error: {r.status_code} {r.reason}")
				time.sleep(10)
				continue
			
			data = r.json().get('data', [])
			if data:
				localizationId = data[0]['id']
				print(f"Found localizationId: {localizationId}")
				break
			
			print("No localization found yet, retrying...")
			time.sleep(10)
		
		if not localizationId:
			raise RuntimeError("Failed to find localizationId after 10 attempts.")
	
		# --- Update What's New ---
		print("---Updating What's New---")
		URL = f"{BASE_URL}betaBuildLocalizations/{localizationId}"
		payload = {
			"data": {
				"id": localizationId,
				"type": "betaBuildLocalizations",
				"attributes": {"whatsNew": whats_new[:4000]},
			}
		}
		
		r = requests.patch(URL, json=payload, headers=HEAD)
		
		if not r.ok:
			raise RuntimeError(f"Failed to update What's New: {r.status_code} {r.text}")
		
		print("Successfully updated What's New.")
		return r.reason
	

def main():

	issuer_id = os.getenv('ISSUER_ID')
	key_id = os.getenv('KEY_ID')
	private_key = os.getenv('PRIVATE_KEY')
	
	app_id = os.getenv('APP_ID')
	whats_new = os.getenv('WHATS_NEW')
	build_number = os.getenv('BUILD_NUMBER')
	
	platform = os.getenv('PLATFORM', 'IOS')
	
	attempts = int(os.getenv('ATTEMPTS', '10'))
	
	print(f"Starting for build: {build_number}")

	service = UploadTestFlightReleaseNotes()
	token = service.generateToken(issuer_id, key_id, private_key)
	reason = service.uploadNotes(app_id, token, whats_new, build_number, platform, attempts)
	
	print(reason)

if __name__ == "__main__":
	main()
