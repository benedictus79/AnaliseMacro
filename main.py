import yt_dlp
import json
from concurrent.futures import ThreadPoolExecutor
from login import analisemacrosession, selected_course, BeautifulSoup
from utils import clean_user_data, create_folder, os, clear_folder_name, shorten_folder_name, generate_file_name, add_link_to_file, log_error, SilentLogger
from pagination import pagination
from tqdm import tqdm


def download_video(url, output_name):
  ydl_opts = {
    'format': 'bv+ba/b',
    'outtmpl': output_name,
    'quiet': True,
    'no_progress': True,
    'logger': SilentLogger(),
    'http_headers': analisemacrosession.headers,
    'concurrent_fragment_downloads': 10,
    'fragment_retries': 50,
    'retry_sleep_functions': {'fragment': 20},
    'buffersize': 104857600,
    'retries': 20,
    'continuedl': True,
    'extractor_retries': 10
  }
  
  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])


def is_vimeo_iframe(iframe):
  return iframe is not None and 'src' in iframe.attrs and 'vimeo' in iframe['src']


def extract_lesson_details(lesson, index, main_course_folder):
  a_tag = lesson.find_parent('a', class_='ld-item-name')

  if not a_tag:
    return None, None, None
  
  lesson_title_text = lesson.text.strip()
  lesson_title = f"{index:03d} - {lesson_title_text}" 
  lesson_folder = create_folder(os.path.join(main_course_folder, clear_folder_name(lesson_title)))

  lesson_link = a_tag['href']
  
  return lesson.text.strip(), lesson_link, lesson_folder


def get_avaliation_test(soup, lesson_folder):
  avaliation_tests = soup.find_all('a', class_='ld-table-list-item-preview ld-topic-row ld-primary-color-hover')

  for avaliation_test in avaliation_tests:
    test_title_tag = avaliation_test.find('div', class_='ld-item-title')
    if test_title_tag:
      topic_title = test_title_tag.text.strip()
      topic_href = avaliation_test.get('href')
      response_lesson = analisemacrosession.get(topic_href)
      soup = BeautifulSoup(response_lesson.text, 'html.parser')
      iframe = soup.find('iframe')
      video_url = iframe['src']
      output_path = create_folder(shorten_folder_name(os.path.join(lesson_folder, f'teste')))
      
      if iframe and is_vimeo_iframe(iframe):
        output_path = shorten_folder_name(os.path.join(output_path, clear_folder_name(topic_title) + '.mp4'))
        download_video(video_url, output_path)

      if not (iframe and is_vimeo_iframe(iframe)):
          save_html_content(soup, output_path, clear_folder_name(topic_title))


def process_topic_links(soup, lesson_folder, analisemacrosession):
  topic_links = soup.find_all('a', class_=lambda x: x and ('learndash-incomplete' in x or 'learndash-complete' in x))

  for index, link in enumerate(topic_links, start=1):
    topic_title_tag = link.find('span', class_='ld-topic-title')
    if topic_title_tag:
      topic_title = topic_title_tag.text.strip()
      topic_href = link.get('href')
      response_lesson = analisemacrosession.get(topic_href)
      soup = BeautifulSoup(response_lesson.text, 'html.parser')
      iframe = soup.find('iframe')
      video_url = iframe['src']
      if iframe and is_vimeo_iframe(iframe):
        output_path = shorten_folder_name(os.path.join(lesson_folder, 'topico', f'{index:03d} - {clear_folder_name(topic_title)}.mp4'))
        download_video(video_url, output_path)

    download_materials_link(soup, lesson_folder, analisemacrosession)


def save_html_content(soup, lesson_folder, file_name):
  scripts = soup.find_all('script')
  html_content = clean_user_data(soup, scripts)
  soup = BeautifulSoup(html_content, 'html.parser')
  ld_focus_header = soup.find('div', class_='ld-focus-header')
  ld_lesson_items = soup.find('div', class_='ld-lesson-items')

  if ld_focus_header:
    ld_focus_header.decompose()

  if ld_lesson_items:
    ld_lesson_items.decompose()

  scripts_to_remove = soup.find_all('script', {'id': 'pys-js-extra'})
  scripts_to_remove.extend(soup.find_all('script', {'data-cfasync': 'false', 'data-pagespeed-no-defer': ''}))
  scripts_to_remove.extend(soup.find_all('script', string=lambda t: 'window.intercomSettings' in t if t else False))

  for script in scripts_to_remove:
    script.decompose()

  file_path = os.path.join(lesson_folder, file_name + ".html")

  if not os.path.exists(file_path):
    with open(file_path, "w", encoding="utf-8") as file:
      file.write(str(soup.prettify()))


