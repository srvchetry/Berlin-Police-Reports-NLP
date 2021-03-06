"""Basic SQLAlchemy Setup (see http://flask.pocoo.org/docs/0.12/patterns/sqlalchemy/).

Creates a SQLite database and connects to it."""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from webui.flaskconfig import  Config
import os
import logging

logger = logging.getLogger(__name__)
engine = create_engine('sqlite:///data/reports.db', convert_unicode=True)
# Next line is the pythonanywhere UNIX config
# engine = create_engine('sqlite:////home/MaxTru/berlinpolicereports/data/reports.db', convert_unicode=True) # UNIX configuration
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    """Method initializes the database and shall be called when the application starts.

    Steps performed:
    1. Delete entire Schema
    2. Set-Up entire Schema
    3. Insert all reports which are found under flaksconfig.Config"""
    logger.info("Database initialization started")
    import webui.database.models
    # First drop all, then create all tables
    Base.metadata.drop_all(bind=engine)
    logger.info("Database schema dropped")
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema re-created")
    # Insert reports from files
    i = 0
    reports_lines = open(os.path.abspath(Config.REPORTS_PAYLOAD), "r").readlines()
    metadata_lines = open(os.path.abspath(Config.REPORTS_METADATA), "r").readlines()
    label_lines = open(os.path.abspath(Config.REPORTS_LABELS), "r").readlines()
    while i < len(reports_lines):
        db_report = webui.database.models.Report(i,
                                                 metadata_lines[i].split(",")[0].strip().decode("utf-8"),
                                                 reports_lines[i][:reports_lines[i].index(".")].strip().decode("utf-8"),
                                                 metadata_lines[i].split(",")[1].strip().decode("utf-8"),
                                                 reports_lines[i][reports_lines[i].index(".") + 1:].strip().decode("utf-8"),
                                                 metadata_lines[i].split(",")[2].strip().decode("utf-8"),
                                                 label_lines[i].strip().decode("utf-8"))
        #print("Insert report with the following ID into the database: " + str(db_report.id))
        db_session.add(db_report)
        i += 1

    db_session.commit()
    logger.info("%s new records inserted into database", str(i))