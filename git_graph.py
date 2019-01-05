import collections
import re

import git_functions as gf


def build_git_trees(path, trees):
    result = collections.defaultdict(list)
    pattern = '(tree|blob) (.+)\t(.+)'
    for each_tree in trees:
        for each_line in gf.read_git_file(path, each_tree):
            match = re.search(pattern, each_line)
            if match:
                result[each_tree].append((match.group(2), match.group(3)))
    return result


def build_git_commits(path, commits):
    result = collections.defaultdict(list)
    pattern = '(tree|parent) (.+)'
    for each_commit in commits:
        for each_line in gf.read_git_file(path, each_commit):
            match = re.search(pattern, each_line)
            if match:
                result[each_commit].append(match.group(2))
    return result


def build_git_remotes(remotes):
    remote_servers = collections.defaultdict(list)
    remote_branches = {}
    for r in remotes:
        separator_index = r[0].find('/')
        server = r[0][:separator_index]
        branch = r[0][separator_index + 1:]
        commit = r[1]
        remote_servers[server].append(branch)
        remote_branches[(server, branch)] = commit
    return remote_servers, remote_branches


def build_git_annotated_tags(path, annotated_tags):
    result = {}
    pattern = '(object) (.+)'
    for each_annotated_tag in annotated_tags:
        for each_line in gf.read_git_file(path, each_annotated_tag):
            match = re.search(pattern, each_line)
            if match:
                result[each_annotated_tag] = match.group(2)
    return result


class GitGraph:

    def __init__(self, path):
        self.path = path
        self.blobs = []                                      # b: color #9ccc66 (green)  - point to nothing
        self.trees = collections.defaultdict(list)           # t: color #bc9b8f (maroon) - point to 0 to N blobs and 0 to N trees
        self.commits = collections.defaultdict(list)         # c: color #6cccf9 (blue)   - point to 1 tree and 0 to N commits
        self.local_branches = {}                             # l: color #ffc61a (yellow) - point to 1 commit
        self.local_head = ('', '')                           # h: color #cc99ff (violet) - point to 1 local_branch
        self.remote_branches = {}                            # r: color #ff6666 (red)    - point to 1 commit
        self.remote_heads = {}                               # d: color #ffa366 (orange) - point to 1 remote branch
        self.remote_servers = collections.defaultdict(list)  # s: color #ff9988 (salmon) - point to 1 to N remote_branches
        self.annotated_tags = {}                             # a: color #00cc99 (turquo) - point to 1 commit
        self.tags = {}                                       # g: color #ff66b3 (pink)   - point to 1 commit or 1 annotated_tag

    def build_graph(self):
        blobs, trees, commits, annotated_tags = gf.get_git_objects(self.path)
        local_branches, remotes, tags = gf.get_git_references(self.path)
        local_head = gf.get_git_local_head(self.path)

        self.blobs = blobs
        self.trees = build_git_trees(self.path, trees)
        self.commits = build_git_commits(self.path, commits)
        self.local_branches = {lb[0]: lb[1] for lb in local_branches}
        self.local_head = ('HEAD', local_head)
        self.remote_servers, self.remote_branches = build_git_remotes(remotes)
#        self.remote_heads =
        self.annotated_tags = build_git_annotated_tags(self.path, annotated_tags)
        self.tags = {t[0]: t[1] for t in tags}
        return self
