from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import os
import re
import img2pdf
import wget
import shutil

def main(url):

    if 'issuu' in url:
        contenido = issuu(url)
    elif 'slideshare' in url:
        contenido = slideshare(url)
    return dowload(contenido)

def slideshare(url):
    contenido = {}
    images = []
    try:
        response = requests.get(url)
        if response.status_code == 200:
            s = BeautifulSoup(response.text, 'html.parser')
            title = s.find('h1',attrs={'class': 'slideshow-title-text'}).span.get_text()
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
            title = s.find('meta',attrs={
                'property' : 'og:title'
            }).get('content')
            print(title)
            imagen_string = s.find('meta',attrs={
                'property' : 'og:image'
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

def dowload(contenido):
    images,title = contenido['link_pages'] , contenido['title']

    if os.path.isdir(f'./{title}/'):
        shutil.rmtree(f'{title}')

    os.mkdir(f'{title}')
    os.mkdir(f'{title}/imagenes')
    for i, image in enumerate(images):
        try:
            img_req = requests.get(image)
            name = f'page{i+1}.jpg'
            if img_req.status_code == 200:
                print(f'Page {i+1}  : {image}')
                with open(f'{title}/imagenes/{name}','wb') as handler:
                    handler.write(img_req.content)
                with open(f'{title}/urls.txt','a') as handler:
                    handler.write(image + '\n')
            else:
                print("No se pudo obtener la pagina")
        except Exception as e:
            print(f'Error {e}')

    imagenes_jpg = [f'{title}/imagenes/' + archivo for archivo in os.listdir(f'{title}/imagenes/') if archivo.endswith(".jpg")]
    imagenes_jpg.sort(key=lambda x: os.path.getmtime(x))
    with open(f'{title}/{title}.pdf', "wb") as documento:
        documento.write(img2pdf.convert(imagenes_jpg))




if __name__ == "__main__":
    url = input('url: ').strip()
    main(url)