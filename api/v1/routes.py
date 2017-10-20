# coding=utf-8

from flask import Flask, jsonify, abort, request 
import json
from . import *
import vk
import api.common as common
import requests

VK_INCORRECT_TOKEN_ID = 15

users_stub = [
    {
        'id': "94338550",
        'name': u'Таянна Болгарова',
        'avatarURLStrings': ['https://pp.userapi.com/c837122/v837122396/48393/j4A3iKYr1ZY.jpg'],
        'gender': 'female',
        'chatId': None,
        'city': u'Санкт-Петербург',
        'age': 24
    },
    {
        'id': "178469391",
        'name': u'Екатерина Черняева',
        'avatarURLStrings': ['https://pp.userapi.com/c836328/v836328586/3e3bf/Xu_ukzC3bXs.jpg'],
        'gender': 'female',
        'chatId': None,
        'city': u'Санкт-Петербург',
        'age': 26
    },
    {
        'id': "35971840",
        'name': u'Александра Закрева',
        'avatarURLStrings': ['https://pp.userapi.com/c604327/v604327840/3a54e/jbGHKsABWuM.jpg'],
        'gender': 'female',
        'chatId': None,
        'city': u'Санкт-Петербург',
        'age': 27
    },
    {
        'id': "58746319",
        'name': u'Лилия Сальникова',
        'avatarURLStrings': ['https://pp.userapi.com/c636228/v636228319/1805d/PIrIFeOF0-0.jpg'],
        'gender': 'female',
        'chatId': None,
        'city': u'Санкт-Петербург',
        'age': 30
    },
]

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
    vk_api = vk.API(session)
    return vk_api.users.get()

def auth_user(vk_token, user_id, user_dict):
    result_dict = user_dict
    result_dict['vk_token'] = vk_token
    result_dict['id'] = user_id
    del result_dict['uid']

    client = common.get_db()

    db_user = client.get_user(user_id)
    if db_user is None:
        db_user = client.create_user(result_dict)

    if db_user is not None:
        auth_token = client.auth_user(user_id)
        return {"token": auth_token}
    
    return None

def get_user_id(token):
    client = common.get_db()
    user_id = client.get_user_id_by_token(token)
    return user_id

@api.route('/users', methods=['GET'])
def get_tasks():
    token = request.args.get('token')
    user_id = get_user_id(token)
    if user_id is None:
        return jsonify({}), 401

    return jsonify({'users': users_stub})

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