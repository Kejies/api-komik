import requests
import time
import re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json

# URL utama
get_url = "https://kotakanimeid.link"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# Ambil halaman utama
res = requests.get(get_url, headers=headers)
soup = BeautifulSoup(res.content, "html.parser")

first_link = soup.find("a")
base_url = first_link["href"]
def get_nonce_by_intercepting_ajax():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False biar kelihatan
        context = browser.new_context()
        page = context.new_page()

        nonce_container = {}

        def handle_route(route, request):
            if "admin-ajax.php" in request.url and request.method == "POST":
                post_data = request.post_data
                if "nonce=" in post_data:
                    match = re.search(r"nonce=([a-zA-Z0-9]+)", post_data)
                    if match:
                        nonce_container["nonce"] = match.group(1)
            route.continue_()

        context.route("**/admin-ajax.php", handle_route)
        page.goto("https://s4.nontonanimeid.boats")

        # Klik tombol load more
        page.wait_for_selector(".misha_loadmore")
        page.click(".misha_loadmore")
        page.wait_for_timeout(2000)  # kasih delay sedikit

        browser.close()

        return nonce_container.get("nonce")
nonce = get_nonce_by_intercepting_ajax()
def getAnimeListTerbaru(page=1):
    with sync_playwright() as p:
        request_context = p.request.new_context(
            base_url="https://s4.nontonanimeid.boats",
            extra_http_headers={
                "accept": "*/*",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "x-requested-with": "XMLHttpRequest",
                "Referer": "https://s4.nontonanimeid.boats/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )

        form_data = {
            "action": "loadmore",
            "nonce": nonce,
            "offset": "1",
            "paged": str(page)
        }

        response = request_context.post(
            "/wp-admin/admin-ajax.php",
            form=form_data
        )

        if response.status != 200:
            print(f"❌ Gagal mengambil data: Status {response.status}")
            return []

        html = response.text()
        request_context.dispose()

    # Parse HTML dari response
    soup = BeautifulSoup(html, "html.parser")
    anime_list = []

    for article in soup.find_all("article"):
        title_tag = article.find("h3", class_="entry-title")
        title = title_tag.text.strip() if title_tag else "Tidak ada judul"

        link_tag = article.select_one("div.sera a")
        link = link_tag["href"].strip("/").replace("https://s4.nontonanimeid.boats/", "") if link_tag else None

        img_tag = article.find("img")
        img = img_tag["src"] if img_tag else "Tidak ada gambar"

        episode_tag = article.find("span", class_="episodes")
        episode = episode_tag.text.strip() if episode_tag else "Tidak ada episode"

        anime_list.append({
            "title": title,
            "link": link,
            "image": img,
            "episode": episode
        })

    return anime_list

def getAnimeDetail(link):
    url_detail = f"{base_url}/anime/{link}"
    headers = {
        "accept": "*/*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "x-requested-with": "XMLHttpRequest",
        "Referer": base_url,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    detail_res = requests.get(url_detail, headers=headers)
    detail_res.raise_for_status()
    s = BeautifulSoup(detail_res.text, "html.parser")

    main = s.find("div", class_="kotakseries")
    title = s.find("h1", class_="entry-title cs").text.strip()
    image = main.find("img")["src"]
    ratting = main.find("span", class_="nilaiseries").text.strip()

    genreDiv = main.find("div", class_="tagline").find_all("a", rel="tag")
    genre = [{
        "title": gen.text.strip(),
        "link": gen["href"].replace(f"{base_url}/genres", "").strip("/")
    } for gen in genreDiv]

    sinsContainer = s.find("div", class_="entry-content seriesdesc")
    titleSins = sinsContainer.find("h2", class_="bold").text.strip()
    sinopsis = sinsContainer.find("p").text.strip()

    duration = studios = released = ""
    bottom_titles = s.find_all("div", class_="bottomtitle")
    if len(bottom_titles) >= 2:
        spans = bottom_titles[1].find_all("span", class_="infoseries")
        for span in spans:
            text = span.get_text(strip=True)
            if text.startswith("Duration:"):
                duration = text.replace("Duration:", "").strip()
            elif text.startswith("Studios:"):
                studios = text.replace("Studios:", "").strip()
            elif text.startswith("Aired:"):
                released = text.replace("Aired:", "").strip()

    # ================== HANDLE LOAD MORE ==================
    episode = []

    # Ambil series_id
    series_id = None
    load_more_div = s.find("div", id="load_more")
    if load_more_div and load_more_div.has_attr("data-series"):
        series_id = load_more_div["data-series"]
    else:
        match = re.search(r'data-series="(\d+)"', detail_res.text)
        if match:
            series_id = match.group(1)

    # Ambil episode awal
    contain = s.find("div", class_="episodelist")
    if contain:
        items_first = contain.find_all("li")
        for ep in items_first:
            a = ep.find("a")
            epsTitle = a.text.strip()
            epslink = a["href"].replace(f"{base_url}", "").strip("/")
            epsUpdate = ep.find("span", class_="t3").text.strip() if ep.find("span", class_="t3") else ""
            episode.append({
                "title": epsTitle,
                "link": epslink,
                "epsupdate": epsUpdate
            })

    # Load more
    if series_id:
        page = 1
        per_page = 100
        print(f"[DEBUG] Series ID: {series_id}")
        print(f"[DEBUG] NONCE: {nonce}")
        while True:
            ajax_url = f"{base_url}/wp-admin/admin-ajax.php"

            query_obj = {
                "posts_per_page": per_page,
                "post_type": "post",
                "paged": page,
                "meta_key": "series_seri",
                "no_found_rows": True,
                "meta_value": series_id,
                "orderby": "date",
                "order": "DESC",
                "ignore_sticky_posts": False,
                "suppress_filters": False,
                "cache_results": True,
                "update_post_term_cache": True,
                "update_menu_item_cache": False,
                "lazy_load_term_meta": True,
                "update_post_meta_cache": True,
                "nopaging": False,
                "comments_per_page": "50"
            }

            payload = {
                "action": "loadmore2",
                "nonce": nonce,
                "query": json.dumps({
                    "posts_per_page": per_page,
                    "post_type": "post",
                    "paged": page,
                    "meta_key": "series_seri",
                    "no_found_rows": True,
                    "meta_value": series_id,
                    "orderby": "date",
                    "order": "DESC",
                    "ignore_sticky_posts": False,
                    "suppress_filters": False,
                    "cache_results": True,
                    "update_post_term_cache": True,
                    "update_menu_item_cache": False,
                    "lazy_load_term_meta": True,
                    "update_post_meta_cache": True,
                    "nopaging": False,
                    "comments_per_page": "50"
                }),
                "page": page,
                "type": "anime",
                "posts_to_display": per_page,
                "is_large_series": 1
            }

            resp = requests.post("https://s4.nontonanimeid.boats/wp-admin/admin-ajax.php", headers=headers, data={
                "action": "loadmore2",
                "nonce": nonce,
                "page": page,
                "type": "anime",
                "posts_to_display": per_page,
                "is_large_series": 1,
                "query": json.dumps({
                    "posts_per_page": per_page,
                    "post_type": "post",
                    "paged": page,
                    "meta_key": "series_seri",
                    "no_found_rows": True,
                    "meta_value": series_id,
                    "orderby": "date",
                    "order": "DESC",
                    "ignore_sticky_posts": False,
                    "suppress_filters": False,
                    "cache_results": True,
                    "update_post_term_cache": True,
                    "update_menu_item_cache": False,
                    "lazy_load_term_meta": True,
                    "update_post_meta_cache": True,
                    "nopaging": False,
                    "comments_per_page": "50"
                })
            })
            print("[DEBUG] Final payload dikirim (form-urlencoded):")
            print(json.dumps(payload, indent=2))

            print(f"\n[DEBUG] Page: {page}")
            print(f"[DEBUG] Status Code: {resp.status_code}")
            print(f"[DEBUG] Response Snippet:\n{resp.text[:500]}\n")  # Tampilkan sebagian isi biar gak panjang

            if not resp.text.strip():
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            items = soup.find_all("li")

            if not items:
                break

            for ep in items:
                try:
                    a = ep.find("a")
                    epsTitle = a.text.strip()
                    epslink = a["href"].replace(f"{base_url}", "").strip("/")
                    epsUpdate = ep.find("span", class_="t3").text.strip() if ep.find("span", class_="t3") else ""
                    episode.append({
                        "title": epsTitle,
                        "link": epslink,
                        "epsupdate": epsUpdate
                    })
                except Exception as e:
                    print(f"[DEBUG] Skipped one item due to error: {e}")
            page += 1

    # ======================================================

    episodefl = []
    container = s.find_all("div", class_="latestest")
    for last in container:
        judul = last.find("div", class_="latestheader").text.strip()
        episodea = last.find("a")
        episodefl.append({
            "title": judul,
            "episode": episodea.text.strip(),
            "link": episodea["href"].replace(f"{base_url}", "").strip("/")
        })

    related = []
    relatedCont = s.find("div", id="related-series")
    if relatedCont:
        for rel in relatedCont.find_all("li"):
            linkRel = rel.find("a")["href"].replace(f"{base_url}/anime", "").strip("/")
            titleRel = rel.find("h3").text.strip()
            imageRel = rel.find("img")["src"]
            descRel = rel.find("div", class_="descs").text.strip()
            rattingRel = rel.find("span", class_="nilaiseries").text.strip()
            catmusimRel = rel.find("span", class_="rsrated").text.strip()
            related.append({
                "link": linkRel,
                "title": titleRel,
                "image": imageRel,
                "desc": descRel,
                "ratting": rattingRel,
                "category": catmusimRel
            })

    return {
        "title": title,
        "image": image,
        "ratting": ratting,
        "episodeFL": episodefl,
        "genre": genre,
        "duration": duration,
        "studios": studios,
        "released": released,
        "titlSinopsis": titleSins,
        "sinopsis": sinopsis,
        "episodeList": episode,
        "relatedAnime": related
    }


def nontonAnime(link):
    with sync_playwright() as p:
        anime_url = f"{base_url}/{link}"
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print(f"[*] Buka halaman: {anime_url}")
        page.goto(anime_url, wait_until="networkidle")

        print("[*] Klik tombol player...")
        try:

            # Tunggu tombol muncul
            page.wait_for_selector('[data-type="Cepat"], [data-type="Vidhide"]', timeout=1000)

            # Cek apakah tombol 'Cepat' ada
            if page.query_selector('[data-type="Cepat"]'):
                print("[+] Tombol 'Cepat' ditemukan. Klik...")
                page.click('[data-type="Cepat"]')
            elif page.query_selector('[data-type="Vidhide"]'):
                print("[+] Tombol 'Vidhide' ditemukan. Klik...")
                page.click('[data-type="Vidhide"]')
            else:
                print("[-] Tidak ada tombol yang bisa diklik.")

            time.sleep(3)
        except Exception as e:
            print("[-] Gagal klik tombol player:", e)

        print("[*] Ambil judul dan iframe video...")
        title = page.query_selector("h1.entry-title").inner_text()

        iframe = page.query_selector("iframe.lazy")
        video_url = iframe.get_attribute("src") if iframe else None

        eps_prev_el = page.query_selector("#navigation-episode .nvs:nth-child(1) a")
        eps_list_el = page.query_selector("#navigation-episode .nvs:nth-child(2) a")
        eps_next_el = page.query_selector("#navigation-episode .nvs:nth-child(3) a")

        episode_prev = eps_prev_el.get_attribute("href").replace(f"{base_url}", "").strip("/") if eps_prev_el else None
        episode_list = eps_list_el.get_attribute("href").replace(f"{base_url}/anime", "").strip("/") if eps_list_el else None
        episode_next = eps_next_el.get_attribute("href").replace(f"{base_url}", "").strip("/") if eps_next_el else None


        browser.close()

        return {
            "title": title,
            "url_video": video_url,
            "episode_prev": episode_prev,
            "eps_list": episode_list,
            "episode_next": episode_next,
        }

def search_anime(query):
    search_url = f"{base_url}?s={query.replace(' ', '+')}"
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    main = soup.find("div", class_="result")
    anime_li = main.find_all("li")

    for list in anime_li:
        title = list.find("h2").text.strip()
        desc = list.find("div", class_="descs").text.strip()
        ratting = list.find("span", class_="nilaiseries").text.strip()
        typeSeries = list.find("span", class_="typeseries").text.strip()
        musim = list.find("span", class_="rsrated").text.strip()
        genreSpans = list.find_all("span", class_="genre")
        genres = [span.text.strip() for span in genreSpans]

    return {
        "title": title,
        "desc": desc,
        "ratting": ratting,
        "typeSeries": typeSeries,
        "musim_rilis": musim,
        "genres": genres
    }

def get_anime_popular():
    url = f"{base_url}/popular-series/"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    anime_popular = []

    tab_genres = {
        "tab-1": "Action",
        "tab-2": "Comedy",
        "tab-3": "Fantasy",
        "tab-4": "Isekai",
        "tab-5": "Romance",
        "tab-6": "School"
    }

    for tab_id, genre in tab_genres.items():
        tab = soup.find("div", id=tab_id)
        if not tab:
            continue

        anime_items = tab.find_all("div", class_="animeseries")
        for anime in anime_items:
            link_tag = anime.find("a")
            title_tag = anime.find("div", class_="title less")
            image_tag = anime.find("img")
            score_tag = anime.find("span", class_="kotakscore")

            data = {
                "title": title_tag.text.strip() if title_tag else None,
                "link": link_tag["href"].replace(f"{base_url}/anime", "").strip("/")  if link_tag else None,
                "image": image_tag["src"] if image_tag else None,
                "score": score_tag.text.strip() if score_tag else None,
                "genre": genre
            }
            anime_popular.append(data)
    
    return anime_popular
