"""
Django settings for wallet project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ.get("DEBUG")))

ALLOWED_HOSTS = ["localhost", "188.121.104.131", "jamshid.app", "127.0.0.1"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'zarinpal',
    'api'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wallet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wallet.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get("DB_NAME"),
        'USER': os.environ.get("DB_USER"),
        'PASSWORD': os.environ.get("DB_PASSWORD"),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / 'static'

# Media files (User Uploaded Images)

MEDIA_ROOT = BASE_DIR / 'media'

MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# DRF CONFIG

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        # 'rest_framework.renderers.BrowsableAPIRenderer',  # Comment out or remove this line
        'rest_framework.renderers.JSONRenderer',

    ],
    # Other DRF settings...
}

# CORS CONFIG

CORS_ALLOW_HEADERS = ['*']

CORS_ALLOW_METHODS = ['*']

CORS_ALLOW_CREDENTIALS = True

CORS_ORIGIN_ALLOW_ALL = False

CORS_ORIGIN_WHITELIST = (
    # 'http://localhost',
    'http://localhost:5173',
    # 'http://localhost:8080',
    'https://jamshid.app',
)

# CSRF CONFIG

CSRF_TRUSTED_ORIGINS = [
    'https://wallet.jamshid.app',
    'http://localhost',
    'http://127.0.0.1:'
    'http://127.0.0.1:8000'
]

# Zarinpal Config

MERCHANT = os.environ.get("MERCHANT")

SANDBOX = True

if SANDBOX:
    sandbox = 'sandbox'
else:
    sandbox = 'www'

ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"
CALL_BACK_URL = 'https://wallet.jamshid.app/zarinpal/verify/'
ZP_ERROR_CODES = {
    -1: "اطلاعات ارسال شده ناقص است.",
    -2: "و یا مرچنت کد پذیرنده صحیح نیست IP",
    -3: "با توجه به محدوديت هاي شاپرك امكان پرداخت با رقم درخواست شده ميسر نمي باشد.",
    -4: "سطح تاييد پذيرنده پايين تر از سطح نقره اي است.",
    -11: "درخواست مورد نظر يافت نشد.",
    -12: "امكان ويرايش درخواست ميسر نمي باشد.",
    -21: "هيچ نوع عمليات مالي براي اين تراكنش يافت نشد.",
    -22: "تراكنش نا موفق ميباشد.",
    -33: "رقم تراكنش با رقم پرداخت شده مطابقت ندارد.",
    -34: "سقف تقسيم تراكنش از لحاظ تعداد يا رقم عبور نموده است",
    -40: "اجازه دسترسي به متد مربوطه وجود ندارد.",
    -41: "غيرمعتبر ميباشد. AdditionalData اطلاعات ارسال شده مربوط به",
    -42: "مدت زمان معتبر طول عمر شناسه پرداخت بايد بين 30 دقيه تا 45 روز مي باشد.",
    -54: "درخواست مورد نظر آرشيو شده است.",
    100: "عمليات با موفقيت انجام گرديده است.",
    101: "تراكنش انجام شده است. PaymentVerification عمليات پرداخت موفق بوده و قبلا"
}
