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

def get_manhua_list(page=1):
    base_url = f"https://komiklab.id/manga?page={page}&categorie=&type=manhua&sort=updated&search="
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    data = []
    items = soup.select('.product__item')

    for item in items:
        title_tag = item.select_one('h5 a')
        type_tag = item.select_one('a[href*="type=manhua"]')

        if title_tag and type_tag:
            link = title_tag['href'].replace("/manga", "").strip()
            detail_url = f"https://komiklab.id/manga/{link}"
            resp = requests.get(detail_url, headers=headers)
            soup = BeautifulSoup(resp.content, "html.parser")
            main = soup.select("div", class_="anime-details")
            title = soup.find("h3")
            type_ = type_tag.text.strip()

            data.append({
                'title': title,
                'link': link,
                'type': type_
            })

    print(data)

get_manhua_list(1)

def get_manhua_detail(link):
    base_url = f"https://komikindo2.com/komik/{link}"
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    komik_detail = soup.find("div", class_="postbody")

    # Judul
    dirty_title = komik_detail.find("h1", class_="entry-title", itemprop="name")
    title = re.sub(r'\s+', ' ', dirty_title.text.strip()) if dirty_title else ""

    # Chapter pertama dan terakhir
    chap_container = komik_detail.find("div", class_="epsbaru")
    first_chap = last_chap = ""
    if chap_container:
        first_chap_link = chap_container.find("div", class_="epsbr chapter-awal")
        last_chap_link = chap_container.find_all("div", class_="epsbr")

        if first_chap_link and first_chap_link.find("a", href=True):
            first_chap = urlparse(first_chap_link.find("a", href=True)["href"]).path.strip("/").replace("komik/", "")
            first_chap_title = re.sub(r'\s+', ' ', first_chap_link.find("span", class_="barunew").text.strip())

        if last_chap_link:
            last_chap = urlparse(last_chap_link[-1].find("a", href=True)["href"]).path.strip("/").replace("komik/", "")
            last_chap_title = re.sub(r'\s+', ' ', last_chap_link[-1].find("span", class_="barunew").text.strip())

    # Gambar
    img_container = komik_detail.find("div", class_="thumb", itemprop="image")
    img = img_container.find("img", itemprop="image")["src"] if img_container and img_container.find("img", itemprop="image") else ""

    # Rating
    ratting = komik_detail.find("i", itemprop="ratingValue")
    ratting = ratting.text.strip() if ratting else ""

    # Informasi tambahan
    info_container = komik_detail.find("div", class_="spe")
    alternative_title = status = author = ilustrator = jenis_komik = ""
    tema = []

    if info_container:
        spans = info_container.find_all("span")

        for span in spans:
            label = span.find("b")
            if label:
                key = label.text.strip().lower().replace(":", "")

                # Hapus <b> agar hanya menyisakan nilai teks setelahnya
                label.extract()
                value = span.text.strip()

                if key == "judul alternatif":
                    alternative_title = value
                elif key == "status":
                    status = value
                elif key == "pengarang":
                    author = value
                elif key == "ilustrator":
                    ilustrator = value
                elif key == "jenis komik":
                    jenis_komik = span.find("a").text.strip() if span.find("a") else value
                elif key == "tema":
                    tema = [a.text.strip() for a in span.find_all("a")] if span.find("a") else [value]

    # Sinopsis
    short_sinopsis = ""
    sinopsis = ""
    short_sinopsis_tag = komik_detail.find("div", class_="shortcsc sht2")
    sinopsis_tag = komik_detail.find("div", id="sinopsis")

    if short_sinopsis_tag and short_sinopsis_tag.find("p"):
        short_sinopsis = re.sub(r'\s+', ' ', short_sinopsis_tag.find("p").text.strip())

    if sinopsis_tag and sinopsis_tag.find("p"):
        sinopsis = re.sub(r'\s+', ' ', sinopsis_tag.find("p").text.strip())

    # Genre
    genre_container = komik_detail.find("div", class_="genre-info")
    genre = [a.text.strip() for a in genre_container.find_all("a")] if genre_container else []

    # Komik terkait
    related_container = komik_detail.find("div", class_="miripmanga")
    related = []
    if related_container:
        for r in related_container.find_all("li"):
            linkrel = urlparse(r.find("a", class_="series")["href"]).path.strip("/").replace("komik/", "") if r.find("a", class_="series") else ""
            rel_img = r.find("img", itemprop="image")["src"] if r.find("img", itemprop="image") else ""
            rel_title = r.find("img", itemprop="image")["title"] if r.find("img", itemprop="image") else ""
            sinopsis = r.find("div", class_="excerptmirip").text.strip() if r.find("div", class_="excerptmirip") else ""
            tipe = r.find("span", class_="typeflag")["class"][-1] if r.find("span", class_="typeflag") else ""
            warna_label = r.find("div", class_="warnalabel")
            warna = re.sub(r'\s+', ' ', warna_label.text.strip()) if warna_label else "Tidak Berwarna"

            related.append({
                "link": linkrel,
                "img": rel_img,
                "title": rel_title,
                "sinopsis": sinopsis,
                "variant": warna,
                "type": tipe
            })

    # Daftar chapter
    chap_list_container = komik_detail.find("div", id="chapter_list")
    chapter_list = []
    if chap_list_container:
        for chapter in chap_list_container.find_all("li"):
            linkch = chapter.find("a")
            chap = re.sub(r'\s+', ' ', linkch.text.strip()) if linkch else ""
            update = chapter.find("span", class_="dt")
            update = update.find("a").text.strip() if update and update.find("a") else ""

            chapter_list.append({
                "link": urlparse(linkch["href"]).path.strip("/").replace("komik/", "") if linkch else "",
                "chapter": chap,
                "update": update
            })

    # Data akhir
    data_list = {
        "title": title,
        "first_chapter": {
            "title": first_chap_title,
            "chapter_url": first_chap,
        },
        "last_chapter": {
            "title": last_chap_title,
            "chapter_url": last_chap,
        },
        "img": img,
        "href":link,
        "ratting": ratting,
        "status": status,
        "author": author,
        "artist": ilustrator,
        "released": "unknown",
        "type": jenis_komik,
        "genre": genre,
        "sinopsis": short_sinopsis,
        "related": related,
        "chapter_list": chapter_list
    }
    return data_list

