import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

# Add SQLALCHEMY_TRACK_MODIFICATIONS as False (boolean, not 'False' string) to avoid significant overhead. It will be disabled by default in the future
SQLALCHEMY_TRACK_MODIFICATIONS = False

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://zhibaichen@localhost:5432/fyyurapp'

