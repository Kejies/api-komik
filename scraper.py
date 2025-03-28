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

# Contoh penggunaan
if __name__ == "__main__":
    result = get_manga_detail("lookism")
    if result:
        print(f"Data diambil dari: {result['source']}")
        print(result)
    else:
        print("Komik tidak ditemukan di kedua sumber.")

    comic_content = get_comic_content("lookism-chapter-541/")
    if comic_content:
        print(comic_content)
    else:
        print("Konten komik tidak ditemukan.")