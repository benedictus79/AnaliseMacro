import requests
from bs4 import BeautifulSoup
from utils import clear_screen, benedictus_ascii_art


analisemacrosession = requests.Session()

headers = {
  'authority': 'aluno.analisemacro.com.br',
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
  'accept-language': 'pt-BR,pt;q=0.9',
  'cache-control': 'no-cache',
  'content-type': 'application/x-www-form-urlencoded',
  'dnt': '1',
  'origin': 'https://aluno.analisemacro.com.br',
  'pragma': 'no-cache',
  'referer': 'https://aluno.analisemacro.com.br/',
  'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Brave";v="120"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-user': '?1',
  'sec-gpc': '1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}


def get_nonce_login():
  response = analisemacrosession.get('https://aluno.analisemacro.com.br/', headers=headers)
  soup = BeautifulSoup(response.text, 'html.parser')
  input_element = soup.find('input', id='woocommerce-login-nonce')

  if input_element:
    value = input_element.get('value')

    return value


def login(nonce):
  benedictus_ascii_art()
  username = input("email: ")
  password = input("senha: ")
  clear_screen()
  data = {
    'username': username,
    'password': password,
    'woocommerce-login-nonce': nonce,
    '_wp_http_referer': '/',
    'login': 'Acessar',
  }
  response = analisemacrosession.post('https://aluno.analisemacro.com.br/', headers=headers, data=data)
  soup = BeautifulSoup(response.text, 'html.parser')
  div_tags = soup.find_all('div', class_=lambda x: x and x.startswith('ld-item-list-item ld-item-list-item-course ld-expandable learndash-'))

  cursos = {}
  for div_tag in div_tags:
    numeric_id = div_tag.get('id').split('-')[-1] if div_tag.get('id') else None

    a_tag = div_tag.find('a', class_='ld-item-name')
    if a_tag:
      curso_url = a_tag.get('href')
      span_tag = a_tag.find('span', class_='ld-course-title')
      curso_titulo = span_tag.text.strip() if span_tag else "Título não encontrado"
      cursos[curso_titulo] = {
        'url': curso_url,
        'id': numeric_id
      }

  return cursos


def choose_course(courses):
  print("Cursos disponíveis:")
  for i, (course_title, course_info) in enumerate(courses.items(), start=1):
    print(f"{i}. {course_title}")

  choice = input("Escolha um curso pelo número: ")
  selected_course_title = list(courses.keys())[int(choice) - 1]
  selected_course_info = courses[selected_course_title]
  
  return selected_course_title, selected_course_info['url'], selected_course_info['id']


nonce = get_nonce_login()
courses = login(nonce)
selected_course = choose_course(courses)
