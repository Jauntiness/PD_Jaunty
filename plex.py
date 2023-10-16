# plex.py
import re
import requests
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
import threading
import settings
from settings import dummy_file
intervall = settings.intervall-1
import datetime
import time



users = settings.users

# Constants
MAX_THREADS = 10

import re

def updatetimestamp():
    global timestamp

    timestamp = ('[' + str(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")) + '] ')





def clean_name(name):
    # Remove special characters and spaces, convert to lowercase
    cleaned_name = re.sub(r'[^a-zA-Z0-9]+', '.', name).strip('.').lower()
    # Remove year numbers at the end (if they exist)
    cleaned_name = re.sub(r'(?:^|\D)(21|20|19)\d{2}(?!\d)', '', cleaned_name)
    # Remove trailing dots
    cleaned_name = cleaned_name.rstrip('.')
    # Adjust season numbers to 's01', 's02', etc.
    cleaned_name = re.sub(r'season\.(\d+)', lambda x: f"s{x.group(1).zfill(2)}.", cleaned_name)
    cleaned_name = re.sub(r'series\.(\d+)', lambda x: f"s{x.group(1).zfill(2)}.", cleaned_name)
    return cleaned_name

def clean_name_with_year(name):
    # Remove special characters and spaces, convert to lowercase
    cleaned_name = re.sub(r'[^a-zA-Z0-9]+', '.', name).strip('.').lower()
    # Remove year numbers at the end (if they exist)
    #cleaned_name = re.sub(r'(?:^|\D)(21|20|19)\d{2}(?!\d)', '', cleaned_name)
    # Remove trailing dots
    cleaned_name = cleaned_name.rstrip('.')
    # Adjust season numbers to 's01', 's02', etc.
    cleaned_name = re.sub(r'season\.(\d+)', lambda x: f"s{x.group(1).zfill(2)}.", cleaned_name)
    cleaned_name = re.sub(r'series\.(\d+)', lambda x: f"s{x.group(1).zfill(2)}.", cleaned_name)
    return cleaned_name

def clean_name_rclonefilter(name):
    #cleaned_name = clean_name(name)
    # Remove special characters and spaces, convert to lowercase
    cleaned_name = re.sub(r'[^a-zA-Z0-9]+', '.', name).strip('.').lower()
    # Remove year numbers at the end (if they exist)
    #cleaned_name = re.sub(r'(?:^|\D)(21|20|19)\d{2}(?!\d)', '', cleaned_name)
    # Remove trailing dots
    cleaned_name = cleaned_name.rstrip('.')
    # Adjust season numbers to 's01', 's02', etc.
    cleaned_name = re.sub(r'season\.(\d+)', lambda x: f"s{x.group(1).zfill(2)}.", cleaned_name)
    cleaned_name = re.sub(r'series\.(\d+)', lambda x: f"s{x.group(1).zfill(2)}.", cleaned_name)

    # Split the cleaned_name into terms and add '+ *' before and '*' after each term
    cleaned_name = '+ *' + '*'.join(cleaned_name.split('.')) + '*'
    # Replace multiple consecutive '*' with a single '*'
    cleaned_name = re.sub(r'\*+', '*', cleaned_name)
    return cleaned_name

def clean_name_rclonefilter_year(name):
    #cleaned_name = clean_name(name)
    # Remove special characters and spaces, convert to lowercase
    cleaned_name = re.sub(r'[^a-zA-Z0-9]+', '.', name).strip('.').lower()
    # Remove year numbers at the end (if they exist)
    cleaned_name = re.sub(r'(?:^|\D)(21|20|19)\d{2}(?!\d)', '', cleaned_name)
    # Remove trailing dots
    cleaned_name = cleaned_name.rstrip('.')
    # Adjust season numbers to 's01', 's02', etc.
    cleaned_name = re.sub(r'season\.(\d+)', lambda x: f"s{x.group(1).zfill(2)}.", cleaned_name)
    cleaned_name = re.sub(r'series\.(\d+)', lambda x: f"s{x.group(1).zfill(2)}.", cleaned_name)

    # Remove the word 'season' from cleaned_name
    cleaned_name = cleaned_name.replace('season', '')

    # Split the cleaned_name into terms and add '+ *' before and '*' after each term
    cleaned_name = '+ *' + '*'.join(cleaned_name.split('.')) + '*'
    # Replace multiple consecutive '*' with a single '*'
    cleaned_name = re.sub(r'\*+', '*', cleaned_name)
    return cleaned_name

def clean_name_check_current_watching(name):
    # Remove "season" or "series" and everything that follows them using regular expressions
    name = re.sub(r'\b(season|series)\b.*$', '', name, flags=re.IGNORECASE)
    return name.strip()  # Remove leading/trailing spaces and return the cleaned name



class PlexLibrary:
    def __init__(self, users):
        self.users = users
        self.title_rating_pairs = []  
        self.lock = threading.Lock()  # Add a lock
        self.metadata_cache1 = {}  # Caches to store metadata information
        self.metadata_cache2 = {}
        self.metadata_cache3 = {}


    def get_user_token(self, username):
        for user in self.users:
            if user['username'] == username:
                return user['token']
        return None

    


    #def fetch_metadata(self, rating_key, user_token):
    #    url = f'https://metadata.provider.plex.tv/library/metadata/{rating_key}?includeUserState=1&X-Plex-Token={user_token}'
    #    response = requests.get(url)
    #    response_content = response.content.decode('utf-8')  # Decode bytes to string
    #    return response_content

    #def fetch_season_metadata(self, rating_key, user_token):
    #    url = f'https://metadata.provider.plex.tv/library/metadata/{rating_key}/children?includeUserState=1&X-Plex-Container-Size=200&X-Plex-Container-Start=0&X-Plex-Token={user_token}'
    #    response = requests.get(url)
    #    response_content = response.content.decode('utf-8')  # Decode bytes to string
    #    return response_content

    def fetch_metadata(self, rating_key, user_token):
        max_retries = 3  # Set your desired maximum retry count
        retry_delay = 2  # Initial retry delay in seconds
        retries = 0
        while retries < max_retries:
            try:
                if rating_key in self.metadata_cache1:
                    metadata, timestamp = self.metadata_cache1[rating_key]
                    if time.time() - timestamp <= 60:
                        return metadata

                url = f'https://metadata.provider.plex.tv/library/metadata/{rating_key}?includeUserState=1&X-Plex-Token={user_token}'
                response = requests.get(url, timeout=24)

                if response.status_code != 200:
                    raise Exception(f"HTTP error {response.status_code}: {response.text}")

                response_content = response.content.decode('utf-8')  # Decode bytes to string

                # Update the cache with the new metadata and timestamp
                self.metadata_cache1[rating_key] = (response_content, time.time())

                return response_content
            except requests.exceptions.RequestException as req_err:
                if max_retries - retries == 1:
                    print(f"Request error: {req_err}")
                retries += 1
                if retries < max_retries:
                    if max_retries - retries == 1: 
                        print(f"Retrying for rating_key: {rating_key} in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 4  # Exponential backoff
            except Exception as e:
                print(f"Error fetching metadata: {e}")
                return None

        print(f"Maximum retries reached. Unable to fetch metadata for rating_key: {rating_key}")
        return None

    def fetch_season_metadata(self, rating_key, user_token):
        max_retries = 3  # Set your desired maximum retry count
        retry_delay = 2  # Initial retry delay in seconds
        retries = 0

        while retries < max_retries:
            try:
                if rating_key in self.metadata_cache2:
                    metadata, timestamp = self.metadata_cache2[rating_key]
                    if time.time() - timestamp <= 60:
                        return metadata

                url = f'https://metadata.provider.plex.tv/library/metadata/{rating_key}/children?includeUserState=1&X-Plex-Container-Size=200&X-Plex-Container-Start=0&X-Plex-Token={user_token}'
                response = requests.get(url, timeout=24)

                if response.status_code != 200:
                    raise Exception(f"HTTP error {response.status_code}: {response.text}")

                response_content = response.content.decode('utf-8')  # Decode bytes to string

                # Update the cache with the new metadata and timestamp
                self.metadata_cache2[rating_key] = (response_content, time.time())

                return response_content
            except requests.exceptions.RequestException as req_err:
                if max_retries - retries == 1:
                    print(f"Request error: {req_err}")
                retries += 1
                if retries < max_retries:
                    if max_retries - retries == 1:
                        print(f"Retrying for rating_key: {rating_key} in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 4  # Exponential backoff
            except Exception as e:
                print(f"Error fetching season metadata: {e}")
                return None

        print(f"Maximum retries reached. Unable to fetch season metadata for rating_key: {rating_key}")
        return None



    def check_title(self, username_to_check, title, rating_key, user_token, watched_movies, unwatched_movies, watched_shows, unwatched_shows, watched_shows_seasons, unwatched_shows_seasons):
        try:
            movie_data = None
            
            # Check if it's a movie
            movie_metadata = self.fetch_metadata(rating_key, user_token) 
            movie_data = ET.fromstring(movie_metadata)

            is_movie = False
            is_show = False

            if movie_data.find('.//Video') is not None:
                is_movie = True

            if movie_data.find('.//Directory') is not None:
                is_show = True

            if is_movie:
                #view_count = int(movie_data.get('viewCount', 0))
                video_element = movie_data.find('.//Video')
                if video_element is not None:
                    view_count = int(video_element.get('viewCount', 0))
                    if view_count == 0:
                        unwatched_movies.append(title)
                    else:
                        watched_movies.append(title)

            if is_show:
                # Fetch season data for shows
                season_metadata = self.fetch_season_metadata(rating_key, user_token)  
                #print("Season Metadata:")
                #print(season_metadata)  # Debugging: Print the season metadata XML

                season_data = ET.fromstring(season_metadata)
                #print("Season Data:")
                #print(ET.tostring(season_data, encoding='utf8').decode('utf8'))  # Debugging: Print the season data XML


                seasons = season_data.findall('.//Directory[@type="season"]')
                seasons = season_data.findall('.//Directory[@type="season"]')
                #print("Seasons:")
                #print(seasons)  
                

                if seasons:
                    # Check if there are any seasons with the title "Specials" or "Season 0"
                    is_specials = any(season.get('title', '') == 'Specials' for season in seasons)
                    is_season_0 = any(season.get('title', '') == 'Season 0' for season in seasons)
                    is_miniseries = any(season.get('title', '') == 'Miniseries' for season in seasons)

                    if not is_specials and not is_season_0 and not is_miniseries:
                        # Process regular seasons
                        all_seasons_watched = all(int(season.get('viewedLeafCount', 0)) >= int(season.get('leafCount', 0)) for season in seasons)
                        all_seasons_unwatched = all(int(season.get('viewedLeafCount', 0)) == 0 for season in seasons)
                        #print("Title is show: ")
                        #print(title)

                        if all_seasons_watched:
                            watched_shows.append(title)
                        elif all_seasons_unwatched:
                            unwatched_shows.append(title)
                        else:
                            for season in seasons:
                                season_title = season.get('title')
                                leaf_count = int(season.get('leafCount', 0))
                                viewed_leaf_count = int(season.get('viewedLeafCount', 0))

                                if viewed_leaf_count >= leaf_count:
                                    watched_shows_seasons.append(f"{title}.{season_title}")
                                else:
                                    unwatched_shows_seasons.append(f"{title}.{season_title}")
                    else:
                        # Handle shows with "Specials" and "Season 0" separately
                        if all(int(season.get('viewedLeafCount', 0)) >= int(season.get('leafCount', 0)) for season in seasons if season.get('title', '') not in ('Specials', 'Season 0')):
                            watched_shows.append(title)
                        elif all(int(season.get('viewedLeafCount', 0)) == 0 for season in seasons if season.get('title', '') not in ('Specials', 'Season 0')):
                            unwatched_shows.append(title)
                        else:
                            for season in seasons:
                                if season.get('title', '') not in ('Specials', 'Season 0'):
                                    season_title = season.get('title')
                                    leaf_count = int(season.get('leafCount', 0))
                                    viewed_leaf_count = int(season.get('viewedLeafCount', 0))

                                    if viewed_leaf_count >= leaf_count:
                                        watched_shows_seasons.append(f"{title}.{season_title}")
                                    else:
                                        unwatched_shows_seasons.append(f"{title}.{season_title}")

        except Exception as e:
            print(f"Error processing title '{title}' for user '{username_to_check,}' with token: {user_token}")
            print(f"Error details: {e}")
            print("Holding process for 2 seconds")
            time.sleep(2)
            if movie_data is not None:
                print(f"Partial data for title: {movie_data}")


    def is_movie(self, metadata):
        return metadata.find('.//Video') is not None

    def is_show(self, metadata):
        return metadata.find('.//Directory') is not None

    def collect_titles_and_rating_keys(self):
        for user in self.users:
            username = user['username']
            user_token = user['token']
            max_retries = 3  # Set your desired maximum retry count
            retry_delay = 2  # Initial retry delay in seconds

            try:
                added = 0
                retries = 0

                while retries < max_retries:
                    url = f'https://metadata.provider.plex.tv/library/sections/watchlist/all?X-Plex-Container-Size=200&X-Plex-Container-Start={added}&X-Plex-Token={user_token}'
                    try:
                        # Create a cache key based on the URL, user_token, and added
                        cache_key = f"{username}:{added}:{user_token}"
                        
                        # Check if the data is already in the cache and not expired
                        if cache_key in self.metadata_cache3 and time.time() - self.metadata_cache3[cache_key]['timestamp'] <= intervall:
                            data = ET.fromstring(self.metadata_cache3[cache_key]['content'])
                        else:
                            response = requests.get(url, timeout=24)  
                            response.raise_for_status()  # Raise an exception if the response has an error status code
                            data = ET.fromstring(response.content)
                            
                            # Update the cache with the new data and timestamp
                            self.metadata_cache3[cache_key] = {
                                'content': response.content,
                                'timestamp': time.time()
                            }
                            
                        self.extract_titles_and_rating_keys(data, user_token)
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
            except Exception as e:
                print(e)
                print(f"Skipping user {username} due to networking errors or an invalid token.")



    def extract_titles_and_rating_keys(self, data, user_token):
        for video in data.findall('.//Video'):
            title = video.get('title')
            rating_key = video.get('ratingKey')
            self.title_rating_pairs.append((title, rating_key, user_token))
        for directory in data.findall('.//Directory'):
            title = directory.get('title')
            rating_key = directory.get('ratingKey')
            self.title_rating_pairs.append((title, rating_key, user_token))

    
    def check_watched_parallel_for_user(self, username_to_check):
        watched_movies = []
        watched_shows = []
        unwatched_movies = []
        unwatched_shows = []
        watched_shows_seasons = []
        unwatched_shows_seasons = []

        max_threads = MAX_THREADS
        with ThreadPoolExecutor(max_threads) as executor:
            for title, rating_key, user_token in self.title_rating_pairs:
                if user_token == self.get_user_token(username_to_check):
                    executor.submit(
                        self.check_title, username_to_check,
                        title, rating_key, user_token,
                        watched_movies, unwatched_movies, watched_shows, unwatched_shows, watched_shows_seasons, unwatched_shows_seasons
                    )
            #print(unwatched_movies)
        return watched_movies, unwatched_movies, watched_shows, unwatched_shows, watched_shows_seasons, unwatched_shows_seasons
    
    def update_watched_lists(self):
        (
            
            self.watched_movies,
            self.unwatched_movies,
            self.watched_shows,
            self.unwatched_shows,
            self.watched_shows_seasons,
            self.unwatched_shows_seasons
        ) = self.check_watched_parallel_all()

def print_different_watchlists(plex_library):
    for user in plex_library.users:
        username = user['username']
        print(f"User: {username}")
        (
            watched_movies,
            unwatched_movies,
            watched_shows,
            unwatched_shows,
            watched_shows_seasons,
            unwatched_shows_seasons
        ) = plex_library.check_watched_parallel_for_user(username)

        print("Watched Movies:")
        print(watched_movies)

        print("\nUnwatched Movies:")
        print(unwatched_movies)

        print("\nWatched Shows:")
        print(watched_shows)

        print("\nUnwatched Shows:")
        print(unwatched_shows)

        print("\nWatched Shows (Seasons):")
        print(watched_shows_seasons)

        print("\nUnwatched Shows (Seasons):")
        print(unwatched_shows_seasons)

        print("\n" + "=" * 30 + "\n")



def create_list_for_users(plex_library, usernames, list_type):
    user_lists = {}  # Create a dictionary to store lists for each user
    for username_to_display in usernames:
        user_token = plex_library.get_user_token(username_to_display)

        if user_token:
            watched_movies, unwatched_movies, watched_shows, unwatched_shows, watched_shows_seasons, unwatched_shows_seasons = plex_library.check_watched_parallel_for_user(username_to_display)

            if list_type == 'ignorefile':
                user_list = [
                    clean_name(name) for name in watched_movies + watched_shows + watched_shows_seasons
                ]
            elif list_type == 'rclonefilter':
                movie_years = get_movie_years(unwatched_movies, user_token, plex_library)
                #print(unwatched_movies)
                #print(movie_years)
                updatetimestamp()

                if "1080p" in username_to_display:
                    user_list = [timestamp] + ["- *2160*"] + ["- *HDR*"] + ["- *4k*"] + [
                        clean_name_rclonefilter(f"{name} {year}") if name in unwatched_movies else clean_name_rclonefilter(name) 
                        for name, year in zip(unwatched_movies, movie_years)
                    ] + [clean_name_rclonefilter_year(name) for name in unwatched_shows + unwatched_shows_seasons] + [
                        * [clean_name_rclonefilter(name) for name in dummy_file],
                            "#filter out the rest", "- *"
                        ]
                else:
                    user_list = [timestamp] + [
                        clean_name_rclonefilter(f"{name} {year}") if name in unwatched_movies else clean_name_rclonefilter(name) 
                        for name, year in zip(unwatched_movies, movie_years)
                    ] + [clean_name_rclonefilter_year(name) for name in unwatched_shows + unwatched_shows_seasons] + [
                        * [clean_name_rclonefilter(name) for name in dummy_file],
                            "#filter out the rest", "- *"
                        ]
            elif list_type == "check_current_watching":
                user_list = [clean_name_check_current_watching(name) for name in unwatched_movies + unwatched_shows]
            user_lists[username_to_display] = user_list

        else:
            print(f"User '{username_to_display}' not found in the list of users.")
    return user_lists

def get_movie_years(movie_titles, user_token, plex_library):
    movie_years = []
    
    for title in movie_titles:
        found_match = False  # Flag to track if a match has been found
        
        for _, rating_key, _ in plex_library.title_rating_pairs:
            metadata = plex_library.fetch_metadata(rating_key, user_token)
            metadata_tree = ET.fromstring(metadata)

            for video in metadata_tree.findall('.//Video'):
                title_match = video.get('title')
                if title.lower() == title_match.lower():
                    year_match = video.get('year')
                    movie_years.append(year_match)
                    found_match = True  # Set the flag to True to indicate a match
                    break  # Exit the inner loop once a match is found
            
            if found_match:
                break  # Exit the outer loop if a match was found
        else:
            # If no match is found, add an empty string
            movie_years.append('')
            break

    return movie_years



def create_ignored_watched_list(plex_library, usernames=None):
    if usernames is None:
        usernames = [user['username'] for user in plex_library.users]
    return create_list_for_users(plex_library, usernames, 'ignorefile')
    

def create_unwatched_list_rclonefilter(plex_library, usernames=None):
    if usernames is None:
        usernames = [user['username'] for user in plex_library.users]
    return create_list_for_users(plex_library, usernames, 'rclonefilter')

def create_only_watched_not_unwatched_all_users(plex_library):
    watchedlist = set()  # Use a set to store unique titles
    unwatchedlist = set()

    for user in plex_library.users:
        username = user['username']
        (
            watched_movies,
            unwatched_movies,
            watched_shows,
            unwatched_shows,
            watched_shows_seasons,
            unwatched_shows_seasons
        ) = plex_library.check_watched_parallel_for_user(username)



        


        #print(unwatched_movies)
        user_token = plex_library.get_user_token(username)
        watched_movies_years = get_movie_years(watched_movies, user_token, plex_library)
        watched_movies = [
                f'{title} {year}' for title, year in zip(watched_movies, watched_movies_years)
            ]
        unwatched_movies_years = get_movie_years(unwatched_movies, user_token, plex_library)
        unwatched_movies = [
                f'{title} {year}' for title, year in zip(unwatched_movies, unwatched_movies_years)
            ]
        
        watched_movies = [clean_name_with_year(name) for name in watched_movies]
        unwatched_movies = [clean_name_with_year(name) for name in unwatched_movies]
        watched_shows = [clean_name(name) for name in watched_shows]
        unwatched_shows = [clean_name(name) for name in unwatched_shows]
        watched_shows_seasons = [clean_name(name) for name in watched_shows_seasons]
        unwatched_shows_seasons  = [clean_name(name) for name in unwatched_shows_seasons]

        
        watchedlist.update(watched_movies + watched_shows + watched_shows_seasons)
        unwatchedlist.update(unwatched_movies + unwatched_shows + unwatched_shows_seasons)


    
    # Create a set of titles that are only in the watchedlist (subtract unwatchedlist)
    only_watched_not_unwatched_all_users = watchedlist - unwatchedlist
    print(only_watched_not_unwatched_all_users)


    
    

    # Clean the names using clean_name() and convert to a list
    #cleaned_only_watched_not_unwatched_all_users = [clean_name(name) for name in only_watched_not_unwatched_all_users]

    # Sort the cleaned titles alphabetically
    #cleaned_only_watched_not_unwatched_all_users.sort()

    #return cleaned_only_watched_not_unwatched_all_users
    return only_watched_not_unwatched_all_users


def print_user_lists(user_lists):
    for username, user_list in user_lists.items():
        print(f"User: {username}")
        print("List:")
        for item in user_list:
            print(item)
        print("\n" + "=" * 30 + "\n")


def main():
    #users = users.users

    plex_library = PlexLibrary(users)

    # Collect titles and rating keys
    plex_library.collect_titles_and_rating_keys()
    
    #create_only_watched_not_unwatched_all_users(plex_library)

    ### Functions:
    #print_different_watchlists(plex_library)

    ## create the user lists using create_ignored_watched_list function [can also be used without specifing usernames, then all users are used]
    #ignored_watched_user_lists = create_ignored_watched_list(plex_library, usernames=['Pikachu', 'Demo_Halle'])
    #unwatched_rclonefilter_user_lists = create_unwatched_list_rclonefilter(plex_library, usernames=['Pikachu', 'Demo_Halle'])
    #unwatched_rclonefilter_user_lists = create_unwatched_list_rclonefilter(plex_library)

    ## Then, print the user lists using the print_user_lists function
    #print_user_lists(ignored_watched_user_lists)
    #print_user_lists(unwatched_rclonefilter_user_lists)



if __name__ == "__main__":
    main()
