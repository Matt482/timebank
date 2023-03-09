import csv
from timebank import app, db

from timebank.models.users_model import User
from timebank.models.services_model import Service
from timebank.models.serviceregister_model import Serviceregister

models = [User, Service, Serviceregister]


@app.cli.command("fill_db")
def fill_db():
    for modeldb in models:
        db.session.query(modeldb).delete()
        db.session.commit()
        with open(f'timebank/data/db-mock/{modeldb.__tablename__}.csv', 'r', encoding='utf-8') as infile:
            incsv = csv.DictReader(infile)
            rows = []
            for row in incsv:
                row = {k: v if v else None for k, v in row.items()}
                rows.append(row)
            obj_list = []
            for record in rows:
                data_obj = modeldb(**record)
                obj_list.append(data_obj)
            db.session.bulk_save_objects(obj_list)
            db.session.commit()
            print(f'table {modeldb.__tablename__} loaded from file {infile.name}')
