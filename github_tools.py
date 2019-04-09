"""Utility functions use by Github scripts."""

from getpass import getpass

import sys
import os, os.path
import argparse
import requests
import json
from operator import itemgetter


def __get_item_url():
    base_url = "https://api.github.com/repos/{owner}/{repo}/{item}"
    url = base_url if not options.number else base_url + "/{number}"
    opt = vars(options)
    opt['url'] = url.format(**opt)
    return opt['url']


def __fold(s, col):
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


def __process_command_line():
    """Process command line to retrieve owner and project."""
    parser = argparse.ArgumentParser(description='Github Project Tools.')
    msg = """The item to run the tools against. You can select to run queries
             against 'issue[s]' (project issues) or 'pull[s]' (pull requests).
          """
    parser.add_argument('item', type=str, choices=['issues', 'pulls'],
                        default="issues", nargs='?', help=msg)
    parser.add_argument('-o', '--owner',
                        help="The repository owner, as shown in the URL.")
    parser.add_argument('-r', '--repo',
                        help="The repository name, as shown in the URL.")
    parser.add_argument('-n', '--number', type=int,
                        help="Query the item with this number.")
    parser.add_argument('-c', '--comments', action='store_true',
                        help="Query the comments for an item.")
    parser.add_argument('-p', '--post', action='store_true',
                        help="Post a new issue or comment.")
    args = parser.parse_args(sys.argv[1:])
    if not (args.owner and args.repo):
        args.owner, args.repo = get_user_and_project()
    return args


def __format_text(text, columns=72, ident=4):
    body = text.strip().replace("\n", " ").replace("  ", " ")
    return "\n".join(["    " + s for s in __fold(body, 72)])


def __print_issue(issue, **kwargs):
    default_formats = {
        "issues": """
Issue #{number}: ({state}) {title}

{body}

Labels: {label_names}
Milestone: {milestone[title]}
Comments: {comments}
--------
    """,
    }

    text = default_formats[options.item]
    labels = [l.get('name', None) for l in issue.get('labels', [])]
    if 'milestone' not in issue or issue['milestone'] is None:
        issue['milestone'] = {'title': "No milestone set."}
    else:
        issue['milestone'].setdefault('title', "No milestone set.")
    issue['body'] = __format_text(issue['body'])
    print(text.format(**issue, label_names=labels))


def __print_items(items, **kwargs):
    sort_field = itemgetter(kwargs.get('sort_by', 'number'))
    reverse = kwargs.get('reverse', False)
    if isinstance(items, list):
        for issue in sorted(items, key=sort_field, reverse=reverse):
            __print_issue(issue)
    else:
        __print_issue(items)


def __print_comments_for_item(item):
    text = """
Comment #{id}: {user[login]} @ {created_at}

{body}
--------"""
    if not item:
        return
    item['body'] = __format_text(item['body'])
    print("-" * 40)
    print("Comments for issue #{number}: {title}\n\n{body}".format(**item))
    print("-" * 16, end="")
    comments = get_item_comments(item['number'])
    for comment in comments:
        comment['body'] = __format_text(comment['body'])
        print(text.format(**comment))
    print("\nTotal de Comentários: ", len(comments))


def __print_comments(items):
    if isinstance(items, list):
        for item in sorted(items, key=itemgetter('number')):
            __print_comments_for_item(item)
    else:
        __print_comments_for_item(items)


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


def __process_get_response(response):
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(__display_result(response))


def get_items():
    """Retrieve issue data."""
    payload = {
        "url": __get_item_url(),
    }
    return __process_get_response(requests.get(payload['url']))


def get_item_comments(number=None):
    """Retrieve issue data."""
    if number:
        vars(options)['number'] = number
    url = (__get_item_url() + "/comments").format(**vars(options))
    return __process_get_response(requests.get(url))


def __perform_post(payload):
    url = payload['url'] + "/comments" if options.comments else ''
    return requests.post(url,
                         data=payload['data'],
                         auth=(payload['username'], payload['password']))


def post_item():
    """Post data to the issue API."""
    data = __create_comment() if options.comments else __create_issue()
    payload = {
        'url': __get_item_url(),
        'data': json.dumps(data).encode('utf-8')
    }
    __add_credentials_to(payload)

    print("\nPosting data...")
    print(__display_result(__perform_post(payload)))


def __display_result(response):
    """Return an error string based on the error_code given."""
    default = "Unknown error."
    msg = {
        200: ("OK", "Data retrieved."),
        201: ("OK", "Item created."),
        401: ("Error", "Failed to autenticate."),
        403: ("Error", "Forbidden access due to many authentication errors."),
        404: ("Error", "This is embarassing... the url was not found {url}."),
    }
    code = response.status_code
    st, text = msg.get(code, default)
    return "{} ({}): {}".format(st, code, text.format(**vars(options)))


def __read_stdin_until_empty_line():
    body = []
    print("Issue Text: (empty line to finish)")
    while True:
        text = input()
        if text:
            body.append(text.strip())
        else:
            break
    return "\n".join(body)


def __add_credentials_to(payload):
    print("Login credentials to Github:")
    payload['username'] = input("Login: ")
    payload['password'] = getpass()


def __create_issue():
    """Create an issue for a project."""
    return {
        "title": input("Issue Title: "),
        "body": __read_stdin_until_empty_line()
    }


def __create_comment():
    """Create a comment for an item."""
    return {
        "body": __read_stdin_until_empty_line()
    }


options = __process_command_line()

if __name__ == "__main__":
    if options.post:
        post_item()
    else:
        data = get_items()
        if data is not None:
            __print_comments(data) if options.comments else __print_items(data)
        else:
            print("No data for '{item}' found.".format(options))
