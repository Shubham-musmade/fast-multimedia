# Media Service (fast-multimedia)

Lightweight backend for uploading, listing and managing media assets.

**Quick start**

- Create a virtual environment and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Provide environment variables in a `.env` file at the project root (see section below).

- Run the app locally:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Environment variables**
The project uses `app/core/config.py` for settings. Required env vars:

- `DATABASE_URL` — asyncpg database URL
- `JWT_SECRET_KEY` — secret used to sign JWTs
- `GCS_BUCKET_NAME` — Google Cloud Storage bucket name

Optional / configurable defaults are defined in `app/core/config.py` such as `JWT_ALGORITHM`, `MAX_UPLOAD_SIZE_MB`, `DAILY_UPLOAD_LIMIT`, and allowed file types.

**Authentication**
Endpoints are protected using a JWT. The service accepts the token in either:

- Cookie: `access_token` (preferred)
- Authorization header: `Authorization: Bearer <token>`

See implementation at [app/core/security.py](app/core/security.py#L1-L40).

**Available HTTP endpoints**

- **GET /health**
  - Public health check
  - Response: `{"status":"healthy","service":"<PROJECT_NAME>"}`
  - See: [app/main.py](app/main.py#L1-L20)

- Base API prefix: `/api/v1` (from `API_V1_STR`) — routers are mounted under this prefix.

--- Media endpoints (mounted at `/api/v1/media`)

- **POST /api/v1/media/upload**
  - Description: Upload a single file.
  - Auth: required
  - Request: `multipart/form-data` with field `file` (type: file)
  - Response: `MediaAssetResponse` JSON with fields:
    - `id`, `uuid`, `filename`, `file_size`, `storage_path`, `created_at`
  - Example curl:

```bash
curl -X POST "http://localhost:8000/api/v1/media/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/file.mp4"
```

- **GET /api/v1/media/**
  - Description: List media assets for the current user
  - Auth: required
  - Query parameters:
    - `page` (int, default=1)
    - `size` (int, default=20, max=100)
    - `search` (string, optional)
    - `file_type` (string, optional)
  - Response: `MediaListResponse` JSON with `items`, `total`, `page`, `size`
  - Example:

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/media/?page=1&size=20"
```

- **GET /api/v1/media/{media_id}**
  - Description: Get a single media asset by id (belongs to current user)
  - Auth: required
  - Path parameter: `media_id` (int)
  - Response: `MediaAssetResponse` or 404 if not found

- **DELETE /api/v1/media/{media_id}**
  - Description: Delete a media asset (removes storage object and DB record)
  - Auth: required
  - Response: `{"status":"deleted"}` on success

See router definitions at [app/api/v1/media.py](app/api/v1/media.py#L1-L120) and response models at [app/schemas/media.py](app/schemas/media.py#L1-L120).

**Notes & next steps**
- The service expects JWTs issued by your auth system that contain `user_id` and `email` in the payload.
- Storage provider is implemented in `app/services/storage_service.py` (GCS by default). Configure GCS credentials and project if using cloud storage.

If you'd like, I can:
- add example Postman collection
- expand the README with deployed/CI instructions
- document the database schema and migrations
FAST API MULTIMEDIA PROJECT