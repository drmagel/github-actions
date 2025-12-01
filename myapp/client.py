#!/usr/bin/env python3

import requests
import threading
import json, sys, os
from time import sleep

threads = 10

url = 'http://myapp.local.k3d/api/status'

color = {
    'reset': '\033[0m',
    'blue': '\033[94m',
    'red': '\033[91m',
    'green': '\033[92m'
}

def get_status():
    global file
    try:
        while True:
            response = json.loads(requests.get(url).text)
            print(response, file=file)
            if color.get(response["version"]):
                print(f'{color.get(response["version"])}{response}{color["reset"]}')
            else: 
                print(response)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    filename = "out.txt"
    if os.path.exists(filename): os.remove(filename)
    file = open(filename, "a")

    for _ in range(threads):
        thread = threading.Thread(target=get_status, daemon=True)
        thread.start()

    while True:
        try: sleep(1)
        except KeyboardInterrupt:
            file.close()
            sys.exit()