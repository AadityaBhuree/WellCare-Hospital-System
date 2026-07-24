# Changelog

All notable changes to the WellCare Hospital Management System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-07-24

### Added
- **Patient Billing & Invoicing Subsystem**: New `BillingFrame` UI allowing hospital staff and administrators to generate invoices, view pending receivables, track total revenue, and process payments.
- **Financial Statistics & Database API**: SQLite database operations for invoice creation (`add_bill`), status updates (`update_bill_status`), and financial KPI aggregation (`get_billing_stats`).
- **Doctor Directory Management**: Interactive doctor management UI frame for managing medical specializations, doctor schedules, and contact details.
- **Record Export Utilities**: Export patient records to structured CSV and JSON formats with comprehensive data validation.
- **Expanded Test Coverage**: Added pytest test suites for billing database logic (`test_billing_db.py`), billing frame UI (`test_billing_frame.py`), and doctors directory (`test_doctors_frame.py`), raising total passing tests to 144.

## [1.0.0] - 2026-07-24

### Added
- **CI/CD Integration**: GitHub Actions workflows for running linter, type checker, pytest test suite, and PyInstaller executable compilation.
- **Security Enhancements**: Password hashing using `bcrypt`, environment variable configuration using `python-dotenv`, and path security for SQLite databases.
- **Testing Infrastructure**: Comprehensive unit and integration test suite with `pytest` (120+ tests covering models, services, controllers, and UI frames).
- **Appointment Management**: Interactive appointment booking, status updates, and doctor schedule lookup.
- **TTLCache & Query Optimization**: Thread-safe in-memory TTL caching for database queries to minimize I/O overhead.
- **Role-Based Access Control**: Separate privileges for Administrator (analytics dashboard) and Medical Staff (patient record management and prescription printing).
- **Automated Prescription PDF Generation**: Standardized PDF output formatted with patient demographics, diagnosis, dosage details, and doctor credentials using `fpdf2`.
