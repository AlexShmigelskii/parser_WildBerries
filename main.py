import csv

from bs4 import BeautifulSoup
from selenium import webdriver
import time
import json

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
}


def get_source_html(url, page):
    driver = webdriver.Chrome(
        executable_path='/home/alexandr/PycharmProjects/parserWB/chromedriver/chromedriver'
    )

    driver.maximize_window()

    try:
        driver.get(url=url)
        time.sleep(10)

        with open(f'index/index{page}.html', 'w') as file:
            file.write(driver.page_source)

    except Exception as ex:
        print(ex)

    finally:
        driver.close()


def get_items_urls(file_path, page=1):
    with open(file_path) as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')
    item_divs = soup.find_all('div', class_='product-card')

    urls = []

    for item in item_divs:
        item_url = item.find('a', class_='product-card__main').get('href')
        urls.append(item_url)

    with open(f'index/urls/{page}.txt', 'w') as file:
        for url in urls:
            file.write(f'{url}\n')

    return '[INFO] URLS collected success!'


def get_data(file_path, page=1):
    with open(file_path) as file:
        urls_list = [url.strip() for url in file.readlines()]
        # print(urls_list)

    count = 1
    result_list = []

    for url in urls_list:

        driver = webdriver.Chrome(
            executable_path='/home/alexandr/PycharmProjects/parserWB/chromedriver/chromedriver'
        )

        driver.maximize_window()

        try:
            driver.get(url=url)
            time.sleep(4)

            with open(f'index/pages/{count}.html', 'w') as file:
                file.write(driver.page_source)

            with open(f'index/pages/{count}.html') as file:
                src = file.read()

            soup = BeautifulSoup(src, 'lxml')

            product_url = url

            try:
                product_article = soup.find('span', {"id": "productNmId"}).text.strip()
            except Exception as ex:
                product_article = None

            try:
                product_cost = soup.find('ins', class_='price-block__final-price').text.strip()
            except Exception as ex:
                product_cost = None

            try:
                amount_review = soup.find('span', class_='user-activity__count').text.strip()
            except Exception as ex:
                amount_review = None

            try:
                stars = soup.find('span', {"data-link": "text{: product^star}"}).text.strip()
            except Exception as ex:
                stars = None

            try:
                merchant = 'https://www.wildberries.ru' + soup.find('div', class_='seller-info__title').find('a').get('href')
            except Exception as ex:
                merchant = None

            try:
                bought = soup.find('span', {"data-link": "{include tmpl='productCardOrderCount' ^~ordersCount=selectedNomenclature^ordersCount}"}).text.strip()
            except Exception as ex:
                bought = None

            result_list.append(
                {
                    'product_url': product_url,
                    'product_article': product_article,
                    'product_cost': product_cost,
                    'amount_review': amount_review,
                    'stars': stars,
                    'merchant': merchant,
                    'bought': bought
                }
            )

            with open(f'result/result.csv', 'a', newline='', errors='replace') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(
                    (
                        product_url,
                        product_article,
                        product_cost,
                        amount_review,
                        stars,
                        merchant,
                        bought
                    )
                )

            count += 1

        except Exception as ex:
            print(ex)

        finally:
            driver.close()

    with open(f'result/index{page}.json', 'w') as file:
        json.dump(result_list, file, indent=4, ensure_ascii=False)

    return '[INFO] Data collected!'


def main():
    for page in range(1, 11):
    #     get_source_html(url=f'https://www.wildberries.ru/catalog/0/search.aspx?page={page}&sort=popular&search=%D0%B2%D0%B8%D0%B1%D1%80%D0%B0%D1%82%D0%BE%D1%80', page=page)

        # print(get_items_urls(file_path=f'/home/alexandr/PycharmProjects/parserWB/index/index{page}.html', page=page))
        get_data(file_path=f'/home/alexandr/PycharmProjects/parserWB/index/urls/{page}.txt', page=page)


if __name__ == '__main__':
    main()
