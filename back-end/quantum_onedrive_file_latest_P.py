import re, os

import requests

def onedrive_file_download(file_link):

    def get_redirected_url(url):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
        }

        response = requests.get(
        url,
        headers=headers,
        allow_redirects=True
        )
        return response.url

    def combine_url(url):
        long_id, cid, auth = re.findall(r'https://photos.onedrive.com/share/(.*?)\?cid=(.*?)&resId=.*?&authkey=(.*?)&', url)[0]
        return f'https://api.onedrive.com/v1.0/drives/{cid}/items/{long_id}/content?authkey={auth}'

    def get_video(new_url):
        headers = {
            'accept': '*/*',
            'accept-language': 'zh-TW,zh;q=0.9',
            'cache-control': 'no-cache',
            'origin': 'https://photos.onedrive.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://photos.onedrive.com/',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
        }
        response = requests.get(new_url, headers=headers, allow_redirects=True)
        with open('./My_Folder/output_.mp4', 'wb') as f:
            f.write(response.content)

    
    download_directory = "My_Folder"
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)
    url = get_redirected_url(file_link)
    get_video(combine_url(url))