import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Suppress SCRF protection.
WTF_CSRF_ENABLED = False

# Connect to the database
# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://apple@localhost:5432/fyyurtest'
SQLALCHEMY_TRACK_MODIFICATIONS = False
