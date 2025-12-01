from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Calendar(Base):
    __tablename__ = "calendars"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="calendars")

    def __repr__(self):
        return f"<Calendar(id={self.id}, user_id={self.user_id})>"