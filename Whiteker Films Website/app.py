import os
from datetime import timedelta

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from wtforms import Form, StringField, TextAreaField, validators
from email_validator import validate_email, EmailNotValidError


app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "CHANGE-ME-IN-PRODUCTION"),
    MAX_CONTENT_LENGTH=2 * 1024 * 1024,
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
    WTF_CSRF_TIME_LIMIT=3600,
)


# --------------------------------------------------
# SECURITY
# --------------------------------------------------

csrf = CSRFProtect(app)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

limiter.init_app(app)


@app.context_processor
def security_context():
    return {
        "csrf_token": generate_csrf()
    }


@app.after_request
def security_headers(response):

    response.headers["X-Content-Type-Options"] = "nosniff"

    response.headers["X-Frame-Options"] = "SAMEORIGIN"

    response.headers["Referrer-Policy"] = (
        "strict-origin-when-cross-origin"
    )

    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )

    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' data: https:; "
        "style-src 'self' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "script-src 'self'; "
        "media-src 'self' https:; "
        "frame-src https:; "
        "connect-src 'self'; "
        "form-action 'self'; "
        "base-uri 'self'; "
        "object-src 'none'"
    )

    if os.environ.get("HSTS", "0") == "1":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    return response


# --------------------------------------------------
# PAGES
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html")


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/galleries")
def galleries():
    return render_template("galleries.html")


@app.route("/about")
def about():
    return render_template("about.html")


# --------------------------------------------------
# CONTACT FORM
# --------------------------------------------------

class ContactForm(Form):

    name = StringField(
        "Name",
        [
            validators.InputRequired(),
            validators.Length(min=2, max=80)
        ]
    )

    email = StringField(
        "Email",
        [
            validators.InputRequired(),
            validators.Length(max=254)
        ]
    )

    project_type = StringField(
        "Project Type",
        [
            validators.Optional(),
            validators.Length(max=100)
        ]
    )

    date = StringField(
        "Date",
        [
            validators.Optional(),
            validators.Length(max=30)
        ]
    )

    message = TextAreaField(
        "Tell us about your project",
        [
            validators.InputRequired(),
            validators.Length(min=10, max=3000)
        ]
    )

    website = StringField(
        "Website",
        [
            validators.Optional(),
            validators.Length(max=200)
        ]
    )


@app.route("/contact", methods=["GET", "POST"])
@limiter.limit("5 per hour", methods=["POST"])
def contact():

    form = ContactForm(request.form)

    if request.method == "POST":

        # Honeypot spam protection
        if form.website.data:
            flash("Thanks for reaching out!")
            return redirect(url_for("contact"))

        # Email validation
        try:
            validate_email(
                form.email.data,
                check_deliverability=False
            )

        except EmailNotValidError:

            form.email.errors.append(
                "Please enter a valid email address."
            )

        if form.validate():

            # Email delivery can be connected later.
            flash(
                "Thank you! Your inquiry was received. "
                "We'll be in touch soon."
            )

            return redirect(url_for("contact"))

    return render_template(
        "contact.html",
        form=form
    )


# --------------------------------------------------
# ERROR HANDLERS
# --------------------------------------------------

@app.errorhandler(413)
def too_large(_):
    return "Request too large.", 413


@app.errorhandler(429)
def rate_limited(_):
    return "Too many requests. Please try again later.", 429


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)