# Library Management System

A reconstructed, educational portfolio implementation for managing a small library's catalogue, members, and circulation workflow.

> **Provenance:** This is a new implementation reconstructed for portfolio demonstration because the original bachelor's source files are no longer available. It is not represented as the recovered original submission.

## Features
- Add and search books
- Register library members
- Issue available copies and record due dates
- Return loans and calculate overdue days
- Prevent issuing unavailable books
- SQLite persistence and automated tests

## Stack
Python 3.10+, SQLite, pytest.

## Quick start
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Tests
```bash
pytest
```

The database is created locally. The included workflow uses fictional demo records. This is a learning project, not a production library platform.