def download_file(url, lesson_folder, session, index):
  response = session.get(url, stream=True, headers=session.headers)

  if response.status_code != 200:
    msg_warning = f"Erro ao acessar {url}: Status Code {response.status_code}"
    log_error(msg_warning)
    return

  content_type = response.headers.get('Content-Type')
  file_name = generate_file_name(url, content_type)

  material_folder = create_folder(os.path.join(lesson_folder, 'material'))
  file_path = os.path.join(material_folder, f'{index:03d} - {clear_folder_name(file_name)}')

  if not os.path.exists(file_path):
    with open(file_path, 'wb') as file:
      for chunk in response.iter_content(chunk_size=8192):
        file.write(chunk)


def download_materials_link(soup, lesson_folder, session):
  materials_div = soup.find('div', {"aria-labelledby": "materials", "class": "ld-tab-content"})

  if materials_div:
    materials_links = materials_div.find_all('a', href=True)
    for i, materials_link in enumerate(materials_links,start=1):
      if materials_link['href']:
        if "github" and ".html" in materials_link['href']:
          download_file(materials_link['href'], lesson_folder, session, i)
        if "github"  in materials_link['href'] and not ".html" in materials_link['href']:
          add_link_to_file(materials_link['href'], lesson_folder, i)
        if "google" in materials_link['href']:
          add_link_to_file(materials_link['href'], lesson_folder, i)
        if "download" in materials_link['href']:
          download_file(materials_link['href'], lesson_folder, session, i)


def find_and_download_video(lesson_link, lesson_folder, lesson_title):
  response_lesson = analisemacrosession.get(lesson_link)
  analisemacrosession.headers['Referer'] = response_lesson.url
  soup = BeautifulSoup(response_lesson.text, 'html.parser')
  iframe = soup.find('iframe')

  if iframe and is_vimeo_iframe(iframe):
    video_url = iframe['src']
    output_path = shorten_folder_name(os.path.join(lesson_folder, clear_folder_name(lesson_title) + ".mp4"))
    download_video(video_url, output_path)
  
  download_materials_link(soup, lesson_folder, analisemacrosession)
  
  if not (iframe and is_vimeo_iframe(iframe)):
    save_html_content(soup, lesson_folder, clear_folder_name((lesson_title)))

  process_topic_links(soup, lesson_folder, analisemacrosession)
  get_avaliation_test(soup, lesson_folder)


def navigate_page(ld_pages):
  data_pager_nonce = ld_pages.get('data-pager-nonce')
  data_pager_results = ld_pages.get('data-pager-results')
  data_pager_results_json = json.loads(data_pager_results)
  data_pager_results_json['nonce'] = data_pager_nonce

  return data_pager_results_json


def extract_lesson_titles(soup):
  lesson_anchors = soup.find_all('a', class_='ld-item-name ld-primary-color-hover')
  return [anchor.find('div', class_='ld-item-title') for anchor in lesson_anchors if anchor.find('div', class_='ld-item-title')]


def process_lessons(course_name, lessons_titles, main_course_folder):
  total_lessons = len(lessons_titles) 
  main_progress_bar = tqdm(total=total_lessons, desc=course_name, leave=True)
  executor = ThreadPoolExecutor(max_workers=5)

  futures = []
  for i, lesson in enumerate(lessons_titles, start=1):
    lesson_title, lesson_link, lesson_folder = extract_lesson_details(lesson, i, main_course_folder)
    if lesson_title and lesson_link:
      future = executor.submit(find_and_download_video, lesson_link, lesson_folder, lesson_title)
      futures.append(future)

  for future in futures:
    future.result()
    main_progress_bar.update(1)

  executor.shutdown()
  main_progress_bar.close()


def list_lessons(course_name, course_link, course_id):
  main_course_folder = create_folder(clear_folder_name(course_name))
  response = analisemacrosession.get(course_link)
  soup = BeautifulSoup(response.text, 'html.parser')
  lessons_titles = extract_lesson_titles(soup)
  ld_pages = soup.find('div', class_='ld-pagination ld-pagination-page-course_content_shortcode')

  if ld_pages:
    data_json = navigate_page(ld_pages)
    additional_html = pagination(data_json, course_id)
    additional_soup = BeautifulSoup(additional_html, 'html.parser')
    lessons_titles = extract_lesson_titles(additional_soup)
    return process_lessons(course_name, lessons_titles, main_course_folder)

  return process_lessons(course_name, lessons_titles, main_course_folder)


if __name__ == "__main__":
  course_name, course_link, course_id = selected_course
  list_lessons(course_name, course_link, course_id)
