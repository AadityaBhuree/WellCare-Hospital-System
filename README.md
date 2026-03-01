# WellCare Hospital Management System

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A professional, object-oriented Clinic Management System designed to streamline patient records and provide real-time healthcare analytics. This project demonstrates advanced GUI development with `CustomTkinter`, data visualization, and robust database management.

## 🌟 Key Features

- **Professional Dashboard**: Real-time analytics with dynamic charts (Age distribution, Gender demographics, Blood group trends).
- **Intelligent Auto-Refresh**: Live data syncing every 10 seconds and instantaneous updates across frames upon data mutation.
- **Role-Based Access Control (RBAC)**: Secure access levels for Administrators (Analytical views) and Medical Staff (Data entry).
- **Automated Documentation**: High-quality PDF prescription generation with structured patient data.
- **Robust Data Layer**: Reliable local storage using SQLite with optimized indexing for performance.
- **Modern UI/UX**: Fluid interface with Light/Dark mode support and responsive design.

## 🛠️ Technical Stack

- **Frontend**: CustomTkinter (Modernized Tkinter wrapping)
- **Data Visualization**: Matplotlib & Seaborn
- **Backend/Logic**: Python 3.x (Object-Oriented Design)
- **Database**: SQLite3
- **Document Generation**: FPDF2

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Pip (Python Package Manager)

### Installation

1. **Clone the project**

   ```bash
   git clone <repository-url>
   cd Clinic_Project_practice
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
   source .venv/bin/activate  # On Linux/macOS
   .venv\Scripts\activate     # On Windows
   pip install -r requirements.txt
   ```

### Execution

```bash
python main.py
```

## 🔐 Default Credentials

| Role          | User ID | Password |
|---------------|---------|----------|
| **Administrator** | `admin`   | `123`      |
| **Staff Member**  | `staff`   | `123`      |

## 🏗️ Project Architecture

The application follows a **Controller-Frame Pattern**:

- `ClinicApp`: Central controller managing state, navigation, and frame transitions.
- `Database`: Decoupled data access layer handling all SQL operations.
- `Frames`: Modular UI components (Dashboard, PatientEntry, etc.) that interact with the controller.

## 📈 Technical Achievements

- **Memory Optimization**: Implemented strict resource management in `matplotlib` to prevent memory leaks during real-time chart rendering.
- **Schema Resilience**: Developed robust counting logic (`COUNT(*)`) to handle legacy data inconsistencies and schema shifts.
- **State Management**: Created a seamless refresh synchronization between the data entry layer and the analytical dashboard.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Developed as a demonstration of high-quality software engineering principles for clinic management.*
