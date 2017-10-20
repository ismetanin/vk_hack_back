from flask import Flask, jsonify

from . import *

items = [
    {
        'id': 1,
        'title': u'First item'
    },
    {
        'id': 2,
        'title': u'Second item'
    }
]

@api.route('/items', methods=['GET'])
def get_tasks():
    return jsonify({'items': items})