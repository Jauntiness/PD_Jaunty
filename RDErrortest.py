# RDErrortest.py
import requests
import time
#import settings 
from settings import api_token
import threading
exit_event = threading.Event()

# Replace <apiToken> with your actual API token
#api_token = "<apiToken>"
headers = {"Authorization": f"Bearer {api_token}"}

error_code_25_responses = []
call_interval = 150  # in ms

# Step 1: Get the list of all torrents
torrents_url = "https://api.real-debrid.com/rest/1.0/torrents?limit=2500"

response = requests.get(torrents_url, headers=headers)
torrents = response.json()


def process_torrent(torrent, call_interval=50):
    try:
        unrestrict_responses = []
        links = torrent.get("links", [])
        
        for i in range(len(links)):
            # Step 2: Unrestrict each link and include id in the payload
            time.sleep(call_interval / 1000)
            unrestrict_url = "https://api.real-debrid.com/rest/1.0/unrestrict/link"
            payload = {"link": links[i]}
            response = requests.post(unrestrict_url, headers=headers, data=payload)
            unrestrict_data = response.json()
            if("error_code" in unrestrict_data and unrestrict_data["error_code"] in [34,36]):
                call_interval += 50
                print(f"Error code {unrestrict_data['error_code']}. Increasing call interval to {call_interval}ms and sleeping for 1 minute")
                time.sleep(60)
                i-=1
                continue
            unrestrict_responses.append(unrestrict_data)
        
        # Step 3: Fetch media info using the id from the payload for each unrestrict response
        media_info_responses = []
        media_info_url = f"https://api.real-debrid.com/rest/1.0/streaming/mediaInfos/{unrestrict_data['id']}"
        for i in range(len(unrestrict_responses)):
            response = requests.get(media_info_url, headers=headers)
            media_info = response.json()
            if("error_code" in media_info and media_info["error_code"] in [34,36]):
                call_interval += 50
                print(f"Error code {media_info['error_code']}. Increasing call interval to {call_interval}ms and sleeping for 1 minute")
                time.sleep(60)
                i-=1
                continue
            media_info_responses.append(media_info)
        
        return (media_info_responses, unrestrict_responses)
    except Exception as err:
        print(err)
        return ([], [])



def main():
    for torrent in torrents :
        result = process_torrent(torrent, call_interval)
        total_torrents_processed = 0

        media_info_responses = result[0]
        unrestricted_responses = result[1]

        # Check for error_code 25 responses in media info
        try:
            for i in range(len(media_info_responses)):
                media_info = media_info_responses[i]
                if "error_code" in media_info:
                    print(f"{unrestricted_responses[i].get('filename')} can't be streamed")
                    error_code_25_responses.append(f"[{unrestricted_responses[i].get('id')}] {unrestricted_responses[i].get('filename')}")
                    # Write the error_code 25 responses to a file
                    with open("result.txt", "a") as result_file:
                        result_file.write(f"[{unrestricted_responses[i].get('id')}] {unrestricted_responses[i].get('filename')} \n")
                else:
                    pass
                    #print(f"OK - {unrestricted_responses[i].get('filename')}")
        except Exception as err:
            print(err)

    print(error_code_25_responses)


if __name__ == "__main__":
    main()