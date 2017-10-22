# coding=utf-8

from flask import Flask, jsonify, abort, request 
import json
from . import api, login_required
import api.common as common


categories = [
    { 'id': u'cinema', 'type': u'cinema', 'title': u'Кино', },
    { 'id': u'ball', 'type': u'culture', 'title': u'Культура', },
    { 'id': u'sport', 'type': u'sport', 'title': u'Спорт', },
    { 'id': u'festival', 'type': u'festival', 'title': u'Фестиваль', },
    { 'id': u'kvn', 'type': u'humor', 'title': u'Юмор', },
    { 'id': u'concert', 'type': u'concert', 'title': u'Концерт', },
    { 'id': u'speed-dating', 'type': u'food', 'title': u'Еда', },
    { 'id': u'games', 'type': u'games', 'title': u'Игры', },
]

def filter_valid_categories(categories_list):
    accepted_ids = set([category['id'] for category in categories])
    invalid_categories = list(set(categories_list).difference(accepted_ids))
    if not invalid_categories:
        return None
    return invalid_categories

def update_user_categories(user_id, categories_list):
    client = common.get_db()
    client.update_categories(user_id, categories_list)


def get_user_categories(user_id):
    client = common.get_db()
    return client.get_user_categories(user_id)


@api.route('/categories', methods=['GET'])
@login_required
def get_categories(user_id):
    filters = request.args.get('filter')
    
    if filters is not None and 'me' in filters:
        result_categories = get_user_categories(user_id)
    else:
        result_categories = categories
    return jsonify({'result': result_categories})


@api.route('/categories', methods=['POST'])
@login_required
def update_categories(user_id):
    data = request.data
    data_dict = json.loads(data)

    categories_list = data_dict['ids']

    invalid_categories = filter_valid_categories(categories_list)
    if invalid_categories is not None and invalid_categories:
        return jsonify({'message': 'Invalid categories: %s' % str(invalid_categories)}), 400

    update_user_categories(user_id, categories_list)

    user_categories = get_user_categories(user_id)

    return jsonify({'result': user_categories})
