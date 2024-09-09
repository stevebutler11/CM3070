from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

from src.detector.coco_names import coco_names

engine = create_engine("sqlite:///instance/surveillance.db")

# create a scoped session, so can be referenced from outside flask app context
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    """Initialise the SQLite DB with SQLAlchemy ORM"""
    # import all SQLAlchemy modules so they are set up correctly
    from .models import VideoSnippet, Labels, EmailRecipient

    Base.metadata.create_all(bind=engine)

    # ensure necessary data is set beforehand
    if db_session.query(Labels).first() is None:
        starting_labels = {l: False for l in coco_names}
        # need to detect at least something
        starting_labels['person'] = True
        db_session.add(Labels(labels_dict=starting_labels))
        db_session.commit()
