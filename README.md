# WellCare Hospital Management System

[![CI](https://github.com/AadityaBhuree/WellCare-Hospital-System/actions/workflows/ci.yml/badge.svg)](https://github.com/AadityaBhuree/WellCare-Hospital-System/actions/workflows/ci.yml)
[![Build Executable](https://github.com/AadityaBhuree/WellCare-Hospital-System/actions/workflows/build.yml/badge.svg)](https://github.com/AadityaBhuree/WellCare-Hospital-System/actions/workflows/build.yml)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A professional, object-oriented Clinic Management System designed to streamline patient records, appointment scheduling, and real-time healthcare analytics. This project demonstrates enterprise-grade Python desktop application architecture using `CustomTkinter`, `SQLite3`, `FPDF2`, and comprehensive `pytest` testing.

---

## 🌟 Key Features

- **Real-Time Analytics Dashboard**: Visual demographics with dynamic charts (Age distribution, Gender demographics, Blood group trends) powered by Matplotlib & Seaborn.
- **Appointment Scheduling**: Interactive appointment booking, doctor schedule lookup, and status tracking (Scheduled, Completed, Cancelled).
- **Intelligent Auto-Refresh**: Live data syncing every 10 seconds and instantaneous frame updates upon data mutations.
- **Role-Based Access Control (RBAC)**: Secure access tiers for Administrators (Analytics & System Overview) and Medical Staff (Patient records, appointments, and prescriptions).
- **Automated Prescription PDF Generation**: High-quality structured PDF prescription document generation using `FPDF2`.
- **Thread-Safe Caching**: In-memory `TTLCache` to reduce redundant database read operations.
- **Robust Data & Security Layer**: Password hashing via `bcrypt`, environment variable configuration via `python-dotenv`, and parameterized SQL query execution.
- **Modern UI/UX**: Fluid desktop GUI supporting Light/Dark mode transitions with responsive frame layouts.

---

## 🛠️ Technical Stack

- **GUI Framework**: CustomTkinter
- **Data Visualization**: Matplotlib & Seaborn
- **Backend / Logic**: Python 3.8+ (Object-Oriented Design)
- **Database**: SQLite3 with thread-safe connection handling
- **Security & Config**: `bcrypt`, `python-dotenv`
- **PDF Engine**: FPDF2
- **Code Quality & Testing**: `pytest`, `pytest-cov`, `ruff`, `mypy`

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- `pip` (Python Package Manager)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AadityaBhuree/WellCare-Hospital-System.git
   cd WellCare-Hospital-System
   ```

2. **Automated Setup (Windows)**:
   ```cmd
   .\setup.bat
   ```

3. **Manual Setup**:
   ```bash
   python -m venv .venv
   # Activate:
   .venv\Scripts\activate     # Windows
   source .venv/bin/activate  # Linux/macOS

   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

### Running the Application

```bash
python -m src.wellcare
# or
python src/wellcare/__main__.py
```

---

## 🔐 Default Credentials

> **⚠️ Security Warning**: Environment variables can be configured in `.env` (copied from `.env.example`).

| Role | User ID | Password |
| :--- | :--- | :--- |
| **Administrator** | `admin` | `123` |
| **Medical Staff** | `staff` | `123` |

---

## 🏗️ Project Architecture

```
WellCare-Hospital-System/
├── .github/
│   └── workflows/
│       ├── ci.yml              # CI test, lint, format & type-check pipeline
│       └── build.yml           # Executable packaging pipeline (PyInstaller)
├── src/wellcare/               # Core application package
│   ├── __init__.py
│   ├── __main__.py             # Main entry point
│   ├── app.py                  # Controller (ClinicApp)
│   ├── config.py               # Environment configuration
│   ├── database.py             # SQLite database layer with caching & schema setup
│   ├── logger.py               # Centralized logging setup
│   ├── frames/                 # Modular CustomTkinter UI frames
│   │   ├── home.py             # Landing page
│   │   ├── about.py            # About & system info
│   │   ├── login.py            # Authentication frame
│   │   ├── dashboard.py        # Analytics & Matplotlib visualizations
│   │   ├── patient_entry.py    # Patient registration & PDF print
│   │   ├── search.py           # Patient search & management
│   │   └── appointments.py     # Appointment booking & scheduling
│   └── utils/                  # Utility helpers
│       ├── cache.py            # Thread-safe TTL Cache
│       ├── pdf.py              # FPDF2 Prescription generator
│       └── validators.py       # Input validation (Email, Phone, Pincode, Age)
├── tests/                      # Unit & integration test suite (120+ tests)
├── assets/                     # UI logos, icons, and themes
├── .env.example                # Environment variables template
├── CHANGELOG.md                # Project release history
├── CONTRIBUTING.md             # Developer contribution guidelines
├── pyproject.toml              # Tool configurations (ruff, mypy, pytest)
└── README.md
```

---

## 🧪 Testing & Quality Assurance

```bash
# Run unit & integration tests
pytest

# Run tests with code coverage report
pytest --cov=src.wellcare --cov-report=term-missing

# Run code linter and formatting checks
ruff check src/ tests/
ruff format --check src/ tests/

# Run static type checking
mypy src/
```

---

## 📦 Building Executables

To bundle the application into a standalone Windows executable using PyInstaller:

```bash
pyinstaller --noconfirm --onedir --windowed --name "WellCare" --add-data "assets;assets" src/wellcare/__main__.py
```

The output executable will be placed in the `dist/WellCare/` folder.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

*Developed by Aditya Bhure*
