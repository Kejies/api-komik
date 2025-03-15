from flask import Blueprint, jsonify
import json
import logging
from scraper import terbaru, popular

api_routes = Blueprint("api_routes", __name__)

@api_routes.route('/api/terbaru/<int:page>', methods=['GET'])
def api_terbaru(page):
    komik_data, total_pages = terbaru(page)

    data = {
    "success": True,
    "message": "Berhasil mengambil data",
    "current_page": str(page),
    "total_page": str(total_pages),
    "data": komik_data 
}
    
    return jsonify(data)

@api_routes.route('/api/popular/', methods=['GET'])
def api_popular():
    komik_data = popular()

    logging.debug(f"DEBUG: Data Popular di Vercel -> {komik_data}")

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "data": komik_data
    }
    
    return jsonify(data)
