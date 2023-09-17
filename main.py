import requests
import time
import hashlib
import threading
import yagmail
import json
from lxml import etree

# load config
file = open('config.json')
config = json.load(file)


def log(name, message):
    print('[' + name + ']: ' + message)


def get_website(url):
    # prevent caching
    headers = {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    return requests.get(url, headers=headers).content


def get_html(site):
    tree = etree.HTML(site)
    elements = tree.xpath(config['xpath'])
    if not elements:
        print('xpath couldnt find a valid element')
        yagmail.SMTP(config['email'], config['password']).send(config['email'],
                                                               subject='Script crashed',
                                                               contents='xpath couldnt find a valid element')
        exit()

    return etree.tostring(elements[0], encoding='unicode')


def get_hash(html):
    return hashlib.sha224(html.encode()).hexdigest()


def monitor(website_info):
    name = website_info[0]
    url = website_info[1]

    website_data = get_website(url)
    last_html = get_html(website_data)
    last_hash = get_hash(last_html)
    while True:
        try:
            time.sleep(15)
            website_data = get_website(url)
            new_html = get_html(website_data)
            new_hash = get_hash(new_html)
            log(name, 'getting new hash: ' + new_hash)
            if new_hash == last_hash:
                log(name, 'website didnt change')
                continue
            else:
                log(name, 'website changed')
                subject = 'Website [' + name + '] got changed!'
                contents = ('<h1>Before:</h1>\n' + last_html + '\n<h1>After:</h1>' + new_html)
                yagmail.SMTP(config['email'], config['password']).send(config['target_email'],
                                                                       subject=subject,
                                                                       contents=contents)
                last_html = new_html
                last_hash = new_hash
        except Exception as error:
            log(name, 'error: ' + error)
            yagmail.SMTP(config['email'], config['password']).send(config['email'],
                                                                   subject='Script crashed',
                                                                   contents=error)


if __name__ == '__main__':
    for website in config['websites']:
        thread = threading.Thread(target=monitor, args=(website,))
        thread.start()
