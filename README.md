# 🐯 Detroit Tigers Dashboard

A live stats dashboard showing today's game score, AL Central standings,
and Tigers player stats — powered by the free MLB Stats API.

---

## Your File Structure

```
tigers-dashboard/
├── app.py              ← Python backend (the "server")
├── requirements.txt    ← List of Python packages needed
├── Procfile            ← Tells Render how to start the app
└── templates/
    └── index.html      ← The webpage your friends will see
```

---

## Step 1 — Run it on your computer first

### Install Python packages
Open your terminal and run:
```
pip install -r requirements.txt
```

### Start the server
```
python app.py
```

### Open the dashboard
Go to http://localhost:5000 in your browser. You should see the Tigers dashboard!

---

## Step 2 — Share it online with Render (free)

### 2a. Put your code on GitHub
1. Go to https://github.com and create a free account
2. Click "New repository", name it `tigers-dashboard`, make it Public
3. Upload all these files (drag and drop works on GitHub)

### 2b. Deploy on Render
1. Go to https://render.com and sign up (free)
2. Click "New +" → "Web Service"
3. Connect your GitHub account and select your `tigers-dashboard` repo
4. Fill in these settings:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Click "Create Web Service"

Render will give you a URL like `https://tigers-dashboard-xxxx.onrender.com`
Share that link with your friends! 🎉

---

## Understanding the code (beginner notes)

- `app.py` is a **Flask** app. Flask is a Python library that lets you
  build websites with Python. Each `@app.route(...)` is a "page" on your server.

- The MLB Stats API is **free and public** — no account needed. We just
  use Python's `requests` library to fetch data from it, the same way
  a browser fetches a webpage.

- `templates/index.html` is the webpage. It uses JavaScript's `fetch()`
  to call your Python server and display the data in a nice layout.

- `gunicorn` is a production-grade way to run Flask apps. Render uses
  it to host your app reliably.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: flask` | Run `pip install -r requirements.txt` |
| Page loads but shows errors | Make sure `python app.py` is running |
| Render deploy fails | Check that your Procfile says `web: gunicorn app:app` |
| Stats show "Could not load" | MLB API may be down briefly — try again in a minute |
