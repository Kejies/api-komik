import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

BASE_URL = "https://manhwalist02.site/"

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
        link_tag = komik.find("a")
        link = link_tag["href"]
        parsed_link = urlparse(link).path.strip("/").replace("manga/", "")

        img_tag = komik.find("img", class_="ts-post-image")
        img_url = img_tag.get("data-src") or img_tag.get("src")

        title_tag = komik.find("div", class_="tt")
        title = title_tag.text.strip() if title_tag else ""

        tipe_span = komik.find("span", class_="type")
        tipe = tipe_span.text.strip() if tipe_span else ""

        warna = ""
        warna_tag = komik.find("span", class_="colored")
        if warna_tag:
            warna = warna_tag.text.strip()

        kolom_chapter = komik.find("div", class_="adds").find("div", class_="epxs")
        chapter = re.sub(r'\s+', ' ', kolom_chapter.text.strip()) if kolom_chapter else ""

        ratting_div = komik.find("div", class_="numscore")
        ratting = ratting_div.text.strip() if ratting_div else ""

        data_list.append({
            "link": parsed_link,
            "title": title,
            "colored": warna,
            "type": tipe,
            "chapter": chapter,
            "ratting": ratting,
            "img": img_url
        })

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
    another_link = link.replace("-", " ").split()

    if 'chapter' in another_link:
        index = another_link.index('chapter')
        another_link = another_link[:index]

    another_chaplist = '-'.join(another_link)
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    main = soup.find("div", class_="chapterbody")

    if not main:
        return None  # Amanin biar ga error

    h1 = main.find("h1", class_="entry-title", itemprop="name")
    title = re.sub(r'\s+', ' ', h1.text.strip()) if h1 else ""

    daftar_element = main.find("div", class_="allc")
    href_tag = daftar_element.find("a", href=True, rel=False) if daftar_element else None

    daftar_chap_link = (
        another_chaplist
        if href_tag and href_tag["href"] == "{{link}}"
        else urlparse(href_tag["href"]).path.strip("/").replace("manga/", "") if href_tag else another_chaplist
    )

    content_container = main.find("div", id="readerarea")
    content = content_container.select("img") if content_container else []
    main_content = [img["src"] for img in content if "src" in img.attrs]

    daftar_chap_data = get_daftar_chapter(daftar_chap_link)
    daftar_chap = daftar_chap_data["chapters"] if daftar_chap_data else []

    plan_link = link.strip("/").replace("-", " ").split()
    if 'chapter' in plan_link:
        index = plan_link.index('chapter')
        plan_link = plan_link[:index+2]

    current_chap = int(plan_link[-1]) if plan_link and plan_link[-1].isdigit() else None

    dirty_prev = current_chap - 1 if current_chap and current_chap > min(daftar_chap) else None
    dirty_next = current_chap + 1 if current_chap and (current_chap + 1) in daftar_chap else None

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
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    main = soup.find("div", class_="listupd")
    if not main:
        return []

    komik_list = []
    for komik in main.find_all("div", class_="bs"):
        tipe_classes = komik.find("span", class_="type").get("class", [])
        tipe = tipe_classes[1] if len(tipe_classes) > 1 else "unknown"
        if tipe.lower() == "manga":
            continue

        link_tag = komik.find("a")
        link = link_tag["href"] if link_tag else ""
        parsed_link = urlparse(link).path.strip("/").replace("manga/", "")

        img_tag = komik.find("img", class_="ts-post-image")
        img_url = img_tag.get("src", "null") if img_tag else "null"

        title_tag = komik.find("div", class_="tt")
        title = title_tag.text.strip() if title_tag else "Tidak Ada Judul"

        chapter_tag = komik.find("div", class_="adds")
        chapter = chapter_tag.find("div", class_="epxs").text.strip() if chapter_tag else ""

        warna_tag = komik.find("span", class_="colored")
        warna = warna_tag.text.strip() if warna_tag else ""

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

