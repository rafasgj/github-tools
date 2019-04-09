"""Utility functions use by Github scripts."""

import sys
import os, os.path
import argparse
import requests
import json
from operator import itemgetter


def __get_item_url():
    base_url = "https://api.github.com/repos/{owner}/{repo}/{item}"
    url = base_url if not options.number else base_url + "/{number}"
    return url.format(**vars(options))


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
    parser.add_argument('item', type=str, default="issues", nargs='?',
                        help=msg)
    parser.add_argument('-o', '--owner',
                        help="The repository owner, as shown in the URL.")
    parser.add_argument('-r', '--repo',
                        help="The repository name, as shown in the URL.")
    parser.add_argument('-n', '--number', type=int,
                        help="Query the item with this number.")
    parser.add_argument('-c', '--comments', action='store_true',
                        help="Query the comments for an item.")
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


def get_items():
    """Retrieve issue data."""
    response = requests.get(__get_item_url())
    if response.status_code == 200:
        return json.loads(response.text)


def get_item_comments(number=None):
    """Retrieve issue data."""
    if number:
        vars(options)['number'] = number
    url = __get_item_url() + "/comments"
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


options = __process_command_line()

if __name__ == "__main__":
    data = get_items()
    if data is not None:
        __print_comments(data) if options.comments else __print_items(data)
    else:
        print("No data for '{item}' found.".format(options))
