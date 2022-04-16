import datetime
import hashlib

from sqlalchemy import inspect, text

from timebank import app, db
from timebank.models.users_model import User


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