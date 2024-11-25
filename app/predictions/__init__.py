from flask import Blueprint

bp = Blueprint('predictions', __name__)

from app.predictions import routes
