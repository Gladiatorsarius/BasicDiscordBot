import subprocess 
import re 


def git_fetch():
    git_fetch = subprocess.run(['git', 'fetch' ,'--tags' ], capture_output=True, text=True)
    return git_fetch.stdout.strip()

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

def git_pull():
    git_fetch()
    git_pull = subprocess.run(['git', 'pull'], capture_output=True, text=True)
    return git_pull.stdout.strip()        


def parse_changelog_diff(clean_text: str) -> dict:
    """Parses clean Markdown text into a structured dictionary."""
    parsed_data = {
        "version": None,
        "date": None,
        "changes": [],  # List of {"type": ..., "content": [...]}
    }

    current_type = None

    for line in clean_text.splitlines():
        line_str = line.strip()
        if not line_str:
            continue

        # Match version header, e.g., ## v1.3.0 (2026-09-18)
        version_match = re.match(r"^##\s*(v?[\d\.]+)\s*(?:\((.*?)\))?", line_str)
        if version_match:
            parsed_data["version"] = version_match.group(1)
            parsed_data["date"] = version_match.group(2)
            continue

        # Match category header, e.g., ### Feat, ### Fix, ### BREAKING CHANGE
        type_match = re.match(r"^###\s*(.+)", line_str)
        if type_match:
            current_type = type_match.group(1).strip()
            parsed_data["changes"].append({"type": current_type, "content": []})
            continue

        # Match bullet points under the current category
        if current_type and (
            line_str.startswith("- ") or line_str.startswith("* ")
        ):
            parsed_data["changes"][-1]["content"].append(line_str)

    return parsed_data


def view_changelogmd() -> dict:
    git_fetch()

    res = subprocess.run(
        ["git", "diff", "HEAD..@{u}", "--", "changelog.md"],
        capture_output=True,
        text=True,
        check=True,
    )

    plain_markdown_lines = []
    for line in res.stdout.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            plain_markdown_lines.append(line[1:])

    plain_text = "\n".join(plain_markdown_lines)

    return parse_changelog_diff(plain_text)