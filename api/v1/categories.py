# coding=utf-8

from flask import Flask, jsonify, abort, request 
import json
from . import api, login_required
import api.common as common


categories = [
    { 'id': u'cinema', 'type': u'cinema', 'title': u'Кино', },
    { 'id': u'sport', 'type': u'sport', 'title': u'Спорт', },
    { 'id': u'festival', 'type': u'festival', 'title': u'Фестиваль', },
    { 'id': u'culture', 'type': u'culture', 'title': u'Культура', },
    { 'id': u'humor', 'type': u'humor', 'title': u'Юмор', },
    { 'id': u'concert', 'type': u'concert', 'title': u'Концерт', },
    { 'id': u'food', 'type': u'food', 'title': u'Еда', },
    { 'id': u'games', 'type': u'games', 'title': u'Игры', },
]

@api.route('/categories', methods=['GET'])
@login_required
def get_categories():
    return jsonify({'result': categories})
