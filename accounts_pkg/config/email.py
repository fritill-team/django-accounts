import os

EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', None) # 'smtp.mailtrap.io'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', None) # 'dc9851cf2e747b'
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', None) # 'd51daf9b5d32f0'
EMAIL_PORT = os.environ.get('EMAIL_PORT', None) # '2525'