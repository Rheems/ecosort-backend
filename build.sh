#!/usr/bin/env bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python populate_data.py
python manage.py expire_listings
python manage.py reset_streaks
python manage.py send_prompts
