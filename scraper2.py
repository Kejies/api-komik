import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

BASE_URL = "https://anime-indo.lol"
base_url2 = "https://tensei.id"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

def anime_terbaru(page=1):
    base_url = f"{BASE_URL}/page/{page}/"
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    anime_container = soup.find("div", class_="menu")
    anime_list = anime_container.find_all("a")
    data_list = []

    for anime in anime_list:
        link = anime["href"]
        parsed_link = urlparse(link).path.strip("/").replace("manga/", "")
        img_tag = anime.find("img")

        # Ambil data-original jika ada
        if img_tag:
            img_url = img_tag.get("data-original") or img_tag.get("src", "null")
        else:
            img_url = "null"

        title_tag = anime.find("p")
        title = title_tag.text.strip() if title_tag else "Tidak Ada Judul"

        eps_tag = anime.find("span", class_="eps")
        eps = eps_tag.text.strip() if eps_tag else ""

        data_list.append({
            "link": parsed_link,
            "title": title,
            "episode": eps,
            "img": img_url
        })

    pagination = soup.find("div", class_="pag")

    if pagination:
        page_elements = pagination.find_all(["a", "span"])

        page_numbers = [
            int(el.text.strip()) for el in page_elements
            if el.text.strip().isdigit()
        ]

        total_pages = max(page_numbers) if page_numbers else 1
    else:
        total_pages = 1

    return data_list, total_pages

def anime_popular():
    pass

def normalize_anime_url(url: str) -> str:
    path = urlparse(url).path.strip("/").lower()

    # Ganti 2nd-season, second-season, etc jadi season-2
    path = re.sub(r"\b(2nd|second)\b[- ]season", "season-2", path)
    path = re.sub(r"\b(3rd|third)\b[- ]season", "season-3", path)
    path = re.sub(r"\b(1st|first)\b[- ]season", "season-1", path)
    
    path = path.rstrip("/")

    return path
def convert_to_ordinal_slug(slug: str) -> str:
    match = re.search(r"(.*)-season-(\d+)$", slug)
    if not match:
        return slug 

    base, season = match.groups()
    season_int = int(season)

    # Map angka ke ordinal
    if season_int == 1:
        ordinal = "1st"
    elif season_int == 2:
        ordinal = "2nd"
    elif season_int == 3:
        ordinal = "3rd"
    else:
        ordinal = f"{season_int}th"

    return f"{base}-{ordinal}-season"
def normalize_ep_link_to_match_anime_link(link: str, ep_link: str) -> str:
    ep_path = urlparse(ep_link).path.strip("/")
    match = re.search(r"(episode-\d+)$", ep_path.lower())
    if not match:
        return None
    
    episode_part = match.group(1)
    ep_base_slug = re.sub(r"-episode-\d+$", "", ep_path.lower())
    normalized_link = normalize_anime_url(link)
    normalized_ep = normalize_anime_url(ep_base_slug)

    if normalized_link == normalized_ep:
        return f"{normalized_link}/{episode_part}"
    
    return None

