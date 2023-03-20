from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from passlib.hash import pbkdf2_sha256

from timebank.models.users_model import User
from timebank import app, db
from timebank.libs.response_helpers import record_sort_params_handler, get_all_db_objects, is_number, ValidationError


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


@app.route('/api/v1/user/<user_id>', methods=['GET'])
def api_single_user_get(user_id):
    # check that argument id exists is int type and bigger than 0
    if not user_id and type(user_id) is int and 0 < user_id:
        # return empty array with error 400 - bad params
        return '', 400

    # return from db specific object identified via id
    db_query = db.session.query(User)
    obj = db_query.get(user_id)

    if not obj:
        # if not obj found return empty array with error 404 - record not found
        return '', 404

    response_obj = [dict(
        id=obj.id,
        phone=obj.phone,
        user_name=obj.user_name,
        time_account=obj.time_account,
    )]

    response = jsonify(response_obj)
    return response, 200


@app.route('/api/v1/user/<user_id>', methods=['PUT'])
def api_single_user_put(user_id):

    # check id validation
    if not user_id and type(user_id) is int and 0 < user_id:
        return '', 400

    # load obj from db
    db_query = db.session.query(User)
    db_obj = db_query.get(user_id)

    if not db_obj:
        return '', 404

    # check if request was made via web form or via data in json format
    # in diff scenarios flask makes available coming data in diff obj request
    req_data = None
    if request.content_type == 'application/json':
        req_data = request.json
    elif request.content_type == 'application/x-www-form-urlencoded':
        req_data = request.form

    if 'phone' in req_data:
        db_obj.phone = req_data['phone']

    if 'user_name' in req_data:
        db_obj.user_name = req_data['user_name']

    if 'password' in req_data:
        hash_pw = pbkdf2_sha256.hash(req_data['password'])
        db_obj.password = hash_pw

    if 'time_account' in req_data:
        try:
            # valid if value is a number
            is_number(req_data['time_account'])
        except ValidationError:
            # if not valid return 400 - bad param
            return '', 400
        # if no except save to obj in db
        db_obj.time_account = int(req_data['time_account'])

    try:
        # save to db
        db.session.commit()
        # update loaded obj from db according actual valid state
        db.session.refresh(db_obj)
    except IntegrityError as e:
        # if exception occurs in saving to db return 405 - not allowed
        return jsonify({'error': str(e.orig)}), 405

    return '', 204


@app.route('/api/v1/user/<user_id>', methods=['DELETE'])
def api_single_user_delete(user_id):

    if not user_id and type(user_id) is int and 0 < user_id:
        return '', 400

    # load record from db
    db_query = db.session.query(User)
    db_obj = db_query.filter_by(id=user_id)

    if not db_obj:
        return '', 404

    try:
        # delete record
        db_obj.delete()
        # save operation to db
        db.session.commit()
    except IntegrityError as e:
        return jsonify({'error': str(e.orig)}), 405
    else:
        return '', 204


@app.route('/api/v1/user-create', methods=['POST'])
def api_single_user_create():
    db_obj = User()

    req_data = None
    if request.content_type == 'application/json':
        req_data = request.json
    elif request.content_type == 'application/x-www-form-urlencoded':
        req_data = request.form

    db_obj.phone = req_data['phone']
    hash_pw = pbkdf2_sha256.hash(req_data['password'])
    db_obj.password = hash_pw
    db_obj.user_name = req_data['user_name']
    try:
        is_number(req_data['time_account'])
    except ValidationError:
        return '', 400
    db_obj.time_account = req_data['time_account']
    try:
        # add record to db
        db.session.add(db_obj)
        # save record to db
        db.session.commit()
        # renewal obj from db, so it show relation and id
        db.session.refresh(db_obj)
    except IntegrityError as e:
        return jsonify({'error': str(e.orig)}), 405

    return '', 201
