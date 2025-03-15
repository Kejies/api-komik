import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def terbaru(page=1):
    base_url = f"https://komikindo2.com/komik-terbaru/page/{page}"
    res = requests.get(base_url)

    if res.status_code != 200:
        print(f"Error: Gagal mengambil data dari {base_url}, Status Code: {res.status_code}")
        return None, 0

    soup = BeautifulSoup(res.content, "html.parser")
    komik_list = soup.find_all("div", class_="animposx")

    data_list = []
    for komik in komik_list:
        link = komik.find("a")["href"]
        parsed_link = urlparse(link).path.strip("/").replace("komik/", "")
        img_url = komik.find("img", itemprop="image")["src"]
        title = komik.find("div", class_="tt").find("h4").text.strip()
        type = komik.find("span", class_="typeflag")["class"][1]
        warna_label = komik.find("div", class_="warnalabel")
        warna = re.sub(r'\s+', ' ', warna_label.text.strip()) if warna_label else "Tidak Berwarna"
        chapter = re.sub(r'\s+', ' ', komik.find("div", class_="lsch").find("a").text.strip())
        last_update = komik.find("span", class_="datech").text.strip()

        data_list.append({
            "link": parsed_link,
            "title": title,
            "ratting": "null",
            "jenis": warna,
            "view": "null",
            "type": type,
            "status": "null",
            "chapter": chapter,
            "last_update": last_update,
            "img": img_url
        })

    # Ambil total halaman dari pagination
    pagination = soup.find("div", class_="pagination")
    if pagination:
        page_numbers = pagination.find_all("a", class_="page-numbers")
        total_pages = int(page_numbers[-2].text.strip()) if page_numbers else 1
    else:
        total_pages = 1

    return data_list, total_pages

def popular():
    base_url = "https://komikindo2.com/"
    res = requests.get(base_url)

    if res.status_code != 200:
        print(f"Error: Gagal mengambil data dari {base_url}, Status Code: {res.status_code}")
        return None, 0

    soup = BeautifulSoup(res.content, "html.parser")
    komik_popular = soup.find("div", class_="post-show mangapopuler")

    if not komik_popular:
        print("Error: Tidak menemukan div dengan class 'post-show mangapopuler'")
        return None, 0

    main_element = soup.find_all("div", class_="animposx")

    data_list = []
    for i, komik in enumerate(main_element, start=1):
        link = komik.find("a")["href"]
        parsed_link = urlparse(link).path.strip("/").replace("komik/", "")
        img_url = komik.find("img", itemprop="image")["src"]
        title = komik.find("div", class_="tt").find("h4").text.strip()
        type = komik.find("span", class_="typeflag")["class"][1]
        warna_label = komik.find("div", class_="warnalabel")
        warna = re.sub(r'\s+', ' ', warna_label.text.strip()) if warna_label else "Tidak Berwarna"        
        chapter = re.sub(r'\s+', ' ', komik.find("div", class_="lsch").find("a").text.strip())
        last_update = komik.find("span", class_="datech").text.strip()
        data_list.append( {
                        "link": parsed_link,
                        "title": title,
                        "ratting": "null",
                        "jenis": warna,
                        "view": "null",
                        "type": type,
                        "status": "null",
                        "chapter": chapter,
                        "last_update": last_update,
                        "img": img_url
                      })
        if i >= 8:
            break


    return data_list