def get_manhua_content(link):
    base_url = f"https://komikindo2.com/{link}"
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    main = soup.find("div", class_="chapter-area")

    title = re.sub(r'\s+', ' ', main.find("h1", class_="entry-title").text.strip()) if main.find("h1", class_="entry-title") else ""

    prev_link = main.find("a", rel="prev")["href"] if main.find("a", rel="prev") else ""
    prev_chap = urlparse(prev_link).path.strip("/").replace("komik/", "")
    next_link = main.find("a", rel="next")["href"] if main.find("a", rel="next") else ""
    next_chap = urlparse(next_link).path.strip("/").replace("komik/", "")

    daftar_element = main.find("div", class_="nextprev")
    daftar_chap_link = daftar_element.find("a", href=True, rel=False)["href"] if daftar_element else ""
    daftar_chap = urlparse(daftar_chap_link).path.strip("/").replace("komik/", "")

    content_alt = link.strip("/").replace("-", " ").title()
    content_container = main.find("div", class_="chapter-image eastengine bc")
    content = content_container.select("img") if content_container else []
    main_content = [img["src"] for img in content if "src" in img.attrs]

    print({
        "title": title,
        "prev_chapter": prev_chap,
        "daftar_chapter": daftar_chap,
        "next_chapter": next_chap,
        "content": main_content,
    })
    return {
        "title": title,
        "prev_chapter": prev_chap,
        "daftar_chapter": daftar_chap,
        "next_chapter": next_chap,
        "content": main_content,
    }

