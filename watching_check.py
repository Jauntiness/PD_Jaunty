# watching_check

import time
import requests
import xml.etree.ElementTree as ET

import settings
from settings import tokenhost
users = settings.users



usernames_cache = {}  

def fetch_username(user_token):
    # Check if the result is already in the cache
    if user_token in usernames_cache:
        username, timestamp = usernames_cache[user_token]
        if time.time() - timestamp <= 3600:  # One-hour TTL
            return username

    max_retries = 3  # Set your desired maximum retry count
    retry_delay = 2  # Initial retry delay in seconds
    retries = 0

    while retries < max_retries:
        try:
            # Construct the URL for fetching user info
            url = f'https://plex.tv/api/v2/user?X-Plex-Token={user_token}'
            
            response = requests.get(url, timeout=24)
            response.raise_for_status()

            user_data = response.text

            # Extract the username from the XML
            username_start = user_data.find('username="') + len('username="')
            username_end = user_data.find('"', username_start)
            username = user_data[username_start:username_end]

            # Update the usernames_cache with the new username and timestamp
            usernames_cache[user_token] = (username, time.time())

            return username

        except requests.exceptions.RequestException as req_err:
            if max_retries - retries == 1:
                print(f"Request error while fetching username: {req_err}")
            retries += 1
            if retries < max_retries:
                if max_retries - retries == 1: 
                    print(f"Retrying for username in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 4  # Exponential backoff

    print(f"Maximum retries reached. Unable to fetch username.")
    return None




def check_current_watching_sessions(user):
    username = user['username']
    user_token = user['token']
    max_retries = 3  # Set your desired maximum retry count
    retry_delay_check = 2  
    retry_delay = 2 # Initial retry delay in seconds
    retries = 0
    checks = 0
    done = None

    username = fetch_username(user_token)

    while retries < max_retries:
        try:
            # Construct the URL for checking currently watching sessions
            url = f'http://localhost:32400/status/sessions/all?X-Plex-Token={tokenhost}'
            
            # Make a request to the Plex server
            response = requests.get(url, timeout=24)
            response.raise_for_status()
            #print(response.content)

            sessions_data = ET.fromstring(response.content)

            # Check if there are no currently watching sessions
            if len(sessions_data) == 0:
                #print("No currently watching sessions found.")
                return True
                break
            
            # Iterate through the <Video> elements to check for titles
            currently_watching_names = set()
            for video_elem in sessions_data.findall('.//Video'):
                

                # Extract the watching username from the <User> element
                user_elem = video_elem.find('.//User')
                watching_username = user_elem.get('title') if user_elem is not None else None
                currently_watching_names.add(watching_username)

         
            for name in currently_watching_names:
                

                if name == username:
                    # Continue processing for this title because the watching_username matches the user's username               
                    # User is currently watching, wait and retry
                    #print(f"User {username} is currently watching. Waiting for them to stop...")
                    time.sleep(retry_delay_check)
                    retry_delay_check = min(retry_delay_check * 2, 60)
                    checks += 1
                    if checks == 4:
                        print(f"User {user['username']} is currently watching on Plex. Waiting for them to stop, to not break their session...")
                        print("The library will latest be refreshed 90 seconds after the user stops watching")
                        

                else:
                    # The name is different, so set the 'done' flag and return
                    done = True
                    #print("done")
                    return True

            if done == True: #and done2 == True:
                #print("done2")
                return True

                #break
            
            # Debugging prints
            #print("End of loop iteration")
            #print(f"checks = {checks}")
            #print(f"retry_delay_check = {retry_delay_check}")

        except requests.exceptions.RequestException as req_err:
            retries += 1
            if max_retries - retries == 1:
                print(f"Request error for user {username}: {req_err}")
            
            if retries < max_retries:
                if max_retries - retries == 1:
                    print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            if retries == max_retries:
                print(f"Invalid Plex user settings for user {username}: {user_token}, or networking issues.")
                print("Please check your user settings and server.")
                print("Terminating User automation.")
            
        except Exception as e:
            print(f"Error processing user {username}: {e}")
    




def main():
    #plex.main()
    for user in users:
        check_current_watching_sessions(user)


if __name__ == "__main__":
    main()
