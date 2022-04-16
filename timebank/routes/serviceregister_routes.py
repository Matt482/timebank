from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from timebank.models.models_base import RegisterserviceStatusEnum
from timebank.models.serviceregister_model import Serviceregister
from timebank import app, db
from timebank.libs.response_helpers import record_sort_params_handler, get_all_db_objects, is_number, ValidationError, \
    user_exists


@app.route('/api/v1/serviceregister', methods=['GET'])
def api_get_all_service_register():
    pass
    sort_field, sort_dir, valid = record_sort_params_handler(request.args, Serviceregister)
    if not valid:
        return '', 400
    db_objs = get_all_db_objects(sort_field, sort_dir, db.session.query(Serviceregister)).all()

    if len(db_objs):
        response_obj = []
        for obj in db_objs:
            response_obj.append(dict(
                id=obj.id,
                note=obj.note,
                Service=dict(
                    id=obj.Service.id,
                    title=obj.Service.title,
                    description=obj.Service.description,
                    service_time=obj.Service.service_time,
                ),
                User=dict(
                    id=obj.User.id,
                    phone=obj.User.phone,
                    user_name=obj.User.user_name,
                    time_account=obj.User.time_account,
                ),
                hours=obj.hours,
                service_status=obj.service_status.name,
                end_time=obj.end_time
            ))

        return jsonify(response_obj), 200
    else:
        return '', 404