def fetch_page(url):
    """Fungsi untuk mengambil halaman dan mengembalikan objek BeautifulSoup."""
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()  # Raise error jika status bukan 200
        return BeautifulSoup(res.content, "html.parser")
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_comic_content(link):
    """Coba ambil data dari Komikindo, jika gagal, coba dari ManhwaList."""
    komikindo_url = f"https://komikindo2.com/{link}"
    manhwa_url = f"{BASE_URL}{link}"  # BASE_URL = URL ManhwaList

    # Coba ambil dari Komikindo
    soup = fetch_page(komikindo_url)
    if soup:
        result = parse_comic_page(soup, source="komikindo")
        if result and result["content"]:  # Pastikan data valid
            return result

    # Jika gagal, coba ambil dari ManhwaList
    soup = fetch_page(manhwa_url)
    if soup:
        return parse_comic_page(soup, source="manhwa")

    return None  # Jika keduanya gagal

def parse_comic_page(soup, source):
    """Parsing halaman komik berdasarkan sumber (Komikindo atau ManhwaList)."""
    main = soup.find("div", class_="chapter-area") or soup.find("div", class_="chapterbody")
    if not main:
        return None

    title_element = main.find("h1", class_="entry-title") or main.find("h1", class_="entry-title", itemprop="name")
    title = re.sub(r'\s+', ' ', title_element.text.strip()) if title_element else ""

    prev_link = main.find("a", rel="prev")["href"] if main.find("a", rel="prev") else ""
    prev_chap = urlparse(prev_link).path.strip("/").replace("komik/", "").replace("manga/", "")

    next_link = main.find("a", rel="next")["href"] if main.find("a", rel="next") else ""
    next_chap = urlparse(next_link).path.strip("/").replace("komik/", "").replace("manga/", "")

    daftar_element = main.find("div", class_="nextprev") or main.find("div", class_="allc")
    daftar_chap_link = daftar_element.find("a", href=True)["href"] if daftar_element else ""
    daftar_chap = urlparse(daftar_chap_link).path.strip("/").replace("komik/", "").replace("manga/", "")

    content_container = main.find("div", class_="chapter-image eastengine bc") or main.find("div", id="readerarea")
    content = content_container.select("img") if content_container else []
    main_content = [img["src"] for img in content if "src" in img.attrs]

    return {
        "title": title,
        "prev_chapter": prev_chap,
        "daftar_chapter": daftar_chap,
        "next_chapter": next_chap,
        "content": main_content,
        "source": source  # Indikasi dari mana data diambil
    }

def get_manga_detail(link):
    """Mengambil data dari Komikindo atau ManhwaList."""
    komikindo_url = f"{BASE_KOMIKINDO_URL}{link}"
    manhwa_url = f"{BASE_MANHWA_URL}manga/{link}"
    
    # Coba ambil dari Komikindo
    soup = fetch_page(komikindo_url)
    if soup:
        result = parse_manga_page(soup, source="komikindo")
        if result:
            return result
    
    # Jika gagal, coba dari ManhwaList
    soup = fetch_page(manhwa_url)
    if soup:
        return parse_manga_page(soup, source="manhwa")
    
    return None
