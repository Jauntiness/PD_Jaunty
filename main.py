# main.py
import threading
import datetime as dt
import time
import schedule
import os
import requests

import plex
import settings
from settings import intervall, autostart, output_directory
import write_ignored
import plex_debrid_rclone_filter_updater
import check_for_changes
import rclone_mainmount
import RDErrortest
import deleter_rclone
import watching_check



version = "1.0"
users = settings.users
plex_library = plex.PlexLibrary(users)
runned_check = None

global x
x = None

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def welcome():
    global x
    global runned_check
    print("Welcome to PD_Jaunty. Version: "+version )
    print("")
    print("You can change your settings and add more users in the settings.py .")
    print("")
    print("What are we doing next?")
    print("1 PD_Jaunty automation:      Running PD_Jaunty automation for all users.")
    print("2 Ignore.txt creator:        Creating ignore.txt .")
    print("3 Error checker:             Checking links on Real Debrid for errors.")
    print("4 PD_Jautny Library-Cleanup :Cleans your library of all no longer needed files.")

    x = None  # Reset x to None before waiting for input

    if runned_check is None and autostart == True:
        # Create a thread to handle user input
        input_thread = threading.Thread(target=get_user_input)
        input_thread.daemon = True
        input_thread.start()

        # Wait for user input or timeout
        input_thread.join(timeout=60)

        if x is None and runned_check is None and autostart == True:
            clear_terminal()
            print("No input received for 60 seconds. Starting automation.")
            print("")
            print("")
            print("Start: Running automation.")
            print("")
            print("")
            automation()
        else:
            #get_user_input()
            clear_terminal()
            handle_user_choice()
    else:
        get_user_input()
        handle_user_choice()


def get_user_input():
    global x
    user_input = input()
    x = user_input

def handle_user_choice():
    if x == '1':
        clear_terminal()
        print("Start: PD_Jaunty automation.")
        print("")
        print("")
        automation()
    elif x == '2':
        clear_terminal()
        print("Start: creating ignore.txt .")
        print("")
        print("")
        if not output_directory or output_directory == []:
            print("No directory for the ignore.txt found.")
            print("Please check your user settings.")
            welcome()
        else:
            write_ignored.main()
    elif x == '3':
        clear_terminal()
        print("Start: Checking links on Real Debrid for errors.")
        print("")
        print("")
        RDErrortest.main()
    elif x == '4':
        clear_terminal()
        print("Start: Cleaning Debrid library of all no longer needed files.")
        print("")
        print("")
        deleter_rclone.main()
    else:
        clear_terminal()
        print("No choice I can recognize. Please choose one of the options from the list.")
        print("Starting again")
        print("")
        print("")
        welcome()

def start_printit_hello_thread():
    #time.sleep(3600)
    
    thread = threading.Thread(target=plex_debrid_rclone_filter_updater.printit_hello)
    thread.daemon = True  # Daemonize the thread to exit when the main program exits
    thread.start()




def check_user_tokens(users):
    if not users:
        print("No users configured. Exiting automation.")
        print("Please check your settings and adjust.")
        print("Starting menu...")
        welcome()  # Call the welcome() function to handle the exception
        return
    
    for user in users:
        username = user['username']
        user_token = user['token']
        max_retries = 3  # Set your desired maximum retry count
        retry_delay = 2  # Initial retry delay in seconds
        retries = 0
        #print(username)

        while retries < max_retries:
            url = f'https://metadata.provider.plex.tv/library/sections/watchlist/all?X-Plex-Container-Size=1&X-Plex-Token={user_token}'
            try:
                response = requests.get(url, timeout=24)  # Set an appropriate timeout value
                response.raise_for_status()  # Raise an exception if the response has an error status code
                break

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
                    print(f"Invalid Plex user token for user {username}: {user_token}")
                    print("Please check your user settings.")
                    print("Exiting automation.")
                    print("")
                    welcome()

            except Exception as e:
                print(f"Error processing user {username}: {e}")






# Create a dictionary to hold the watching_check threads for each user
watching_check_threads = {}


