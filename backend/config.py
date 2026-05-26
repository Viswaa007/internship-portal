# =============================================================
# File: backend/config.py
# =============================================================

import os
from datetime import timedelta


class Config:

    SECRET_KEY = os.getenv("SECRET_KEY")

    GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
    # =========================================================
    # DATABASE
    # =========================================================

    SQLALCHEMY_DATABASE_URI = \
        "mysql+pymysql://root:@localhost:3306/internship_portal_db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280
    }

    # =========================================================
    # MAIL CONFIG
    # =========================================================

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True

    MAIL_USERNAME = 'viswaamekala@gmail.com'

    # GOOGLE APP PASSWORD HERE
    MAIL_PASSWORD = 'sxfesalsxzubqbqu'

    MAIL_DEFAULT_SENDER = 'viswaamekala@gmail.com'

    # =========================================================
    # CSRF
    # =========================================================

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    WTF_CSRF_SSL_STRICT = False

    # =========================================================
    # SESSION
    # =========================================================

    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # =========================================================
    # FILES
    # =========================================================
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    CERTIFICATE_FOLDER = os.path.join(BASE_DIR, "certificates")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "png", "jpg", "jpeg"}

    LOGIN_VIEW = "auth.login"

    # =========================================================
    # UPLOADS
    # =========================================================

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "static",
        "uploads"
    )

    CERTIFICATE_FOLDER = os.path.join(
        BASE_DIR,
        "certificates"
    )

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    ALLOWED_EXTENSIONS = {
        "pdf",
        "doc",
        "docx",
        "png",
        "jpg",
        "jpeg"
    }

    LOGIN_VIEW = "auth.login"


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}