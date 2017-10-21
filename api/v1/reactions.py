# coding=utf-8

from flask import Flask, jsonify, abort, request 
import json
from . import api, login_required
import api.common as common
import vk

def vk_get_users(vk_token, user_ids):
    session = vk.Session(access_token=vk_token)
    vk_api = vk.API(session, v='5.68')
    return vk_api.users.get(user_ids=user_ids, fields='photo_200_orig,sex,bdate,city,country')

def insert_like(user_id, liked_id):
    client = common.get_db()
    return client.add_reaction(user_id, liked_id, reaction_type='like')

def insert_dislike(user_id, disliked_id):
    client = common.get_db()
    return client.add_reaction(user_id, disliked_id, reaction_type='dislike')

def get_reactions_from_db(user_id, user):
    client = common.get_db()
    reactions = client.get_reactions(user_id, reaction_type='like')

    vk_token = user['vk_token']

    user_ids_to_load = [reaction['user_id'] for reaction in reactions if reaction['user'] is None]
    vk_users = vk_get_users(vk_token, user_ids_to_load)
    result_users = {user_dict['id']: user_dict for user_dict in map(common.map_vk_user_dict, vk_users)}

    filled_reactions = []
    for reaction in reactions:
        reacted_id = reaction['user_id']
        if reaction['user'] is None and reacted_id in result_users:
            reaction['user'] = result_users[reacted_id]
            
        filled_reactions.append(reaction)

    return filled_reactions

@api.route('/reactions', methods=['GET'])
@login_required
def get_reactions(user_id, user):
    reactions = get_reactions_from_db(user_id, user)
    return jsonify({'result': reactions})

@api.route('/likes', methods=['POST'])
@login_required
def add_like(user_id):
    data = request.data
    print data
    data_dict = json.loads(data)

    liked_id = data_dict['user_id']
    result = insert_like(user_id, liked_id)
    
    return jsonify({'result': result})


@api.route('/dislikes', methods=['POST'])
@login_required
def add_dislike(user_id):
    data = request.data
    data_dict = json.loads(data)

    disliked_id = data_dict['user_id']
    result = insert_dislike(user_id, disliked_id)

    return jsonify({'result': result})
