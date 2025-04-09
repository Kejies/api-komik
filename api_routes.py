from flask import Blueprint, jsonify, Response
import json
from scraper import terbaru, popular, detail, content, search, find_genre, get_manhua_list, get_search_manhua, get_manhua_detail, get_manhua_content
from scraper_2 import getAnimeListTerbaru, getAnimeDetail, nontonAnime, search_anime, get_anime_popular

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
        komik_data = content(link)
    except Exception as e:
        komik_data = None
        print(f"[ERROR] content() gagal: {e}")

    # Jika gagal atau hasil None, coba find_manhua
    if not komik_data:
        try:
            komik_data = get_manhua_detail(link)
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

    # Jika gagal atau hasil None, coba find_manhua
    if not komik_data:
        try:
            komik_data = get_manhua_content(link)
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
    try:
        komik_data = search(query)
    except Exception as e:
        komik_data = []
    
    try:
        manhua_data = get_search_manhua(query)
    except Exception as e:
        manhua_data = []
    
    try:
        anime_data = search_anime(query)
    except Exception as e:
        anime_data = []

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "data": {
            "komik": komik_data,
            "manhua": manhua_data,
            "anime": anime_data
        }
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

@api_routes.route('/api/anime-terbaru/<int:page>', methods=['GET'])
def api_anime_terbaru(page):
    anime_data = getAnimeListTerbaru(page)

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "current_page": str(page),
        "total_pages": str(25),
        "data": anime_data 
    }
    
    return Response(jsonify(data).data, mimetype="application/json")

@api_routes.route('/api/anime-detail/<path:link>', methods=['GET'])
def api_anime_detail(link):
    anime_data = getAnimeDetail(link)

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "data": anime_data
    }
    
    return Response(json.dumps(data, ensure_ascii=False, indent=4), mimetype="application/json")

@api_routes.route('/api/nontonanime/<path:link>', methods=['GET'])
def api_nonton_anime(link):
    anime_data = nontonAnime(link)

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "data": anime_data
    }
    
    return Response(json.dumps(data, ensure_ascii=False, indent=4), mimetype="application/json")

@api_routes.route('/api/anime-popular/', methods=['GET'])
def api_anime_popular():
    anime_data = get_anime_popular()

    data = {
        "success": True,
        "message": "Berhasil mengambil data",
        "data": anime_data
    }
    
    return Response(json.dumps(data, ensure_ascii=False, indent=4), mimetype="application/json")