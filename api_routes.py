from flask import Blueprint, jsonify, Response
import json
from scraper import terbaru, popular, detail, content, search_all_sources, search_manga_manhua, find_genre, get_manhua_list, get_manga_manhua_detail, get_manga_manhua_content, get_manga_list
from scraper2 import anime_terbaru, anime_detail, anime_content, anime_search
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
    try:
        komik_data = detail(link)
    except Exception as e:
        komik_data = None
        print(f"[ERROR] content() gagal: {e}")

    if not komik_data:
        try:
            komik_data = get_manga_manhua_detail(link)
        except Exception as e:
            komik_data = None
            print(f"[ERROR] find_manhua() gagal: {e}")
    data = {
        "success": True,
        "message": "Berhasil mengambil data" if komik_data else "Gagal mengambil data",
        "data": komik_data if komik_data else None
    }
    
    return Response(json.dumps(data, ensure_ascii=False, indent=4), mimetype="application/json")

@api_routes.route('/api/content/<path:link>', methods=['GET'])
def api_content(link):
    try:
        komik_data = content(link)
    except Exception as e:
        komik_data = None
        print(f"[ERROR] content() gagal: {e}")

    if not komik_data:
        try:
            komik_data = get_manga_manhua_content(link)
        except Exception as e:
            komik_data = None
            print(f"[ERROR] find_manhua() gagal: {e}")
    data = {
        "success": bool(komik_data),
        "message": "Berhasil mengambil data" if komik_data else "Gagal mengambil data",
        "data": komik_data if komik_data else None
    }
    
    return Response(json.dumps(data, ensure_ascii=False, indent=4), mimetype="application/json")


@api_routes.route('/api/search/<path:query>', methods=['GET'])
def api_search(query):
    komik_data = search_all_sources(query)
    anime_data = anime_search(query)

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "data": [komik_data, anime_data]
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

@api_routes.route('/api/manhua/', methods=['GET'])
def api_get_manhua(page=1):
    komik_data, total_pages = get_manhua_list()

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "current_page": str(page),
        "total_pages": str(total_pages),
        "data": komik_data 
    }
    return Response(json.dumps(data, ensure_ascii=False, indent=4), mimetype="application/json")

@api_routes.route('/api/manga/', methods=['GET'])
def api_get_manga(page=1):
    komik_data, total_pages = get_manga_list()

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "current_page": str(page),
        "total_pages": str(total_pages),
        "data": komik_data 
    }
    return Response(json.dumps(data, ensure_ascii=False, indent=4), mimetype="application/json")


@api_routes.route('/api/anime-terbaru/<int:page>', methods=['GET'])
def api_anime_terbaru(page):
    anime_data, total_pages = anime_terbaru(page)

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "current_page": str(page),
        "total_pages": total_pages,
        "data": anime_data 
    }
    
    return Response(jsonify(data).data, mimetype="application/json")

@api_routes.route('/api/anime-detail/<path:link>', methods=['GET'])
def api_anime_detail(link):
    anime_data = anime_detail(link)

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "data": anime_data
    }
    
    return Response(json.dumps(data, ensure_ascii=False, indent=4), mimetype="application/json")

@api_routes.route('/api/nontonanime/<path:link>', methods=['GET'])
def api_nonton_anime(link):
    anime_data = anime_content(link)

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "data": anime_data
    }
    
    return Response(json.dumps(data, ensure_ascii=False, indent=4), mimetype="application/json")