kiryu = "https://kiryuu03.com/"
def search_manga_manhua(query):
    all_results = []
    page = 1
    max_pages = 1  # default, akan diperbarui dari pagination di halaman 1

    while page <= max_pages:
        if page == 1:
            search_url = f"{kiryu}/?s={query.replace(' ', '+')}"
        else:
            search_url = f"{kiryu}/page/{page}/?s={query.replace(' ', '+')}"

        try:
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error saat request halaman {page}: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        if page == 1:
            # Ambil max_pages dari pagination
            pagination = soup.find("div", class_="pagination")
            if pagination:
                page_links = pagination.find_all("a", class_="page-numbers")
                numbers = []
                for link in page_links:
                    try:
                        number = int(link.text.strip())
                        numbers.append(number)
                    except ValueError:
                        continue
                if numbers:
                    max_pages = max(numbers)

        komik_container = soup.find("div", class_="listupd")
        if not komik_container:
            break

        komik_list = komik_container.find_all("div", class_="bs")
        if not komik_list:
            break

        for komik in komik_list:
            type_span = komik.find("span", class_="type")
            tipe_class = type_span.get("class", []) if type_span else []
            tipe = tipe_class[1] if len(tipe_class) > 1 else "unknown"
            if tipe.lower() == "manhwa":
                continue

            link_tag = komik.find("a")
            link = link_tag["href"] if link_tag else ""
            parsed_link = urlparse(link).path.strip("/").replace("manga/", "")

            img_tag = komik.find("img", class_="ts-post-image")
            img_url = img_tag.get("src", "null") if img_tag else "null"

            title_tag = komik.find("div", class_="tt")
            title = title_tag.text.strip() if title_tag else "Tidak Ada Judul"

            chapter_tag = komik.find("div", class_="adds")
            chapter = chapter_tag.find("div", class_="epxs").text.strip() if chapter_tag else ""

            warna_tag = komik.find("span", class_="colored")
            warna = warna_tag.text.strip() if warna_tag else ""

            rating_tag = komik.find("div", class_="numscore")
            ratting = rating_tag.text.strip() if rating_tag else ""

            all_results.append({
                "link": parsed_link,
                "title": title,
                "ratting": ratting,
                "colored": warna,
                "type": tipe,
                "chapter": chapter,
                "img": img_url
            })

        page += 1

    return all_results


def get_manhua_list(page=1):
    base_url = f"{kiryu}manga/?page={page}&status=&type=manhua&order="
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    komik_container = soup.find("div", class_="listupd")
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
        ratting = komik.find("div", class_="numscore").text


        data_list.append({
            "link": parsed_link,
            "title": title,
            "ratting": ratting,
            "colored": warna,
            "type": tipe,
            "chapter": chapter,
            "img": img_url
        })

    pagination = soup.find("div", class_="pagination")

    if pagination:
        page_numbers = [a.text.strip() for a in pagination.find_all("a", class_="page-numbers") if a.text.strip().isdigit()]
        
        total_pages = int(max(page_numbers)) if page_numbers else 1
    else:
        total_pages = 34

    current_page_elem = soup.find("span", class_="page-numbers current")
    current_page = int(current_page_elem.text.strip()) if current_page_elem else 1

    if current_page >= total_pages:
        total_pages = current_page


    return data_list, total_pages

def get_manga_list(page=1):
    base_url = f"{kiryu}manga/?page={page}&status=&type=manga&order="
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    komik_container = soup.find("div", class_="listupd")
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
        ratting = komik.find("div", class_="numscore").text


        data_list.append({
            "link": parsed_link,
            "title": title,
            "ratting": ratting,
            "colored": warna,
            "type": tipe,
            "chapter": chapter,
            "img": img_url
        })

    pagination = soup.find("div", class_="pagination")

    if pagination:
        page_numbers = [a.text.strip() for a in pagination.find_all("a", class_="page-numbers") if a.text.strip().isdigit()]
        
        total_pages = int(max(page_numbers)) if page_numbers else 1
    else:
        total_pages = 90

    current_page_elem = soup.find("span", class_="page-numbers current")
    current_page = int(current_page_elem.text.strip()) if current_page_elem else 1

    if current_page >= total_pages:
        total_pages = current_page


    return data_list, total_pages

def filter_duplicates(main, to_filter):
    existing_titles = {komik['title'].lower() for komik in main}
    return [komik for komik in to_filter if komik['title'].lower() not in existing_titles]

def search_all_sources(query):
    manhwa_results = search(query)  # hanya manhwa
    kiryu_results = search_manga_manhua(query)       # tanpa manhwa

    kiryu_filtered = filter_duplicates(manhwa_results, kiryu_results)

    return manhwa_results + kiryu_filtered


