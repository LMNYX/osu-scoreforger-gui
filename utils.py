import requests



class GithubInteractions:
    def GetRepoDirectory(user, repo):
        return requests.get(f'https://api.github.com/repos/{user}/{repo}/git/trees/master?recursive=1').json()

    def GetRepoFile(user, repo, path):
        return requests.get(f'https://raw.githubusercontent.com/{user}/{repo}/master/{path}').text

    def TreeToList(tree):
        return [x['path'] for x in tree['tree']]