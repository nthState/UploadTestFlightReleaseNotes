# Upload TestFlight Release Notes

## About

This GitHub Action allows you to upload Release Notes to a particular build on TestFlight

## Example

```yml
name: Example Workflow

on: [push]

jobs:
  example_job:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Run custom action
        uses: nthState/UploadTestFlightReleaseNotes
        with:
          ISSUER_ID: ${{ secrets.APPCONNECT_API_ISSUER }}
          KEY_ID: ${{ secrets.APPCONNECT_API_KEY_ID }}
          AUTH_KEY: ${{ secrets.APPCONNECT_API_KEY_PRIVATE }}
          APP_ID: id of the app
          WHATS_NEW: "detail item that has changed"
          BUILD_NUMBER: the build number you want to change

```

## Testing

### Docker

```bash
docker build . -t githubactiontest -f Dockerfile
docker run -d githubactiontest
```