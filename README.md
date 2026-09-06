# Sri Anjaneya Traders – Fertilizer Shop Management System

A complete web application for managing a fertilizer shop: products, inventory, purchases, sales/billing, customer & supplier ledgers, reports, and Excel exports.

## Technology Stack

- Python 3, Flask, SQLAlchemy, SQLite (dev) / PostgreSQL (production)
- HTML5, CSS3, Vanilla JavaScript, Bootstrap 5
- openpyxl (Excel export), Werkzeug (password hashing), Gunicorn (production)

## 1. Install Python

Download and install Python 3.10+ from [python.org](https://www.python.org/downloads/).

Verify installation:

```bash
python --version
```

## 2. Create Virtual Environment

```bash
cd SriAnjaneyaTraders
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/Mac:**

```bash
source venv/bin/activate
```

## 3. Install Requirements

```bash
pip install -r requirements.txt
```

## 4. Configure Environment

Copy the example environment file:

```bash
copy .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=sqlite:///instance/shop.db
SECRET_KEY=your-random-secret-key-here
FLASK_ENV=development
```

> **Note:** If `DATABASE_URL` is not set, the app automatically uses `instance/shop.db`.

For PostgreSQL:

```env
DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your-random-secret-key
FLASK_ENV=production
```

## 5. Initialize Database

**Option A – Quick start (creates tables + seed data):**

```bash
python app.py
```

**Option B – Using Flask-Migrate (recommended for production):**

```bash
set FLASK_APP=app.py
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
flask seed
```

## 6. Default Admin Account

| Field    | Value     |
|----------|-----------|
| Username | `admin`   |
| Password | `admin123` |

Change the password after first login in production.

## 7. Run Locally

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## 8. Excel Export

Excel download buttons are available on:

- Products, Customers, Suppliers, Purchases, Bills pages
- Sales, Purchase, and Inventory reports

Files are generated using `openpyxl` with formatted headers and column widths.

## 9. Deploy to Render

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### Step 2: Create PostgreSQL on Render

1. Go to [render.com](https://render.com)
2. Create a new **PostgreSQL** database
3. Copy the **Internal Database URL**

### Step 3: Create Web Service

1. New → **Web Service** → Connect your repo
2. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment Variables:**
     - `DATABASE_URL` = your PostgreSQL URL
     - `SECRET_KEY` = a strong random string
     - `FLASK_ENV` = `production`

### Step 4: Initialize Production Database

In Render Shell:

```bash
flask db upgrade
flask seed
```

## 10. Connect PostgreSQL

The same SQLAlchemy models work with both SQLite and PostgreSQL. Switch by changing `DATABASE_URL` in `.env` or Render environment variables.

Render may provide `postgres://` URLs — the app automatically converts them to `postgresql://`.

For PostgreSQL backups, use Render dashboard backups or:

```bash
pg_dump DATABASE_URL > backup.sql
```

## Project Structure

```
SriAnjaneyaTraders/
├── app.py              # Application entry point
├── config.py           # Configuration
├── extensions.py       # SQLAlchemy & Migrate
├── utils.py            # Helpers, auth, inventory
├── excel_export.py     # Excel export functions
├── models/             # Database models
├── routes/             # Flask blueprints
├── templates/          # HTML templates
├── static/             # CSS & JS
└── instance/           # SQLite database (local)
```

## Features

- Admin login with session authentication
- Dashboard with sales, stock, and outstanding summaries
- Product, category, brand, unit management
- Customer & supplier CRUD with ledger tracking
- Purchase entry (auto stock increase)
- Sales billing (auto stock decrease, invoice generation)
- Bill history with print-ready A4 invoice
- Inventory with batch/expiry tracking
- Stock adjustments with audit trail
- Reports (daily/weekly/monthly/custom)
- Excel exports
- Settings (shop name, GST, invoice prefix)
- Audit logs
- SQLite database backup download

## Invoice Customization

Edit these files to customize the invoice layout:

- `templates/bills/invoice.html` — structure and data
- `static/css/invoice.css` — styling and print layout

## License

Private use for Sri Anjaneya Traders.
