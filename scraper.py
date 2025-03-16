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
            "variant": warna,
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
                        "variant": warna,
                        "type": tipe,
                        "chapter": chapter,
                        "last_update": last_update,
                        "img": img_url
                      })
        if i >= 8:
            break
    return data_list

def detail(link):
    base_url = f"https://komikindo2.com/komik/${link}"

    res = requests.get(base_url)
    soup = BeautifulSoup(res.content, "html.parser")
    komik_detail = soup.find("div", class_="postbody")
    title = komik_detail.find("h1", class_="entry_title")
    chap_container = komik_detail.find("div", class_="epsbaru")

    # Mengambil chapter pertama dan terakhir
    first_chap_link = chap_container.find("div", class_="epsbr chapter-awal").find("a", href=True)["href"]
    first_chap = urlparse(first_chap_link).path.strip("/").replace("komik/", "")
    last_chap_link = chap_container.find_all("div", class_="epsbr")[-1].find("a", href=True)["href"]
    last_chap = urlparse(last_chap_link).path.strip("/").replace("komik/", "")
    img_container = komik_detail.find("div", class_="thumb", itemprop="image")
    img = komik_detail.find("img", itemprop="image")["src"] if img_container and img_container.find("img", itemprop="image") else None
    ratting = komik_detail.find("i", itemprop="ratingValue").text.strip()
    info_container = komik_detail.find("div", class_="spe").find_all("span")
    info_komik = []
    for span in info_container:
        b_tag = span.find("b")
        if b_tag:
            b_tag.extract() 
        alternative_title_text = span.text.strip()
        info_komik.append(alternative_title_text)
    short_sinopsis =  re.sub(r'\s+', ' ', komik_detail.find("div", class_="shortcsc sht2").find("p").text.strip()) 
    sinopsis =  re.sub(r'\s+', ' ', komik_detail.find("div", id="sinopsis").find("p").text.strip())
    genre_container = komik_detail.find("div", class_="genre-info").find_all("a")
    genre = []
    for a in genre_container:
        text = a.text.strip()
        genre.append(text)
    related_container = komik_detail.find("div", class_="miripmanga").find_all("li")
    related = []
    for r in related_container:
        link = urlparse(r.find("a", class_="series")["href"]).path.strip("/").replace("komik/", "")
        img = r.find("img", itemprop="image")["src"]
        title = r.find("img", itemprop="image")["title"]
        sinopsis = r.find("div", class_="excerptmirip").text.strip()
        tipe = r.find("span", class_="typeflag")["class"][-1]
        warna_label = r.find("div", class_="warnalabel")
        warna = re.sub(r'\s+', ' ', warna_label.text.strip()) if warna_label else "Tidak Berwarna"

        related.append({
                "link": link,
                "img": img,
                "title": title,
                "sinopsis": sinopsis,
                "variant": warna,
                "Type": tipe
        })

    chap_list_container = komik_detail.find("div", id="chapter_list").find_all("li")
    chapter_list = []
    for chapter in chap_list_container:
        link = chapter.find("a")
        chap = re.sub(r'\s+', ' ', link.text.strip())
        update = chapter.find("span", class_="dt").find("a").text.strip()
        
        chapter_list.append({
                "link": link["href"],
                "chapter": chap,
                "update": update
        })

    data_list = {
        "title": title,
        "first_chapter": first_chap,
        "last_chapter": last_chap,
        "img": img,
        "ratting": ratting,
        "alternative_title": info_komik[0],
        "status": info_komik[1],
        "author": info_komik[2],
        "ilustrator": info_komik[3],
        "Type": info_komik[6],
        "tema": info_komik[5],
        "genre": genre,
        "short_sinopsis": short_sinopsis,
        "sinopsis": sinopsis,
        "related": related,
        "chapter_list": chapter_list
    }
    return data_list

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