"""Utility functions use by Github scripts."""

import sys
import os, os.path
import requests
import json


def __get_issue_url(options):
    issue_url = "https://api.github.com/repos/{owner}/{project}/issues"
    return issue_url.format(**options)


def fold(s, col):
    """Fold text in s, to the column col, breaking on spaces."""
    r = []
    last, cut, count = 0, 0, 0
    for c in s:
        count += 1
        if c == " ":
            cut = count - 1
        if count % col == 0:
            r.append(s[last:cut])
            last = cut + 1
    r.append(s[last:])
    return r


def process_command_line():
    """Process command line to retrieve owner and project."""
    if len(sys.argv) > 1 and len(sys.argv) != 3:
        print("usage: {} <owner> <project>".format(sys.argv[0]))
        sys.exit()
    if len(sys.argv) == 1:
        return default_options()
    else:
        return {"owner": sys.argv[1], "project": sys.argv[2]}


def get_user_and_project():
    """Use git scripts to deduce username and project."""
    git_cmd = 'git remote -v|cut -f 2-|grep fetch|sed -n 1p|cut -d " " -f 1'
    with os.popen(git_cmd, 'r') as p:
        url = p.read().strip().split('/')
        if len(url) == 5:
            return (url[3], os.path.splitext(url[4])[0])


def default_options():
    """Create a default options dictionary for the current git repo."""
    return {k: v for k, v in
            zip(['owner', 'project'], get_user_and_project())}


def get_issues(options):
    """Retrieve issue data."""
    response = requests.get(__get_issue_url(options))
    if response.status_code == 200:
        return json.loads(response.text)


def post_issue(options):
    """Post data to the issue API."""
    return requests.post(__get_issue_url(options),
                         data=options['data'],
                         auth=(options['username'], options['password']))
