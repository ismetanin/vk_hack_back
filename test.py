import vk

# my_session = vk.AuthSession(user_login='+79118377618', user_password='vwifmitotmmctmswowlibe', app_id='3913450')
# my_vk_api = vk.API(my_session)
# print my_vk_api._session.__dict__

# VK_INCORRECT_TOKEN_ID = 15

# token = '913cbd35b3996f4db9f8a9c9f7a30aba7f2dd9c99870872d566ba537692d2dab72092494f04244046c2fc'

# session = vk.Session(access_token='a1a34ebaa1a34ebaa1f6a56123a198f850aa1a3a1a34ebaf8496d5c198935649ef175bc')
# vk_api = vk.API(session)
    
# try:
#     result = vk_api.secure.checkToken(token=token, client_secret='p72cKlxhQF69nEO4psgc')
# except vk.exceptions.VkAPIError as e:
#     result = ""
#     if e.code == VK_INCORRECT_TOKEN_ID:
#         print 'Incorrect token'

# print result

from pymongo import MongoClient


class MongoDBClient():

    def __init__(self):
        self.client = MongoClient('localhost', 27017)

    def get_user(self, id):
        users = self.client.db.users
        user = users.find_one({"id": id})
        return user

    def create_user(self, user_dict):
        users = self.client.db.users
        user = users.insert_one(user_dict)
        return user

test = MongoDBClient()

# print test.create_user({'la': 'bla', 'id': '1298018'})
print test.get_user('1298018')