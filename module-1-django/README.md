# Django TODO Application

A demo Django application for managing tasks with basic CRUD functionality.

## Features

- Add new tasks
- Edit existing tasks
- Delete tasks
- Assign due dates
- Mark tasks as done/complete

## Requirements

- Python 3.12
- Django 5.1
- uv (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd module-1-django
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   ```

3. Run migrations:
   ```bash
   uv run python manage.py migrate
   ```

4. Start the development server:
   ```bash
   uv run python manage.py runserver
   ```

5. Open your browser and navigate to `http://127.0.0.1:8000`

## Usage

- Create tasks with titles, descriptions, and due dates
- Update task details as needed
- Mark tasks complete when finished
- Delete tasks you no longer need

## License

This project is for demonstration purposes.
