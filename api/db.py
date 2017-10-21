
from pymongo import MongoClient
import os
import time
import hashlib

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

    def __clean(self, data):
        del data['_id']
        return data

    def get_user_id_by_token(self, token):
        sessions = self.client.db.sessions
        user_session = sessions.find_one({"token": token})
        if user_session is not None:
            return user_session['user_id']
        return None

    def auth_user(self, user_id):
        hash_str = hashlib.sha224(str(user_id)+str(time.time())).hexdigest()
        sessions = self.client.db.sessions
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
        user = users.find_one({"id": user_id})
        return user

    def get_user_dict(self, user_id):
        return self.__clean(self.get_user(user_id))

    def create_user(self, user_dict):
        users = self.client.db.users
        object_id = users.insert_one(user_dict).inserted_id
        user = users.find_one(object_id)
        return user

    def update_categories(self, user_id, categories_list):
        users = self.client.db.users
        users.update_one({'id': user_id}, {"$set": {USER_CATEGORIES_KEY: categories_list}}, upsert=False)

    def get_user_categories(self, user_id):
        user = self.get_user(user_id)
        if user is not None and USER_CATEGORIES_KEY in user:
            return user[USER_CATEGORIES_KEY]
        return None
