
from pymongo import MongoClient
import os
import time
import hashlib
import datetime

USER_CATEGORIES_KEY = "categories"

class DBClient:

    def __init__(self):
        pass

    def get_user(self, id):
        pass

    def create_user(self, user_dict):
        pass

class MongoDBClient(DBClient):

    def __init__(self):
        self.client = MongoClient(os.environ['DB_HOST'], 27017)


    def __clean(self, data, scope='sec'):

        def perform_clean(dict_item):
            if data is None:
                return None

            keys_to_delete = ['_id']

            if scope != 'raw':
                keys_to_delete.extend(['vk_token'])
            
            for key in keys_to_delete:
                if key in data:
                    del data[key]

            return data

        if type(data) is list:
            return [self.__clean(item, scope) for item in data]

        return perform_clean(data)
        


    def get_user_id_by_token(self, token):
        sessions = self.client.db.sessions
        user_session = sessions.find_one({"token": token})
        if user_session is not None:
            return user_session['user_id']
        return None


    def auth_user(self, user_id):
        hash_str = hashlib.sha224(str(user_id)+str(time.time())).hexdigest()
        sessions = self.client.db.sessions
        user_id = str(user_id)
        user_session = sessions.find_one({"user_id": user_id})
        if user_session is None:
            data_dict = {
                "user_id": user_id,
                "token": hash_str 
            }
            object_id = sessions.insert_one(data_dict).inserted_id
            user_session = sessions.find_one(object_id)
        
        return user_session['token']


    def get_user(self, user_id):
        users = self.client.db.users
        user_id = str(user_id)
        user = users.find_one({"id": user_id})
        return user


    def get_user_dict(self, user_id, scope='sec'):
        return self.__clean(self.get_user(user_id), scope)


    def create_user(self, user_dict):
        users = self.client.db.users
        user_id = str(user_dict["id"])
        users.delete_many({"id": user_id})
        object_id = users.insert_one(user_dict).inserted_id
        user = users.find_one(object_id)
        return user


    def update_user(self, user_id, user_dict):
        users = self.client.db.users
        user_id = str(user_id)
        users.update_one({'id': user_id}, {"$set": user_dict}, upsert=False)

        return self.get_user_dict(user_id)

    def update_categories(self, user_id, categories_list):
        users = self.client.db.users
        user_id = str(user_id)
        users.update_one({'id': user_id}, {"$set": {USER_CATEGORIES_KEY: categories_list}}, upsert=False)


    def get_user_categories(self, user_id):
        user_id = str(user_id)
        user = self.get_user(user_id)
        if user is not None and USER_CATEGORIES_KEY in user:
            return user[USER_CATEGORIES_KEY]
        return None

    def add_reaction(self, user_id, liked_id, reaction_type):
        reactions = self.client.db.reactions
        user_id = str(user_id)
        liked_id = str(liked_id)
        num = reactions.count({ "$and": [{"id": user_id }, {"reactions.user_id": liked_id}]})

        result_item = {}
        if not num:
            def check_mutuality():
                mutually_user = reactions.find_one({ "$and": [{"id": liked_id }, {"reactions.user_id": user_id}, {"reactions.type": "like"}]})
                if mutually_user:
                    for item in mutually_user['reactions']:
                        if item[u'type'] == "like" and item[u'user_id'] == user_id:
                            item['is_mutually'] = True
                            break
                    reactions.update({ "id": liked_id },  mutually_user)
                    return True
                return False

            is_mutually = check_mutuality()

            reactions.find_and_modify({ "id": user_id },  { "$push": { "reactions": {
                "user_id": liked_id, 
                "type": reaction_type,
                "timestamp": datetime.datetime.now(),
                "is_mutually": is_mutually
                } }}, upsert=True)

            updated_items = reactions.find_one({ "$and": [{"id": user_id }, {"reactions.user_id": liked_id}]})

            for item in updated_items['reactions']:
                if item[u'type'] == reaction_type and item[u'user_id'] == liked_id:
                    result_item = item
                    break
        return self.__clean(result_item)

    def get_not_viewed(self, user_id, user_ids):
        reactions = self.client.db.reactions
        user_id = str(user_id)
        user_reaction = reactions.find_one({ "$and": [{"id": user_id }]})

        if not user_reaction or user_reaction is None:
            return user_ids

        viewed_user_ids = set([reaction['user_id'] for reaction in user_reaction['reactions']])

        not_viewed_users = list(set(user_ids).difference(viewed_user_ids))
        return not_viewed_users

    def is_user_a_likes_b(self, user_a_id, user_b_id):
        reactions = self.client.db.reactions
        mutually_user = reactions.find_one({ "$and": [{"id": user_a_id }, {"reactions.user_id": user_b_id}, {"reactions.type": "like"}]})
        if mutually_user:
            for item in mutually_user['reactions']:
                if item[u'type'] == "like" and item[u'user_id'] == user_b_id:
                    item['is_mutually'] = True
                    break
            return True
        return False

    def get_reactions(self, user_id, reaction_type):
        reactions = self.client.db.reactions
        user_id = str(user_id)
        user_reaction = reactions.find_one({ "$and": [{"id": user_id }, {"reactions.type": reaction_type}]})

        if user_reaction is None and not user_reaction:
            return []

        filtered_reactions = [reaction for reaction in user_reaction['reactions'] if reaction['type'] == reaction_type]
        
        filled_reactions = []
        for reaction in filtered_reactions:
            reaction['user'] = self.get_user_dict(reaction['user_id'])
            filled_reactions.append(reaction)

        return self.__clean(filled_reactions)