BASE_MANHWA_URL = "https://manhwa.example.com/"  # Ganti dengan URL yang benar
BASE_KOMIKINDO_URL = "https://komikindo2.com/komik/"
def parse_manga_page(soup, source):
    """Parsing halaman manga berdasarkan sumber."""
    main_info = soup.find("div", class_="postbody") or soup.find("div", class_="main-info")
    if not main_info:
        return None
    
    # Judul
    title_tag = main_info.find("h1", class_="entry-title", itemprop="name")
    title = re.sub(r'\s+', ' ', title_tag.text.strip()) if title_tag else ""
    
    # Gambar
    img_tag = main_info.find("img", itemprop="image")
    img = img_tag["src"] if img_tag else ""
    
    # Rating
    rating_tag = main_info.find("i", itemprop="ratingValue") or main_info.find("div", itemprop="ratingValue")
    rating = rating_tag.text.strip() if rating_tag else ""
    
    # Status, author, artist, type
    info_container = main_info.find("div", class_="spe") or main_info.find("div", class_="tsinfo bixbox")
    status = author = artist = type_manga = ""
    if info_container:
        for span in info_container.find_all("span"):
            label = span.find("b")
            if label:
                key = label.text.strip().lower().replace(":", "")
                label.extract()
                value = span.text.strip()
                if "status" in key:
                    status = value
                elif "pengarang" in key or "author" in key:
                    author = value
                elif "ilustrator" in key or "artist" in key:
                    artist = value
                elif "jenis komik" in key or "type" in key:
                    type_manga = span.find("a").text.strip() if span.find("a") else value
    
    # Genre
    genre_container = main_info.find("div", class_="genre-info") or main_info.find("span", class_="mgen")
    genre = [a.text.strip() for a in genre_container.find_all("a")] if genre_container else []
    
    # Sinopsis
    sinopsis_tag = main_info.find("div", id="sinopsis") or main_info.find("div", class_="entry-content entry-content-single", itemprop="description")
    sinopsis = re.sub(r'\s+', ' ', sinopsis_tag.text.strip()) if sinopsis_tag else ""
    
    # Daftar chapter
    chapter_list = []
    chap_list_container = main_info.find("div", id="chapter_list") or main_info.find("div", id="chapterlist")
    if chap_list_container:
        for chapter in chap_list_container.find_all("li"):
            link_tag = chapter.find("a")
            chap_title = chapter.find("span", class_="chapternum").text.strip() if chapter.find("span", class_="chapternum") else ""
            update_tag = chapter.find("span", class_="chapterdate") or chapter.find("span", class_="dt")
            update = update_tag.text.strip() if update_tag else ""
            chapter_list.append({
                "link": urlparse(link_tag["href"]).path.strip("/") if link_tag else "",
                "chapter": chap_title,
                "update": update
            })
    
    # Chapter pertama dan terakhir
    first_chapter = chapter_list[-1] if chapter_list else {}
    last_chapter = chapter_list[0] if chapter_list else {}
    
    return {
        "title": title,
        "first_chapter": first_chapter,
        "last_chapter": last_chapter,
        "img": img,
        "rating": rating,
        "status": status,
        "author": author,
        "artist": artist,
        "type": type_manga,
        "genre": genre,
        "sinopsis": sinopsis,
        "chapter_list": chapter_list,
        "source": source
    }

import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

