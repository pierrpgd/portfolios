#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Apply any outstanding database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser if CREATE_SUPERUSER is set
if [[ $CREATE_SUPERUSER ]]; then
  python manage.py createsuperuser --no-input
fi

if [[ $INIT_DB ]]; then
  # Initiate database for 'pierrpgd' user
  python manage.py init_db --force
fi

# Convert static asset files
python manage.py collectstatic --no-input