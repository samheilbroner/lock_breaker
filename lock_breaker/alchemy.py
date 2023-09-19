from sqlalchemy import create_engine
import os
from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from passlib.hash import sha256_crypt

from lock_breaker import PROJECT_ID, LOCAL_CREDENTIALS_PATH


def create_bigquery_engine():
    # Check if the app is running on Google Cloud or locally
    if os.environ.get('GAE_APPLICATION'):
        # App is running on Google Cloud, credentials are automatically available
        connection_string = f"bigquery://{PROJECT_ID}"
    else:
        # Load the service account info and set the credentials
        connection_string = f"bigquery://{PROJECT_ID}?credentials_path={LOCAL_CREDENTIALS_PATH}"

    # Create and return the SQLAlchemy engine
    return create_engine(connection_string)



Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    password_hash = Column(String(128))

    def set_password(self, password):
        self.password_hash = sha256_crypt.hash(password)

    def verify_password(self, password):
        return sha256_crypt.verify(password, self.password_hash)

