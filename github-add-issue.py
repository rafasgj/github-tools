#!/usr/bin/env python3

"""Add an issue to a Github repository."""

import json
from getpass import getpass
import github_util

title = input("Issue Title: ")

body = ""
print("Issue Text: (empty line to finish)")
while True:
    text = input()
    if text:
        body += text + "\n"
    else:
        break

payload = {}

print("Contacting Github...")
payload['username'] = input("Login: ")
payload['password'] = getpass()
payload['data'] = json.dumps({"title": title, "body": body}).encode('utf-8')

print("\nCreating issue...")
r = github_util.post_issue(payload)
if r.status_code == 201:
    print("Issue #{number} created.".format(**json.loads(r.text)))
else:
    print(github_util.display_error(r.status_code))
