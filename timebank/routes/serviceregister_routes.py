import datetime
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from timebank.models.serviceregister_model import Serviceregister
from timebank import app, db
from timebank.libs.response_helpers import record_sort_params_handler, get_all_db_objects, is_number, ValidationError, \
    user_exists, service_exists, one_of_enum_status, is_date


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
    # zkontroluj, ze argument id existuje, je typu integer a je vesti nez 0
    if not serviceregister_id and type(serviceregister_id) is int and 0 < serviceregister_id:
        # vrat prazdny retezec s chybou 400 - bad params
        return '', 400

    # vrat z databaze konkretni objekt identifikovany pomoci id zaznamu
    db_query = db.session.query(Serviceregister)
    obj = db_query.get(serviceregister_id)

    if not obj:
        # pokud nebyl objekt nalezen, vrat prazdny retezec a kod 404 - record not found
        return '', 404

    # dopocitej delku vypujcky z data vzniku zaznamu a predpokladaneho data vraceni
    response_obj = [dict(
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
        end_time=obj.end_time,
        rating=obj.rating
    )]

    response = jsonify(response_obj)
    return response, 200


@app.route('/api/v1/serviceregister/<serviceregister_id>', methods=['PUT'])
def api_single_serviceregister_put(serviceregister_id):

    # zkontroluj validitu id
    if not serviceregister_id and type(serviceregister_id) is int and 0 < serviceregister_id:
        return '', 400

    # nacti puvodni objekt z db
    db_query = db.session.query(Serviceregister)
    db_obj = db_query.get(serviceregister_id)

    if not db_obj:
        return '', 404

    # zjisti zda byl request proveden pomoci weboveho formulare nebo s daty ve formatu json
    # v ruzny pripadech flask zpristupnuje prijata data v ruznych objektech requestu
    req_data = None
    if request.content_type == 'application/json':
        req_data = request.json
    elif request.content_type == 'application/x-www-form-urlencoded':
        req_data = request.form

    if 'note' in req_data:
        db_obj.note = req_data['note']

    if 'service_id' in req_data:
        try:
            # validuj ze hodnota je number
            is_number(req_data['service_id'])
            # validuj ze uzivatel v db existuje
            service_exists(req_data['service_id'])
        except ValidationError:
            # pokud validace neni platna, tak vrat hodnotu chyby a kod 400 - bad param
            return '', 400
        # pokud nedojde k vyjimce, uloz do objektu db
        db_obj.service_id = int(req_data['service_id'])

    if 'customer_id' in req_data:
        try:
            # validuj ze hodnota je number
            is_number(req_data['customer_id'])
            # validuj ze uzivatel v db existuje
            user_exists(req_data['customer_id'])
        except ValidationError:
            # pokud validace neni platna, tak vrat hodnotu chyby a kod 400 - bad param
            return '', 400
        # pokud nedojde k vyjimce, uloz do objektu db
        db_obj.customer_id = int(req_data['customer_id'])

    if 'hours' in req_data:
        try:
            # validuj ze hodnota je number
            is_number(req_data['hours'])
        except ValidationError:
            # pokud validace neni platna, tak vrat hodnotu chyby a kod 400 - bad param
            return '', 400
        # pokud nedojde k vyjimce, uloz do objektu db
        db_obj.hours = int(req_data['hours'])

    if 'service_status' in req_data:
        try:
            one_of_enum_status(req_data['service_status'])
        except ValidationError:
            return '', 400
        db_obj.service_status = req_data['service_status']

    end_time = None
    if 'end_time' in req_data and len(req_data['end_time']) > 0:
        # try:
        #     is_date(req_data['end_time'])
        #     end_time = datetime.datetime.strptime(str(req_data['end_time']), '%Y-%m-%d').date()
        # except ValidationError:
        #     return '', 400
        end_time = datetime.datetime.now()
        db_obj.end_time = end_time

    try:
        # uloz do db
        db.session.commit()
        # aktualizuj nacteny objekt z db podle aktualniho platneho stavu
        db.session.refresh(db_obj)
    except IntegrityError as e:
        # pokud dojde k vyjimce pri ukladani do db, pak vrat chybu 405 - not allowed
        return jsonify({'error': str(e.orig)}), 405

    return '', 204


@app.route('/api/v1/serviceregister/<serviceregister_id>', methods=['DELETE'])
def api_single_registerservice_delete(serviceregister_id):

    if not serviceregister_id and type(serviceregister_id) is int and 0 < serviceregister_id:
        return '', 400

    # nacti z db konkretni zaznam
    db_query = db.session.query(Serviceregister)
    db_obj = db_query.filter_by(id=serviceregister_id)

    if not db_obj:
        return '', 404

    try:
        # smaz zaznam
        db_obj.delete()
        # uloz operaci do db
        db.session.commit()
    except IntegrityError as e:
        return jsonify({'error': str(e.orig)}), 405
    else:
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

    # try:
    #     end_time = datetime.datetime.strptime(str(req_data['end_time']), '%Y-%m-%d').date()
    #     is_date(req_data['end_time'])
    # except ValidationError:
    #     return 'dadada', 400

    end_time = datetime.datetime.now()
    db_obj.end_time = end_time

    #Pridaj rating na vytvorenie service registra
    rating = req_data['rating']
    if rating not in range(0, 6):
        return "zazaza", 400
    else:
        db_obj.rating = rating

    try:
        # pridej zaznam do tabulky
        db.session.add(db_obj)
        # uloz zaznam do db
        db.session.commit()
        # obnov objekt z db, tak aby se zorbazili relace a id
        db.session.refresh(db_obj)
    except IntegrityError as e:
        return jsonify({'error': str(e.orig)}), 405

    return '', 201
