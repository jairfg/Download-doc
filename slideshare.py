from selenium import webdriver
from time import sleep, time
from selenium.webdriver.chrome.options import Options
import urllib.request as ureq
import os
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
# img2pdf is not avilable by default please install via pip install img2pdf
import img2pdf as i2p


options = webdriver.ChromeOptions()
options.add_argument('--incognito')
driver = webdriver.Chrome(executable_path='/home/jkevin/Documents/Proyectos/download-doc/chromedriver',options=options)
driver.get("https://es.slideshare.net/jairjairobarzolacuba391/itgs-trabajo-final")


wait = WebDriverWait(driver, 10)
wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="btnNext"]/div')))
driver.find_element_by_xpath('//*[@id="btnNext"]/div').click()
images = driver.find_elements_by_class_name('slide_image')


for image in images:
    url_link = image.get_attribute('src')
    # since the orginal url has a get parametr we need to remove that for
    # urllib to retreive with out erre i.e invalid parameter
    print(url_link)
    url_link = url_link.split('?')[0]
    # SildesBC is prexisting directory on the same path with the script.
    img_name = '/home/jkevin/Documents/Proyectos/download-doc/' + os.path.basename(url_link)
    image = ureq.urlretrieve(url_link, img_name)
    #print img Link duirng debug time
    #print(url_link.split('?')[0])
    wait = WebDriverWait(driver, 1)
    # xpath can be found by using chrome inspet window and right click
    # on the target object(div) then copy >> copy Xpath
    wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="btnNext"]/div')))
    driver.find_element_by_xpath('//*[@id="btnNext"]/div').click()

#Convert all Pics to a single slides
imglist = ['/home/jkevin/Documents/Proyectos/download-doc/' + i for i in os.listdir('/home/jkevin/Documents/Proyectos/download-doc/') if i.endswith(".jpg")]
imglist.sort(key=lambda x: os.path.getmtime(x))
print(imglist)
with open("/home/jkevin/Documents/Proyectos/download-doc/final_slide.pdf", "wb") as f:
    f.write(i2p.convert(imglist))
driver.close()