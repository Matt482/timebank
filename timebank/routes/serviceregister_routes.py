import datetime
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from timebank.models.serviceregister_model import Serviceregister
from timebank.models.services_model import Service
from timebank import app, db
from timebank.libs.response_helpers import record_sort_params_handler, get_all_db_objects, is_number, ValidationError, \
    user_exists, service_exists, one_of_enum_status, is_date, calc_avg_rat


@app.route('/api/v1/serviceregister', methods=['GET'])
def api_get_all_service_register():
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
                    avg_rating=obj.Service.avg_rating
                ),
                User=dict(
                    id=obj.User.id,
                    phone=obj.User.phone,
                    user_name=obj.User.user_name,
                    time_account=obj.User.time_account,
                ),
                hours=obj.hours,
                service_status=obj.service_status.name,
                end_time=obj.end_time,
                rating=obj.rating
            ))

        return jsonify(response_obj), 200
    else:
        return '', 404


@app.route('/api/v1/serviceregister/<serviceregister_id>', methods=['GET'])
def api_single_registerservice_get(serviceregister_id):
    # check that argument id exists is int type and bigger than 0
    if not serviceregister_id and type(serviceregister_id) is int and 0 < serviceregister_id:
        # return empty array with error 400 - bad params
        return '', 400

    # return from db specific object identified via id
    db_query = db.session.query(Serviceregister)
    obj = db_query.get(serviceregister_id)

    if not obj:
        # if not obj found return empty array with error 404 - record not found
        return '', 404

    response_obj = [dict(
        id=obj.id,
        note=obj.note,
        Service=dict(
            id=obj.Service.id,
            title=obj.Service.title,
            description=obj.Service.description,
            service_time=obj.Service.service_time,
            avg_rating=obj.Service.avg_rating
        ),
        User=dict(
            id=obj.User.id,
            phone=obj.User.phone,
            user_name=obj.User.user_name,
            time_account=obj.User.time_account,
        ),
        hours=obj.hours,
        service_status=obj.service_status.name,
        end_time=obj.end_time,
        rating=obj.rating
    )]

    response = jsonify(response_obj)
    return response, 200


@app.route('/api/v1/serviceregister/<serviceregister_id>', methods=['PUT'])
def api_single_serviceregister_put(serviceregister_id):

    # check validity of id
    if not serviceregister_id and type(serviceregister_id) is int and 0 < serviceregister_id:
        return '', 400

    db_query = db.session.query(Serviceregister)
    db_obj = db_query.get(serviceregister_id)

    if not db_obj:
        return '', 404

    req_data = None
    if request.content_type == 'application/json':
        req_data = request.json
    elif request.content_type == 'application/x-www-form-urlencoded':
        req_data = request.form

    if 'note' in req_data:
        db_obj.note = req_data['note']

    if 'service_id' in req_data:
        try:
            is_number(req_data['service_id'])
            service_exists(req_data['service_id'])
        except ValidationError:
            return '', 400
        db_obj.service_id = int(req_data['service_id'])

    if 'customer_id' in req_data:
        try:
            is_number(req_data['customer_id'])
            user_exists(req_data['customer_id'])
        except ValidationError:
            return '', 400
        db_obj.customer_id = int(req_data['customer_id'])

    if 'hours' in req_data:
        try:
            is_number(req_data['hours'])
        except ValidationError:
            return '', 400
        db_obj.hours = int(req_data['hours'])

    if 'service_status' in req_data:
        try:
            one_of_enum_status(req_data['service_status'])
        except ValidationError:
            return '', 400
        db_obj.service_status = req_data['service_status']

    end_time = None
    if 'end_time' in req_data and len(req_data['end_time']) > 0:
        end_time = datetime.datetime.now()
        db_obj.end_time = end_time

    try:
        db.session.commit()
        db.session.refresh(db_obj)
    except IntegrityError as e:
        return jsonify({'error': str(e.orig)}), 405

    return '', 204


@app.route('/api/v1/serviceregister/<serviceregister_id>', methods=['DELETE'])
def api_single_registerservice_delete(serviceregister_id):

    if not serviceregister_id and type(serviceregister_id) is int and 0 < serviceregister_id:
        return '', 400

    db_query = db.session.query(Serviceregister)
    db_obj_del = db_query.filter_by(id=serviceregister_id)
    db_obj = db_query.get(serviceregister_id)
    servis_reg_id = db_obj.service_id
    print(servis_reg_id)

    if not db_obj:
        return '', 404

    try:
        db_obj_del.delete()
        db.session.commit()
    except IntegrityError as e:
        return jsonify({'error': str(e.orig)}), 405

    print("IDEME RATAT AVG RATING!!!!")
    objec = db.session.query(Serviceregister)
    serv_count = 0
    avg_rat = 0
    print('ideme iterovat!')
    for x in objec:

        if x.service_id == int(servis_reg_id):
            print("BINGO MAME TA!!!")
            avg_rat += x.rating
            serv_count += 1
    try:
        final_rat = round(avg_rat / serv_count, 1)

    except ZeroDivisionError as ze:
        raise ze

    db_query = db.session.query(Service)
    obj = db_query.get(servis_reg_id)
    print("avg rating is: ", obj.avg_rating)

    print("avg final rat is: ", final_rat)
    obj.avg_rating = final_rat
    print("avg final rat for our object is: ", obj.avg_rating)
    db.session.commit()

    return '', 204


@app.route('/api/v1/serviceregister-create', methods=['POST'])
def api_single_serviceregister_create():
    db_obj = Serviceregister()

    req_data = None
    if request.content_type == 'application/json':
        req_data = request.json
    elif request.content_type == 'application/x-www-form-urlencoded':
        req_data = request.form

    db_obj.note = req_data['note']

    try:
        is_number(req_data['service_id'])
        service_exists(req_data['service_id'])
    except ValidationError:
        return 'sasasa', 400
    db_obj.service_id = req_data['service_id']

    try:
        is_number(req_data['consumer_id'])
        user_exists(req_data['consumer_id'])
    except ValidationError:
        return 'bababa', 400
    db_obj.consumer_id = req_data['consumer_id']

    try:
        one_of_enum_status(req_data['service_status'])
    except ValidationError:
        return 'wawawa', 400

    db_obj.service_status = req_data['service_status']

    end_time = datetime.datetime.now()
    db_obj.end_time = end_time

    # add rating for creating service reg
    rating = req_data['rating']
    if rating not in range(0, 6):
        return "zazaza", 400
    else:
        db_obj.rating = rating

    try:
        db.session.add(db_obj)
        db.session.commit()
        # renewal obj from db, so it show relation and id
        db.session.refresh(db_obj)
    except IntegrityError as e:
        return jsonify({'error': str(e.orig)}), 405

    #####################################################################################
    print("IDEME RATAT AVG RATING!!!!")
    serv_id = req_data['service_id']
    db_query = db.session.query(Service)
    obj = db_query.get(serv_id)

    #calc rating by func!!!
    objec = db.session.query(Serviceregister)
    serv_count = 0
    avg_rat = 0
    for x in objec:
        if x.service_id == int(serv_id):
            avg_rat += x.rating
            serv_count += 1
    try:
        final_rat = round(avg_rat / serv_count, 1)
    except ZeroDivisionError as ze:
        raise ze

    obj.avg_rating = final_rat
    db.session.commit()
    db.session.refresh(obj)
    print(obj.avg_rating)
    return "", 200
