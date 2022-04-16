from datetime import datetime, timezone, timedelta
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, set_access_cookies, get_jwt
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
if app.config["ENV"] == "production":
    app.config.from_object("timebank.utils.config.ProductionConfig")
else:
    app.config.from_object("timebank.utils.config.DevelopmentConfig")

db = SQLAlchemy(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
jwt = JWTManager(app)


@app.after_request
def add_header(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    response.headers.add('X-Content-Type-Options', 'nosniff')

    if response.content_type == '':
        response.content_type = 'application/json'

    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response


import timebank.models
import timebank.routes
import timebank.utils


import timebank.utils.dump_db
import timebank.utils.fill_db
