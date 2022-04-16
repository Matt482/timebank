from flask import request, jsonify
from sqlalchemy.exc import IntegrityError

from timebank.models.services_model import Service
from timebank import app, db
from timebank.libs.response_helpers import record_sort_params_handler, get_all_db_objects, is_number, ValidationError, \
    user_exists


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
                service_time=obj.service_time
            ))

        return jsonify(response_obj), 200
    else:
        return '', 404


@app.route('/api/v1/service-create', methods=['POST'])
def api_single_borrow():
    sort_field, sort_dir, valid = record_sort_params_handler(request.args, Service)
    db_obj = Service()
    db_objs = get_all_db_objects(sort_field, sort_dir, db.session.query(Service)).all()

    req_data = None
    if request.content_type == 'application/json':
        req_data = request.json
    elif request.content_type == 'application/x-www-form-urlencoded':
        req_data = request.form

    # for obj in db_objs:
    #     if int(req_data['book_id']) == int(obj.book.id):
    #         return 'Book is not available anymore!', 404
    try:
        is_number(req_data['user_id'])
        user_exists(req_data['user_id'])
    except ValidationError as e:
        return e, 400
    db_obj.user_id = int(req_data['user_id'])
    db_obj.title = req_data['title']
    db_obj.description = req_data['description']
    try:
        is_number(req_data['service_time'])
    except ValidationError as e:
        return e, 400
    db_obj.service_time = req_data['service_time']
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


@app.route('/api/v1/service/<services_id>', methods=['GET'])
def api_single_service_get(services_id):
    # zkontroluj, ze argument id existuje, je typu integer a je vesti nez 0
    if not services_id and type(services_id) is int and 0 < services_id:
        # vrat prazdny retezec s chybou 400 - bad params
        return '', 400

    # vrat z databaze konkretni objekt identifikovany pomoci id zaznamu
    db_query = db.session.query(Service)
    obj = db_query.get(services_id)

    if not obj:
        # pokud nebyl objekt nalezen, vrat prazdny retezec a kod 404 - record not found
        return '', 404

    # dopocitej delku vypujcky z data vzniku zaznamu a predpokladaneho data vraceni
    response_obj = [dict(
        id=obj.id,
        title=obj.title,
        description=obj.description,
        User=dict(
            id=obj.User.id,
            phone=obj.User.phone,
            user_name=obj.User.user_name,
            time_account=obj.User.time_account,
        )
    )]

    response = jsonify(response_obj)
    return response, 200


@app.route('/api/v1/service/<services_id>', methods=['PUT'])
def api_single_service_put(services_id):

    # zkontroluj validitu id
    if not services_id and type(services_id) is int and 0 < services_id:
        return '', 400

    # nacti puvodni objekt z db
    db_query = db.session.query(Service)
    db_obj = db_query.get(services_id)

    if not db_obj:
        return '', 404

    # zjisti zda byl request proveden pomoci weboveho formulare nebo s daty ve formatu json
    # v ruzny pripadech flask zpristupnuje prijata data v ruznych objektech requestu
    req_data = None
    if request.content_type == 'application/json':
        req_data = request.json
    elif request.content_type == 'application/x-www-form-urlencoded':
        req_data = request.form

    # zpracuje pole user_id, pokud je zadane, tak zmen hodnotu
    if 'user_id' in req_data:
        try:
            # validuj ze hodnota je number
            is_number(req_data['user_id'])
            # validuj ze uzivatel v db existuje
            user_exists(req_data['user_id'])
        except ValidationError as e:
            # pokud validace neni platna, tak vrat hodnotu chyby a kod 400 - bad param
            return e, 400
        # pokud nedojde k vyjimce, uloz do objektu db
        db_obj.user_id = int(req_data['user_id'])

    if 'title' in req_data:
        db_obj.title = req_data['title']

    if 'description' in req_data:
        db_obj.title = req_data['description']

    if 'service_time' in req_data:
        db_obj.service_time = req_data['service_time']

    try:
        # uloz do db
        db.session.commit()
        # aktualizuj nacteny objekt z db podle aktualniho platneho stavu
        db.session.refresh(db_obj)
    except IntegrityError as e:
        # pokud dojde k vyjimce pri ukladani do db, pak vrat chybu 405 - not allowed
        return jsonify({'error': str(e.orig)}), 405

    return '', 204


@app.route('/api/v1/service/<services_id>', methods=['DELETE'])
def api_single_service_delete(services_id):

    if not services_id and type(services_id) is int and 0 < services_id:
        return '', 400

    # nacti z db konkretni zaznam
    db_query = db.session.query(Service)
    db_obj = db_query.filter_by(id=services_id)

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
