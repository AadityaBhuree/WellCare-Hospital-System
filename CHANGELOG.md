# Changelog

All notable changes to the WellCare Hospital Management System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-24

### Added
- **CI/CD Integration**: GitHub Actions workflows for running linter, type checker, pytest test suite, and PyInstaller executable compilation.
- **Security Enhancements**: Password hashing using `bcrypt`, environment variable configuration using `python-dotenv`, and path security for SQLite databases.
- **Testing Infrastructure**: Comprehensive unit and integration test suite with `pytest` (120+ tests covering models, services, controllers, and UI frames).
- **Appointment Management**: Interactive appointment booking, status updates, and doctor schedule lookup.
- **TTLCache & Query Optimization**: Thread-safe in-memory TTL caching for database queries to minimize I/O overhead.
- **Role-Based Access Control**: Separate privileges for Administrator (analytics dashboard) and Medical Staff (patient record management and prescription printing).
- **Automated Prescription PDF Generation**: Standardized PDF output formatted with patient demographics, diagnosis, dosage details, and doctor credentials using `fpdf2`.