def get_manga_manhua_detail(link):
    base_url = f"{kiryu}manga/{link}"
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    komik_detail = soup.find("div", class_="postbody")

    # Judul
    dirty_title = komik_detail.find("h1", class_="entry-title", itemprop="name")
    title = re.sub(r'\s+', ' ', dirty_title.text.strip()) if dirty_title else ""

    # Gambar
    img_container = komik_detail.find("div", class_="thumb", itemprop="image")
    img = img_container.find("img", itemprop="image")["src"] if img_container and img_container.find("img", itemprop="image") else ""

    # Rating
    ratting = komik_detail.find("div", itemprop="ratingValue")
    ratting = ratting.text.strip() if ratting else ""

    rows = soup.select("table.infotable tr")
    info = {}
    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 2:
            key = cells[0].get_text(strip=True).lower()
            value = cells[1].get_text(strip=True)

            if key == "author":
                # Pisahkan Author dan Artist
                author_match = re.search(r"(.*?)(?=\s*\(Author\))", value)
                artist_match = re.search(r"(.*?)(?=\s*\(ArtistI)", value.split("(Author)")[-1])
                
                author = author_match.group(1).strip() if author_match else None
                artist = artist_match.group(1).strip() if artist_match else None

                info["author"] = author
                info["artist"] = artist
            else:
                info[key] = value

    # Sinopsis
    short_sinopsis = ""
    sinopsis_tag = komik_detail.find("div", itemprop="description")
    sinopsis = sinopsis_tag.find('p').text.strip()

    # Genre
    genre_container = komik_detail.find("div", class_="seriestugenre")
    genre = [a.text.strip() for a in genre_container.find_all("a")] if genre_container else []

    komik_related = soup.find("div", class_="listupd")
    komik_list = komik_related.find_all("div", class_="bs")

    related = []
    for komik in komik_list:
        linkrel = komik.find("a")["href"]
        parsed_link = urlparse(linkrel).path.strip("/").replace("manga/", "")
        img_tag = komik.find("img", class_="ts-post-image")
        img_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else "null"
        title_tag = komik.find("div", class_="tt")
        titlerel = title_tag.text.strip() if title_tag else "Tidak Ada Judul"
        chapterCont = komik.find("div", class_="adds")
        chapter = chapterCont.find("div", class_="epxs").text.strip()
        tipe = komik.find("span", class_="type")["class"][1]
        warna = komik.find("span", class_="colored").text.strip() if komik.find("span", class_="colored") else ""
        ratting = komik.find("div", class_="numscore").text


        related.append({
            "link": parsed_link,
            "title": titlerel,
            "ratting": ratting,
            "colored": warna,
            "type": tipe,
            "chapter": chapter,
            "img": img_url
        })

    # Daftar chapter
    chap_list_container = komik_detail.find("div", id="chapterlist")
    chapter_list = []
    if chap_list_container:
        chap_li = chap_list_container.find_all("li")
        for chapter in chap_li:
            linkch = chapter.find("a")
            titlech = linkch.find("span", class_="chapternum")
            chap = titlech.text.strip() if titlech else ""
            update = linkch.find("span", class_="chapterdate")
            update = update.text.strip() if update else ""

            chapter_list.append({
                "link": urlparse(linkch["href"]).path.strip("/").replace("komik/", "") if linkch else "",
                "chapter": chap,
                "update": update
            })

    # Data akhir
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
        "href":link,
        "ratting": ratting,
        "status": info['status'],
        "author": info["author"],
        "artist": info["artist"],
        "released": info["released"],
        "type": info["type"],
        "genre": genre,
        "sinopsis": sinopsis,
        "related": related,
        "chapter_list": chapter_list
    }
    return data_list
 
def get_daftar_chapter_kiryu(link):
    base_url = f"{kiryu}manga/{link}"
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    komik_detail = soup.find("div", class_="postbody")
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
def get_manga_manhua_content(link):
    base_url = f"{kiryu}/{link}"
    another_link = link.replace("-", " ").split()

    if 'chapter' in another_link:
        index = another_link.index('chapter')
        another_link = another_link[:index]

    another_chaplist = '-'.join(another_link)
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    main = soup.find("div", class_="chapterbody")

    title = re.sub(r'\s+', ' ', main.find("h1", class_="entry-title").text.strip()) if main.find("h1", class_="entry-title") else ""

 
    daftar_element = main.find("div", class_="allc")
    href_tag = daftar_element.find("a", href=True, rel=False) if daftar_element else None
    daftar_chap_link = (
        another_chaplist
        if href_tag and href_tag["href"] == "{{link}}"
        else urlparse(href_tag["href"]).path.strip("/").replace("manga/", "") if href_tag else another_chaplist
    )
    daftar_chap_data = get_daftar_chapter_kiryu(daftar_chap_link)
    daftar_chap = daftar_chap_data["chapters"] if daftar_chap_data else []
    plan_link = link.strip("/").replace("-", " ").split()
    if 'chapter' in plan_link:
        index = plan_link.index('chapter')
        plan_link = plan_link[:index+2]

    current_chap = int(plan_link[-1]) if plan_link and plan_link[-1].isdigit() else None

    dirty_prev = current_chap - 1 if current_chap and current_chap > min(daftar_chap) else None
    dirty_next = current_chap + 1 if current_chap and (current_chap + 1) in daftar_chap else None
    prev_chap = "-".join(plan_link[:-1] + [str(dirty_prev)]) if dirty_prev else None
    next_chap = "-".join(plan_link[:-1] + [str(dirty_next)]) if dirty_next else None
    content_container = main.find("div", id="readerarea")
    content = content_container.select("img") if content_container else []
    main_content = [img["src"] for img in content if "src" in img.attrs]

    print({
        "title": title,
        "prev_chapter": prev_chap,
        "daftar_chapter": daftar_chap_link,
        "next_chapter": next_chap,
        "content": main_content,
    })
    return {
        "title": title,
        "prev_chapter": prev_chap,
        "daftar_chapter": daftar_chap_link,
        "next_chapter": next_chap,
        "content": main_content,
    }
