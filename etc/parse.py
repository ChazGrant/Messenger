import requests
from bs4 import BeautifulSoup

cont = requests.get('http://www.russki-mat.net/e/mat_slovar.htm')
cont.encoding = 'utf-8'
soup = BeautifulSoup(cont.text, 'html.parser')
for tag in soup.find_all("span"):
        print("{0}".format( tag.text))