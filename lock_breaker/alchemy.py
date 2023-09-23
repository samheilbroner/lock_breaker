import os

import pg8000
import sqlalchemy
from google.cloud.sql.connector import Connector, IPTypes
from sqlalchemy import create_engine

from lock_breaker import PROJECT_ID, REGION, POSTGRES_PASSWORD_LABEL
from lock_breaker.utility import get_gcp_secret


def connect_with_connector(username, password, dbname) -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of Postgres.

    Uses the Cloud SQL Python Connector package.
    """
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.

    instance_connection_name = f"{PROJECT_ID}:{REGION}:lockbreaker"

    db_user = username
    db_pass = password
    db_name = dbname

    ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    # initialize Cloud SQL Python Connector object
    connector = Connector()

    def getconn() -> pg8000.dbapi.Connection:
        conn: pg8000.dbapi.Connection = connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=ip_type
        )
        return conn

    # The Cloud SQL Python Connector can be used with SQLAlchemy
    # using the 'creator' argument to 'create_engine'
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        # ...
    )
    return pool




def connect_via_proxy(username, password, dbname, host_path):
    """
    Establishes a connection to a Google Cloud SQL Postgres instance via Cloud SQL Proxy.
    Returns an SQLAlchemy Engine instance.
    """

    # Connection string for Cloud SQL Proxy
    # Format: dialect+driver://username:password@/dbname?host=host_path
    # Replace 'username', 'password', 'dbname', and 'host_path' with your specific values

    connection_string = f"postgresql+psycopg2://{username}:{password}@/{dbname}?host={host_path}"

    # Create SQLAlchemy engine
    engine = create_engine(connection_string)

    return engine

def is_running_on_app_engine() -> bool:
    """
    Determines if the script is running on Google App Engine.

    Returns:
        bool: True if running on App Engine, False otherwise.
    """
    return bool(os.environ.get('GAE_ENV', ''))
def get_engine():
    """
    Returns an SQLAlchemy Engine instance for a Google Cloud SQL Postgres instance.

    If running on Google App Engine, uses Cloud SQL Proxy.
    Otherwise, uses the Cloud SQL Python Connector.
    """
    if not is_running_on_app_engine():
        # Use Cloud SQL Proxy
        username = 'postgres'
        password = get_gcp_secret(PROJECT_ID, POSTGRES_PASSWORD_LABEL)
        dbname = 'user_info'
        host_path = 'localhost'
        engine = connect_via_proxy(username, password, dbname, host_path)
    else:
        # Use Cloud SQL Python Connector
        username = 'postgres'
        password = get_gcp_secret(PROJECT_ID, POSTGRES_PASSWORD_LABEL)
        dbname = 'user_info'
        engine = connect_with_connector(username, password, dbname)
    return engine