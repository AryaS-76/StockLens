from sqlalchemy import create_engine, Column, Integer, String, Float, Date, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()
# PostgreSQL Connection URL


# Create Database Engine
engine = create_engine(os.getenv("DATABASE_URL"))

# Create a Session Local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define Base for Models
Base = declarative_base()