def separate_watching_check_threads(user):
    global watching_check_threads 
    #print(f"Starting separate watching threads for {user}")

    
    username = user['username']
        # Check if a thread is already running for this user
    if username not in watching_check_threads or not watching_check_threads[username]['thread'].is_alive():
        thread = threading.Thread(target=watching_check_thread, args=(user,))
        thread.daemon = True
        watching_check_threads[username] = {'thread': thread, 'watching_check_done': False}
        thread.start()
    else:
        #print(f"Thread already running for user {username}")
        return

    return watching_check_threads



def watching_check_thread(user):
    username = user['username']
    while True:
        result = watching_check.check_current_watching_sessions(user)
        roundi = 1
        #print(roundi)
        roundi += 1
        #print(result)
        if result:
            watching_check_threads[username]['watching_check_done'] = True
            #print("watching check threads is true now")
            write_ignored.main()
            plex_debrid_rclone_filter_updater.main(user)
            break
        else:
            watching_check_threads[username]['watching_check_done'] = False

        time.sleep(30)  # Adjust the sleep interval as needed



def process_user(user):


    if check_for_changes.check_for_added_titles(user, current_titles, previous_titles[user['username']]):
        separate_watching_check_threads(user)
        
        write_ignored.main()
        #plex_debrid_rclone_filter_updater.main(user)

    elif check_for_changes.check_for_removed_titles(user, current_titles, previous_titles[user['username']]):
        write_ignored.main()

    # Update previous titles
    previous_titles[user['username']] = set(current_titles)


def night_refresh(user):
    schedule.every().day.at("03:00").do(plex_debrid_rclone_filter_updater.hardupdatefilterlist, user=user)


def automation():
    global plex_library
    global users
    global runned_check
    global current_titles
    global previous_titles
    global watching_check_threads
    first_iteration = True
    runned_check = True

    previous_titles = {user['username']: set() for user in users}
    first_iteration = True  # Flag to track the first iteration
    # Call the check_user_tokens function to validate user tokens
    check_user_tokens(users)

    night_refresh_done = 0
  

    ## running a main mount, for being able to access all files
    print("Starting Rclone main-mount(s). ")
    rclone_mainmount.main()
    #time.sleep(3)
    print("")

    print("Running automation:")
    print("")

    start_printit_hello_thread()

    while True:

        if first_iteration:
            write_ignored.main()
            for user in users:
                # Schedule the hardupdatefilterlist task for this user
                #schedule.every().day.at("03:00").do(plex_debrid_rclone_filter_updater.hardupdatefilterlist(user))
                #night_refresh_threads = []
                #night_refresh_thread = threading.Thread(target=night_refresh, args=(user,))
                #night_refresh_thread.start()
                #night_refresh_threads.append(night_refresh_thread)
                current_titles = check_for_changes.fetch_watchlist_titles(plex_library, user)
                if current_titles is not None:
                    if check_for_changes.check_for_added_titles(user, current_titles, previous_titles[user['username']]):
                        #print("added titles procedure: ")
                        plex_debrid_rclone_filter_updater.main(user)
                    elif check_for_changes.check_for_removed_titles(user, current_titles, previous_titles[user['username']]):
                        #print("removed titles procedure")
                        plex_debrid_rclone_filter_updater.main(user)

                    # Update previous titles
                    previous_titles[user['username']] = set(current_titles)

            first_iteration = False  # Update the flag
        

        if dt.datetime.now().hour == 2 and night_refresh_done == 1:
            night_refresh_done = 0
        if dt.datetime.now().hour == 3 and night_refresh_done == 0:
            for user in users:
                plex_debrid_rclone_filter_updater.hardupdatefilterlist(user)
            night_refresh_done = 1

        else:
            for user in users:
                time.sleep(2)
                # Start separate watching_check threads for each user
                #watching_check_threads = separate_watching_check_threads(users)
                
                current_titles = check_for_changes.fetch_watchlist_titles(plex_library, user)
                if current_titles is not None:
                    
                    process_user(user)

        # Sleep for the specified interval before checking again
        sleep_time = max(intervall - (len(users) * 2), 1)
        time.sleep(sleep_time)


def main():
    global runned_check

    welcome()

    exit_event = threading.Event()

    print("In 10 seconds returning back to home.")
    time.sleep(10)
    print("")
    print("")
    runned_check = True
    global input_thread
    global thread
 
    

    main()
   



if __name__ == "__main__":
    main()
