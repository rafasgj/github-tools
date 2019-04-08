#!/usr/bin/env python3

"""Read and post comments to Github issues."""

import sys
import github_util
from github_util import options


text = """
Comment #{id}: {user[login]} @ {created_at}

{body}
--------"""

if not options.issue:
    print("An specific issue must be selected. Use -i/--issue.")
    sys.exit()

issue = github_util.get_items(options)
body = issue['body'].replace("\n", " ").replace("  ", " ")
issue['body'] = "\n".join(["    " + s for s in github_util.fold(body, 72)])
print("Comments for issue #{number}: {title}\n\n{body}".format(**issue))
comments = github_util.get_comments_on_item(options)
for comment in comments:
    body = comment['body'].strip().replace("\n", " ").replace("  ", " ")
    comment['body'] = "\n".join(["    " + s
                                for s in github_util.fold(body, 72)])
    print(text.format(**comment))
print("\nTotal de Comentários: ", len(comments))
