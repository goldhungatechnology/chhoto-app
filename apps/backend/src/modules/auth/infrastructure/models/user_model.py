
from src.shared.infrastructure.db import Base

# TODO: Define ORM schemas mapping to database tables.
# Keep SQLAlchemy structures separated from pure business domain entities.


class UserModel(Base):
    """
    SQLAlchemy database model for User mapping to standard DB columns.
    """

    __tablename__ = "sys_auth_users"

    # Example setup:
    # id = Column(Integer, primary_key=True)
    # email = Column(String(255), unique=True, nullable=False)
    # password_hash = Column(String(255), nullable=False)
    pass
