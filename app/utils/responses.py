# app/utils/responses.py

from flask import jsonify


def success_response(data=None, message="Operación realizada correctamente.", status_code=200):
    return jsonify({
        "data": data,
        "message": message,
    }), status_code


def error_response(message, code="VALIDATION_ERROR", status_code=400):
    return jsonify({
        "error": {
            "code": code,
            "message": message,
        }
    }), status_code