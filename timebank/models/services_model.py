from timebank.models.models_base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship


class Service(Base):
    __tablename__ = "Service"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=False)
    user_id = Column(Integer(), ForeignKey('User.id'), nullable=False)
    service_time = Column(Integer(), nullable=False)
    avg_rating = Column(Float(), nullable=True)

    User = relationship("User", order_by="User.id", back_populates="Service", cascade="all")
    Serviceregister = relationship("Serviceregister", order_by="Serviceregister.id",
                                   back_populates="Service", cascade="all")

    def __repr__(self):
        return f"Service(id={self.id!r}, fullname={self.title!r}, phone_number={self.description})"
