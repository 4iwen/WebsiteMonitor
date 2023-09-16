import requests
import time
import hashlib
import threading
from lxml import etree


def log(name, message):
    print('[' + name + ']: ' + message)


def get_hash(url):
    # prevent caching
    headers = {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    response = requests.get(url, headers=headers)
    tree = etree.HTML(response.content)
    elements = tree.xpath('//*/div[@class="row pb-5"]/div[@class="col-md-8"]')
    # for element in elements:
        # print(etree.tostring(element))
    return hashlib.sha224(etree.tostring(elements[0])).hexdigest()


def monitor(website_info):
    name = website_info[0]
    url = website_info[1]
    last_hash = get_hash(url)
    while True:
        try:
            time.sleep(2)
            new_hash = get_hash(url)
            log(name, 'getting new hash: ' + new_hash)
            if new_hash == last_hash:
                log(name, 'website didnt change')
                continue
            else:
                log(name, 'website changed')
                last_hash = new_hash
        except Exception as error:
            log(name, 'error: ' + error)


if __name__ == '__main__':
    websites = [
        ['Temelin', 'https://www.cez.cz/cs/o-cez/infocentra/temelin-136405/'],
        ['Dukovany', 'https://www.cez.cz/cs/o-cez/infocentra/dukovany-135065/']
    ]
    for website in websites:
        thread = threading.Thread(target=monitor, args=(website,))
        thread.start()
