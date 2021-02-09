import time
from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import os
import img2pdf
import shutil
from string import Template

# download documents issue , slideshare, academia.edu
def main(url):
    if 'issuu' in url:
        contenido = issuu(url)
        dowload(contenido)
    elif 'slideshare' in url:
        contenido = slideshare(url)
        dowload(contenido)
    elif 'academia' in url:
        contenido = academia(url)


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

'''def scribd_images(url):
    contenido = {}
    images = []
    try:
        response = requests.get(url)
        if response.status_code == 200:
            s = BeautifulSoup(response.text, 'html.parser')
            title = s.find("h1").get_text().strip()
            scripts = s.find_all("script", type="text/javascript")
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
                div = extract_html(url)
                print(div)
                link = div.find("img").get('src')
                images.append(link)
            contenido['title'] = title
            contenido['link_pages'] = images
        else:
            print('No se pudo obtener el documento', url)
    except Exception as e:
        print(f'Error {e}')
    dowload(contenido)
'''

def academia(url):
    divs_string = ""
    styles_string = ""

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
    driver.close()

    for style in styles:
        style = str(style)
        style = style.replace("{display: none;}", " ")
        styles_string = styles_string + style

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
        div = extract_html(url)
        divs_string = divs_string + str(div)

    generate_html(divs_string, styles_string, title)


def extract_html(url):
    response = requests.get(url).text
    page_no = response[11:13]
    if ('_' in page_no):
        page_no = page_no.replace("_", "")
    response_head = response.replace("window.page" + page_no + '_callback(["', "").replace("\\n", "").replace("\\",
                                                                                                              "").replace(
        '"]);', "").replace("orig", "src")
    page = BeautifulSoup(response_head, "html.parser")
    return page


def generate_html(divs_string, styles_string, title):

    with open(f'{title}.html', "w") as f:
        f.write(f"""
           <!DOCTYPE html>
           <html lang="en"> 
           <head>
           <meta charset="UTF-8">   
           <title>Title</title>
           </head>
           $list_styles
           <body>
           $divs
           </body>
           </html>
           """)

    filein = open(f'{title}.html')
    src = Template(filein.read())
    d = {'divs': divs_string, 'list_styles': styles_string}
    result = src.substitute(d)

    with open(f'{title}.html', "w") as f:
        f.write(result)


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
    url = input("url documents: ")
    main(url)
