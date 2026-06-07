# Google Cloud Storage (GCS) — Configuration & Troubleshooting

This project uploads files to Google Cloud Storage using the `google-cloud-storage` Python client.

## How authentication works
- The client looks for credentials in this order (common patterns):
  1. Explicit credentials passed when creating the client (service account JSON).
 2. Application Default Credentials (ADC), e.g. from `gcloud auth application-default login` or running on GCP with a service account.

In this repo we support an explicit credential file via the `GCS_CREDENTIALS_FILE` environment variable (added to `app/core/config.py`). If set, the app will load the service account JSON from that path.

## Recommended setup (server/runtime)
1. Create a service account in Google Cloud with `Storage Object Admin` (or more restrictive) permissions for the target bucket.
2. Create and download a JSON key for that service account.
3. Place the JSON file on the server and set the path in your `.env` (or environment):

```
GCS_CREDENTIALS_FILE=/path/to/service-account.json
GCS_PROJECT_ID=your-gcp-project-id
GCS_BUCKET_NAME=your-bucket-name
```

4. Restart the application.

The app will then use the provided credentials to initialize the `google.cloud.storage.Client`.

## Quick local developer option (ADC)
If you prefer ADC for development, run:

```bash
gcloud auth application-default login
```

This stores credentials that the `google-cloud-storage` library can use.

## Common error: `invalid_grant: Bad Request`
This is returned by Google's OAuth endpoint and commonly means one of:

- The credentials are invalid or revoked (wrong JSON file, removed service account, or revoked key).
- The system clock is significantly skewed from real time (must be within a few minutes).
- Using ADC and the refresh token expired or is invalid.

How to fix:
- Verify the JSON key file is valid and the `GCS_CREDENTIALS_FILE` path points to it.
- Ensure the service account still exists and has access to the bucket.
- Check server time and sync with NTP if needed.
- If using ADC, re-run `gcloud auth application-default login` to refresh credentials.

## App changes we made
- The `StorageService` now supports an explicit credentials file via `GCS_CREDENTIALS_FILE` and logs clearer errors when initialization or uploads fail. See `app/services/storage_service.py`.
- The upload endpoint now returns a `502` with a clearer message when storage operations fail.

## Debugging steps
1. Verify `.env` values for `GCS_PROJECT_ID` and `GCS_BUCKET_NAME`.
2. If using a JSON key, confirm the file exists and is readable by the app process.
3. Tail app logs during an upload to see the detailed error returned and adjust accordingly.
