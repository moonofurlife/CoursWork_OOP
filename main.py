from tqdm import tqdm
import requests
import token_1
from datetime import datetime
import json


class VkDownloader:
    def __init__(self, user_id, version='5.131'):
        self.user_id = user_id
        self.params = {
            'access_token': token_1.TOKEN_VK,
            'v': version
        }

    def get_photos(self, count=20):
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'album_id': 'profile',
            'owner_id': self.user_id,
            'extended': '1',
            'count': count,
        }
        res = requests.get(url, params={**self.params, **params}).json()
        return res

    def get_all_photos(self):
        data = self.get_photos()
        photos = {}  # Словарь с парами: название фото - URL фото максимального разрешения

        for item_ph in data['response']['items']:
            likes_count = str(item_ph['likes']['count'])
            if likes_count in photos:
                date_str = datetime.utcfromtimestamp(item_ph['date']).strftime('%d%m%Y-%H%M%S')
                name = f"{likes_count}_{date_str}"
            else:
                name = likes_count
            max_sized = max(item_ph['sizes'], key=lambda x: x['height'] * x['width'])
            photos[name] = {'size': max_sized['type'], 'url': max_sized['url']}

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
            print(f"Загрузка файла '{file_name}' прошла успешно")

    def upload_photos_to_yandex_disk(self, photos_dict, folder_name):
        count = 0
        json_data = []  # Список для формирования JSON
        for name, photo in tqdm(photos_dict.items(), desc='Загрузка фотографий'):
            self.upload_from_url(photo['url'], name + '.jpg', folder_name)
            count += 1
            json_data.append({'name': name, 'size': photo['size']})  # Добавляем данные в список

        # Сохранение списка в файл JSON
        json_filename = f'{folder_name}_photos.json'
        with open(json_filename, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)
        print(f'Список фотографий сохранен в файле: {json_filename}')


if __name__ == '__main__':
    user_id = input('Введите id пользователя: ')
    downloader = VkDownloader(user_id)

    ya_token = input('Введите Яндекс Диск: ')
    uploader = YaUploader(ya_token)
    folder_name = input('Введите имя папки на Яндекс диске, в которую необходимо сохранить фото: ')
    uploader.create_folder(folder_name)
    photos_dict = downloader.get_all_photos()
    uploader.upload_photos_to_yandex_disk(photos_dict, folder_name)
