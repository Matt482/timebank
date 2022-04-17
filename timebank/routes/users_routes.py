from flask import request, jsonify
from sqlalchemy.exc import IntegrityError

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
    # zkontroluj, ze argument id existuje, je typu integer a je vesti nez 0
    if not user_id and type(user_id) is int and 0 < user_id:
        # vrat prazdny retezec s chybou 400 - bad params
        return '', 400

    # vrat z databaze konkretni objekt identifikovany pomoci id zaznamu
    db_query = db.session.query(User)
    obj = db_query.get(user_id)

    if not obj:
        # pokud nebyl objekt nalezen, vrat prazdny retezec a kod 404 - record not found
        return '', 404

    # dopocitej delku vypujcky z data vzniku zaznamu a predpokladaneho data vraceni
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

    # zkontroluj validitu id
    if not user_id and type(user_id) is int and 0 < user_id:
        return '', 400

    # nacti puvodni objekt z db
    db_query = db.session.query(User)
    db_obj = db_query.get(user_id)

    if not db_obj:
        return '', 404

    # zjisti zda byl request proveden pomoci weboveho formulare nebo s daty ve formatu json
    # v ruzny pripadech flask zpristupnuje prijata data v ruznych objektech requestu
    req_data = None
    if request.content_type == 'application/json':
        req_data = request.json
    elif request.content_type == 'application/x-www-form-urlencoded':
        req_data = request.form

    if 'phone' in req_data:
        db_obj.title = req_data['phone']

    if 'user_name' in req_data:
        db_obj.title = req_data['user_name']

    if 'password' in req_data:
        db_obj.password = req_data['password']

    if 'time_account' in req_data:
        try:
            # validuj ze hodnota je number
            is_number(req_data['time_account'])
        except ValidationError:
            # pokud validace neni platna, tak vrat hodnotu chyby a kod 400 - bad param
            return '', 400
        # pokud nedojde k vyjimce, uloz do objektu db
        db_obj.time_account = int(req_data['time_account'])

    try:
        # uloz do db
        db.session.commit()
        # aktualizuj nacteny objekt z db podle aktualniho platneho stavu
        db.session.refresh(db_obj)
    except IntegrityError as e:
        # pokud dojde k vyjimce pri ukladani do db, pak vrat chybu 405 - not allowed
        return jsonify({'error': str(e.orig)}), 405

    return '', 204


@app.route('/api/v1/user/<user_id>', methods=['DELETE'])
def api_single_user_delete(user_id):

    if not user_id and type(user_id) is int and 0 < user_id:
        return '', 400

    # nacti z db konkretni zaznam
    db_query = db.session.query(User)
    db_obj = db_query.filter_by(id=user_id)

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


@app.route('/api/v1/user-create', methods=['POST'])
def api_single_user_create():
    db_obj = User()

    req_data = None
    if request.content_type == 'application/json':
        req_data = request.json
    elif request.content_type == 'application/x-www-form-urlencoded':
        req_data = request.form

    db_obj.phone = req_data['phone']
    db_obj.password = req_data['password']
    db_obj.user_name = req_data['user_name']
    try:
        is_number(req_data['time_account'])
    except ValidationError:
        return '', 400
    db_obj.time_account = req_data['time_account']
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
