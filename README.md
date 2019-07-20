# Github Project Management Tools

The goal of these tools is to allow project management using Github, but
minimizing the need to access their website. These tools provide a text
based, command line interface and make use of Github web API.

## Usage

The main script is `github_tools.py`, which can be used to manage project
_issues_ and _pull requests_.

You may provide the name of the repository and its owner to access any
public repository. If you are currently working in a repository, you can
omit this information, and they will be infered.

## Issues

By default, the tool will list all the open issues in a project. To list
all the open issues in the project, you issue:

```sh
github_tools.py issues
```

### Retrieving information

You can retrieve the information of an specific issue by its number, and,
in this case, it does not matter the status of the issue (open, closed,
etc), the issue information will be retrieved (assuming the issue exists):

```sh
github_tools.py issues -n 4
```

To list the commets on the issues, use the `-c` (or `--commets`) flag.

```sh
github_tools.py issues -c -n 3
```

### Posting

You can create an issue by using the `-p` (or `--post`) flag.

```sh
github_tools.py issues -p
```

This command will ask for the issue title and the text, for the issue.
An empty line is used to mark the end of the issue text.

If using along with the comment flag (`-c` or `--comment`), it requires
an issue number (`-n` or `--number`), and allows you to add a comment to
that issue.

