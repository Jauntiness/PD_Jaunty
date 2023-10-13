# check_for_changes.py
import os
import time
import requests
import xml.etree.ElementTree as ET
import settings
from settings import intervall
users = settings.users
import plex

plex_library = plex.PlexLibrary(users)

def updatetimestamp():
    global timestamp
    import datetime
    timestamp = ('[' + str(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")) + '] ')


def check_for_added_titles(user, current_titles, previous_titles):
    added_titles = [title for title in current_titles if title not in previous_titles]
    if added_titles:
        print(f"New titles added for user {user['username']}: {', '.join(added_titles)}")
        # Call your processing function here
        return True
    return False

def check_for_removed_titles(user, current_titles, previous_titles):
    removed_titles = [title for title in previous_titles if title not in current_titles]
    if removed_titles:
        print(f"Titles removed for user {user['username']}: {', '.join(removed_titles)}")
        # Call your processing function here
        return True
    return False

        

def fetch_watchlist_titles(plex_library, user):
    username = user['username']
    user_token = user['token']
    max_retries = 3  # Set your desired maximum retry count
    retry_delay = 2  # Initial retry delay in seconds
    titles = {}

    try:
        
        added = 0
        retries = 0

        while retries < max_retries:
            url = f'https://metadata.provider.plex.tv/library/sections/watchlist/all?X-Plex-Container-Size=200&X-Plex-Container-Start={added}&X-Plex-Token={user_token}'
            try:
                response = requests.get(url, timeout=24)  
                # Check the status code and raise an exception if it's an error
                if response.status_code != 200:
                    raise Exception(f"HTTP error {response.status_code}: {response.text}")
                data = ET.fromstring(response.content)

                # Extract titles from Video elements
                for video in data.findall('.//Video'):
                    title = video.get('title')
                    rating_key = video.get('ratingKey')
                    titles[title] = rating_key

                # Extract titles from Directory elements
                for directory in data.findall('.//Directory'):
                    title = directory.get('title')
                    rating_key = directory.get('ratingKey')
                    titles[title] = rating_key

                added += 200
                total_size = int(data.get('totalSize'))
                if added >= total_size:
                    break
            except requests.exceptions.RequestException as req_err:
                if max_retries - retries == 1:
                    print(f"Request error for user {username}: {req_err}")
                retries += 1
                if retries < max_retries:
                    if max_retries - retries == 1:
                        print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 4  # Exponential backoff
            except Exception as e:
                print(f"Error processing user {username}: {e}")

        return titles
    except Exception as e:
        print(e)
        print(f"Skipping user {username} due to an invalid token.")
        return None
  
def main():
    global plex_library
    global users

    previous_titles = {user['username']: set() for user in users}

    while True:
        for user in users:
            current_titles = fetch_watchlist_titles(plex_library, user)
            if current_titles is not None:
                if check_for_added_titles(user, current_titles, previous_titles[user['username']]):
                    pass  
                elif check_for_removed_titles(user, current_titles, previous_titles[user['username']]):
                    pass  

                # Update previous titles
                previous_titles[user['username']] = set(current_titles)

        # Sleep for the specified interval before checking again
        time.sleep(intervall)
if __name__ == '__main__':
  main()

