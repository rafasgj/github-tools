"""Utility functions use by Github scripts."""

import sys
import os, os.path
import argparse
import requests
import json


def __get_item_url(options):
    urls = {
        "issues": "https://api.github.com/repos/{owner}/{repo}/issues",
        "pulls": "https://api.github.com/repos/{owner}/{repo}/pulls"
    }
    url = urls['issues'] if options.issue else urls['pulls']
    if options.number:
        url += "/{number}"
    return url.format(**vars(options))


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
    parser = argparse.ArgumentParser(description='Github Project Tools.')
    parser.add_argument('-o', '--owner',
                        help="The repository owner, as shown in the URL.")
    parser.add_argument('-r', '--repo',
                        help="The repository name, as shown in the URL.")
    parser.add_argument('-i', '--issue', action='store_true', default=True,
                        help="Query repository issues.")
    parser.add_argument('-p', '--pulls', action='store_true',
                        help="Query repository pull requests.")
    parser.add_argument('-n', '--number', type=int,
                        help="Query the item with this number.")
    args = parser.parse_args(sys.argv[1:])
    if not (args.owner and args.repo):
        args.owner, args.repo = get_user_and_project()
    return args


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
            zip(['owner', 'repo'], get_user_and_project())}


def get_items(options):
    """Retrieve issue data."""
    response = requests.get(__get_item_url(options))
    if response.status_code == 200:
        return json.loads(response.text)


def get_comments_on_item(options):
    """Retrieve issue data."""
    url = __get_item_url(options) + "/comments"
    response = requests.get(url.format(**vars(options)))
    if response.status_code == 200:
        return json.loads(response.text)


def post_issue(payload):
    """Post data to the issue API."""
    return requests.post(__get_item_url(options),
                         data=payload['data'],
                         auth=(payload['username'], payload['password']))


def display_error(error_code):
    """Return an error string based on the error_code given."""
    default = "Unknown error."
    msg = {
        401: "Failed to autenticate.",
        403: "Forbidden access due to many authentication errors.",
    }
    return "Error ({}): {}".format(error_code, msg.get(error_code, default))


options = process_command_line()
