# Upload TestFlight Release Notes

## About

This GitHub Action allows you to upload Release Notes to a particular build on TestFlight

Requires: python3

## Example

```yml
name: Example Workflow

on: [push]

jobs:
  example_job:
    runs-on: macos-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Upload Release Notes to TestFlight
        uses: nthState/UploadTestFlightReleaseNotes@v2.0.0
        with:
          ISSUER_ID: ${{ secrets.APPCONNECT_API_ISSUER }}
          KEY_ID: ${{ secrets.APPCONNECT_API_KEY_ID }}
          PRIVATE_KEY: ${{ secrets.APPCONNECT_API_KEY_PRIVATE }}
          APP_ID: id of the app
          WHATS_NEW: "detail item that has changed"
          BUILD_NUMBER: the build number you want to change

```

## Testing

```bash
export ISSUER_ID=appstore connect api issuer id
export KEY_ID=appstore connect api key id
export PRIVATE_KEY=appstore connect api private key
export APP_ID=app id
export WHATS_NEW="Your update text, max 4000 chars"
export BUILD_NUMBER= your build number
python3 ./main.py
```


### Build

Generating the requirements.txt

Create a virtual env

```bash
cd /tmp
mkdir api_venv 
cd api_venv/                                             
python3.10 -m venv venv
cd venv/bin
source activate
```

Then install the libraries
```bash
pip3 install cryptography                                
pip3 install requests
pip3 install pyjwt
```

Export the requirements
```bash
pip3 freeze > requirements.txt 
```