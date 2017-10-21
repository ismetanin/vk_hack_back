# coding=utf-8

from flask import Flask, jsonify, abort, request 
import json
from . import api, login_required
import vk
import api.common as common
import requests
import datetime
from dateutil.relativedelta import relativedelta

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
    vk_api = vk.API(session, v='5.68')
    return vk_api.users.get(fields='photo_200_orig,sex,bdate,city')

def map_vk_user_dict(vk_user_dict):

    def get_age_value(source_dict):
        bdate_key = 'bdate'
        if bdate_key not in source_dict:
            return None
        bdate = source_dict[bdate_key]
        result_date = datetime.datetime.strptime(bdate, "%d.%m.%Y").date()
        result_age = relativedelta(datetime.date.today(), result_date).years
        return result_age

    def get_id_value(source_dict):
        value_key = 'id'
        return str(source_dict[value_key])

    def get_gender_value(source_dict):
        value_key = 'sex'
        if value_key not in source_dict:
            return None
        sex = source_dict[value_key]
        
        result_gender = None
        if sex == 1:
            result_gender = 'female'
        elif sex == 2:
            result_gender = 'male'
        
        return result_gender

    def get_photo_value(source_dict):
        value_key = 'photo_200_orig'
        if value_key not in source_dict:
            return None
        return source_dict[value_key]

    def get_name_value(source_dict):
        return u'%(first_name)s %(last_name)s' % source_dict

    def get_city_value(source_dict):
        city_value_key = 'city'
        city_title_value_key = 'title'

        if city_value_key not in source_dict:
            return None

        city_dict = source_dict[city_value_key]

        if city_title_value_key not in city_dict:
            return None

        return unicode(city_dict[city_title_value_key])

    result_dict = {
        'id': get_id_value(vk_user_dict),
        'name': get_name_value(vk_user_dict),
        'avatarURLStrings': [get_photo_value(vk_user_dict)],
        'gender': get_gender_value(vk_user_dict),
        'chatId': None,
        'city': get_city_value(vk_user_dict),
        'age': get_age_value(vk_user_dict)
    }

    print result_dict

    return result_dict

def auth_user(vk_token, user_id, user_dict):
    result_dict = map_vk_user_dict(user_dict)

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
def get_users():
    return jsonify({'result': users_stub})

@api.route('/profile', methods=['GET'])
@login_required
def get_profile(user_id):
    client = common.get_db()
    user = client.get_user_dict(user_id)
    return jsonify({'result': user})

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