#!/usr/bin/env python3

"""List all open issues from a Github project."""

import sys
import json
from operator import itemgetter
from urllib.request import urlopen


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


if len(sys.argv) != 3:
    print("usage: github-issues.py <username> <project>")
    sys.exit()

options = {"username": sys.argv[1], "project": sys.argv[2]}

issue_url = "https://api.github.com/repos/{username}/{project}/issues"
text = """
Issue #{number}: {title}

{body}

Labels: {label_names}
Milestone: {milestone[title]}
--------\n"""

data = None
with urlopen(issue_url.format(**options)) as url:
    data = json.loads(url.read().decode())

if data is not None:
    for issue in sorted(data, key=itemgetter('number')):
        labels = [l.get('name', None) for l in issue.get('labels', [])]
        if 'milestone' not in issue or issue['milestone'] is None:
            issue['milestone'] = {'title': "No milestone set."}
        else:
            issue['milestone'].setdefault('title', "No milestone set.")
        body = issue['body'].replace("\n"," ").replace("  "," ")
        issue['body'] = "\n".join(["    " + s for s in fold(body, 72)])
        print(text.format(**issue, label_names=labels))
