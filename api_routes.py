from flask import Blueprint, jsonify
import logging
from scraper import terbaru, popular, content

api_routes = Blueprint("api_routes", __name__)

@api_routes.route('/api/terbaru/<int:page>', methods=['GET'])
def api_terbaru(page):
    komik_data, total_pages = terbaru(page)

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "current_page": str(page),
        "total_pages": str(total_pages),
        "data": komik_data
    }
    
    return jsonify(data)  # Flask otomatis mengatur Content-Type: application/json

@api_routes.route('/api/popular/', methods=['GET'])
def api_popular():
    komik_data = popular()

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "data": komik_data
    }
    
    return jsonify(data)

@api_routes.route('/api/content/<path:link>', methods=['GET'])
def api_content(link):
    komik_data = content(link)

    if komik_data is None:
        return jsonify({
            "success": False,
            "message": "Gagal mengambil data. Pastikan link benar atau coba lagi nanti.",
            "data": None
        }), 404  # Tambahkan status 404 jika gagal

    return jsonify({
        "success": True,
        "message": "Berhasil mengambil data",
        "data": komik_data
    })
