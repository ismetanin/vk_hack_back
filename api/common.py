from flask import current_app

VK_SERVER_ACCESS_TOKEN = 'a1a34ebaa1a34ebaa1f6a56123a198f850aa1a3a1a34ebaf8496d5c198935649ef175bc'
VK_CLIENT_SECRET = 'p72cKlxhQF69nEO4psgc'

def get_db():
    return current_app._database