import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

BASE_URL = "https://manhwalist.xyz/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

def popular():
    res = requests.get(BASE_URL, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    main_element = soup.find("div", class_="popularslider")
    element = main_element.find_all("div", class_="bs")

    data_list = []
    for i, komik in enumerate(element, start=1):
        link = komik.find("a")["href"]
        parsed_link = urlparse(link).path.strip("/").replace("manga/", "")
        img_url = komik.find("img", class_="ts-post-image")["src"]
        title = komik.find("div", class_="tt").text.strip()
        tipe = komik.find("span", class_="type")["class"][1]
        warna = komik.find("span", class_="colored").text.strip() if komik.find("span", class_="colored") else ""
        kolom_chapter = komik.find("div", class_="adds").find("div", class_="epxs")
        chapter = re.sub(r'\s+', ' ', kolom_chapter.text.strip()) if kolom_chapter else ""
        ratting = komik.find("div", class_="numscore").text.strip()
        data_list.append( {
                        "link": parsed_link,
                        "title": title,
                        "colored": warna,
                        "type": tipe,
                        "chapter": chapter,
                        "ratting": ratting,
                        "img": img_url
                      })
        if i >= 8:
            break
    return data_list

def terbaru(page=1):
    base_url = f"{BASE_URL}/project/page/{page}"
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    komik_container = soup.find("div", class_="listupd cp")
    komik_list = komik_container.find_all("div", class_="bs styletere")

    data_list = []
    for komik in komik_list:
        link = komik.find("a")["href"]
        parsed_link = urlparse(link).path.strip("/").replace("manga/", "")
        img_tag = komik.find("img", class_="ts-post-image")
        img_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else "null"
        title_tag = komik.find("div", class_="tt")
        title = title_tag.text.strip() if title_tag else "Tidak Ada Judul"
        chapterCont = komik.find("div", class_="adds")
        chapter = chapterCont.find("div", class_="epxs").text.strip()
        tipe = komik.find("span", class_="type")["class"][1]
        warna = komik.find("span", class_="colored").text.strip() if komik.find("span", class_="colored") else ""
        last_update = chapterCont.find("div", class_="epxdate").text.strip()

        data_list.append({
            "link": parsed_link,
            "title": title,
            "colored": warna,
            "type": tipe,
            "chapter": chapter,
            "last_update": last_update,
            "img": img_url
        })

    pagination = soup.find("div", class_="pagination")

    if pagination:
        page_numbers = [a.text.strip() for a in pagination.find_all("a", class_="page-numbers") if a.text.strip().isdigit()]
        
        total_pages = int(max(page_numbers)) if page_numbers else 1
    else:
        total_pages = 1

    current_page_elem = soup.find("span", class_="page-numbers current")
    current_page = int(current_page_elem.text.strip()) if current_page_elem else 1

    if current_page >= total_pages:
        total_pages = current_page


    return data_list, total_pages

def detail(link):
    base_url = f"{BASE_URL}manga/{link}"
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    komik_detail = soup.find("div", class_="main-info")

    # Judul
    dirty_title = komik_detail.find("h1", class_="entry-title", itemprop="name")
    title = re.sub(r'\s+', ' ', dirty_title.text.strip()) if dirty_title else ""
    # Gambar
    img_container = komik_detail.find("div", class_="thumb", itemprop="image")
    img = img_container.find("img", itemprop="image")["src"] if img_container and img_container.find("img", itemprop="image") else ""

    # Rating
    ratting = komik_detail.find("div", itemprop="ratingValue")
    ratting = ratting.text.strip() if ratting else ""

    # Informasi tambahan
    info_container = komik_detail.find("div", class_="tsinfo bixbox")
    status = author = artist = typeKomik = released = ""
    if info_container:
        divs = info_container.find_all("div", class_="imptdt")

        for div in divs:
            key = div.text.strip().lower().replace(":", "").replace('"', '').strip()
            div.extract()
            value = div.find("i").text.strip() if div.find("i") else ""

            if "status" in key:
                status = value
            elif "type" in key:
                typeKomik = div.find("a").text.strip() if div.find("a") else ""
            elif "released" in key:
                released = value
            elif "author" in key:
                author = value
            elif "artist" in key:
                artist = value

    # Sinopsis

    short_sinopsis_tag = komik_detail.find("div", class_="entry-content entry-content-single", itemprop="description")
    sinopsis = short_sinopsis_tag.find("p").text.strip()
    # Genre
    genre_container = komik_detail.find("span", class_="mgen")
    genre = [a.text.strip() for a in genre_container.find_all("a")] if genre_container else []

    # Komik terkait
    related_container = soup.find("div", class_="listupd")
    related = []
    if related_container:
        for komik in related_container.find_all("div", class_="bsx"):
            linkrel = komik.find("a")["href"]
            parsed_link = urlparse(linkrel).path.strip("/").replace("manga/", "")
            img_tag = komik.find("img", class_="ts-post-image")
            img_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else "null"
            title_tag = komik.find("div", class_="tt")
            title_related = title_tag.text.strip() if title_tag else "Tidak Ada Judul"
            chapterCont = komik.find("div", class_="adds")
            chapter_related = chapterCont.find("div", class_="epxs").text.strip()
            tipe = komik.find("span", class_="type")["class"][1]
            warna = komik.find("span", class_="colored").text.strip() if komik.find("span", class_="colored") else ""
            last_update = chapterCont.find("div", class_="epxs").text.strip()

            related.append({
                "link": parsed_link,
                "title": title_related,
                "colored": warna,
                "type": tipe,
                "chapter": chapter_related,
                "last_update": last_update,
                "img": img_url
            })
    # Daftar chapter
    chap_list_container = komik_detail.find("div", id="chapterlist")
    chapter_list = []
    if chap_list_container:
        chap_li = chap_list_container.find_all("li")
        for chapter in chap_li:
            linkch = chapter.find("a")
            chap = chapter.find("span", class_="chapternum").text.strip()
            update = chapter.find("span", class_="chapterdate").text.strip()

            chapter_list.append({
                "link": urlparse(linkch["href"]).path.strip("/") if linkch else "",
                "chapter": chap,
                "update": update
            })
    data_list = {
        "title": title,
        "first_chapter": {
            "title": chap_li[-1].find("span", class_="chapternum").text.strip(),
            "chapter_url": urlparse(chap_li[-1].find("a")["href"]).path.strip("/"),
        },
        "last_chapter": {
            "title": chap_li[0].find("span", class_="chapternum").text.strip(),
            "chapter_url": urlparse(chap_li[0].find("a")["href"]).path.strip("/"),
        },
        "img": img,
        "href": link,
        "ratting": ratting,
        "status": status,
        "author": author,
        "artist": artist,
        "released": released,
        "type": typeKomik,
        "genre": genre,
        "sinopsis": sinopsis,
        "related": related,
        "chapter_list": chapter_list
    }
    return data_list

def get_daftar_chapter(link):
    base_url = f"{BASE_URL}manga/{link}"
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    komik_detail = soup.find("div", class_="main-info")
    chap_list_container = komik_detail.find("div", id="chapterlist")

    chapter_list = []

    if chap_list_container:
        chap_li = chap_list_container.find_all("li")

        for chapter in chap_li:
            chap_text = chapter.find("span", class_="chapternum").text.strip()
            chap_number = re.search(r'\d+', chap_text)

            if chap_number:
                chapter_list.append(int(chap_number.group())) 
    return {"chapters": sorted(chapter_list, reverse=True)}

def content(link):
    base_url = f"{BASE_URL}{link}"
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    main = soup.find("div", class_="chapterbody")
    title = re.sub(r'\s+', ' ', main.find("h1", class_="entry-title", itemprop="name").text.strip()) if main.find("h1", class_="entry-title", itemprop="name") else ""
    prev_link = main.find("a", rel="prev")["href"] if main.find("a", rel="prev") else ""
    prev_chap = urlparse(prev_link).path.strip("/")
    next_link = main.find("a", rel="next")["href"] if main.find("a", rel="next") else ""
    next_chap = urlparse(next_link).path.strip("/")

    daftar_element = main.find("div", class_="allc")
    daftar_chap_link = urlparse(daftar_element.find("a", href=True, rel=False)["href"] ).path.strip("/").replace("manga/", "")

    content_container = main.find("div", id="readerarea")
    content = content_container.select("img") if content_container else []
    main_content = [img["src"] for img in content if "src" in img.attrs]
    daftar_chap = get_daftar_chapter(daftar_chap_link)["chapters"]
    plan_link = link.strip("/").replace("-", " ").split()
    
    current_chap = int(plan_link[-1])

    dirty_prev = current_chap - 1 if current_chap > min(daftar_chap) else None
    dirty_next = current_chap + 1 if (current_chap + 1) in daftar_chap else None

    prev_chap = "-".join(plan_link[:-1] + [str(dirty_prev)]) if dirty_prev else None
    next_chap = "-".join(plan_link[:-1] + [str(dirty_next)]) if dirty_next else None

    return {
        "title": title,
        "prev_chapter": prev_chap,
        "daftar_chapter": daftar_chap_link,
        "next_chapter": next_chap,
        "content": main_content,
    }
    
def search(query):
    search_url = f"{BASE_URL}?s={query.replace(' ', '+')}"
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    main = soup.find("div", class_="listupd")
    main_post = main.find_all("div", class_="bs")

    komik_list = []

    for komik in main_post:
        link = komik.find("a")["href"]
        parsed_link = urlparse(link).path.strip("/").replace("manga/", "")
        img_tag = komik.find("img", class_="ts-post-image")
        img_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else "null"
        title_tag = komik.find("div", class_="tt")
        title = title_tag.text.strip() if title_tag else "Tidak Ada Judul"
        chapterCont = komik.find("div", class_="adds")
        chapter = chapterCont.find("div", class_="epxs").text.strip()
        tipe = komik.find("span", class_="type")["class"][1]
        warna = komik.find("span", class_="colored").text.strip() if komik.find("span", class_="colored") else ""

        komik_list.append({
            "link": parsed_link,
            "title": title,
            "colored": warna,
            "type": tipe,
            "chapter": chapter,
            "img": img_url
        })
    return komik_list

def find_genre(genre, page=1):
    base_url = f"{BASE_URL}genres/{genre}/page/{page}"
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    komik_container = soup.find("div", class_="postbody full")
    komik_list = komik_container.find_all("div", class_="bs")

    data_list = []
    for komik in komik_list:
        link = komik.find("a")["href"]
        parsed_link = urlparse(link).path.strip("/").replace("manga/", "")
        img_tag = komik.find("img", class_="ts-post-image")
        img_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else "null"
        title_tag = komik.find("div", class_="tt")
        title = title_tag.text.strip() if title_tag else "Tidak Ada Judul"
        chapterCont = komik.find("div", class_="adds")
        chapter = chapterCont.find("div", class_="epxs").text.strip()
        tipe = komik.find("span", class_="type")["class"][1]
        warna = komik.find("span", class_="colored").text.strip() if komik.find("span", class_="colored") else ""

        data_list.append({
            "link": parsed_link,
            "title": title,
            "genre": warna,
            "type": tipe,
            "chapter": chapter,
            "img": img_url
        })

    pagination = soup.find("div", class_="pagination")

    if pagination:
        page_numbers = [a.text.strip() for a in pagination.find_all("a", class_="page-numbers") if a.text.strip().isdigit()]
        
        total_pages = int(max(page_numbers)) if page_numbers else 1
    else:
        total_pages = 1

    current_page_elem = soup.find("span", class_="page-numbers current")
    current_page = int(current_page_elem.text.strip()) if current_page_elem else 1

    if current_page >= total_pages:
        total_pages = current_page
    return data_list, total_pages

def get_search_manhua(query):
    search_url = f"https://komikindo2.com/daftar-manga/?status=&type=Manhua&format=&order=&title={query.replace(' ', '+')}"
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    main = soup.find("div", class_="listupd")
    main_post = main.find_all("div", class_="animepost")

    komik_list = []

    for komik in main_post:
        link = komik.find("a")["href"]
        parsed_link = urlparse(link).path.strip("/").replace("komik/", "")
        img_tag = komik.find("img", itemprop="image")
        img_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else "null"
        title_tag = komik.find("div", class_="tt").find("h4")
        title = title_tag.text.strip() if title_tag else "Tidak Ada Judul"
        tipe = komik.find("span", class_="typeflag")["class"][1]
        warna = komik.find("div", class_="warnalabel").text.strip() if komik.find("div", class_="warnalabel") else ""

        komik_list.append({
            "link": parsed_link,
            "title": title,
            "colored": warna,
            "type": tipe,
            "img": img_url
        })
        print(komik_list)
    return komik_list

def get_manhua_list():
    base_url = f"https://komikindo2.com/manhua/"
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    komik_container = soup.find("div", class_="postbody")
    komik_list = komik_container.find_all("div", class_="animepost")

    data_list = []
    for komik in komik_list:
        link = komik.find("a")["href"]
        parsed_link = urlparse(link).path.strip("/").replace("manga/", "")
        img_tag = komik.find("img", itemprop="image")
        img_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else "null"
        title_tag = komik.find("div", class_="tt").find("h4")
        title = title_tag.text.strip() if title_tag else ""
        chapter = komik.find("a", itemprop="url").text.strip()
        chapter = " ".join(chapter.split())
        tipe = komik.find("span", class_="typeflag")["class"][1] if komik.find("span", class_="typeflag") else ""
        warna = komik.find("div", class_="warnalabel").text.strip() if komik.find("div", class_="warnalabel") else ""
        last_update = komik.find("span", class_="datech").text.strip()

        data_list.append({
            "link": parsed_link,
            "title": title,
            "colored": warna,
            "type": tipe,
            "chapter": chapter,
            "last_update": last_update,
            "img": img_url
        })

    pagination = soup.find("div", class_="pagination")

    if pagination:
        page_numbers = [a.text.strip() for a in pagination.find_all("a", class_="page-numbers") if a.text.strip().isdigit()]
        
        total_pages = int(max(page_numbers)) if page_numbers else 1
    else:
        total_pages = 1

    current_page_elem = soup.find("span", class_="page-numbers current")
    current_page = int(current_page_elem.text.strip()) if current_page_elem else 1

    if current_page >= total_pages:
        total_pages = current_page

    return data_list, total_pages