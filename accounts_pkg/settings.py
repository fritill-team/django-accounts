import sys

from accounts_pkg.config.apps import *
from accounts_pkg.config.auth import *
from accounts_pkg.config.database import *
from accounts_pkg.config.email import *
from accounts_pkg.config.locale import *
from accounts_pkg.config.main import *
from accounts_pkg.config.middleware import *
from accounts_pkg.config.templates import *
from dj_accounts.settings import *

if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test.sqlite3',
    }
