#!/usr/bin/env python3
import sys, os
def importError(package):
    print(f'package {package} needs to be installed. install with: "python3 -m pip install {package} --user"', file=sys.stderr)
    exit(1)
try:
    from bs4 import BeautifulSoup
except:
    importError('bs4')
import argparse

try:
    import requests
    import requests.exceptions
except:
    importError('requests')

import time
import configparser

_HEADERS = {'User-Agent': 'kattis-cli-downloader'}


class ConfigError(Exception):
    pass

def get_config(fileName):
    """Returns a ConfigParser object for the .kattisrc file(s)
    """
    cfg = configparser.ConfigParser()
    if os.path.exists(fileName):
        try:
            if cfg.read(fileName):
                return cfg
        except: pass
    raise ConfigError(f'''\
I failed to read in a config file from {fileName}. 
To download a .kattisrc file please visit
https://open.kattis.com/download/kattisrc
The file should look something like this:
[user]
username: yourusername
token: *********
[kattis]
hostname: <kattis>
loginurl: https://<kattis>/login
submissionurl: https://<kattis>/submit
submissionsurl: https://<kattis>/submissions''')

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('kattisrc', help='path to your kattisrc config file')
    return parser.parse_args()


def login(login_url, username, password=None, token=None):
    """Log in to Kattis.

    At least one of password or token needs to be provided.

    Returns a requests.Response with cookies needed to be able to submit
    """
    login_args = {'user': username, 'script': 'true'}
    if password:
        login_args['password'] = password
    if token:
        login_args['token'] = token

    return requests.post(login_url, data=login_args, headers=_HEADERS)


def login_from_config(cfg):
    """Log in to Kattis using the access information in a kattisrc file

    Returns a requests.Response with cookies needed to be able to submit
    """
    username = cfg.get('user', 'username')
    password = token = None
    try:
        password = cfg.get('user', 'password')
    except configparser.NoOptionError:
        pass
    try:
        token = cfg.get('user', 'token')
    except configparser.NoOptionError:
        pass
    if password is None and token is None:
        raise ConfigError('''\
Your .kattisrc file appears corrupted. It must provide a token (or a
KATTIS password).

Please download a new .kattisrc file''')

    loginurl = get_url(cfg, 'loginurl', 'login')
    return login(loginurl, username, password, token)

def get_login_reply(cfg):
    try:
        login_reply = login_from_config(cfg)
    except ConfigError as exc:
        print(exc)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print('Login connection failed:', err)
        sys.exit(1)

    if not login_reply.status_code == 200:
        print('Login failed.')
        if login_reply.status_code == 403:
            print('Incorrect username or password/token (403)')
        elif login_reply.status_code == 404:
            print('Incorrect login URL (404)')
        else:
            print('Status code:', login_reply.status_code)
        sys.exit(1)
    return login_reply

def get_url(cfg, option, default):
    if cfg.has_option('kattis', option):
        return cfg.get('kattis', option)
    else:
        return 'https://%s/%s' % (cfg.get('kattis', 'hostname'), default)

def get_problem_page_url(cfg, p_id):
    return get_url(cfg, 'problem_page', 'problems') + f'?page={p_id}&show_solved=on&show_tried=off&show_untried=off'

def get_problem_page(cfg, p_id, cookies):
    page_url = get_problem_page_url(cfg, p_id)
    r = requests.get(page_url, cookies=cookies, headers=_HEADERS)
    if r.status_code != 200:
        print(f'failed to fetch {page_url}: {r.status_code}', file=sys.stderr)
        exit(1)
    html = r.text
    return html

def parseProblems(html):
    soup = BeautifulSoup(html, 'html.parser')
    problems = []
    for tr in soup.find_all('tr'):
        td = tr.find('td')
        if td:
            a = td.find('a')
            if a:
                problems.append(a.get('href').split('/')[-1])
    return problems

def main():
    cfg = get_config(parseArgs().kattisrc)

    login_reply = get_login_reply(cfg)
    problems = []
    p_id = 0
    userName = cfg.get('user', 'username')
    while True:
        print(f'fetching page {p_id}')
        html = get_problem_page(cfg, p_id, login_reply.cookies)
        new_problems = parseProblems(html)
        if not new_problems: break
        problems.extend(new_problems)
        time.sleep(0.5)

        p_id += 1
    fileName = f'kattis_solved_problems_{userName}.txt'
    print('\n'.join(sorted(problems)), file=open(fileName, 'w'))
    print(f'Wrote {len(problems)} problem to "{fileName}"')

if __name__ == '__main__':
    main()