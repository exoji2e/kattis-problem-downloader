# Kattis problem downloader

_Downloads a list of all your solved kattis-problems._

- Clone this repo: `git clone git@github.com:exoji2e/kattis-problem-downloader.git`
- Login to kattis at [https://open.kattis.com](https://open.kattis.com)
- Download your kattisrc from [https://open.kattis.com/download/kattisrc](https://open.kattis.com/download/kattisrc)
    - Save it as kattisrc in this folder.
- install python dependencies (bs4 and requests):
    - `python3 -m pip install -r requirements.txt --user`
- run the python script and pass your kattisrc file as the first parameter:
    - `python3 download_solved_problems.py kattisrc`.
    - It will output a file "kattis_solved_problems_{katts-username}.txt" with all solved problem ids.