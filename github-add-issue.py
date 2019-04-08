#!/usr/bin/env python3

"""Add an issue to a Github repository."""

import json
from getpass import getpass
import github_util

options = github_util.process_command_line()

title = input("Issue Title: ")

body = ""
print("Issue Text: (empty line to finish)")
while True:
    text = input()
    if text:
        body += text + "\n"
    else:
        break

print("Contacting Github...")
options['username'] = input("Login: ")
options['password'] = getpass()

options['data'] = json.dumps({"title": title, "body": body}).encode('utf-8')

print("\nCreating issue...")
r = github_util.post_issue(options)
if r.status_code == 201:
    print("Issue #{number} created.".format(**json.loads(r.text)))
else:
    print("An error occured: %d" % r.status_code)
