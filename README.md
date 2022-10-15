# Kattis problem downloader

_Downloads a list of all your solved kattis-problems._

- Login to kattis at [https://open.kattis.com](https://open.kattis.com)
- Download a kattisrc (and place it in this folder) from [https://open.kattis.com/download/kattisrc](https://open.kattis.com/download/kattisrc)
- install python dependencies (bs4 and requests): `python3 -m pip install -r requirements.txt --user`
- run the python script `python3 download_solved_problems.py kattisrc`.
    - It will output a file "kattis_solved_problems_{katts-username}.txt" with all solved problem ids.