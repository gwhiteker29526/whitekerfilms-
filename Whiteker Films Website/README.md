# Whiteker Films

Elegant wedding videography website built with Flask.

## Local setup

1. Install Python 3.11+.
2. Create a virtual environment:
   `python -m venv .venv`
3. Activate it.
4. Install:
   `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and create a strong `SECRET_KEY`.
6. Run:
   `flask --app app run`
7. Open http://127.0.0.1:5000

For production, use HTTPS and a WSGI server such as Gunicorn.

## Add your media later

- Put portfolio images in `static/images/`.
- Put self-hosted video files in `static/videos/`.
- Replace the portfolio placeholders in `templates/portfolio.html`.
- Replace the Vidflow placeholder in `templates/galleries.html`.

## Contact form

The form is validated and rate-limited, but this starter project intentionally does not send email itself.
For production, connect it to a trusted transactional email provider using server-side environment variables. Never put SMTP/API credentials in HTML, JavaScript, or Git.

## Squarespace domain

The domain can remain registered with Squarespace. Once the site is hosted, point the domain's DNS records to the hosting provider according to that provider's instructions.
