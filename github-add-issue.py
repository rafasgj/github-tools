#!/usr/bin/env python3

"""Add an issue to a Github repository."""

import sys
import json
import requests
from getpass import getpass

if len(sys.argv) != 3:
    print("usage: github-issues.py <username> <project>")
    sys.exit()

options = {"username": sys.argv[1], "project": sys.argv[2]}
issue_url = "https://api.github.com/repos/{username}/{project}/issues"

title = input("Issue Title: ")

body = ""
print("Issue Text: (empty line to finish)")
text = input()
while text:
    body = body + text + "\n"
    text = input()

username = input("Login: ")
password = getpass()

data = json.dumps({"title": title, "body": body}).encode('utf-8')
url = issue_url.format(**options)
print("\nCreating issue...")
r = requests.post(url, data=data, auth=(username, password))
if r.status_code == 201:
    print("Issue #{number} created.".format(**json.loads(r.text)))
else:
    print("An error occured: %d" % r.status_code)
