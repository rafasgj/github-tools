#!/usr/bin/env python3

"""List all open issues from a Github project."""

from operator import itemgetter
import github_util

options = github_util.process_command_line()

text = """
Issue #{number}: {title}

{body}

Labels: {label_names}
Milestone: {milestone[title]}
--------\n"""

data = github_util.get_issues(options)
if data is not None:
    for issue in sorted(data, key=itemgetter('number')):
        labels = [l.get('name', None) for l in issue.get('labels', [])]
        if 'milestone' not in issue or issue['milestone'] is None:
            issue['milestone'] = {'title': "No milestone set."}
        else:
            issue['milestone'].setdefault('title', "No milestone set.")
        body = issue['body'].replace("\n", " ").replace("  ", " ")
        issue['body'] = "\n".join(["    " + s
                                   for s in github_util.fold(body, 72)])
        print(text.format(**issue, label_names=labels))
