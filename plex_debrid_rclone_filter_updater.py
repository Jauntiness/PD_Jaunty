# plex_debrid_rclone_filter_updater.py
import os
import plex
import settings
from settings import sources, destination, dircachetime, dircachetimesetting, vfscachemode, vfscachemodesetting, buffersize, buffersizesetting, tokenhost, users, intervall
import schedule
import datetime
import threading, random
import time
import requests
import watching_check
result = None
def updatetimestamp():
    global timestamp
    timestamp = ('[' + str(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")) + '] ')

# Create a dictionary to hold subprocesses for each user
rclone_processes = {}  

def startrclone(user):
    global rclone_processes
    import subprocess
    username = user["username"]

    try:
        for source_info in sources:
            source_name = source_info['source_name']
            source = source_info['source']
            
            # Construct the destination path based on the username and source_name
            user_destination = f'C:\\User-Cloud\\{username}-{source_name}'
            
            command = (["rclone", "mount", source, user_destination, dircachetime, dircachetimesetting, vfscachemode, vfscachemodesetting, buffersize, buffersizesetting, "--ignore-case", "--filter-from", f"{username}-filter.txt"])
            
            result = subprocess.Popen(command, stderr=subprocess.DEVNULL)
            
            # Store the subprocess in the dictionary
            rclone_processes[f"{username}_{source_name}"] = result

    except Exception as e:
        print("Error rclone:", str(e))

def terminaterclone(username):
    global rclone_processes
    try:
        for source_info in sources:
            source_name = source_info['source_name']
            process_key = f"{username}_{source_name}"
            if process_key in rclone_processes:
                result = rclone_processes[process_key]
                result.terminate()
                result.wait()
                # Remove the subprocess from the dictionary
                del rclone_processes[process_key]
    except Exception as e:
        print(f"Error stopping rclone for user {username}: {e}")

## random messages which are populated per hour, to show the tool is still working.
random_messages = [
    "Still updating every {} seconds.",
    "I am still here, working as a donkey.",
    "Are you still checking in?",
    "Short update from me.",
    "When my son told me to stop impersonating a flamingo, I had to put my foot down.",
    "Random bullshit",
    "Just that you know the current time.",
    "Thanks for checking in on me.",
    "Bee Boo Bipp",
    "How are you?",
        "Why don't scientists trust atoms? Because they make up everything!",
    "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them.",
    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
    "Parallel lines have so much in common. It's a shame they'll never meet.",
    "Why did the scarecrow win an award? Because he was outstanding in his field.",
    "I used to play piano by ear, but now I use my hands.",
    "I'm writing a book on reverse psychology. Please don't buy it.",
    "I'm reading a book on anti-gravity. It's impossible to put down.",
    "I'm friends with all electricians. We have such great current connections.",
    "Why did the tomato turn red? Because it saw the salad dressing!",
    "How do you organize a space party? You planet!",
    "Why couldn't the bicycle stand up by itself? It was two tired.",
    "I'm on a seafood diet. I see food and I eat it.",
    "I couldn't figure out why my computer was so slow. Then I realized it couldn't run.",
    "I don't trust stairs because they're always up to something.",
    "What did one wall say to the other wall? 'I'll meet you at the corner!'",
    "How does a penguin build its house? Igloos it together!",
    "What do you call a bear with no teeth? A gummy bear!",
    "Why was the math book sad? It had too many problems.",
]

def printit_hello():
    time.sleep(1800)
    updatetimestamp()

    if random.random() < 0.75:
        random_message = "Still updating every {} seconds.".format(intervall)
    else:
        random_message = random.choice(random_messages)
    
    timestamp_message = "{}{}".format(timestamp, random_message)
    
    print(timestamp_message)
    threading.Timer(1800, printit_hello).start()

def updatefilterlistonlyunwatched(plex_library, user):
    try:
        username = user["username"]
        updatetimestamp()
        plex_library.collect_titles_and_rating_keys()
        unwatched_rclonefilter_user_lists = plex.create_unwatched_list_rclonefilter(plex_library)
        outputlist = unwatched_rclonefilter_user_lists
        
        # Open the file for writing
        with open(f"{username}-filter.txt", 'w') as f:
            # Iterate through the keys and values in the dictionary
            for key, value_list in outputlist.items():
                # Write the key (username) preceded by "#" and followed by a colon
                f.write(f"# {key}:\n")

        
                # Write each item in the list, one item per line
                for index, item in enumerate(value_list):
                    if index == 0:
                        f.write(f"# {item}\n")  # Add "#" only to the first item
                    else:
                        f.write(f"{item}\n")

        updatetimestamp()
        print(timestamp + "       : "+ f"{username}-filter.txt" + " updated and created.")
    except Exception as e:
        print(f"An error occurred while updating filter list for user {user['username']}: {str(e)}")


last_request_time = 0
def refresh_library():
    global last_request_time

    # Check if enough time has passed since the last request
    current_time = time.time()
    if current_time - last_request_time < (30 + scan_offset):
        updatetimestamp()
        print(timestamp + "       : Skipping Plex library refresh (recently refreshed).")
    else:
        last_request_time = current_time
        # Delay for 10 seconds
        time.sleep(scan_offset)
        # Refresh Plex library
        url = "http://localhost:32400/library/sections/all/refresh"
        token = tokenhost
        complete_url = f"{url}?X-Plex-Token={token}"
        response = requests.get(complete_url)

        if response.status_code == 200:
            updatetimestamp()
            print(timestamp + "       :" + " Plex library refresh request was successful.")
        else:
            updatetimestamp()
            print(timestamp + f" Failed to update Plex library. Status code: {response.status_code}")

        # Update the last request time


        

def updateprocess(plex_library, user):
    username = user["username"]
    #print(timestamp + "       : "+"Changes in watchlist detected, updating", f"{username}-filter.txt", "and restarting rclone")
    updatefilterlistonlyunwatched(plex_library, user)
    #watching_check.check_current_watching_sessions(user)
    terminaterclone(username)
    startrclone(user)
    updatetimestamp()
    print(timestamp + "       :"+" Rclone restarted for "+ f"{username}")

    # Create a thread for library refresh
    refresh_thread = threading.Thread(target=refresh_library)
    refresh_thread.start()





def hardupdatefilterlist(user):
    username = user["username"]
    plex_library = plex.PlexLibrary(users)
    updatetimestamp()
    print(timestamp, "Nightly hard-refresh of filterlist for User: ", username)
    print("This also removes watched movies and shows if not already happened.")
    try:
        updateprocess(plex_library, user)
    except Exception:
        print("Update process failed, repeating in 90 seconds.")
        time.sleep(90)
        hardupdatefilterlist(plex_library, user)
        


def run_user_operations(user):
    username = user["username"]
    updatetimestamp()
    print(timestamp, "Start : creation of ",f"{username}-filter.txt", " and run rclone.")
    # Create a PlexLibrary instance for the current user
    plex_library = plex.PlexLibrary([user])

    updateprocess(plex_library, user)
    print(timestamp+" End   : creation of ",f"{username}-filter.txt")
    #schedule.every().day.at("03:00").do(hardupdatefilterlist, user)



def main(user):

    # Create a list to hold the thread objects
    threads = []

    # Create and start a thread for each user
    
    thread = threading.Thread(target=run_user_operations, args=(user,))
    thread.start()
    threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
