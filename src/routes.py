from flask import Blueprint, request, jsonify

riders_bp = Blueprint("riders", __name__, url_prefix="/riders")
