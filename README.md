# GradQuest

GradQuest is a premium, modern, dark-themed tech interview preparation platform designed to help students crack technical interviews. It displays custom resources, coding links, and question banks for top tech companies, along with an intuitive dynamic administration interface.

---

## 🚀 Key Features

- **Company Cards Grid:** Browse targeted interview coding rounds for top-tier companies. Each card showcases the company's logo, question counts, and a direct link to practice materials.
- **Dynamic Resources Redirection:** Provides a dynamic link redirection view (`/pyq/`) to point users to the **IEM Previous Year Questions** question bank.
- **Custom Admin Dashboard:** A fully tailored administrative panel restricted to staff/superusers to manage (Add, Edit, Delete) company resource cards on the fly.
- **Site Settings Manager:** An administrative widget inside the dashboard allows managers to instantly update the destination URL for the IEM Previous Year Questions redirection link.
- **Premium Aesthetics:** Sleek, glassmorphic dark-theme design matching professional standards, featuring:
  - Custom fluid layouts & transitions.
  - Floating auto-dismiss glassmorphic toasts.
  - Bespoke form controls, custom upload indicators, and custom checkboxes.

---

## 🛠️ Technology Stack

- **Backend Framework:** Django (Python)
- **Database:** SQLite
- **Frontend Core:** Vanilla HTML5, CSS3, ES6 JavaScript
- **Styling:** Custom Vanilla CSS variables and glassmorphic UI system (Cache-busting queries implemented for seamless stylesheets loading)

---

## 🔒 Administrative Credentials

Authenticated administrative dashboard actions require staff/superuser privileges. You can create a local superuser account by running:

```bash
python gradquest/manage.py createsuperuser
```

---

## ⚙️ Setup & Installation

Follow these steps to run the application locally:

### 1. Prerequisites
Ensure you have **Python 3.x** installed.

### 2. Set Up Virtual Environment
Activate the pre-configured virtual environment or create a new one:
```bash
# Activate the existing virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# (Alternative) Create a new virtual environment
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies
Install Django and image processing libraries (Pillow is used for company logo generation/uploads):
```bash
pip install django pillow
```

### 4. Database Migrations
Initialize the SQLite database schema and migrate:
```bash
python gradquest/manage.py migrate
```

### 5. Run Development Server
Start the Django development server:
```bash
python gradquest/manage.py runserver
```
Visit the application in your browser at: `http://127.0.0.1:8000/`

---

## 🧪 Testing

To run the automated Django unit tests (which cover login flows, authorization security constraints, company card CRUD operations, and setting updates):

```bash
python gradquest/manage.py test core
```
