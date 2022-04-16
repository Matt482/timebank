from flask import request, jsonify
from timebank.models.users_model import User
from timebank import app, db
from timebank.libs.response_helpers import record_sort_params_handler, get_all_db_objects


@app.route('/api/v1/users', methods=['GET'])
def api_users():
    sort_field, sort_dir, valid = record_sort_params_handler(request.args, User)
    if not valid:
        return '', 400
    db_objs = get_all_db_objects(sort_field, sort_dir, db.session.query(User)).all()

    if len(db_objs):
        response_obj = []
        for obj in db_objs:
            response_obj.append(dict(
                id=obj.id,
                phone=obj.phone,
                user_name=obj.user_name,
                time_account=obj.time_account,
            ))

        return jsonify(response_obj), 200
    else:
        return '', 404
