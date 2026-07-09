# WellCare Hospital Management System

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A professional, object-oriented Clinic Management System designed to streamline patient records and provide real-time healthcare analytics. This project demonstrates advanced GUI development with `CustomTkinter`, data visualization, and robust database management.

## 🌟 Key Features

- **Professional Dashboard**: Real-time analytics with dynamic charts (Age distribution, Gender demographics, Blood group trends)
- **Intelligent Auto-Refresh**: Live data syncing every 10 seconds and instantaneous updates across frames upon data mutation
- **Role-Based Access Control (RBAC)**: Secure access levels for Administrators (Analytical views) and Medical Staff (Data entry)
- **Automated Documentation**: High-quality PDF prescription generation with structured patient data
- **Robust Data Layer**: Reliable local storage using SQLite with optimized queries
- **Modern UI/UX**: Fluid interface with Light/Dark mode support and responsive design
- **Modular Architecture**: Clean separation of concerns with modular package structure

## 🛠️ Technical Stack

- **Frontend**: CustomTkinter (Modernized Tkinter wrapping)
- **Data Visualization**: Matplotlib & Seaborn
- **Backend/Logic**: Python 3.8+ (Object-Oriented Design)
- **Database**: SQLite3
- **Document Generation**: FPDF2
- **Testing**: pytest
- **Code Quality**: ruff (linter & formatter)

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Pip (Python Package Manager)

### Installation

1. **Clone the project**

   ```bash
   git clone https://github.com/AadityaBhuree/WellCare-Hospital-System.git
   cd WellCare-Hospital-System
   ```

2. **Automated Setup (Recommended)**
   Run the included setup script to create a virtual environment and install dependencies:

   ```bash
   # On Windows
   .\setup.bat
   ```

3. **Manual Setup**

   ```bash
   python -m venv .venv
   # Activate:
   .venv\Scripts\activate     # On Windows
   source .venv/bin/activate  # On Linux/macOS
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Dev dependencies (optional)
   ```

### Execution

```bash
python -m src.wellcare
# Or
python src/wellcare/__main__.py
```

## 🔐 Default Credentials

> **⚠️ IMPORTANT**: Change these immediately in production!

| Role          | User ID | Password |
|---------------|---------|----------|
| **Administrator** | `admin`   | `123`      |
| **Staff Member**  | `staff`   | `123`      |

Credentials are configured via environment variables (see `.env.example`).

## 🏗️ Project Architecture

```
wellcare-hospital-system/
├── src/wellcare/           # Main application package
│   ├── __init__.py
│   ├── __main__.py         # Entry point
│   ├── app.py              # Central controller (ClinicApp)
│   ├── config.py           # Configuration management
│   ├── database.py         # Database operations
│   ├── logger.py           # Logging setup
│   ├── frames/             # UI frame components
│   │   ├── home.py
│   │   ├── about.py
│   │   ├── login.py
│   │   ├── dashboard.py
│   │   ├── patient_entry.py
│   │   └── search.py
│   └── utils/              # Utilities
│       ├── validators.py   # Input validation
│       └── pdf.py          # PDF generation
├── tests/                  # Test suite
├── assets/                 # Static assets (images)
├── .env.example            # Environment template
└── README.md
```

The application follows a **Controller-Frame Pattern**:

- `ClinicApp` (`app.py`): Central controller managing state, navigation, and frame transitions
- `Database` (`database.py`): Decoupled data access layer handling all SQL operations
- `Frames` (`frames/`): Modular UI components that interact with the controller
- `Config` (`config.py`): Centralized configuration via environment variables

## 🧪 Running Tests

```bash
pytest
# With coverage:
pytest --cov=src.wellcare
```

## 🔍 Code Quality

```bash
# Lint
ruff check src/
# Format
ruff format src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Developed by Aditya Bhure*
