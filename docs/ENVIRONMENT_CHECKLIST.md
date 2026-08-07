# Production Environment Variable Checklist

| Environment Variable | Required Mode | Production Value / Constraints | Verified |
| :--- | :---: | :--- | :---: |
| `ENVIRONMENT` | Production | `production` | [x] |
| `LOG_LEVEL` | Production | `INFO` | [x] |
| `DATABASE_URL` | Production | `postgresql+asyncpg://...` (No SQLite) | [x] |
| `REDIS_URL` | Production | `redis://redis:6379/0` | [x] |
| `SECRET_KEY` | Production | 64+ char random hex key (No defaults) | [x] |
| `GEMINI_API_KEY` | Production | Valid Google AI Gemini API Key | [x] |
| `CORS_ORIGINS` | Production | `["https://app.aivisibility.com"]` | [x] |
| `VITE_API_BASE_URL`| Frontend | `https://api.aivisibility.com/api/v1` | [x] |