BASE_MANHWA_URL = "https://manhwalist.xyz/"
BASE_KOMIKINDO_URL = "https://komikindo2.com/"
headers = {
    "User -Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

def fetch_page(url):
    """Fungsi untuk mengambil halaman dan mengembalikan objek BeautifulSoup."""
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()  # Raise error jika status bukan 200
        return BeautifulSoup(res.content, "html.parser")
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_manga_page(soup, source):
    """Parsing halaman manga berdasarkan sumber."""
    main_info = soup.find("div", class_="postbody") or soup.find("div", class_="main-info")
    if not main_info:
        return None
    
    # Judul
    title_tag = main_info.find("h1", class_="entry-title", itemprop="name")
    title = re.sub(r'\s+', ' ', title_tag.text.strip()) if title_tag else ""
    
    # Gambar
    img_tag = main_info.find("img", itemprop="image")
    img = img_tag["src"] if img_tag else ""
    
    # Rating
    rating_tag = main_info.find("i", itemprop="ratingValue") or main_info.find("div", itemprop="ratingValue")
    rating = rating_tag.text.strip() if rating_tag else ""
    
    # Status, author, artist, type
    info_container = main_info.find("div", class_="spe") or main_info.find("div", class_="tsinfo bixbox")
    status = author = artist = type_manga = ""
    if info_container:
        for span in info_container.find_all("span"):
            label = span.find("b")
            if label:
                key = label.text.strip().lower().replace(":", "")
                label.extract()
                value = span.text.strip()
                if "status" in key:
                    status = value
                elif "pengarang" in key or "author" in key:
                    author = value
                elif "ilustrator" in key or "artist" in key:
                    artist = value
                elif "jenis komik" in key or "type" in key:
                    type_manga = span.find("a").text.strip() if span.find("a") else value
    
    # Genre
    genre_container = main_info.find("div", class_="genre-info") or main_info.find("span", class_="mgen")
    genre = [a.text.strip() for a in genre_container.find_all("a")] if genre_container else []
    
    # Sinopsis
    sinopsis_tag = main_info.find("div", id="sinopsis") or main_info.find("div", class_="entry-content entry-content-single", itemprop="description")
    sinopsis = re.sub(r'\s+', ' ', sinopsis_tag.text.strip()) if sinopsis_tag else ""
    
    # Daftar chapter
    chapter_list = []
    chap_list_container = main_info.find("div", id="chapter_list") or main_info.find("div", id="chapterlist")
    if chap_list_container:
        for chapter in chap_list_container.find_all("li"):
            link_tag = chapter.find("a")
            chap_title = chapter.find("span", class_="chapternum").text.strip() if chapter.find("span", class_="chapternum") else ""
            update_tag = chapter.find("span", class_="chapterdate") or chapter.find("span", class_="dt")
            update = update_tag.text.strip() if update_tag else ""
            chapter_list.append({
                "link": urlparse(link_tag["href"]).path.strip("/") if link_tag else "",
                "chapter": chap_title,
                "update": update
            })
    
    # Chapter pertama dan terakhir
    first_chapter = chapter_list[-1] if chapter_list else {}
    last_chapter = chapter_list[0] if chapter_list else {}
    
    return {
        "title": title,
        "first_chapter": first_chapter,
        "last_chapter": last_chapter,
        "img": img,
        "rating": rating,
        "status": status,
        "author": author,
        "artist": artist,
        "type": type_manga,
        "genre": genre,
        "sinopsis": sinopsis,
        "chapter_list": chapter_list,
        "source": source
    }

def get_manga_detail(link):
    """Mengambil data dari Komikindo atau ManhwaList."""
    manhwa_url = f"{BASE_MANHWA_URL}manga/{link}"
    komikindo_url = f"{BASE_KOMIKINDO_URL}{link}"
    
    # Coba ambil dari ManhwaList
    soup = fetch_page(manhwa_url)
    if soup:
        result = parse_manga_page(soup, source="manhwa")
        if result:
            return result
    
    # Jika gagal, coba dari Komikindo
    soup = fetch_page(komikindo_url)
    if soup:
        return parse_manga_page(soup, source="komikindo")
    
    return None

def get_comic_content(link):
    """Coba ambil data dari Komikindo, jika gagal, coba dari ManhwaList."""
    manhwa_url = f"{BASE_MANHWA_URL}{link}"
    komikindo_url = f"{BASE_KOMIKINDO_URL}{link}"

    # Coba ambil dari ManhwaList
    soup = fetch_page(manhwa_url)
    if soup:
        result = parse_comic_page(soup, source="manhwa")
        if result and result["content"]:  # Pastikan data valid
            return result

    # Jika gagal, coba ambil dari Komikindo
    soup = fetch_page(komikindo_url)
    if soup:
        return parse_comic_page(soup, source="komikindo")

    return None  # Jika keduanya gagal

def parse_comic_page(soup, source):
    """Parsing halaman komik berdasarkan sumber (Komikindo atau ManhwaList)."""
    main = soup.find("div", class_="chapter-area") or soup.find("div", class_="chapterbody")
    if not main:
        return None

    title_element = main.find("h1", class_="entry-title") or main.find("h1", class_="entry-title", itemprop="name")
    title = re.sub(r'\s+', ' ', title_element.text.strip()) if title_element else ""

    prev_link = main.find("a", rel="prev")["href"] if main.find("a", rel="prev") else ""
    prev_chap = urlparse(prev_link).path.strip("/").replace("komik/", "").replace("manga/", "")

    next_link = main.find("a", rel="next")["href"] if main.find("a", rel="next") else ""
    next_chap = urlparse(next_link).path.strip("/").replace("komik/", "").replace("manga/", "")

    daftar_element = main.find("div", class_="nextprev") or main.find("div", class_="allc")
    daftar_chap_link = daftar_element.find("a", href=True)["href"] if daftar_element else ""
    daftar_chap = urlparse(daftar_chap_link).path.strip("/").replace("komik/", "").replace("manga/", "")

    content_container = main.find("div", class_="chapter-image eastengine bc") or main.find("div", id="readerarea")
    content = content_container.select("img") if content_container else []
    main_content = [img["src"] for img in content if "src" in img.attrs]

    return {
        "title": title,
        "prev_chapter": prev_chap,
        "daftar_chapter": daftar_chap,
        "next_chapter": next_chap,
        "content": main_content,
        "source": source  # Indikasi dari mana data diambil
    }
