from flask import current_app

VK_CLIENT_SECRET = 'p72cKlxhQF69nEO4psgc'
VK_CLIENT_ID = '3913450'

def get_db():
    return current_app._database