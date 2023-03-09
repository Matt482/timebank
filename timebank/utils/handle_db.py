from sqlalchemy import create_engine

from timebank.models.models_base import Base

# engine = create_engine("mysql+pymysql://mato:Matomato1@localhost:3306/timebank?charset=utf8mb4")
engine = create_engine("mysql+pymysql://root:root@localhost:3306/testdatabase?charset=utf8mb4")

# drop tables
Base.metadata.drop_all(engine)

# populate DB
Base.metadata.create_all(engine)
