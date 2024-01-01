import os
import re
import platform


def clear_screen():
  command = 'cls' if platform.system() == 'Windows' else 'clear'
  os.system(command)


def create_folder(folder_name):
  path = os.path.join(os.getcwd(), folder_name)

  if not os.path.exists(path):
    os.mkdir(path)

  return path


def clear_folder_name(name):
  sanitized_name = re.sub(r'[<>:"/\\|?*]', ' ', name)
  sanitized_name = re.sub(r'\s+', ' ', sanitized_name).strip()

  return sanitized_name


def shorten_folder_name(full_path, max_length=210):
  if len(full_path) > max_length:
    num_chars_to_remove = len(full_path) - max_length
    directory, file_name = os.path.split(full_path)
    base_name, extension = os.path.splitext(file_name)
    num_chars_to_remove = min(num_chars_to_remove, len(base_name))
    shortened_name = base_name[:-num_chars_to_remove] + extension
    new_full_path = os.path.join(directory, shortened_name)
    return new_full_path
    
  return full_path


def benedictus_ascii_art():
  benedictus = """
     ___ ___ _  _ ___ ___ ___ ___ _____ _   _ ___ 
    | _ ) __| \| | __|   \_ _/ __|_   _| | | / __|
    | _ \ _|| .` | _|| |) | | (__  | | | |_| \__ \\
    |___/___|_|\_|___|___/___\___| |_|  \___/|___/
    
  Author: Benedictus ©
  Community: https://t.me/alex4ndriagroup
  Version: Beta 2.0
  """
  print(benedictus)


def generate_file_name(url, content_type):
  default_name = 'downloaded_material'
  extension = {
    'application/rar': '.rar',
    'application/zip': '.zip',
    'application/pdf': '.pdf',
    'text/html': '.html',
    'text/csv;charset=UTF-8': '.csv',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
  }.get(content_type, '')
  url_file_name = os.path.basename(url).split('?')[0]

  if url_file_name:
    url_file_name =  url_file_name.split('#1')[0]
    return url_file_name

  return default_name + extension


def clean_user_data(page, scripts):
  html_content = str(page)
  html_content = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '', html_content)
  html_content = re.sub(r'\d{3}\.\d{3}\.\d{3}-\d{2}', '', html_content)
  html_content = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '', html_content)

  for script in scripts:
    if script.string:
      script.string = re.sub(r'user_id:\s*\d+\s*,', '', script.string)

  return html_content


def add_link_to_file(link, lesson_folder, index):
  file_path = create_folder(os.path.join(lesson_folder, 'material'))
  with open(os.path.join(file_path, f'{index:03d} - links.txt'), 'a') as file:
    file.write(link + '\n')


def log_error(error_message):
  with open("erros.txt", "a") as file:
    file.write(error_message + "\n")


class SilentLogger(object):
  def debug(self, msg):
    pass

  def warning(self, msg):
    print(msg)

  def error(self, msg):
    print(msg)
