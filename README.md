# rogue_code_backend

## Python environment (required on Linux / PEP 668)

Use a **virtual environment** and install dependencies with the **same interpreter** you use for `manage.py runserver`:

```bash
cd rogue_code_backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python manage.py runserver
```

If Google sign-in reports missing packages, your server is not using the venv where `google-auth` was installed—activate `.venv` (or reinstall into that environment).

## Google sign-in

Needs `google-auth`, `PyJWT`, and `requests` (listed in `requirements.txt`). Configure OAuth client IDs in `.env` — see `../docs/GOOGLE_SIGNIN.md`.
