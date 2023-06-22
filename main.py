import requests
import os
import json
import token_1
from datetime import datetime


class VkDownloader:
    
    def __init__(self, vk_token, version='5.131'):
        self.params = {
            'access_token': vk_token,
            'v': version
        }

    def get_photos(self, user_id=None, count=20):
        url = 'https://api.vk.com/method/photos.get'
        params = {
        'album_id': 'profile',
        'owner_id': user_id,
        'extended': '1',
        'count': count,
        }
        res = requests.get(url, params={**self.params, **params}).json()
        return res

    def get_all_photos(self):
        data = self.get_photos()
        i = 0
        photos = []  # Список всех загруженных фото
        likes_count = {}  # Словарь с парой название фото - URL фото максимального разрешения

        for i in data['response']['items']:
            if i['likes']['count'] not in likes_count:
                likes_count[i['likes']['count']] = 1
            else:
                likes_count[i['likes']['count']] += 1
        for item_ph in data['response']['items']:
            max_sized = max(item_ph['sizes'], key=(lambda x: x['height']))
            if likes_count[item_ph['likes']['count']] == 1:
                name = str(item_ph['likes']['count']) + '.jpg'
            else:
                name = f"{item_ph['likes']['count']}" \
                       f"({datetime.utcfromtimestamp(item_ph['date']).strftime('%d%m%Y-%H%M%S')}).jpg"
            photos.append({'name': name, 'size': max_sized['type'], 'url': max_sized['url']})
        return photos
        
class YaUploader:
    host = 'https://cloud-api.yandex.net:443/'
    def __init__(self, token: str):
        self.token = token
        
    def get_headers(self):
        return {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.token}'}

    def create_folder(self, folder_name):
        uri = 'v1/disk/resources/'
        url = self.host + uri
        params = {'path': f'/{folder_name}'}
        requests.put(url, headers=self.get_headers(), params=params)

    def upload_from_url(self, file_url, file_name, folder_name):
        uri = 'v1/disk/resources/upload/'
        url = self.host + uri
        params = {'path': f'/{folder_name}/{file_name}', 'url': file_url}
        response = requests.post(url, headers=self.get_headers(), params=params)
        if response.status_code == 202:
            print(f" Загрузка файла '{file_name}' прошла успешно")

if __name__ == '__main__':
    vk_token = token_1.TOKEN_VK
    user_id = str(input('Введите id пользователя: '))
    downloader = VkDownloader(vk_token)
    downloader.get_all_photos()
    
    ya_token = token_1.TOKEN_YA
    uploader = YaUploader(ya_token)
    folder_name = str(input('Введите имя папки на Яндекс диске, в которую необходимо сохранить фото: '))
    uploader.create_folder(folder_name)
    count = 0
    photos_list = downloader.get_all_photos()
    for photo in photos_list:
        uploader.upload_from_url(photo['url'], photo['name'], folder_name)
        count += 1
        print(f'Фотографий загружено на Яндекс диск: {count}')