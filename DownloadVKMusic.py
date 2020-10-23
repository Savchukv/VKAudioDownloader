#pip3 install requests
#pip3 install vk_api (необходима версия минимум 11.9.0)
#pip3 install BeautifulSoup4			
#pip3 install tqdm

import datetime
import time
import os
import os.path

import requests
import vk_api
from vk_api import audio

import getpass
from tqdm import tqdm
import sys

# Авторизация
def auth():
    vk_login = input('Введите телефон c 8: ')
    vk_password = getpass.getpass('Введите пароль: ')
    return vk_login, vk_password

# Если включена функция подтверждения входа
def two_step_auth():
    code = input('Введите код подтверждения входа: ')
    remember_device = False
    return code, remember_device

def folder():
    path = os.path.expanduser(r'/Users/Riedel 1/Desktop') + r'\music_vk'

    if not os.path.exists(path):
        os.makedirs(path)
    return path

def main():
    vk_login, vk_password = auth()

    try:
        vk_session = vk_api.VkApi(login=vk_login, password=vk_password, auth_handler=two_step_auth)

        vk_session.auth()
        print('Авторизация')
        vk = vk_session.get_api()
        vk_audio = audio.VkAudio(vk_session)
        print('Авторизация прошла успешно')

        # Загрузка
        def download(v_id):
            path = folder()
            os.chdir(path)
            song = 0
            time_start = datetime.datetime.now()
            print('Начало загрузки', datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y'))
            print('Путь загрузки:', path)
            print(vk_audio.get(owner_id=v_id))
            for i in vk_audio.get(owner_id=v_id):
                try:
                    song += 1
                    r = requests.get(i['url'])
                    size = int(r.headers['Content-Length'])
                    if r.status_code == 200:
                        with open(str(song) + '_' + i['artist'] + ' - ' + i['title'] + '.mp3', 'wb') as file:
                            print('Загрузка:', i['artist'] + ' - ' + i['title'])
                            time.sleep(0.5)
                            for data in tqdm(iterable=r.iter_content(chunk_size=1024), total=size / 1024, unit='KB',
                                             leave=True):
                                file.write(data)
                except OSError:
                    print('Ошибка загрузки:', song, i['artist'] + ' - ' + i['title'])
            time_end = datetime.datetime.now()
            print('Загружено', len(next(os.walk(path))[2]), 'песен за', (time_end - time_start))

            question = input('Выйти или продолжить?\nq/c: ')

            if question == 'q':
                print('Завершение работы скрипта')
                sys.exit(0)

            elif question == 'c':
                main()

        # Загрузка своей музыки
        def own_music():
            v_id = vk.users.get()[0]['id']
            print('Анализ музыки', vk.users.get()[0]['first_name'] + ' ' + vk.users.get()[0]['last_name'])
            print('Будет скачано:', len(vk_audio.get(owner_id=v_id)), 'аудиозаписей.')
            download(v_id)

        question_1 = input('Загрузить свою музыку?\ny/n: ')

        if question_1 == 'y':
            own_music()

    except vk_api.AuthError:
        print('Неверный логин или пароль')
        main()
й
if __name__ == '__main__':
    main()