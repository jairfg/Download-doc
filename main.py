from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import os
import re
import img2pdf
import wget


def main(url):
    images = issuu(url)
    dowloadImg(images)
#  dowload(images)
def slideshare(url):
    images = []
    try:
        response = requests.get(url)
        if response.status_code == 200:
            s = BeautifulSoup(response.text, 'html.parser')
            pages = s.findAll('section', attrs={'class': 'slide'})
            for page in pages:
                page = page.img.get('data-full')
                images.append(page)
        else:
            print('No se pudo obtener el documento', url)
    except Exception as e:
        print(f'Error {e}')
    return images


def issuu(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            s = BeautifulSoup(response.text, 'html.parser')
            title = s.find('meta',attrs={
                'property' : 'og:title'
            }).get('content')
            imagen_string = s.find('meta',attrs={
                'property' : 'og:image'
            }).get('content')
            return issuu_images(imagen_string)
    except Exception as e:
        print(f'Error {e}')

def issuu_images(imagen_string):
    images = []
    imglink2 = imagen_string.replace('1.jpg', '')
    i = 0
    while True:
        i = i +1
        imglink = imglink2 + str(i) + ".jpg"
        response = requests.get(imglink)
        if response.status_code == 403:
            break
        images.append(imglink)
    return images

def dowloadImg(images):
    os.mkdir('dir1')
    for i, image in enumerate(images):
        try:
            img_req = requests.get(image)
            nombre = f'page{i+1}.jpg'
            if img_req.status_code == 200:
                print(f'Page {i+1}  : {image}')
                with open(f'dir1/{nombre}','wb') as handler:
                    handler.write(img_req.content)

                with open('dir1/urls.txt','a') as handler:
                    handler.write(image + '\n')
            else:
                print("no se pudo")
        except:
            print('No se pudo obtener la imagen')

    imagenes_jpg = ['dir1/' + archivo for archivo in os.listdir('dir1/') if archivo.endswith(".jpg")]
    print(imagenes_jpg)
    imagenes_jpg.sort(key=lambda x: os.path.getmtime(x))
    with open("dir1/documento.pdf", "wb") as documento:
        documento.write(img2pdf.convert(imagenes_jpg))




if __name__ == "__main__":
    url = 'https://issuu.com/edifaua/docs/catalogo_faua-uni_-20.09'
    main(url)