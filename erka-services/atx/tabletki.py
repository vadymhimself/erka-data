from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import urllib

url = 'https://tabletki.ua/atc/'

atx = ['A09AA02']


def get(name):
    try:
        URL = url + urllib.parse.quote_plus(name)
        print(URL)
        req = Request(URL, headers={
            'User-Agent': "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"})
        webpage = urlopen(req).read()

        soup = BeautifulSoup(webpage, "lxml")
        div = soup.find("div", attrs={"id": "ctl00_ctl00_MAIN_ContentPlaceHolder_MAIN_ContentPlaceHolder_GoodsPanel"})
        a = div.find_all("a")
        # print(div)
        return [t.text.strip() for t in a]

    except:
        return []


if __name__ == "__main__":
    for i in atx:
        get(i)
