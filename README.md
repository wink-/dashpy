# DashPy

A Flask-based dashboard application that uses SQLite for local settings and MySQL for data display.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your MySQL credentials:
```
MYSQL_HOST=localhost
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database
```

4. Run the application:
```bash
python app.py
```

## Features
- Local settings storage using SQLite
- Data display from MySQL database
- Modern UI with Bootstrap 5
- Interactive data tables using DataTables.js

dashpy/                 # Project root
├── app.py              # Main application file
├── models.py           # Database models
├── routes.py           # Application routes
├── requirements.txt    # Python dependencies
├── config.py           # Optional: App configuration (if needed)
├── instance/           # Instance folder (optional, for configs and DB)
│   └── config.py       # Instance-specific config (e.g., secrets, production settings)
├── users.db            # SQLite database file (automatically created)
├── templates/          # Folder for HTML templates
│   ├── base.html       # Base layout for extending other templates
│   ├── login.html      # Login page
│   └── index.html      # Dashboard page
├── static/             # Folder for static files (CSS, JS, images)
│   ├── css/            # Folder for CSS files
│   │   └── styles.css  # Example CSS file
│   ├── js/             # Folder for JavaScript files
│   │   └── scripts.js  # Example JS file
│   └── img/            # Folder for images
│       └── logo.png    # Example image
├── tests/              # Folder for unit tests (optional)
│   └── test_app.py     # Example test file
└── README.md           # Project documentation
