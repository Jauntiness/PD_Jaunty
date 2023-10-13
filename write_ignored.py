# write_ignored.py
import os
import settings
from settings import users, manually_ignored_titles
import plex
from plex import PlexLibrary, create_only_watched_not_unwatched_all_users, create_ignored_watched_list, create_unwatched_list_rclonefilter

output_directory = settings.output_directory

# Create a PlexLibrary instance using user data
plex_library = plex.PlexLibrary(users)

#plex.main()

def updatetimestamp():
    global timestamp
    import datetime
    timestamp = ('[' + str(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")) + '] ')



def updatefilterlistonlywatched():
    
    updatetimestamp()
    print(timestamp+" Start : creation of ignore.txt")
    # 1. Collect titles and rating keys
    plex_library.collect_titles_and_rating_keys()


    only_watched_not_unwatched_all_users_lists = create_only_watched_not_unwatched_all_users(plex_library)


    only_watched_not_unwatched_all_users_lists.extend(manually_ignored_titles)
    
    #write ignored.txt
    filename = os.path.join(output_directory, f"ignored.txt")
    try:
        with open(filename, 'w') as f:
            f.write('\n'.join(only_watched_not_unwatched_all_users_lists))
        updatetimestamp()
        print(timestamp+"       : "+f"File '{filename}' created with {len(only_watched_not_unwatched_all_users_lists)} titles.")
        print(timestamp+" End   : creation of ignored.txt")
    except Exception as e:
        print(f"Error creating ignore.txt ! ")
        print("Please check your settings, especially the directiory for the ignored list.")
  
def main():
    #"""Updates the watchedlist.txt file with only watched items."""

    if not output_directory or output_directory == []:
        return
    else:
        updatefilterlistonlywatched()

if __name__ == '__main__':
  main()

