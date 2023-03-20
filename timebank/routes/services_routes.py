from flask import request, jsonify
from sqlalchemy.exc import IntegrityError

from timebank.models.services_model import Service
from timebank.models.serviceregister_model import Serviceregister
from timebank import app, db
from timebank.libs.response_helpers import record_sort_params_handler, get_all_db_objects, is_number, ValidationError, \
    user_exists, calc_avg_rat


@app.route('/api/v1/services', methods=['GET'])
def api_services():
    sort_field, sort_dir, valid = record_sort_params_handler(request.args, Service)
    if not valid:
        return '', 400
    db_objs = get_all_db_objects(sort_field, sort_dir, db.session.query(Service)).all()

    if len(db_objs):
        response_obj = []
        for obj in db_objs:
            response_obj.append(dict(
                id=obj.id,
                title=obj.title,
                description=obj.description,
                User=dict(
                    id=obj.User.id,
                    phone=obj.User.phone,
                    user_name=obj.User.user_name,
                    time_account=obj.User.time_account,
                ),
                service_time=obj.service_time,
                avg_rating=obj.avg_rating
            ))

        return jsonify(response_obj), 200
    else:
        return '', 404


@app.route('/api/v1/service/<services_id>', methods=['GET'])
def api_single_service_get(services_id):
    # check that argument id exists is int type and bigger than 0
    if not services_id and type(services_id) is int and 0 < services_id:
        # return empty array with error 400 - bad params
        return '', 400

    # return from db specific object identified via id
    db_query = db.session.query(Service)
    obj = db_query.get(services_id)

    if not obj:
        # if not obj found return empty array with error 404 - record not found
        return '', 404

    response_obj = [dict(
        id=obj.id,
        title=obj.title,
        description=obj.description,
        User=dict(
            id=obj.User.id,
            phone=obj.User.phone,
            user_name=obj.User.user_name,
            time_account=obj.User.time_account,
        ),
        service_time=obj.service_time,
        avg_rating=obj.avg_rating
    )]

    response = jsonify(response_obj)
    return response, 200


@app.route('/api/v1/service/<services_id>', methods=['PUT'])
def api_single_service_put(services_id):

    # check id validation
    if not services_id and type(services_id) is int and 0 < services_id:
        return '', 400

    # load obj from db
    db_query = db.session.query(Service)
    db_obj = db_query.get(services_id)

    if not db_obj:
        return '', 404

    # check if request was made via web form or via data in json format
    # in diff scenarios flask makes available coming data in diff obj request
    req_data = None
    if request.content_type == 'application/json':
        req_data = request.json
    elif request.content_type == 'application/x-www-form-urlencoded':
        req_data = request.form

    # will process field user_id, if entered, change value
    if 'user_id' in req_data:
        try:
            is_number(req_data['user_id'])
            # valid if user exists in db
            user_exists(req_data['user_id'])
        except ValidationError:
            # if validation not valid than return error with code 400 - bad param
            return '', 400
        db_obj.user_id = int(req_data['user_id'])

    if 'title' in req_data:
        db_obj.title = req_data['title']

    if 'description' in req_data:
        db_obj.description = req_data['description']

    if 'service_time' in req_data:
        db_obj.service_time = req_data['service_time']

    try:
        # save to db
        db.session.commit()
        # renewal obj from db, so it show relation and id
        db.session.refresh(db_obj)
    except IntegrityError as e:
        # if exception occurs in saving to db return 405 - not allowed
        return jsonify({'error': str(e.orig)}), 405

    return '', 204


@app.route('/api/v1/service/<services_id>', methods=['DELETE'])
def api_single_service_delete(services_id):

    if not services_id and type(services_id) is int and 0 < services_id:
        return '', 400

    db_query = db.session.query(Service)
    db_obj = db_query.filter_by(id=services_id)

    if not db_obj:
        return '', 404

    try:
        db_obj.delete()
        db.session.commit()
    except IntegrityError as e:
        return jsonify({'error': str(e.orig)}), 405
    else:
        return '', 204


@app.route('/api/v1/service-create', methods=['POST'])
def api_single_service_create():
    serv_db_obj = Service()

    req_data = None
    if request.content_type == 'application/json':
        req_data = request.json
    elif request.content_type == 'application/x-www-form-urlencoded':
        req_data = request.form

    try:
        is_number(req_data['user_id'])
        user_exists(req_data['user_id'])
    except ValidationError:
        return '', 400
    serv_db_obj.user_id = int(req_data['user_id'])
    serv_db_obj.title = req_data['title']
    serv_db_obj.description = req_data['description']
    try:
        is_number(req_data['service_time'])
    except ValidationError:
        return '', 400
    serv_db_obj.service_time = req_data['service_time']
    try:
        db.session.add(serv_db_obj)
        db.session.commit()
        db.session.refresh(serv_db_obj)
    except IntegrityError as e:
        return jsonify({'error': str(e.orig)}), 405

    return '', 201


@app.route('/api/v1/trying/<serviceregister_id>', methods=['GET'])
def get_avg_rat(serviceregister_id):

    obj = db.session.query(Serviceregister)
    serv_count = 0
    avg_rat = 0
    for x in obj:
        if x.service_id == int(serviceregister_id):
            avg_rat += x.rating
            serv_count += 1
    try:
        final_rat = round(avg_rat / serv_count, 1)
    except ZeroDivisionError as ze:
        raise ze

    serv = db.session.query(Service).where(Service.id == obj.service_id)
    serv.avg_rating = final_rat
    db.session.commit()
    return "", 200
