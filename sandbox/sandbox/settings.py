"""Proyecto mínimo para desarrollar geneos-ui y ver el catálogo.

    cd sandbox && python manage.py runserver
    → http://127.0.0.1:8000/            catálogo (UI Kit)
    → http://127.0.0.1:8000/demo/       layout real con menú y paginación

    DJANGO_SETTINGS_MODULE=sandbox.settings_geflota python manage.py runserver
    → http://127.0.0.1:8000/geflota/    producto ficticio GEFLOTA, sin cambios en geneos_ui
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "solo-para-desarrollo-local"
DEBUG = True
ALLOWED_HOSTS = ["*"]
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "geneos_ui",
    "geflota",   # producto ficticio de pruebas (solo sandbox); ver settings_geflota.py
]
MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]
ROOT_URLCONF = "sandbox.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "geneos_ui.context_processors.geneos_ui",
    ]},
}]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
USE_TZ = True
LANGUAGE_CODE = "es-ar"

_PRODUCT = os.environ.get("GN_PRODUCT", "gelectric")
_NAV = {
    "gelectric": "geneos_ui.catalog_data.nav_gelectric",
    "gema": "geneos_ui.catalog_data.nav_gema",
    "geagro-cereales": "geneos_ui.catalog_data.nav_geagro_cereales",
    "geagro-vid": "geneos_ui.catalog_data.nav_geagro_vid",
}
GENEOS_UI = {
    "PRODUCT": _PRODUCT,
    "NAV": _NAV[_PRODUCT],
    "LOGO_FULL": f"demo/logos/{_PRODUCT}-full.svg",
    "LOGO_ICON": f"demo/logos/{_PRODUCT}-icon.svg",
    "TAGLINE": "Sandbox",
}
