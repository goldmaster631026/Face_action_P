
import re
import os
import requests

def sharepoint_folder_download(folder_link):
    def get_redirected_url_and_cookies(url):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
        }

        response = requests.get(
        url,
        headers=headers,
        allow_redirects=True
        )
        digest_value = re.findall(r'"formDigestValue":"(.*?)",', response.text)[0]
        id_ = re.findall(r'id=(.*?)%2FDir', response.url)[0]
        return response.url, {'FedAuth': response.cookies['FedAuth']}, digest_value, id_


    def get_video_list(url, cookies, digest_value, id_):
        headers = {
            'authorization': 'Bearer',
            'collectspperfmetrics': 'SPSQLQueryCount',
            'content-type': 'application/json;odata=verbose',
            'referer': url,
            'scenariotype': 'AUO',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
            'x-clientservice-clienttag': 'ODB Web',
            'x-ms-cc': 't',
            'x-requestdigest': digest_value,
            'x-serviceworker-strategy': 'CacheFirst',
            'x-sp-requestresources': f'listUrl={id_}',
        }

        json_data = {
            'parameters': {
                '__metadata': {
                    'type': 'SP.RenderListDataParameters',
                },
                'RenderOptions': 5445383,
                'AllowMultipleValueFilterForTaxonomyFields': True,
                'AddRequiredFields': True,
                'RequireFolderColoringFields': True,
            },
        }
        cookies.update({'FeatureOverrides_experiments': '[]'})
        route = re.findall(r'id=(.*)', url)[0].replace('ga=1', '')
        pid = re.findall(r'personal%2F(.*?)%2F', route)[0]
        response = requests.post(
            f"https://idinnovsas-my.sharepoint.com/personal/{pid}/_api/web/GetListUsingPath(DecodedUrl=@a1)/RenderListDataAsStream?@a1='/personal/{pid}/Documents'&RootFolder={route}&TryNewExperienceSingle=TRUE",
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
        return response.json()


    def get_video(url, cookies):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-TW,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'service-worker-navigation-preload': '{"supportsFeatures":[]}',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
        }

        response = requests.get(
            url,
            cookies=cookies,
            headers=headers,
        )
        directory = "My_Folder"
        file_path = os.path.join(directory , f"{url.split('/')[-1]}.mp4")
        with open(file_path, 'wb') as f:
            f.write(response.content)

    
    from urllib.parse import urljoin
    download_directory = "My_Folder"
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)
    url = folder_link
    config = {
        'personal_id': re.findall(r'/personal/(.*?)/', url)[0],
    }
    base = 'https://idinnovsas-my.sharepoint.com/'
    info = get_redirected_url_and_cookies(url)
    rows = get_video_list(*info)['ListData']['Row']
    print(info[1])
    for row in rows:
        print(urljoin(base, row['FileRef']))
        get_video(urljoin(base, row['FileRef']), info[1])
