import random
import sys
import time

from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import os
import re
import img2pdf
import wget
import shutil
import sys
from string import Template


# SLIDESHARE , ISSUE , SCRIBD , ACADEMIA.EDU
# images , document => scribd , academia.edu


def main(url):
    if 'issuu' in url:
        contenido = issuu(url)
    elif 'slideshare' in url:
        contenido = slideshare(url)
    elif 'scribd' in url:
        contenido = scribd(url)
    elif 'academia' in url:
        contenido = academia(url)


# return dowload(contenido)


def slideshare(url):
    contenido = {}
    images = []
    try:
        response = requests.get(url)
        if response.status_code == 200:
            s = BeautifulSoup(response.text, 'html.parser')
            title = s.find('h1', attrs={'class': 'slideshow-title-text'}).span.get_text()
            title = title.strip()
            print(title)
            pages = s.findAll('section', attrs={'class': 'slide'})
            for page in pages:
                page = page.img.get('data-full')
                images.append(page)
            contenido['title'] = title
            contenido['link_pages'] = images
        else:
            print('No se pudo obtener el documento', url)
    except Exception as e:
        print(f'Error {e}')
    return contenido


def issuu(url):
    contenido = {}
    images = []
    try:
        response = requests.get(url)
        if response.status_code == 200:
            s = BeautifulSoup(response.text, 'html.parser')
            title = s.find('meta', attrs={
                'property': 'og:title'
            }).get('content')
            print(title)
            imagen_string = s.find('meta', attrs={
                'property': 'og:image'
            }).get('content')
            imglink2 = imagen_string.replace('1.jpg', '')
            while True:
                imglink = imglink2 + str(len(images) + 1) + ".jpg"
                response = requests.get(imglink)
                if response.status_code == 403:
                    break
                images.append(imglink)
            contenido['title'] = title
            contenido['link_pages'] = images
        else:
            print('No se pudo obtener el documento', url)
    except Exception as e:
        print(f'Error {e}')
    return contenido


# dowloand document


# contenido = { title : "titulo" , link_pages : [ links ] }

def scribd(url):
    contenido = {}
    images = []
    try:
        response = requests.get(url)
        if response.status_code == 200:
            s = BeautifulSoup(response.text, 'html.parser')
            title = s.find("h1").get_text().strip()
            scripts = s.find_all("script", type="text/javascript")
            print(scripts)
            jsonp_urls = []
            for script in scripts:
                for content in script:
                    inicio_url = content.find("https://")
                    final_url = content.find(".jsonp")
                    if inicio_url != -1 and final_url != -1:
                        jsonp = content[inicio_url: final_url + 6]
                        jsonp_urls.append(jsonp)
            print(f'Extrayendo documento : {title}')
            for url in jsonp_urls:
                link_images = extract_html(url)
                print(link_images)
                images.append(link_images)
            contenido['title'] = title
            contenido['link_pages'] = images
        else:
            print('No se pudo obtener el documento', url)
    except Exception as e:
        print(f'Error {e}')
    return contenido


def academia(url):
    divs = []
    list_styles = []
    options = webdriver.ChromeOptions()
    options.add_argument('--incognito')
    driver = webdriver.Chrome(executable_path='/home/jkevin/Projects/python/download-doc/chromedriver', options=options)
    driver.get(url)
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(10)
    page_source = driver.page_source
    s = BeautifulSoup(page_source, 'lxml')
    title = s.find("h1").get_text().strip()
    scripts = s.find_all("script", type="text/javascript")
    styles = s.find_all("style")
    for style in styles:
        list_styles.append(style)
    jsonp_urls = []
    for script in scripts:
        for content in script:
            inicio_url = content.find("https://")
            final_url = content.find(".jsonp")
            if inicio_url != -1 and final_url != -1:
                jsonp = content[inicio_url: final_url + 6]
                jsonp_urls.append(jsonp)
    print(f'Extrayendo documento : {title}')
    for i, url in enumerate(jsonp_urls):
        print(f'Extrayendo pagina {i + 1}')
        divParrafos = extract_html(url)

        divs.append(divParrafos)
    create_html(divs, list_styles)
    driver.close()


def extract_html(url):
    response = requests.get(url).text
    page_no = response[11:13]
    if ('_' in page_no):
        page_no = page_no.replace("_", "")
    response_head = response.replace("window.page" + page_no + '_callback(["', "").replace("\\n", "").replace("\\",
                                                                                                              "").replace(
        '"]);', "").replace("orig", "src")
    s = BeautifulSoup(response_head, "html.parser")
    return s


def create_html(divs, list_styles):
    divs_string = ""
    styles_string = ""
    for div in divs:
        divs_string = divs_string + str(div)
    for style in list_styles:
        styles_string = styles_string + str(style)
    filein = open('main.html')
    src = Template(filein.read())
    d = {'divs': divs_string, 'list_styles': styles_string}
    result = src.substitute(d)
    filein2 = open('nuevo.html', 'w')
    filein2.writelines(result)


def dowload(contenido):
    images, title = contenido['link_pages'], contenido['title']
    if os.path.isdir(f'./{title}/'):
        shutil.rmtree(f'{title}')
    os.mkdir(f'{title}')
    os.mkdir(f'{title}/imagenes')
    for i, image in enumerate(images):
        try:
            img_req = requests.get(image)
            name = f'page{i + 1}.jpg'
            if img_req.status_code == 200:
                print(f'Page {i + 1}  : {image}')
                with open(f'{title}/imagenes/{name}', 'wb') as handler:
                    handler.write(img_req.content)
                with open(f'{title}/urls.txt', 'a') as handler:
                    handler.write(image + '\n')
            else:
                print("No se pudo obtener la pagina")
        except Exception as e:
            print(f'Error {e}')

    imagenes_jpg = [f'{title}/imagenes/' + archivo for archivo in os.listdir(f'{title}/imagenes/') if
                    archivo.endswith(".jpg")]
    imagenes_jpg.sort(key=lambda x: os.path.getmtime(x))
    with open(f'{title}/{title}.pdf', "wb") as documento:
        documento.write(img2pdf.convert(imagenes_jpg))


if __name__ == "__main__":
    url = 'https://www.academia.edu/44919129/The_Role_of_Science_Technology_and_the_Individual_on_the_Way_of_Software_Systems_Since_1968'
    main(url)
