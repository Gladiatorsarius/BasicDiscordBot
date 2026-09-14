import subprocess 
import re 


def git_fetch():
    git_fetch = subprocess.run(['git', 'fetch' ,'--tags' ], capture_output=True, text=True)
    return git_fetch.stdout.strip()


def git_differences(difference_Type: str):
    git_fetch()
    if difference_Type == "long_hash":
        git_log = subprocess.run(['git', 'log', 'HEAD..@{u}', '--format=%H'], capture_output=True, text=True)
    elif difference_Type == "commit_message":
        git_log = subprocess.run(['git', 'log', 'HEAD..@{u}', '--format=%s'], capture_output=True, text=True)
    elif difference_Type == "short_hash":
        git_log = subprocess.run(['git', 'log', 'HEAD..@{u}', '--format=%h'], capture_output=True, text=True)
    elif difference_Type == "short_hash_with_commit_message":
        git_log = subprocess.run(['git', 'log', 'HEAD..@{u}', '--format=%h %s'], capture_output=True, text=True)
    elif difference_Type == "commit_count":
        git_log = subprocess.run(['git', 'rev-list', '--count', 'HEAD..@{u}'], capture_output=True, text=True)
    if difference_Type != "commit_count":
        return git_log.stdout.strip().splitlines()
    return git_log.stdout.strip()

def git_url_origin():
    git_fetch()
    git_url_origin = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True, text=True)
    return git_url_origin.stdout.strip().removesuffix('.git')

def git_show(file):
    git_fetch()
    git_show = subprocess.run(['git', 'show', file], capture_output=True, text=True)
    return git_show.stdout.strip()

def get_version(version_Type: str) -> str | None:
    if version_Type == "Remote":
        try:
            result = subprocess.run(
                ["git", "tag", "--merged", "@{u}", "--no-merged", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            tags = [tag.strip() for tag in result.stdout.strip().splitlines() if tag.strip()]
            latest_tag = tags[-1] if tags else None
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            latest_tag = None
        return latest_tag
    elif version_Type == "Local":
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip() or None
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None



def author_name():
    url_origin = git_url_origin()
    return url_origin.split('/')[-2]

def commit_links():
    url_origin = git_url_origin()
    long_hashes = git_differences("long_hash")
    return [f"{url_origin}/commit/{long_hash}" for long_hash in long_hashes]

def git_pull():
    git_fetch()
    git_pull = subprocess.run(['git', 'pull'], capture_output=True, text=True)
    return git_pull.stdout.strip()        

def git_diff(difference_Type: str):
    git_fetch()
    if difference_Type == "stat":
        git_diff_stat = subprocess.run(['git', 'diff', '--stat', 'HEAD..@{u}'], capture_output=True, text=True)
        return git_diff_stat.stdout.strip()