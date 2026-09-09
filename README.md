# Flask and MongoDB Atlas application

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. In MongoDB Atlas, create a database user, allow the client IP address, and copy the connection string. Create a file named `.env` in the project folder with:

```text
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=flask_app
MONGO_COLLECTION_NAME=submissions
```

Use `.env.example` as a template. Do not commit `.env` because it contains database credentials.

4. Start or restart the application:

```powershell
python app.py
```

Open http://127.0.0.1:5000/ for the form. The JSON API is available at http://127.0.0.1:5000/api.

## Behavior

- `GET /api` reads and returns the list in `data.json`.
- `POST /submit` validates the form and inserts the submission into MongoDB Atlas.
- Successful submissions redirect to `/success`.
- Missing fields, missing MongoDB configuration, and database failures render an error on the form page.
