from flask import Blueprint, jsonify, Response
import json
from scraper import terbaru, popular, detail, content, search, find_genre, get_manhua_list, get_search_manhua, get_manhua_content, get_manhua_detail

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
    
    return Response(jsonify(data).data, mimetype="application/json")

@api_routes.route('/api/popular/', methods=['GET'])
def api_popular():
    komik_data = popular()

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "data": komik_data
    }
    
    return Response(json.dumps(data, ensure_ascii=False, indent=4), mimetype="application/json")

@api_routes.route('/api/detail/<path:link>', methods=['GET'])
def api_detail(link):
    komik_data = detail(link)
    manhua_data = get_manhua_detail(link)

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "data": [komik_data, manhua_data]
    }
    
    return Response(json.dumps(data, ensure_ascii=False, indent=4), mimetype="application/json")

@api_routes.route('/api/content/<path:link>', methods=['GET'])
def api_content(link):
    komik_data = content(link)
    manhua_data = get_manhua_content(link)

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "data": [komik_data, manhua_data]
    }
    
    return Response(json.dumps(data, ensure_ascii=False, indent=4), mimetype="application/json")

@api_routes.route('/api/search/<path:query>', methods=['GET'])
def api_search(query):
    komik_data = search(query)
    manhua_data = get_search_manhua(query)

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "data": [komik_data, manhua_data]
    }
    
    return Response(json.dumps(data, ensure_ascii=False, indent=4), mimetype="application/json")

@api_routes.route('/api/genre/<path:genre>/', defaults={'page': 1}, methods=['GET'])
@api_routes.route('/api/genre/<path:genre>/page/<int:page>', methods=['GET'])
def api_genre(genre, page):
    komik_data, total_pages = find_genre(genre, page)

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "current_page": str(page),
        "total_pages": str(total_pages),
        "data": komik_data 
    }
    
    return Response(json.dumps(data, ensure_ascii=False, indent=4), mimetype="application/json")

@api_routes.route('/api/manhua/',defaults={'page': 1}, methods=['GET'])
@api_routes.route('/api/manhua/page/<int:page>', methods=['GET'])
def api_get_manhua(page):
    komik_data, total_pages = get_manhua_list(page)

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "current_page": str(page),
        "total_pages": str(total_pages),
        "data": komik_data 
    }
    return Response(json.dumps(data, ensure_ascii=False, indent=4), mimetype="application/json")