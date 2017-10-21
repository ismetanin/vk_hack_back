# coding=utf-8

from flask import Flask, jsonify, abort, request 
import json
from . import api, login_required
import api.common as common

def insert_like(user_id, liked_id):
    client = common.get_db()
    client.add_reaction(user_id, liked_id, reaction_type='like')

def insert_dislike(user_id, disliked_id):
    client = common.get_db()
    client.add_reaction(user_id, disliked_id, reaction_type='dislike')

@api.route('/likes', methods=['POST'])
@login_required
def add_like(user_id):
    data = request.data
    print data
    data_dict = json.loads(data)

    liked_id = data_dict['user_id']
    insert_like(user_id, liked_id)
    
    return jsonify({'result': 1})


@api.route('/dislikes', methods=['POST'])
@login_required
def add_dislike(user_id):
    data = request.data
    data_dict = json.loads(data)

    disliked_id = data_dict['user_id']
    insert_dislike(user_id, disliked_id)

    return jsonify({'result': 1})
