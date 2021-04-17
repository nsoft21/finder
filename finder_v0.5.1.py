from flask import Flask, request
import requests
import json
import time
import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
#from selenium import webdriver
#from selenium.webdriver.common.keys import Keys

app = Flask(__name__)

cache = []

# Приготовление хрома для ускорения запросов
#driver = webdriver.Chrome()
#driver.set_window_position(0, 0)
#driver.set_window_size(1400, 900)
#driver.get('https://dns-shop.ru/')
#driver.find_element_by_link_text('Выбрать другой').click()
#time.sleep(2)
#driver.find_element_by_xpath("//input[@class='form-control' and @data-role='search-city']").send_keys("Симферополь")  
#driver.find_element_by_xpath("//input[@class='form-control' and @data-role='search-city']").send_keys(Keys.RETURN)


def get_html(url):
    url = url.replace(' ', '+')
    headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
    r = requests.get(url, headers=headers)
    print(url)
    return r.text


def get_html_dns(url):
    global driver
    driver.get(url)
    time.sleep(2)
    html = driver.page_source
    return html


def sort_array(i):
    return i[3] # 3 потому что price


def get_products(html, products, shop):
    soup = BeautifulSoup(html, 'lxml')
    if shop == "komtek":
    	no_items = soup.find('p', class_='note-msg misspell fallback')
    	if no_items:
    		return products
    	else:
    		print(no_items)
    		print(type(no_items))
    	ul = soup.find('ul', class_='products-list hover-effect')
    	try:
    		li = ul.find_all('li', class_='item')
    	except:
    		if soup.find('p', class_='note-msg empty-catalog category-products'):
    			return products
    	span = ul.find_all('span', class_='item-name')
    	for i in li:
            href = i.find('span', class_='item-name').a.get('href')
            name = i.find('span', class_='item-name').a.get('title')              
            price = i.find('span', class_='price').text.replace('\xa0руб.', '')
            price = float(price.replace('\xa0', '').replace(',', '.'))
            try:
                available = i.find('span', class_='simferopol').find('span').text
            except:
                time.sleep(2)
                try:
                    available = i.find('span', class_='simferopol').find('span').text.replace('    ', '')
                except:
                    available = ''

            product = ['komtek', href, name, price, available]
            products.append(product)
    elif shop == "dns":
        div = soup.find_all('div', class_='catalog-product ui-button-widget')
        for i in div:
            a = i.find('a', class_='catalog-product__name ui-link ui-link_black')
            href = a.get('href')
            name = a.text[0:a.text.find('[')]

            try:
                price = float(i.find('div', class_='product-buy__price').text.replace(' ', '').replace('₽', ''))
            except:
                price = 0
            
            try:
                available = i.find('a', class_='order-avail-wrap__link ui-link ui-link_blue ui-link_pseudolink').find('span').text.replace('    ', '')
            except:
                try:
                    available = i.find('div', class_='order-avail-wrap').text
                except:
                    available = 'Нет в наличии EXCEPT'

            product_url = f'https://www.dns-shop.ru' + href
            product = ['dns', product_url, name, price, available]
            products.append(product)
    elif shop == "indicator":
        div = soup.find_all('div', class_='ty-grid-list__item ty-quick-view-button__wrapper')
        for i in div:
            available = i.find('span', class_='product-label').text.replace('    ', '') 
            href = i.find('a', class_='product-title').get('href')            
            name = i.find('a', class_='product-title').get('title')
            price = float(i.find('span', class_='ty-price-num').text.replace('\xa0', ''))
               
            product = ['indicator', href, name, price, available]
            products.append(product)
    elif shop == "optima":
        div = soup.find_all('div', class_='grid-box')
        for i in div:
            a = i.find('strong', class_='sale-title')
            try:
                href = 'https://optima-computers.ru' + a.find('a').get('href')
                name_arr = a.find_all('span')
                name = name_arr[0].text + name_arr[1].text  
                try:         
                    price = float(i.find('div', class_='price-text').find('strong').find('span').text.replace('\t', '').replace('\xa0', '').replace('\n', '').replace('руб', ''))
                except:
                    price = 0   
                try:
                    available = i.find('em', class_='present').text.replace('    ', '')
                except:
                    available = 'except'
            except:
                continue

            product = ['optima', href, name, price, available]
            products.append(product)
    elif shop == "patron":
        div = soup.find_all('div', class_='ty-compact-list__content')
        for i in div:
            a = i.find('a', class_='product-title')
            try:
                href = a.get('href')
                name = a.text
                try:         
                    price = float(i.find('span', class_='ty-price-num').text.replace('\xa0', '').replace('\n', ''))
                except:
                    price = 0   
                try:
                    available = i.find('div', class_='ty-control-group product-list-field').find('span', class_='ty-control-group__item').text
                except:
                    available = 'except'
            except:
                continue

            product = ['patron', href, name, price, available]
            products.append(product)
    elif shop == "fotosklad":
        div = soup.find_all('div', class_='js-an-product-global box_product_2')
        for i in div:
            a = i.find('a', class_='title')
            try:
                href = 'https://www.fotosklad.ru' + a.get('href')
                name = a.find('span').text
                try:         
                    price = float(i.find('div', class_='price_list').find('p').find('span').text.replace('\xa0', '').replace(' ', '').replace('₽', ''))
                except:
                    price = 0  
                try:
                    available = i.find('div', class_='status_have in_warehouse').text
                except:
                    available = 'except'
            except:
                continue

            product = ['fotosklad', href, name, price, available]
            products.append(product)
    elif shop == "top100":
        file = open('top100.txt', 'w', encoding='utf-8')
        div = soup.find_all('div', class_='multi-item')
        file.write(html)
        for i in div:
            a = i.find('div', class_='multi-content').find('a')
            href = a.get('href')
            name = a.find('span').text
            try:         
                price = float(i.find('span', class_='multi-price').text.replace('\xa0', '').replace(' ', ''))
            except:
                price = 0  
            available = 'Нет информации'

            product = ['top100', href, name, price, available]
            products.append(product)

    return products


