import re
import json
import requests
from bs4 import BeautifulSoup as bs
from fake_headers import Headers


def get_headers():
    return Headers(browser = 'firefox', os = 'win').generate()

def get_params():
    params = {
        'area': [1, 2],
        'text': 'python'
    }
    return params

def search(HOST):
    pat = r'(^\w+-?\w*)(,.*)'
    repl = r'\1'

    html = requests.get(HOST, headers=get_headers(), params=get_params()).text
    soup = bs(html, features='lxml')

    link_list = soup.find(id="a11y-main-content")
    vacancy = link_list.find_all(class_='serp-item')

    parse_vacancy = []
    for tag in vacancy:
        link = tag.find('a')['href']
        link_html = requests.get(link, headers=get_headers()).text
        soup_html = bs(link_html, features='lxml')
        info = soup_html.find(class_='main-content')
        description = info.find(class_='vacancy-section').text
        if 'django' in description.lower() or 'flask' in description.lower():
            salary = info.find(class_='vacancy-title').find('span').text
            if 'usd' in salary.lower():
                name_c = info.find(class_='vacancy-company-details').find('span', class_='vacancy-company-name').text
                try:
                    city = re.sub(pat, repl, (info.find(class_='vacancy-company-redesigned').find('p').text))
                except AttributeError:
                    city = re.sub(pat, repl, (info.find(class_='vacancy-company-redesigned').find('a', class_='bloko-link bloko-link_kind-tertiary bloko-link_disable-visited').text))
                parse_vacancy.append({
                    'link': link,
                    'fork_salary': salary,
                    'name_company': name_c,
                    'city': city
                })
    return parse_vacancy

if __name__ == '__main__':
    HOST = 'https://spb.hh.ru/search/vacancy'

    with open("vacancy_file.json", "w", encoding='utf-8') as file:
        json.dump(search(HOST), file, indent=2, ensure_ascii=False)