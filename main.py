import requests
import os
import json
import token_1

def main():
    class VkDownloader:

        def __init__(self, vk_token):
            self.token = vk_token

        def get_photos(self, offset=0, count=20):

            url = 'https://api.vk.com/method/photos.get'
            params = {'owner_id': user_id,
                      'album_id': 'profile',
                      'access_token': vk_token,
                      'v': '5.131',
                      'extended': '1',
                      'photo_sizes': '1',
                      'count': count,
                      'offset': offset
                      }
            res = requests.get(url=url, params=params)
            return res.json()

        def get_all_photos(self):
            data = self.get_photos()
            all_photo_count = data['response']['count']  
            i = 0
            count = 20
            photos = []  # Список всех загруженных фото
            max_size_photo = {}  # Словарь с парой название фото - URL фото максимального разрешения


            if not os.path.exists('images_vk'):
                os.mkdir('images_vk')

            while i <= all_photo_count:
                if i != 0:
                    data = self.get_photos(offset=i, count=count)

                for photo in data['response']['items']:
                    max_size = 0
                    photos_info = {}

                    for size in photo['sizes']:
                        if size['height'] >= max_size:
                            max_size = size['height']
                    if photo['likes']['count'] not in max_size_photo.keys():
                        max_size_photo[photo['likes']['count']] = size['url']
                        photos_info['file_name'] = f"{photo['likes']['count']}.jpg"
                    else:
                        max_size_photo[f"{photo['likes']['count']} + {photo['date']}"] = size['url']
                        photos_info['file_name'] = f"{photo['likes']['count']}+{photo['date']}.jpg"



                    photos_info['size'] = size['type']
                    photos.append(photos_info)

                for photo_name, photo_url in max_size_photo.items():
                    with open('images_vk/%s' % f'{photo_name}.jpg', 'wb') as file:
                        img = requests.get(photo_url)
                        file.write(img.content)

                print(f'Загружено {len(max_size_photo)} фото')
                i += count

            with open("photos.json", "w") as file:
                json.dump(photos, file, indent=4)

    class YaUploader:
        def __init__(self, token: str):
            self.token = token

        def folder_creation(self):
            url = f'https://cloud-api.yandex.net/v1/disk/resources/'
            headers = {'Content-Type': 'application/json',
                       'Authorization': f'OAuth {ya_token}'}
            params = {'path': f'{folder_name}',
                      'overwrite': 'false'}
            response = requests.put(url=url, headers=headers, params=params)

        def upload(self, file_path: str):
            url = f'https://cloud-api.yandex.net/v1/disk/resources/upload'
            headers = {'Content-Type': 'application/json',
                       'Authorization': f'OAuth {ya_token}'}
            params = {'path': f'{folder_name}/{file_name}',
                      'overwrite': 'true'}

            # Получение ссылки на загрузку
            response = requests.get(url=url, headers=headers, params=params)
            href = response.json().get('href')

            # Загрузка файла
            uploader = requests.put(href, data=open(files_path, 'rb'))

    
    vk_token = token_1.TOKEN_VK
    user_id = token_1.USER_ID
    downloader = VkDownloader(vk_token)
    downloader.get_all_photos()
    
    ya_token = token_1.TOKEN_YA
    uploader = YaUploader(ya_token)
    folder_name = str(input('Введите имя папки на Яндекс диске, в которую необходимо сохранить фото: '))
    uploader.folder_creation()

    photos_list = os.listdir('images_vk')
    count = 0
    for photo in photos_list:
        file_name = photo
        files_path = os.getcwd() + '/images_vk/' + photo
        res = uploader.upload(files_path)
        count += 1
        print(f'Фотографий загружено на Яндекс диск: {count}')


if __name__ == '__main__':
    main()