def search_avail(products):
    res = []
    for product in products:
        product_avail = product[4].replace(' ', '').replace('\n', '').replace('\t', '')
        if (product_avail.find('вналичии') != -1) or (product_avail.find('Вналичии') != -1) or (product_avail.find('магазинах') != -1) or (product_avail.find('магазине') != -1) or (product_avail.find('заканчивается') != -1):
            res.append(product)
        else:
            pass

    res.sort(key=sort_array)
    return res



def find_product(quest, available=False):
    shops = [['komtek', 'https://komtek.net.ru/catalogsearch/result/?cat=0&q='], 
    ['dns', 'https://www.dns-shop.ru/search/?q='], 
    #['top100', 'https://topsto-crimea.ru/#/search/'],
    ['fotosklad', 'https://www.fotosklad.ru/search/?q='], 
    ['patron', 'https://patron-service.ru/?subcats=Y&pcode_from_q=Y&pshort=Y&pfull=Y&pname=Y&pkeywords=Y&search_performed=Y&q={quest}&dispatch=products.search&security_hash=97984a6c767563bbd9f0325f5235f793'],
    ['indicator', 'https://indicator.com.ru/?subcats=Y&status=A&pshort=Y&pfull=Y&pname=Y&pkeywords=Y&search_performed=Y&q={quest}&cid=0&dispatch=products.search&search_id=&pshort=Y&pfull=N&pname=Y&pkeywords=Y&pcode=Y&match=all&subcats=N&subcats=Y&security_hash=3eccd700fa9859b8011be30804ca58bd'],
    ['optima', 'https://optima-computers.ru/search?st=']]
    products = []

    for i in cache:
        if i[0] == quest:
            if ((datetime.datetime.now() - i[2]) < timedelta(hours = 4)):
                products = i[1]
                if available:
                    products = search_avail(products)
                return products
            else: del i
            
    for shop in shops:
        if shop[0] == 'indicator' or shop[0] == 'patron':
            products = get_products(get_html(shop[1].replace('{quest}', quest)), products, shop[0])
        elif shop[0] == 'dns':
            pass
            #products = get_products(get_html_dns(shop[1] + quest), products, shop[0])
        else:
            products = get_products(get_html(shop[1] + quest), products, shop[0])

    products.sort(key=sort_array)
    for_cache = [quest, products, datetime.datetime.now()]
    cache.append(for_cache)        

    if available:
        products = search_avail(products)        
    
    return products


def gen_html(products):
    template = open('template.html', 'r', encoding='utf-8')
    html = template.read()

    if products != []:
        table_template = open('templ_block.html', 'r', encoding='utf-8')
        block_i = table_template.read()
        block = block_i
        i = 0
        for product in products:
            if i != 0:
                block = block.replace('{find_list}', block_i)
            else: i = i + 1
            if product[0] == "komtek":
                block = block.replace('{img}', 'https://cloud.qcoder.ru/f/ea15b94b38054828b85e/?dl=1')
            elif product[0] == "dns":
                block = block.replace('{img}', 'https://cloud.qcoder.ru/f/2efb94f61edd489e8f7d/?dl=1')
            elif product[0] == "indicator":
                block = block.replace('{img}', 'https://cloud.qcoder.ru/f/cb6236c67eff417d8388/?dl=1')
            elif product[0] == "optima":
                block = block.replace('{img}', 'https://cloud.qcoder.ru/f/c3cfd9e2633a4067b166/?dl=1') 
            elif product[0] == "patron":
                block = block.replace('{img}', 'https://cloud.qcoder.ru/f/cf8631af1a414254b1a4/?dl=1') 
            elif product[0] == "fotosklad":
                block = block.replace('{img}', 'https://cloud.qcoder.ru/f/bbaa2d85387b4a61b218/?dl=1') 
            elif product[0] == "top100":
                block = block.replace('{img}', 'https://cloud.qcoder.ru/f/32e1aa698f9c472fae83/?dl=1')  

            block = block.replace('{href}', product[1])
            block = block.replace('{product}', product[2])
            block = block.replace('{price}', str(product[3]) + ' руб.')
            block = block.replace('{available}', product[4])
            
        block = block.replace('{find_list}', '')
        block = block.replace('block_i', '')
        html = html.replace('{table}', block)
    else:
        text = 'Для того чтобы воспользоваться поиском введите в строку поисковой запрос и нажмите "Найти"'
        html = html.replace('{table}', text)
    
    return html


@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        if request.args.get('finder') and request.args.get('available'):
            products = find_product(request.args.get('finder'), request.args.get('available'))
        elif request.args.get('finder'):
            products = find_product(request.args.get('finder'))
        else:
            products = []
        html = gen_html(products)
        return html
   
    if request.method == 'POST':
        pass
        # Пока не надо


if __name__ == '__main__':
    app.run('0.0.0.0', 90)
