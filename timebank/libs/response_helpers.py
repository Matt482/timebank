import datetime
import hashlib

from sqlalchemy import inspect, text

from timebank import app, db
from timebank.models.users_model import User
from timebank.models.services_model import Service
from timebank.models.models_base import RegisterserviceStatusEnum


def record_sort_params_handler(args, modeldb):
    valid = True
    if args.get('field'):
        sort_field = args.get('field')
    else:
        sort_field = 'id'

    if args.get('sort'):
        sort_dir = args.get('sort')
    else:
        sort_dir = 'asc'

    if not (sort_dir == 'asc' or sort_dir == 'desc'):
        valid = False

    if sort_field:
        col_exist = False
        for col in [column.name for column in inspect(modeldb).columns]:
            if col == sort_field:
                col_exist = True
        if not col_exist:
            valid = False

    return sort_field, sort_dir, valid


def get_all_db_objects(sort_field, sort_dir, base_query):
    sort_query = base_query.order_by(text(sort_field + ' ' + sort_dir))
    return sort_query


def calculate_borrow_duration(start_date, end_date):
    if not start_date or type(start_date) is not datetime.date:
        return None
    if not end_date or type(start_date) is not datetime.date:
        return None
    return abs((end_date - start_date).days)


def format_date(date):
    if date is None:
        return date
    else:
        date = date.isoformat()
        return date


class ValidationError(Exception):
    def __init__(self, value, message):
        self.value = str(value)
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.value} -> {self.message}'


def is_number(field):
    try:
        int(field)
    except ValueError:
        raise ValidationError(field, 'Number is not valid.')


def user_exists(field):
    if not db.session.query(User).get(field):
        raise ValidationError(field, 'User id does not exist.')


def service_exists(field):
    if not db.session.query(Service).get(field):
        raise ValidationError(field, 'Service id does not exist.')


def one_of_enum_status(field):
    db_objs = RegisterserviceStatusEnum
    exist = False
    for db_obj in db_objs:
        if db_obj.name == field:
            exist = True

    if not exist:
        raise ValidationError(field, 'Status is not valid.')


def is_date(field, date_format='%Y-%m-%d'):
    if field:
        try:
            date = datetime.datetime.strptime(str(field), date_format).date()
        except ValueError:
            raise ValidationError(field, f"Incorrect data format, should be {date_format}")


def calc_avg_rat(model, reg_id):
    serv_count = 0
    avg_rat = 0
    for x in model:
        if x.id == int(reg_id):
            avg_rat += x.avg_rating
            serv_count += 1
    final_rat = round(avg_rat/serv_count, 1)
    return final_rat
