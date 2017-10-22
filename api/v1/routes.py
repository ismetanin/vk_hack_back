# coding=utf-8

from flask import Flask, jsonify, abort, request 
import json
from . import api, login_required
import vk
import api.common as common
import requests
import datetime
from time import sleep

import events as ev

VK_INCORRECT_TOKEN_ID = 15

def add_mutually_info(user_id, target_user_dict):
    result_user_dict = target_user_dict
    client = common.get_db()
    result_user_dict['is_mutually'] = client.is_user_a_likes_b(target_user_dict['id'], user_id)
    return result_user_dict

def get_recomended_users(user):
    result_users = []

    user_id = user['id']
    vk_token = user['vk_token']

    session = vk.Session(access_token=vk_token)
    vk_api = vk.API(session, v='5.68')
    
    def make_filters():
        res_args = {}

        if user['gender'] in ['male', 'female']:
            res_args['sex'] = 1 if user['gender'] == 'male' else 0

        user_city = user['city_id']
        if user_city and user_city is not None:
            res_args['city'] = user_city

        return res_args

    res_args = make_filters()

    client = common.get_db()

    def load_users(offset, count):
        vk_users = vk_api.users.search(offset=offset, sort=0, count=count, has_photo=1, age_from=18, age_to=39, fields='photo_200_orig,sex,bdate,city,country', **res_args)['items']
        vk_users_ids = [str(vk_user['id']) for vk_user in vk_users]
        not_viewed_ids = client.get_not_viewed(user_id, vk_users_ids)
        not_viewed_vk_users = [vk_user for vk_user in vk_users if str(vk_user['id']) in not_viewed_ids]
        not_viewed_users = [add_mutually_info(user_id, common.map_vk_user_dict(vk_user)) for vk_user in not_viewed_vk_users]
        non_null_viewed_users = [user_dict for user_dict in not_viewed_users if user_dict['id'] is not None and user_dict['age'] is not None]
        return non_null_viewed_users

    batch_count = 50
    loaded_count = 0
    result_users = []
    while len(result_users) < batch_count:
        result_users.extend(load_users(loaded_count, batch_count))
        loaded_count += batch_count
        if len(result_users) < batch_count:
            sleep(0.5)

    return result_users

def get_vk_server_token(client_id, client_secret):
    # Request (3)
    # GET https://oauth.vk.com/access_token

    response = requests.get(
        url="https://oauth.vk.com/access_token",
        params={
            "client_id": client_id,
            "client_secret": client_secret,
            "v": "5.68",
            "grant_type": "client_credentials",
        }
    )

    result = json.loads(response.content)["access_token"]
    return result

def vk_get_user(vk_token, user_id):
    session = vk.Session(access_token=vk_token)
    vk_api = vk.API(session, v='5.68')
    return vk_api.users.get(fields='photo_200_orig,sex,bdate,city,country')

def vk_create_event_post(event):
    vk_group_key = common.VK_GROUP_KEY
    group_id = common.VK_GROUP_ID
    session = vk.Session(access_token=vk_group_key)
    vk_api = vk.API(session, v='5.68')

    event_text = "%(title)s\n\n%(summary)s" % event
    attachments = event['url']

    post_data = vk_api.wall.post(owner_id=group_id, from_group=1, message=event_text, attachments=attachments)

    return post_data

def auth_user(vk_token, user_id, user_dict):
    result_dict = common.map_vk_user_dict(user_dict)

    result_dict['vk_token'] = vk_token

    client = common.get_db()

    db_user = client.get_user(user_id)
    if db_user is None:
        db_user = client.create_user(result_dict)
    else:
        db_user = client.update_user(user_id, result_dict)

    if db_user is not None:
        auth_token = client.auth_user(user_id)
        return {"token": auth_token}
    
    return None

@api.route('/users', methods=['GET'])
@login_required
def get_users(user):
    return jsonify({'result': get_recomended_users(user)})

@api.route('/profile', methods=['GET'])
@login_required
def get_profile(user_id):
    client = common.get_db()
    user = client.get_user_dict(user_id)
    return jsonify({'result': user})

@api.route('/chat', methods=['POST'])
@login_required
def create_chat(user):
    data = request.data
    data_dict = json.loads(data)

    object_id = None
    if 'event_id' in data_dict and data_dict['event_id']:
        event_id = data_dict['event_id']
        event = ev.map_event(ev.load_kuda_go_event(event_id))
        post_dict = vk_create_event_post(event)
        object_id = "wall%s_%s,%s" % (common.VK_GROUP_ID, post_dict['post_id'], event['image'])
    
    recipient_user_id = data_dict['recipient_id']
    message = data_dict['message']
    vk_token = user['vk_token']

    session = vk.Session(access_token=vk_token)
    vk_api = vk.API(session, v='5.68')

    if object_id is not None:
        vk_api.messages.send(user_id=recipient_user_id, message=message, attachment=object_id)
    else:
        vk_api.messages.send(user_id=recipient_user_id, message=message)

    return jsonify({'result': 1})
    

@api.route('/auth', methods=['POST'])
def get_vk_users():
    data = request.data
    data_dict = json.loads(data)

    token = data_dict['token']

    vk_server_token = get_vk_server_token(client_id=common.VK_CLIENT_ID, client_secret=common.VK_CLIENT_SECRET)
    session = vk.Session(access_token=vk_server_token)
    vk_api = vk.API(session)
    
    try:
        result = vk_api.secure.checkToken(token=token, client_secret=common.VK_CLIENT_SECRET)

        user_token = token
        user_id = result['user_id']
        user_data = vk_get_user(user_token, user_id)

        if user_data:
            user_dict = user_data[0]
            result_user = auth_user(user_token, user_id, user_dict)
            print result_user
            result = result_user

    except vk.exceptions.VkAPIError as e:
        result = {'vk_error_code': e.code}
        error_code = 400
        if e.code == VK_INCORRECT_TOKEN_ID:
            error_code = 401
            print 'Incorrect token'
        return jsonify(result), error_code

    return jsonify(result)