from flask import Blueprint, render_template, abort
from functools import wraps
import json
import inspect

api = Blueprint('api', __name__)

def get_user(token):
    client = common.get_db()
    user_id = get_user_id(token)
    return client.get_user_dict(user_id, scope='raw')

def get_user_id(token):
    client = common.get_db()
    user_id = client.get_user_id_by_token(token)
    return user_id

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.args.get('token')

        if token is None:
            data = request.data
            data_dict = json.loads(data)
            token = data_dict['token']

        user_id = get_user_id(token)
        if user_id is None:
            return jsonify({}), 401

        user_id_key = 'user_id'
        user_dict_key = 'user'
        func_arg_names = inspect.getargspec(f).args
        if user_id_key in func_arg_names:
            kwargs[user_id_key] = user_id
        if user_dict_key in func_arg_names:
            kwargs[user_dict_key] = get_user(token)
        return f(*args, **kwargs)
    return decorated_function

from .routes import *
from .categories import *
from .reactions import *
from .events import *