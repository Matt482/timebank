from timebank.models.models_base import Base, RegisterserviceStatusEnum
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship


class Serviceregister(Base):
    __tablename__ = "Serviceregister"
    id = Column(Integer, primary_key=True, autoincrement=True)
    note = Column(String(200), nullable=False)
    service_id = Column(Integer(), ForeignKey('Service.id'), nullable=False)
    consumer_id = Column(Integer(), ForeignKey('User.id'), nullable=False)
    hours = Column(Integer())
    service_status = Column(Enum(RegisterserviceStatusEnum), nullable=False)
    end_time = Column(Date())
    rating = Column(Integer(), nullable=True)

    User = relationship("User", order_by="User.id", back_populates="Serviceregister", cascade="all")
    Service = relationship("Service", order_by="Service.id", back_populates="Serviceregister", cascade="all")

    def __repr__(self):
        return f"Serviceregister(id={self.id!r}, note={self.note}, service_status={self.service_status!r})"
