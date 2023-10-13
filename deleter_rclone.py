# deleter_rclone.py
import time
import subprocess
import settings
from settings import sources, dummy_file
import plex
import threading
import re
exit_event = threading.Event()


users = settings.users

plex_library = plex.PlexLibrary(users)

drytest = False
drytest2 = False

def start_rclone(command):
    return subprocess.Popen(command)

def terminate_rclone(process):
    process.terminate()

def format_title(title):
    # Step 1: Replace "." with "*"
    formatted_title = title.replace('.', '*')

    # Step 2: Add "+ *" in the beginning
    formatted_title = '+ *' + formatted_title

    # Step 3: Add "*." at the end
    formatted_title = formatted_title + '*'

    # Step 4: Remove spots with two or repetitive "*"
    formatted_title = formatted_title.replace('**', '*')

    return formatted_title

def format_title_keep(title):
    # Remove special characters and spaces, convert to lowercase
    formatted_title = re.sub(r'[^a-zA-Z0-9]+', '.', title).strip('.').lower()
    # Step 1: Replace "." with "*"
    formatted_title = formatted_title.replace('.', '*')
    # Step 1: Replace "." with "*"
    #formatted_title = title.replace(' ', '*')

    # Step 2: Add "- *" in the beginning
    formatted_title = '- *' + formatted_title

    # Step 3: Add "*." at the end
    formatted_title = formatted_title + '*'

    # Step 4: Remove spots with two or repetitive "*"
    formatted_title = formatted_title.replace('**', '*')

    return formatted_title

def create_delete_list(plex_library):
    plex_library.collect_titles_and_rating_keys()
    list_of_filter = plex.create_only_watched_not_unwatched_all_users(plex_library)
    formatted_list = [format_title(title) for title in list_of_filter]
    formatted_list_keep = [format_title_keep(title) for title in dummy_file]
    for title in formatted_list_keep:
        #title = format_title_keep(title)
        formatted_list.insert(0 , title)
    formatted_list.append('- *')
    return formatted_list

def main():
    global drytest, drytest2

    print("Welcome to your debrid cleaner.")
    print("You should start with a dry run to test your settings.")
    print("Important: This script is dangerous to your data - always use a dry run first.")
    print("")

    # Ask the user to choose a source
    def choose_source():
        global source  

        print("Available sources:")
        for index, source_info in enumerate(sources):
            print(f"{index + 1}. {source_info['source_name']}")
        print("")
        source_choice = input("Enter the number of the source you want to use: ")

        try:
            source_choice = int(source_choice)
            if 1 <= source_choice <= len(sources):
                source_info = sources[source_choice - 1]
                source = source_info['source']
                print("")
                print(f"You selected source: {source_info['source_name']}")
            else:
                print("Invalid source number.")
                choose_source()
        except ValueError:
            print("Invalid input. Please enter a number.")
            choose_source()
    choose_source()
    print("")

    print("Important: This script is dangerous to your data - always use a dry run first.")
    drytest = input("Do you want to use the dry run? y/n ")

    if drytest == "n":
        print("Your answer was no.")
        drytest2 = input("Do you want to start removing your files? y/n ")

        if drytest2 == "y":
            print("Your answer was yes.")
            print("Your files will be deleted in 30 seconds.")
            print("Please close this window if this was not intended or files could get lost forever.")
            for i in range(30, 0, -1):
                time.sleep(1)
                print(f"{i} seconds left")

            print("Starting.")
            
        else:
            print("Starting dry run.")
    else:
        print("Starting dry run.")

    deletelist = create_delete_list(plex_library)
    print("This is the list of items which will be deleted:")
    print("")
    print(deletelist)

    with open("deletefilter.txt", 'w') as f:
        f.write('\n'.join(deletelist))

    if drytest == "y":
        print("Run dry process")
        command = ["rclone", "--dry-run", "delete", source, "--ignore-case", "--filter-from", "deletefilter.txt"]
        startdeleterclone = start_rclone(command)
        time.sleep(5)
        print("The above files would be deleted.")

    elif drytest2 == "n":
        print("Run dry process")
        command = ["rclone", "--dry-run", "delete", source, "--ignore-case", "--filter-from", "deletefilter.txt"]
        startdeleterclone = start_rclone(command)
        time.sleep(5)
        print("The above files would be deleted.")

    elif drytest2 == "y":
        time.sleep(3)
        print("Running deletion five times to delete possible remnants.")
        for i in range(1, 6):
            print(f"{i}")
            command = ["rclone", "delete", source, "--ignore-case", "--filter-from", "deletefilter.txt"]
            startdeleterclone = start_rclone(command)
            time.sleep(3)
    else:
        print("Incorrect input detected")
        main()

    if drytest2 == "y":
        print("I will start another dry run so you can check if there are still files that need to be deleted.")
        time.sleep(3)
        command = ["rclone", "--dry-run", "delete", source, "--ignore-case", "--filter-from", "deletefilter.txt"]
        startdeleterclone = start_rclone(command)
        time.sleep(5)
        print("If you see any file logs above, you will need to restart the deletion.")

if __name__ == "__main__":
    main()
    if drytest == "y" or drytest2 == "n":
        print("The above files would be deleted.")
    elif drytest2 == "y":
        print("If you see any file logs above, you will need to restart the deletion.")
    exit_event.set()

