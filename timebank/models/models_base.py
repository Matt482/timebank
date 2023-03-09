from sqlalchemy import Enum
import enum
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class RegisterserviceStatusEnum(enum.Enum):
    inprogress = 1
    ended = 2
