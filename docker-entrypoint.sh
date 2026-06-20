#!/usr/bin/env bash
# exit on error
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting services..."
exec "$@"
