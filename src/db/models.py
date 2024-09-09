import json
from sqlalchemy import String, Integer, Column, DateTime, JSON
from datetime import datetime, timezone
from .database import Base


class VideoSnippet(Base):
    """SQLAlchemy ORM class that represents a video_snippet table in the SQLite DB"""

    __tablename__ = "video_snippet"

    id = Column(Integer, primary_key=True)
    snippetTitle = Column(String(40), nullable=False)
    thumbnailTitle = Column(String(40), nullable=False)
    created = Column(DateTime, default=datetime.now(timezone.utc))
    description = Column(String(150), nullable=True)

    def __init__(
        self,
        snippet_title: str,
        thumbnail_title: str,
        description: str,
        created: datetime = datetime.now(),
    ):
        self.snippetTitle = snippet_title
        self.thumbnailTitle = thumbnail_title
        self.created = created
        self.description = description

    def __repr__(self) -> str:
        return f"<VideoSnippet {self.snippetTitle!r}>"


class Labels(Base):
    """SQLAlchemy ORM class that represents a labels table in the SQLite DB"""

    __tablename__ = "labels"

    id = Column(Integer, primary_key=True)
    labelsJson = Column(JSON, nullable=False, default={})

    def __init__(self, labels_dict: dict = {}):
        self.labelsJson = labels_dict

    def __repr__(self) -> str:
        return f"<Labels {self.id!r}>"


class EmailRecipient(Base):
    """SQLAlchemy ORM class that represents a email_recipients table in the SQLite DB"""

    __tablename__ = "email_recipients"

    id = Column(Integer, primary_key=True)
    emailAddress = Column(String(100), nullable=False, unique=True)

    def __init__(self, email_address: str) -> None:
        self.emailAddress = email_address

    def __repr__(self) -> str:
        return f"<EmailRecipient {self.emailAddress!r}>"
