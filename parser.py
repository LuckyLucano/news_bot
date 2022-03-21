from bs4 import BeautifulSoup
import requests
import re
from database import db, cursor

class Parser:

    def __init__(self, page_name):
        self.page_name = page_name
        self.URL = 'https://russian.rt.com'
        self.HEADERS = {
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
        }

    def get_soup(self):
        response = requests.get(f'{self.URL}/{self.page_name}', headers=self.HEADERS)

        try:
            response.raise_for_status()
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            return soup
        except requests.HTTPError:
            print('Не удалось получить данные')

    def get_image_link_and_article_link(self, block):
        main_block = block.find('div', class_='cover__media')
        image_link = re.search(r'https:[\w\/.]+', main_block['style'])[0]
        article_link = self.URL + block.find('a', class_='cover__link')['href']
        return {'image_link': image_link, 'article_link': article_link}

    def get_category_id(self, block):
        category_tag = block.find('div', class_='card__trend')
        if category_tag:
            category_name = category_tag.get_text(strip=True)
        else:
            category_name = 'Общее'

        cursor.execute('''
        insert into categories (category_name) values (%s)
        on conflict do nothing;
        select category_id
        from categories
        where category_name = %s;
        ''', (category_name, category_name))
        category_id = cursor.fetchone()[0]
        return category_id

    def get_json_data(self, soup):
        json_data = []
        cards = soup.find_all('div', class_='card_sections')
        for card in cards:
            category_id = self.get_category_id(card)
            title = card.find('div', class_='card__heading').get_text(strip=True)
            date = card.find('div', class_='card__date').get_text(strip=True)
            author = card.find('div', class_='card__author').get_text(strip=True).replace('\n                  ', ' ')
            description = card.find('div', class_='card__summary').get_text(strip=True)
            image_link = self.get_image_link_and_article_link(card)['image_link']
            article_link = self.get_image_link_and_article_link(card)['article_link']

            json_data.append({
                'category_id': category_id,
                'title': title,
                'date': date,
                'author': author,
                'description': description,
                'image_link': image_link,
                'article_link': article_link
            })

        return json_data

    def fill_database(self, soup):
        json_data = self.get_json_data(soup)
        for data in json_data:
            cursor.execute('''
        insert into articles(title, date, author, description, image_link, article_link, category_id)
        values (%s, %s, %s, %s, %s, %s, %s)
        ''', (
                data['title'],
                data['date'],
                data['author'],
                data['description'],
                data['image_link'],
                data['article_link'],
                data['category_id']
            ))

    def run(self):
        soup = self.get_soup()
        if soup:
            self.fill_database(soup)
        else:
            print('Не удалось обработать HTML страницу')


world = Parser(page_name='world')
world.run()
russia = Parser(page_name='russia')
russia.run()
ussr = Parser(page_name='ussr')
ussr.run()

db.commit()
db.close()
