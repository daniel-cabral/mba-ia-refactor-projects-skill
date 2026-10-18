from flask import Blueprint, current_app, jsonify, request

from controllers import user_controller
from middlewares.guards import admin_only
from utils.validators import parse_pagination

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['GET'])
def get_users():
    limit, offset = parse_pagination(request.args)
    return jsonify(user_controller.list_users(limit, offset)), 200


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return jsonify(user_controller.get_user(user_id)), 200


@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json(silent=True)
    allow_privileged = current_app.config['ADMIN_ENABLED']
    return jsonify(user_controller.create_user(data, allow_privileged)), 201


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json(silent=True)
    allow_privileged = current_app.config['ADMIN_ENABLED']
    return jsonify(user_controller.update_user(user_id, data, allow_privileged)), 200


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_only
def delete_user(user_id):
    return jsonify(user_controller.delete_user(user_id)), 200


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    return jsonify(user_controller.get_user_tasks(user_id)), 200


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    return jsonify(user_controller.login(data, current_app.config['SECRET_KEY'])), 200
