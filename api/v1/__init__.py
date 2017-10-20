from flask import Blueprint, render_template, abort

api = Blueprint('api', __name__)

from .routes import *
