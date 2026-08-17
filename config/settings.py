# config/settings.py
from pathlib import Path #modern way to handle file paths in Python
import environ #allows django to read environment variables from a .env file
import dj_database_url #it parses the database URL from the environment variable and returns a dictionary that can be used to configure the database connection in Django.

BASE_DIR = Path(__file__).resolve().parent.parent #to find main/root(manage.py) directory of the project.
env = environ.Env() #creates an environment variable reader that can read variables from the .env file.
environ.Env.read_env(BASE_DIR / '.env') #go to .env file and read the environment variables from it.

SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

INSTALLED_APPS = [
    'django.contrib.admin', # enables django admin panel.
    'django.contrib.auth', # provides authentication and authorization features for user management.
    'django.contrib.contenttypes',# provides a framework for handling different types of content in the application.
    'django.contrib.sessions', # provides session management for user authentication and authorization.
    'django.contrib.messages', # shows temporary messages to users, such as success or error messages.
    'django.contrib.staticfiles', # provides a framework for managing static files, such as CSS and JavaScript files.

    'dashboard',
    'projects',
    'finance',
    'expenses',
    'reports',
    'common',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware', # This adds several security-related protections to your Django application.
    'whitenoise.middleware.WhiteNoiseMiddleware', # Its main purpose is to help Django serve static files directly.
    'django.contrib.sessions.middleware.SessionMiddleware', # This middleware enables session management in Django,
    'django.middleware.common.CommonMiddleware',# This middleware provides several useful features for handling common tasks in web applications, such as URL normalization, content type handling, and caching.
    'django.middleware.csrf.CsrfViewMiddleware',# This middleware provides protection against Cross-Site Request Forgery (CSRF) attacks by adding a CSRF token to each form submitted by the user.
    'django.contrib.auth.middleware.AuthenticationMiddleware',# This middleware enables user authentication in Django, allowing users to log in and access protected resources.
    'django.contrib.messages.middleware.MessageMiddleware',# This middleware enables the use of temporary messages in Django
    'django.middleware.clickjacking.XFrameOptionsMiddleware',# This middleware provides protection against clickjacking attacks by adding an X-Frame-Options header to HTTP responses, which prevents the page from being embedded in an iframe on another site.
]

ROOT_URLCONF = 'config.urls' #Go to the config project package and use its urls.py file as the main URL configuration.

TEMPLATES = [ # When a view wants to render an HTML page, how should Django find and process that HTML?
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates', # This tells Django which template engine to use. Django has its own template language called the Django Template Language (DTL).
        'DIRS': [BASE_DIR / 'templates'], # tells django to look for templates inside project's main directory(amcco/templates).
        'APP_DIRS': True, # also check for templates inside project apps.(projects/templates/project_detais.html)
        'OPTIONS': { # contains other django configuration setting for template engine.
            'context_processors': [ #A context processor is a function that can automatically add data to the context of your templates.
                'django.template.context_processors.request', # These run for every template request and add variables automatically.
                'django.contrib.auth.context_processors.auth', #This is why you can use {{ afghan_date }} in ANY template without passing them from the view!
                'django.contrib.messages.context_processors.messages',
                'common.context_processors.afghan_date',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application' #"Go to the config package → open wsgi.py → use the application object."

DATABASES = {
    'default': dj_database_url.config(
        default=env('DATABASE_URL', default='sqlite:///db.sqlite3'),
        conn_max_age=600 #This controls how long Django can reuse an existing database connection.(600sec = 10min)
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

#STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage' #This tells Django to use WhiteNoise to serve static files
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kabul'
USE_I18N = True # It allows your application to support multiple languages if you later want something like: eng, dari, pashto
USE_TZ = True # application can correctly handle dates across different locations.

STATIC_URL = '/static/' #This defines the URL prefix used to access static files.  /static/js/app.js
STATICFILES_DIRS = [BASE_DIR / 'static']  # "Look inside my project's static folder for additional static files."
STATIC_ROOT = BASE_DIR / 'staticfiles' #STATIC_ROOT tells Django where to collect all static files for deployment.

MEDIA_URL = '/media/' #This defines the URL prefix for user-uploaded files.
MEDIA_ROOT = BASE_DIR / 'media' #This tells Django where to physically store uploaded files.

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField' #This controls the default type of the automatically generated primary key (id) for your models.

LOGIN_URL = 'login' #If an unauthenticated user tries to access a page that requires login, send them to the URL named login.
LOGIN_REDIRECT_URL = 'dashboard' # when authenticated redirect to dashboard
LOGOUT_REDIRECT_URL = 'login' #when logout redirect to login page.