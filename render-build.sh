#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create a superuser if one doesn't exist (Optional/One-time)
# python manage.py createsuperuser --no-input || true
