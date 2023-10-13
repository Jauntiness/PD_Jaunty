#seettings.py

#!!! are essential settings

#!!!
### The users for which filtered folders will be created.
users = [
    {'username': 'User1', 'token': 'TokenNumber123'},
    {'username': 'User2-1080p', 'token': 'TokenNumber123'},
    {'username': 'User3', 'token': 'TokenNumber123'},
    {'username': 'User4', 'token': 'TokenNumber123'},
    {'username': 'User5', 'token': 'TokenNumber123'},
    # Add more users as needed
    # if you add 1080p to the username it will start rclone filtering out everything bigger than 1080p
    # find tokens by visiting by logging into plex.tv, then visit:
    # first https://plex.tv/devices and then https://plex.tv/devices.xml
]



### Essential Automation settings:
#!!!
##the time between the watchlist checks for changes. Standard intervall = 30 seconds.
intervall = 30
## If autostart = True the automation will start after 60 seconds if no selection was made.
autostart = False
#!!!
## Plex host settings, used for rescaning the plex library after changes
tokenhost="TokenHost Number"
BASEURLHOST="http://localhost:32400" #standard: http://localhost:32400

###rclone settings
#!!!
## Sources set up in rclone. These will be mounted with the created filters. Remember to add the : for the source.
sources = [
    {'source_name': 'your-remote', 'source': 'your-remote:'},       #{'source_name': 'your-remote', 'source': 'your-remote:'}
    #{'source_name': 'Google', 'source': 'google-remote:'},     #{'source_name': 'your-remote2', 'source': 'your-remote2:'}
    #{'source_name': 'your-remote3', 'source': 'your-remote3:'},     #{'source_name': 'your-remote3', 'source': 'your-remote3:'}
    #{'source_name': 'your-remote4', 'source': 'your-remote4:'},
    #{'source_name': 'your-remote5', 'source': 'your-remote5:'},
]
#!!!
## Destination for the user-filtered folders. It could be a driver letter or an existing folder. Please check the rclone FAQs for further information.
## In this example the following folder exists C:\User-Cloud\ . 
destination="C:\\User-Cloud\\"

#optional
## These titles will be added for all your users folders. You could add one movie and one show to prevent plex_debrid from stopping for emtpy folders.
dummy_file = [
    'dummy_file1', 'dummy_file2'#, 'dummy_file3', 'dummy_file3',   
    #'dummy_file4', 'dummy_file5', 'dummy_file6', 'dummy_file7',  
    #'dummy_file8', 'dummy_file9', 'dummy_fil10', 'dummy_file11',           

]




#optional
## available drive letters for the main mounts. If no main mount is wanted, leave blank. drive_letters = []
drive_letters = ['X:', 'Y:', 'Z:', "V:", "W:"]  # Available drive letters, which are not used by other drives or tools. Standard: ['X:', 'Y:', 'Z:', "V:", "W:"]


#optional
### Creation of ignore.txt Settings:

##The directiory for the ignored list. Should be the same as in plex_debrid.
##If no ignored list is wanted, leave blank. output_directory = []
output_directory = r'C:\Users\ClemS\OneDrive\Desktop\plex-addons-python\New plex Script All in One\plex_jaunty'

## Titles to manually add to the ignored list
## These titles wont be added again by plex_debrid if plex_debrid was set up correctly.
manually_ignored_titles = [
    "Show Title 1"        #"ManualTitle 1",
    #"ManualTitle 2",
    #"ManualTitle 3",
    # Add more titles as needed
]


#!!! 
## settings for the rclone startup command. If unsure, leave the standards.
dircachetime="--dir-cache-time" #standard dircachetime="--dir-cache-time"
dircachetimesetting="10s" #standard dircachetimesetting="10s"
vfscachemode="--vfs-cache-mode" #standard vfscachemode="--vfs-cache-mode"
vfscachemodesetting="full" #standard vfscachemodesetting="full"
buffersize="--buffer-size" #standard buffersize="--buffer-size"
buffersizesetting="0.25G" #standard buffersizesetting="0.25G"


#Optional
### RealDebrid error link checker Settings:
## Replace <apiToken> with your actual API token
api_token = "<apiToken>"