def anime_detail(link):
    base_url = f"{base_url2}/anime/{normalize_anime_url(link)}/"
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    main = soup.find("div", class_="postbody")

    # Title
    title_tag = main.find("h1", itemprop="name", class_="entry-title")
    title = title_tag.text.strip() if title_tag else ""

    # Image
    img_container = main.find("div", class_="thumb")
    img_tag = img_container.find("img") if img_container else None
    image = img_tag["src"] if img_tag and "src" in img_tag.attrs else ""

    # Rating
    rating_div = main.find("div", class_="rating")
    ratting = rating_div.find("strong").text.strip().replace("Rating", "").strip() if rating_div else ""

    # Duration
    info_tags = main.find_all("span")
    duration, released, studios = "", "", ""
    for span in info_tags:
        text = span.text.lower()
        if "durasi" in text:
            duration = span.text.split(":")[-1].strip()
        elif "dirilis" in text:
            released = span.text.split(":")[-1].strip()
        elif "studio" in text:
            studio_link = span.find("a")
            studios = studio_link.text.strip() if studio_link else span.text.split(":")[-1].strip()

    # Genre
    genre_container = main.find("div", class_="genxed")
    genre = []
    if genre_container:
        for a in genre_container.find_all("a"):
            genre.append({
                "title": a.text.strip(),
                "link": urlparse(a["href"]).path.strip("/")  # atau a["href"] langsung kalau sudah rapi
            })

    # Title + Sinopsis
    title_sinopsis = main.find("div", class_="releases").text.strip() if main.find("div", class_="releases") else ""
    sinopsis_container = main.find("div", class_="entry-content")

    if sinopsis_container:
        sinopsis = sinopsis_container.get_text(separator="\n", strip=True)
        # Hapus kalimat promosi yang cocok dengan pola
        sinopsis = re.sub(r'Temukan Anime .*? di Tensei\.id', '', sinopsis).replace("|", "").strip()
    else:
        sinopsis = ""


    episode = []
    eplist_container = main.find("div", class_="eplister")
    if eplist_container:
        for li in eplist_container.find_all("li"):
            a = li.find("a")
            if a:
                ep_num = a.find("div", class_="epl-num").text.strip() if a.find("div", class_="epl-num") else ""
                ep_title = a.find("div", class_="epl-title").text.strip() if a.find("div", class_="epl-title") else ""
                ep_update = a.find("div", class_="epl-date").text.strip() if a.find("div", class_="epl-date") else ""
                ep_link = a["href"]

                matched_slug = normalize_ep_link_to_match_anime_link(link, ep_link)

                if matched_slug:
                    episode.append({
                        "episode": ep_num,
                        "title": ep_title,
                        "link": matched_slug,
                        "epsupdate": ep_update
                    })

    episodeFL = {}
    lastend_container = main.find("div", class_="lastend")
    if lastend_container:
        first_episode = lastend_container.find("div", class_="inepcx").find("a")
        last_episode = lastend_container.find_all("div", class_="inepcx")[-1].find("a")
        
        if first_episode:
            episodeFL['first_episode'] = {
                "title": first_episode.find("span", class_="epcurfirst").text.strip() if first_episode.find("span", class_="epcurfirst") else "",
                "link": episode[-1]['link']  
            }
        
        if last_episode:
            episodeFL['last_episode'] = {
                "title": last_episode.find("span", class_="epcurlast").text.strip() if last_episode.find("span", class_="epcurlast") else "",
                "link": episode[0]['link']  
            }

    related = []
    recommended_container = soup.find("div", class_="listupd")
    for article in recommended_container.find_all("article", class_="bs"):
        a = article.find("a", href=True)
        if not a:
            continue

        rel_link = a["href"]
        rel_title_tag = a.find("h2", itemprop="headline")
        rel_title = rel_title_tag.text.strip() if rel_title_tag else ""

        img_tag = a.find("img")
        rel_img = img_tag.get("data-src") or img_tag.get("src", "") if img_tag else ""

        related.append({
            "title": rel_title,
            "image": rel_img,
            "link": urlparse(rel_link).path.strip("/")
        })


    return {
        "title": title,
        "image": image,
        "ratting": ratting,
        "episodeFL": episodeFL,
        "genre": genre,
        "duration": duration,
        "studios": studios,
        "released": released,
        "titlSinopsis": title_sinopsis,
        "sinopsis": sinopsis,
        "episodeList": episode,
        "relatedAnime": related
    }

def anime_content(link):
    base_url = f"{BASE_URL}/{link}/"
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    main = soup.find("div", class_="ngiri")
    title_tag = main.find("h1", class_="title")
    title = title_tag.text.strip()
    source_tag = soup.find("a", class_="server")
    source = source_tag['data-video']
    pag = main.find("div", class_="navi")
    pagin = []

    if pag:
        pag_a = pag.find_all("a")
        episode_prev = None
        episode_next = None
        eps_list = None

        for a in pag_a:
            title_pag = a.text.strip()

            if "Download Mp4" in title_pag:
                continue

            link_pag_tag = a["href"]
            link_pag = link_pag_tag.replace("/anime", "/")

            if "Prev" in title_pag:
                episode_prev = link_pag
            elif "Next" in title_pag:
                episode_next = link_pag
            elif "Semua Episode" in title_pag:
                eps_list = link_pag

    return {
        'title': title,
        'video_url': f'{BASE_URL}{source}',
        'episode_prev': episode_prev,
        'episode_next': episode_next,
        'eps_list': eps_list
    }

def anime_search(query):
    base_url = f"{base_url2}?s={query}"
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    articles = soup.find_all("article", class_="bs")
    results = []

    for article in articles:
        link_tag = article.find("a", href=True)
        img_tag = article.find("img", src=True)
        type_tag = article.find("div", class_="typex")
        epx_tag = article.find("span", class_="epx")
        title_tag = article.find("h2", itemprop="headline")

        link = link_tag["href"] if link_tag else ""
        img = img_tag["src"] if img_tag else ""
        typex = type_tag.get_text(strip=True) if type_tag else ""
        epx = epx_tag.get_text(strip=True) if epx_tag else ""
        title = title_tag.get_text(strip=True) if title_tag else ""

        results.append({
            "link": urlparse(link).path.strip("/"),
            "img": img,
            "type": typex,
            "epx": epx,
            "title": title
        })

    return results
