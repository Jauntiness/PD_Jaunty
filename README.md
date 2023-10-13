# PD_Jaunty
*Tested on Windows only*

PD_Jaunty is an add-on for the excellent plex_debrid tool by iTsToggle:
[GitHub Repository](https://github.com/itsToggle/plex_debrid)

## Overview
PD_Jaunty allows you to create separate libraries for each of your Plex users, filtering only the content they have added to their watchlists and have not yet watched. This can be achieved without the need for a Plex Pass.

## How It Works
1. **Prerequisites**
   - Start by downloading the latest rclone-fork release by iTsToggle and placing it in the same folder as PD_Jaunty:
     [rclone_RD GitHub Repository](https://github.com/itsToggle/rclone_RD#windows)
   - Modify the `settings.py` file to configure your users, sources, and other settings. Additionally, install the required dependencies listed in `requirements.txt`.

2. **PD_Jaunty Automation**
   - PD_Jaunty will gather all the titles from your users' Plex watchlists.
   - It will then check which movies, shows, or seasons have already been marked as watched.
   - PD_Jaunty will create a filter file for each user, containing only the unwatched titles. This reduces the size of the library and speeds up the rescan process, saving bandwidth.
   - You can create separate libraries in Plex for each user, ensuring they only see the items they have watchlisted in Plex, without being cluttered by content from other users.
   - The automation can also create an `ignored.txt` file, which can be linked in plex_debrid. It includes movies, shows, or seasons that have been watched by all users and do not need to be readded by plex_debrid. This is essential when using the PD_Jaunty Library Cleanup feature.
   - Additionally, you can add specific titles to a list in the settings that will always be included in all libraries.

3. **Creating `ignored.txt`**
   - If needed, you can manually create an `ignored.txt` file without using the automation. Alternatively, the automation will do this for you for all changes recognized.

4. **Error Checker**
   - This error-checking feature was originally posted by "Majestyck" on Discord [Link](https://discord.com/channels/1021692389368283158/1155806221408931881/1156150014096191528).
   - Have you ever experienced a library scan taking forever and seeming to hang at a specific file you can't find? Sometimes, files or links can become corrupt on Real Debrid. The Error Checker slowly checks all files for errors and lists them, making it easier to locate and remove problematic files.

5. **Library Cleanup**
   - As you may recall, the PD_Jaunty automation creates an `ignored.txt` file containing movies, shows, or seasons that have been watched by all users. These files are no longer needed and can be removed to make your Real Debrid library more lightweight.
   - When performing this cleanup, ensure that you have set up the `ignored.txt` file in plex_debrid. Failing to do so will result in all movies and shows being re-added by plex_debrid.
   - Always use the dry-run option first, as errors during this process could potentially lead to the deletion of your entire library.
