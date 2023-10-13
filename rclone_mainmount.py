# rclone_mainmount.py
import settings
import subprocess
from settings import drive_letters, sources, dircachetime, dircachetimesetting, vfscachemode, vfscachemodesetting, buffersize, buffersizesetting


def startrclone():
    result = {}  

    for index, source_info in enumerate(sources):
        if index >= len(drive_letters):
            print(f"Error: Maximum number of sources reached. Last created source: {source_info['source_name']} and following sources won't be created.")
            break

        source_name = source_info['source_name']
        source = source_info['source']
        destination = drive_letters[index]

        command = [
            "rclone", "mount", source, destination,
            dircachetime, dircachetimesetting,
            vfscachemode, vfscachemodesetting,
            buffersize, buffersizesetting
        ]

        try:
            result[source_name] = subprocess.Popen(command, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Error rclone for {source_name}:", str(e))
            pass


def terminaterclone():
    global result
    result.terminate()




def main():
    if not drive_letters or drive_letters == []:
        return
    else:
        startrclone()


if __name__ == "__main__":
    main()