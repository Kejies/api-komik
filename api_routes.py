from flask import Blueprint, jsonify, Response
import json
from collections import OrderedDict
from scraper import terbaru, popular, detail, content

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

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "data": komik_data
    }
    
    return Response(json.dumps(data, ensure_ascii=False, indent=4), mimetype="application/json")

@api_routes.route('/api/content/<path:link>', methods=['GET'])
def api_content(link):
    komik_data = content(link)

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "data": komik_data
    }
    
    return Response(json.dumps(data, ensure_ascii=False, indent=4), mimetype="application/json")
