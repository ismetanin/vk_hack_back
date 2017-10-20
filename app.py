from flask import Flask, jsonify
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

from api.v1 import api as api_v1

__all__ = ['make_json_app']

def make_json_app(import_name, **kwargs):
    """
    { "message": "405: Method Not Allowed" }
    """
    def make_json_error(ex):
        response = jsonify(message=str(ex))
        response.status_code = (ex.code
                                if isinstance(ex, HTTPException)
                                else 500)
        return response

    app = Flask(import_name, **kwargs)

    for code in default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = make_json_error

    return app

app = make_json_app('vk_hack_back')

app.register_blueprint(api_v1, url_prefix='/v1')

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, ssl_context='adhoc')