from flask import Blueprint, Response
import json
import sys
from collections import OrderedDict
from scraper import terbaru, popular

api_routes = Blueprint("api_routes", __name__)

@api_routes.route('/api/terbaru/<int:page>', methods=['GET'])
def api_terbaru(page):
    komik_data, total_pages = terbaru(page)

    data = OrderedDict([
        ("success", True),
        ("message", "Berhasil mengambil data"),
        ("data", {
            "current_page": str(page),
            "total_page": str(total_pages),
            "data": komik_data
        })
    ])
    
    return Response(json.dumps(data, indent=4), mimetype="application/json")

@api_routes.route('/api/popular/', methods=['GET'])
def api_popular():
    komik_data = popular()

    print("DEBUG: Data Popular di Vercel ->", komik_data, file=sys.stderr)

    data = OrderedDict([
        ("success", True),
        ("message", "Berhasil mengambil data"),
        ("data", {
            "data": komik_data
        })
    ])
    
    return Response(json.dumps(data, indent=4), mimetype="application/json")
