from sqlalchemy import create_engine

from timebank.models.models_base import Base

engine = create_engine("mysql+pymysql://root:Bootcamp2022@localhost:3306/Timebank?charset=utf8mb4")

# drop tables
Base.metadata.drop_all(engine)

# populate DB
Base.metadata.create_all(engine)
