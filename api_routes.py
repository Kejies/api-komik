<<<<<<< HEAD
from flask import Blueprint, jsonify, Response
import json
from collections import OrderedDict
from scraper import terbaru, popular, detail, content
=======
from flask import Blueprint, jsonify
import logging
from scraper import terbaru, popular, content
>>>>>>> 505741acd8ad308f50f1ccc78a2a938f7fa45822

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
    
    return jsonify(data) 

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

    return jsonify({
        "success": True,
        "message": "Berhasil mengambil data",
        "data": komik_data
<<<<<<< HEAD
    }
    
    return Response(json.dumps(data, ensure_ascii=False, indent=4), mimetype="application/json")
=======
    })
>>>>>>> 505741acd8ad308f50f1ccc78a2a938f7fa45822
