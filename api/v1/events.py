# coding=utf-8

from flask import Flask, jsonify, abort, request 
import json
from . import api, login_required
import api.common as common
from .categories import categories

import requests


def load_kuda_go_events(category, city):
    # KudaGo events list
    # GET https://kudago.com/public-api/v1.2/events/

    try:
        response = requests.get(
            url="https://kudago.com/public-api/v1.2/events/",
            params={
                "categories": category,
                "fields": "description,price,images,id,title,place,age_restriction",
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
        if value_key not in source_dict or not source_dict[value_key]:
            return None
        value = source_dict[value_key]
        return value[0].upper() + value[1:]

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

        fields_keys = [
            ('place', u'Адрес'),
            ('price', u'Цена'),
            ('age_restriction', u'Возрастные ограничения'),
            ('tags', u'Тэги'),
            ('participants', u'Агенты'),
        ]

        for value_key, field_name in fields_keys:
            if value_key in source_dict and source_dict[value_key]:
                result_fields.append({'name': field_name, 'value': source_dict[value_key]})

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
def get_events(user_id, user):
    requested_category = request.args.get('category')
    
    cur_categories = [category for category in categories if category['id'] == requested_category]

    result_events = []

    if cur_categories:
        category_dict = cur_categories[0]
        kuda_go_result = load_kuda_go_events(requested_category, user['city'])
        if 'results' in kuda_go_result:
            kuda_go_events = kuda_go_result['results']
            print kuda_go_events
            mapped_events = map(map_event, kuda_go_events)

            for event in mapped_events:
                event['category'] = category_dict

            result_events = mapped_events
    return jsonify({'result': result_events})