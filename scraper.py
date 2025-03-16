import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def terbaru(page=1):
    base_url = f"https://komikindo2.com/komik-terbaru/page/{page}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    res = requests.get(base_url, headers=headers)

    if res.status_code != 200:
        print(f"Error: Gagal mengambil data dari {base_url}, Status Code: {res.status_code}")
        return None, 0

    soup = BeautifulSoup(res.content, "html.parser")
    komik_list = soup.find_all("div", class_="animposx")

    data_list = []
    for komik in komik_list:
        link = komik.find("a")["href"]
        parsed_link = urlparse(link).path.strip("/").replace("komik/", "")
        img_tag = komik.find("img", itemprop="image")
        img_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else "null"
        title_tag = komik.find("div", class_="tt")
        title = title_tag.text.strip() if title_tag else "Tidak Ada Judul"

        chapter_tag = komik.find("div", class_="lsch").find("a")
        chapter = chapter_tag.text.strip() if chapter_tag else "null"
        tipe = komik.find("span", class_="typeflag")["class"][1]
        warna_label = komik.find("div", class_="warnalabel")
        warna = re.sub(r'\s+', ' ', warna_label.text.strip()) if warna_label else "Tidak Berwarna"
        chapter = re.sub(r'\s+', ' ', komik.find("div", class_="lsch").find("a").text.strip())
        last_update = komik.find("span", class_="datech").text.strip()

        data_list.append({
            "link": parsed_link,
            "title": title,
            "genre": warna,
            "type": tipe,
            "chapter": chapter,
            "last_update": last_update,
            "img": img_url
        })

    pagination = soup.find("div", class_="pagination")
    if pagination:
        page_numbers = pagination.find_all("a", class_="page-numbers")
        total_pages = int(page_numbers[-2].text.strip()) if page_numbers else 1
    else:
        total_pages = 1

    return data_list, total_pages

def popular():
    base_url = "https://komikindo2.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    res = requests.get(base_url, headers=headers)


    soup = BeautifulSoup(res.content, "html.parser")
    main_element = soup.find_all("div", class_="animposx")

    data_list = []
    for i, komik in enumerate(main_element, start=1):
        link = komik.find("a")["href"]
        parsed_link = urlparse(link).path.strip("/").replace("komik/", "")
        img_url = komik.find("img", itemprop="image")["src"]
        title = komik.find("div", class_="tt").find("h4").text.strip()
        tipe = komik.find("span", class_="typeflag")["class"][1]
        warna_label = komik.find("div", class_="warnalabel")
        warna = re.sub(r'\s+', ' ', warna_label.text.strip()) if warna_label else "Tidak Berwarna"
        kolom_chapter = komik.find("div", class_="lsch").find("a")
        chapter = re.sub(r'\s+', ' ', kolom_chapter.text.strip()) if kolom_chapter else ""
        last_update = komik.find("span", class_="datech").text.strip()
        data_list.append( {
                        "link": parsed_link,
                        "title": title,
                        "genre": warna,
                        "type": tipe,
                        "chapter": chapter,
                        "last_update": last_update,
                        "img": img_url
                      })
        if i >= 8:
            break
    return data_list

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

def detail(link):
    base_url = f"https://komikindo2.com/komik/{link}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
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
            link = urlparse(r.find("a", class_="series")["href"]).path.strip("/").replace("komik/", "") if r.find("a", class_="series") else ""
            rel_img = r.find("img", itemprop="image")["src"] if r.find("img", itemprop="image") else ""
            rel_title = r.find("img", itemprop="image")["title"] if r.find("img", itemprop="image") else ""
            sinopsis = r.find("div", class_="excerptmirip").text.strip() if r.find("div", class_="excerptmirip") else ""
            tipe = r.find("span", class_="typeflag")["class"][-1] if r.find("span", class_="typeflag") else ""
            warna_label = r.find("div", class_="warnalabel")
            warna = re.sub(r'\s+', ' ', warna_label.text.strip()) if warna_label else "Tidak Berwarna"

            related.append({
                "link": link,
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
            link = chapter.find("a")
            chap = re.sub(r'\s+', ' ', link.text.strip()) if link else ""
            update = chapter.find("span", class_="dt")
            update = update.find("a").text.strip() if update and update.find("a") else ""

            chapter_list.append({
                "link": urlparse(link["href"]).path.strip("/").replace("komik/", "") if link else "",
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
        "ratting": ratting,
        "alternative_title": alternative_title,
        "status": status,
        "author": author,
        "ilustrator": ilustrator,
        "type": jenis_komik,
        "tema": ", ".join(tema),
        "genre": genre,
        "short_sinopsis": short_sinopsis,
        "sinopsis": sinopsis,
        "related": related,
        "chapter_list": chapter_list
    }
    print(first_chap_title, last_chap_title)
    return data_list

detail("reign")


def content(link):
    try:
        base_url = f"https://komikindo2.com/{link}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
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
        content = main.find_all("img", alt=content_alt)
        main_content = [img["src"] for img in content]

        return {
            "title": title,
            "prev_chapter": prev_chap,
            "daftar_chapter": daftar_chap,
            "next_chapter": next_chap,
            "content": main_content,
        }
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}