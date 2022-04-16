from sqlalchemy import Enum
from sqlalchemy.inspection import inspect

import csv
from timebank import app, db

from timebank.models.users_model import User
from timebank.models.services_model import Service
from timebank.models.serviceregister_model import Serviceregister

models = [User, Service, Serviceregister]


@app.cli.command("dump_db")
def dump_db():
    for modeldb in models:
        records = db.session.query(modeldb).all()
        if len(records) > 0:
            with open(f'timebank/data/db-mock/{modeldb.__tablename__}.csv', 'w', encoding='utf-8') as outfile:
                outcsv = csv.writer(outfile)
                headerrow = [column.name for column in inspect(modeldb).columns]
                outcsv.writerow(headerrow)
                for curr in records:
                    colval = []
                    for column in modeldb.__mapper__.columns:
                        if type(column.type) is Enum:
                            val = getattr(curr, column.name).name
                        else:
                            val = getattr(curr, column.name)
                        colval.append(val)
                    outcsv.writerow(colval)
                print(f'table {modeldb.__tablename__} dumped to file {outfile.name}')
