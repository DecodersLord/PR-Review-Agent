# PR Review Agent

This project implements an AI-powered agent that reviews GitHub Pull Requests (PRs) and generates appropriate titles and descriptions based on the repository's contribution guidelines.

## Features

- **PR Diff Analysis**: Fetches and analyzes the code changes in a PR.
- **Contribution Guidelines**: Automatically fetches `CONTRIBUTING.md` from the repository.
- **Smart Generation**: Generates PR titles and descriptions that match the repository's style and requirements.
- **Multi-Model Support**: Built on `smolagents`, allowing easy switching between different LLMs.

## Prerequisites

- Python 3.8+
- Hugging Face Token (for Qwen model)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd PR-Review-Agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory with your Hugging Face token:
   ```env
   HF_TOKEN=your_huggingface_token_here
   ```

## Usage

Run the agent and provide a GitHub PR URL when prompted:

```bash
python main.py
```

Example input:
```
Enter the GitHub Pull Request URL: https://github.com/huggingface/transformers.js/pull/1540
```

The agent will then:
1. Fetch the PR diff.
2. Analyze the changes.
3. Fetch the `CONTRIBUTING.md`.
4. Generate a title and description.
5. Print the result.

## Code Structure

- `main.py`: The main entry point for the application.
- `requirements.txt`: Lists all necessary Python dependencies.
- `.env`: Stores environment variables (e.g., API keys).
