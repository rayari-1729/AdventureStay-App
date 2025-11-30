#!/bin/bash
source /var/app/venv/*/bin/activate
exec gunicorn adventurestay.wsgi:application --bind 127.0.0.1:8000 --timeout 120

