# coding=utf-8

from flask import Flask, jsonify, abort, request 
import json
from . import api, login_required
import api.common as common
from .categories import categories

events = {
    "cinema": [
        {
            "id": "",
            "title": "",
            "image": "",
            "category": { 'id': u'cinema', 'type': u'cinema', 'title': u'Кино'},
            "score": 15.0,
            "summary": "",
            "fields": [
                {"name": "t", "value":"a"},
                {"name": "t", "value":"a"}
            ]
        }
    ]
}

# [
#     { 'id': u'cinema', 'type': u'cinema', 'title': u'Кино', },
#     { 'id': u'sport', 'type': u'sport', 'title': u'Спорт', },
#     { 'id': u'festival', 'type': u'festival', 'title': u'Фестиваль', },
#     { 'id': u'culture', 'type': u'culture', 'title': u'Культура', },
#     { 'id': u'humor', 'type': u'humor', 'title': u'Юмор', },
#     { 'id': u'concert', 'type': u'concert', 'title': u'Концерт', },
#     { 'id': u'food', 'type': u'food', 'title': u'Еда', },
#     { 'id': u'games', 'type': u'games', 'title': u'Игры', },
# ]

import requests


def load_kuda_go_events(category):
    # KudaGo events list
    # GET https://kudago.com/public-api/v1.2/events/

    try:
        response = requests.get(
            url="https://kudago.com/public-api/v1.2/events/",
            params={
                "categories": category,
                "fields": "description,price,images,id",
            },
        )
        return json.loads(response.content)
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

def map_event(event_dict):

    def get_id_value(source_dict):
        value_key = 'id'
        return str(source_dict[value_key])

    def get_title_value(source_dict):
        value_key = 'title'
        if value_key not in source_dict:
            return None
        return source_dict[value_key]

    def get_image_value(source_dict):
        value_key = 'images'
        if value_key not in source_dict or not source_dict[value_key]:
            return None
        return source_dict[value_key][0]['image']

    def get_score_value(source_dict):
        value_key = 'favorites_count'
        if value_key not in source_dict:
            return None
        return source_dict[value_key]

    def get_summary_value(source_dict):
        value_key = 'description'
        if value_key not in source_dict:
            return None
        return source_dict[value_key].replace('<p>', '').replace('</p>', '')

    def get_fields_value(source_dict):
        result_fields = []

        value_key = 'price'
        if value_key in source_dict:
            result_fields.append({'name': u'Цена', 'value': source_dict[value_key]})

        return result_fields

    result_dict = {
        'id': get_id_value(event_dict),
        'title': get_title_value(event_dict),
        'image': get_image_value(event_dict),
        'score': get_score_value(event_dict),
        'summary': get_summary_value(event_dict),
        'fields': get_fields_value(event_dict),
    }

    return result_dict

@api.route('/events', methods=['GET'])
@login_required
def get_events(user_id):
    requested_category = request.args.get('category')
    
    cur_categories = [category for category in categories if category['id'] == requested_category]

    result_events = []

    if cur_categories:
        category_dict = cur_categories[0]
        kuda_go_result = load_kuda_go_events(requested_category)
        if 'results' in kuda_go_result:
            kuda_go_events = kuda_go_result['results']
            print kuda_go_events
            mapped_events = map(map_event, kuda_go_events)

            for event in mapped_events:
                event['category'] = category_dict

            result_events = mapped_events
    return jsonify({'result': result_events})