from smolagents import CodeAgent, InferenceClientModel, tool
import requests
import re
import json
import dotenv

dotenv.load_dotenv()  # Load HF_TOKEN from .env into the environment


@tool
def fetch_pr_diff(pr_url: str) -> str:
    """Fetches the raw diff from a GitHub Pull Request URL.
    Args:
        pr_url: A GitHub PR URL like 'https://github.com/owner/repo/pull/123'
    """
    diff_url = pr_url + ".diff"
    response = requests.get(diff_url)

    if response.status_code != 200:
        return f"Error: Could not fetch diff (HTTP {response.status_code}). Is the PR URL correct and public?"

    return response.text

@tool
def get_CONTRIBUTION_GUIDELINES(pr_url: str) -> str:
    """Fetches the contribution guidelines from a GitHub repository.
    Args:
        pr_url: A GitHub PR URL like 'https://github.com/owner/repo/pull/123'
    """
    owner = pr_url.split("/")[3]
    repo = pr_url.split("/")[4]

    # Use the raw URL to get plain text directly (API returns base64-encoded JSON)
    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/CONTRIBUTING.md"
    response = requests.get(raw_url)

    if response.status_code != 200:
        # Try 'master' branch as fallback
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/CONTRIBUTING.md"
        response = requests.get(raw_url)

    if response.status_code != 200:
        return "No CONTRIBUTING.md found in this repository."

    return response.text

@tool
def analyze_diff(diff_text: str) -> str:
    """Analyzes a git diff and returns structured stats about the changes.
    Args:
        diff_text: The raw git diff text to analyze
    """
    files_changed = re.findall(r"^diff --git a/(.+?) b/", diff_text, re.MULTILINE)
    lines_added = len(re.findall(r"^\+[^+]", diff_text, re.MULTILINE))
    lines_removed = len(re.findall(r"^-[^-]", diff_text, re.MULTILINE))

    # Extract function/method names touched in the diff (Python + JS patterns)
    functions_touched = re.findall(
        r"^[+-]\s*(?:def|function|const|let|var|async\s+function)\s+(\w+)",
        diff_text,
        re.MULTILINE,
    )
    functions_touched = list(set(functions_touched))

    # Count hunks (@@...@@ markers) to gauge how spread out the changes are
    hunk_count = len(re.findall(r"^@@", diff_text, re.MULTILINE))

    # Check for test file changes
    test_files = [f for f in files_changed if "test" in f.lower()]

    # Check for new variables/constants added
    new_variables = re.findall(
        r"^\+\s*(?:const|let|var|self\.)\s*(\w+)\s*=",
        diff_text,
        re.MULTILINE,
    )
    new_variables = list(set(new_variables))

    # Complexity hint: deeply nested additions
    deep_additions = sum(
        1 for line in diff_text.split("\n")
        if line.startswith("+") and len(line) - len(line.lstrip()) > 16
    )

    result = {
        "files_changed": files_changed,
        "num_files": len(files_changed),
        "lines_added": lines_added,
        "lines_removed": lines_removed,
        "net_change": lines_added - lines_removed,
        "hunks": hunk_count,
        "functions_touched": functions_touched,
        "test_files_changed": test_files,
        "has_tests": len(test_files) > 0,
        "new_variables": new_variables,
        "deeply_nested_additions": deep_additions,
    }

    return json.dumps(result, indent=2)


def main():
    model = InferenceClientModel(
        model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
        max_tokens=2096,
        temperature=0.5,
    )

    agent = CodeAgent(
        model=model,
        tools=[fetch_pr_diff, analyze_diff, get_CONTRIBUTION_GUIDELINES],
        max_steps=6,
        verbosity_level=2,
    )

    pr_url = input("Enter the GitHub Pull Request URL: ")

    result = agent.run(
        f"Review this GitHub Pull Request: {pr_url}\n\n"
        "Steps:\n"
        "1. Use fetch_pr_diff to get the diff from the PR URL\n"
        "2. Use analyze_diff to get structured stats about the changes\n"
        "3. Use get_CONTRIBUTION_GUIDELINES to fetch the repo's contributing guidelines\n"
        "4. Based on the diff content, analysis stats, AND the contributing guidelines, generate:\n"
        "   - A concise, descriptive PR title (max 10 words)\n"
        "   - A PR description (2-3 paragraphs) following the repo's contributing style, covering: what changed, why it matters, and any risks\n\n"
        "Return the final answer as a formatted string with the PR title and description."
    )

    print("\n" + "=" * 60)
    print("PR REVIEW BOT OUTPUT")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    main()