# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ SQLAlchemy Database Configuration ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SQLAlchemy is a Python library that lets you work with databases using Python objects and functions instead of writing raw SQL everywhere.


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# -------------------- connect postgresql with the fastapi application 
# url format : "postgresql://postgres:password@localhost_name/DatabaseName"
# for post gresql = postgresql://postgres:postgresql@localhost/TodoApplicationDatabase

SQLALCHEMY_DATABASE_URL = "postgresql://postgres.oxnmhezetgketgiynjih:abcdalvi9421@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"  # for sqlite database

# create_engine() creates the main connection/communication mechanism between your Python application and the database.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL  
)

# A session is basically a temporary working area through which your application interacts with the database.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# as the parent/foundation of all your database models.
Base = declarative_base()


