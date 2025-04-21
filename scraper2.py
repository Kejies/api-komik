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
    base_url = f"{base_url2}/page/{page}/"
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")

    anime_container = soup.find_all("div", class_="listupd")[1]
    articles = anime_container.find_all("article", class_="bs")
    
    data_list = []

    for article in articles:
        link_tag = article.find("a", href=True)
        img_tag = article.find("img", src=True)
        type_tag = article.find("div", class_="typez")
        epx_tag = article.find("span", class_="epx")
        title_tag = article.find("h2", itemprop="headline")

        link = link_tag["href"] if link_tag else ""
        img = img_tag["src"] if img_tag else ""
        typex = type_tag.get_text(strip=True) if type_tag else ""
        epx = epx_tag.get_text(strip=True) if epx_tag else ""
        title = title_tag.get_text(strip=True) if title_tag else ""

        data_list.append({
            "link": urlparse(link).path.strip(),
            "img": img,
            "type": typex,
            "epx": epx,
            "title": title
        })

    total_pages = 85

    return data_list, total_pages

def anime_popular():
    pass

def anime_detail(link):
    base_url = f"{base_url2}/anime/{link}/"
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
    status, duration, released, studios = "", "", ""
    for span in info_tags:
        text = span.text.lower()
        if "status" in text:
            status = span.text.split(":")[-1].strip()
        elif "durasi" in text:
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

                episode.append({
                    "episode": ep_num,
                    "title": ep_title,
                    "link": urlparse(ep_link).path.strip("/"),
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
        "href": link,
        "ratting": ratting,
        "episodeFL": episodeFL,
        "genre": genre,
        "status": status,
        "duration": duration,
        "studios": studios,
        "released": released,
        "titlSinopsis": title_sinopsis,
        "sinopsis": sinopsis,
        "episodeList": episode,
        "relatedAnime": related
    }
def parse_path(url, replace=None):
    if not url:
        return None
    path = urlparse(url).path.strip()
    return path.replace(replace, "") if replace else path

def anime_content(link):
    base_url = f"{base_url2}/{link}/"
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    main = soup.find("div", class_="postbody")
    title_tag = main.find("h1", class_="entry-title")
    title = title_tag.text.strip() if title_tag else None
    container = main.find("div", class_="player-embed")
    source_tag = container.find("iframe") if container else None
    source = source_tag['src'] if source_tag else None

    pag = main.find("div", class_="naveps")
    prevBTN = nextBTN = daftarEPS = None

    if pag:
        prevBTN_tag = pag.find("a", rel="prev")
        nextBTN_tag = pag.find("a", rel="next")
        daftarEPS_tag = pag.find("div", class_="nvsc").find("a") if pag.find("div", class_="nvsc") else None

        prevBTN = prevBTN_tag['href'] if prevBTN_tag else None
        nextBTN = nextBTN_tag['href'] if nextBTN_tag else None
        daftarEPS = daftarEPS_tag['href'] if daftarEPS_tag else None

    return {
        'title': title,
        'video_url': source,
        'episode_prev': parse_path(prevBTN),
        'episode_next': parse_path(nextBTN),
        'eps_list': parse_path(daftarEPS, replace="/anime")
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
        type_tag = article.find("div", class_="typez")
        epx_tag = article.find("span", class_="epx")
        title_tag = article.find("h2", itemprop="headline")

        link = link_tag["href"] if link_tag else ""
        img = img_tag["src"] if img_tag else ""
        typex = type_tag.get_text(strip=True) if type_tag else ""
        epx = epx_tag.get_text(strip=True) if epx_tag else ""
        title = title_tag.get_text(strip=True) if title_tag else ""

        results.append({
            "link": urlparse(link).path.replace("/anime", ""),
            "img": img,
            "type": typex,
            "epx": epx,
            "title": title
        })

    return results