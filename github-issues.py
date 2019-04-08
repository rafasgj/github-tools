#!/usr/bin/env python3

"""List all open issues from a Github project."""

from operator import itemgetter
from github_util import options
import github_util


text = """
Issue #{number}: ({state}) {title}

{body}

Labels: {label_names}
Milestone: {milestone[title]}
Comments: {comments}
--------\n"""


def __print_issue(issue):
    labels = [l.get('name', None) for l in issue.get('labels', [])]
    if 'milestone' not in issue or issue['milestone'] is None:
        issue['milestone'] = {'title': "No milestone set."}
    else:
        issue['milestone'].setdefault('title', "No milestone set.")
    body = issue['body'].replace("\n", " ").replace("  ", " ")
    issue['body'] = "\n".join(["    " + s
                               for s in github_util.fold(body, 72)])
    print(text.format(**issue, label_names=labels))


data = github_util.get_items(options)
if data is not None:
    if isinstance(data, list):
        for issue in sorted(data, key=itemgetter('number')):
            __print_issue(issue)
    else:
        __print_issue(data)
