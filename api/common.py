from flask import current_app
import datetime
from dateutil.relativedelta import relativedelta

VK_CLIENT_SECRET = 'p72cKlxhQF69nEO4psgc'
VK_CLIENT_ID = '3913450'

def get_db():
    return current_app._database

def map_vk_user_dict(vk_user_dict):

    def get_age_value(source_dict):
        bdate_key = 'bdate'
        if bdate_key not in source_dict:
            return None
        bdate = source_dict[bdate_key]
        try:
            result_date = datetime.datetime.strptime(bdate, "%d.%m.%Y").date()
        except:
            return None
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
        return u'%(first_name)s' % source_dict

    def get_city_value(source_dict):
        city_value_key = 'city'
        city_title_value_key = 'title'

        if city_value_key not in source_dict:
            return None

        city_dict = source_dict[city_value_key]

        if city_title_value_key not in city_dict:
            return None

        return unicode(city_dict[city_title_value_key])

    def get_country_value(source_dict):
        city_value_key = 'country'
        city_title_value_key = 'title'

        if city_value_key not in source_dict:
            return None

        city_dict = source_dict[city_value_key]

        if city_title_value_key not in city_dict:
            return None

        return unicode(city_dict[city_title_value_key])

    def get_city_id(source_dict):
        city_value_key = 'city'
        city_title_value_key = 'id'

        if city_value_key not in source_dict:
            return None

        city_dict = source_dict[city_value_key]

        if city_title_value_key not in city_dict:
            return None

        return unicode(city_dict[city_title_value_key])

    def get_country_id(source_dict):
        city_value_key = 'country'
        city_title_value_key = 'id'

        if city_value_key not in source_dict:
            return None

        city_dict = source_dict[city_value_key]

        if city_title_value_key not in city_dict:
            return None

        return unicode(city_dict[city_title_value_key])

    def get_chat_value(source_dict):
        vk_user_id = get_id_value(source_dict)
        return "https://vk.com/im?sel=%s" % vk_user_id

    result_dict = {
        'id': get_id_value(vk_user_dict),
        'name': get_name_value(vk_user_dict),
        'avatarURLStrings': [get_photo_value(vk_user_dict)],
        'gender': get_gender_value(vk_user_dict),
        'chatId': get_chat_value(vk_user_dict),
        'city': get_city_value(vk_user_dict),
        'country': get_country_value(vk_user_dict),
        'city_id': get_city_id(vk_user_dict),
        'country_id': get_country_id(vk_user_dict),
        'age': get_age_value(vk_user_dict)
    }

    return result_dict