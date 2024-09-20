import re
import os
import requests
import gdown


def onedrive_folder_download(folder_link):

    def get_redirected_intro_url_for_onedrive_folder_download(headers, url):
        response = requests.get(url, headers=headers, allow_redirects=True)
        return response.url


    def get_authkey_and_ids_for_onedrive_folder_download(url):
        id_, resid_, authkey, cid = re.findall(
            r"https:\/\/onedrive.live.com\/\?id=(.*?)&resid=(.*?)&ithint=folder&authkey=(.*?)&cid=(.*)",
            url,
        )[0]
        return authkey, cid, id_


    def get_video_urls_for_onedrive_folder_download(headers, authkey, cid, id_):
        response = requests.get(
            f"https://api.onedrive.com/v1.0/drives/{cid}/items/{id_}/children?%24top=100&orderby=folder%2Cname&%24expand=thumbnails%2Clenses%2Ctags&select=*%2Cocr%2CwebDavUrl%2CsharepointIds%2CisRestricted%2CcommentSettings%2CspecialFolder%2CcontainingDrivePolicyScenarioViewpoint&ump=1&authKey={authkey}",
            headers=headers,
        )

        return [value["@content.downloadUrl"] for value in response.json()["value"]]



    # folder_link = "https://1drv.ms/f/s!AmJWwgacrnJNzQwBZgq9n6tA28X3?e=UbzLf6"
    individualfilelink_foronedrivefolder = []
    config = {
        "headers": {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        },
        "url": folder_link,
    }
    redir_url = get_redirected_intro_url_for_onedrive_folder_download(config["headers"], config["url"])
    
    print("\n")
    # print(get_video_urls_for_onedrive_folder_download(config["headers"], *get_authkey_and_ids_for_onedrive_folder_download(redir_url)))
    individualfilelink_foronedrivefolder = get_video_urls_for_onedrive_folder_download(config["headers"], *get_authkey_and_ids_for_onedrive_folder_download(redir_url))
    
    
    download_directory = "My_Folder"
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)
        
    for index,  link in enumerate(individualfilelink_foronedrivefolder):
        try :
            output_filename = f"file_{index}.mp4"
            output_path = os.path.join(download_directory, output_filename)
            gdown.download(link, output_path, quiet=False)
            print(f"Downloaded {output_filename}")
        except Exception as e:
            print(f"Error downloading {output_filename}: {e}")
        
    
    
    
   
    
