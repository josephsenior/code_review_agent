#  Intelligent Code Review Agent

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-orange.svg)](https://www.langchain.com/)

A code review system where multiple specialized AI agents work together to analyze your code, find issues, suggest improvements, and generate detailed review reports. Think of it as having a team of expert code reviewers, each focusing on their area of expertise.

## What This Does

I built this to showcase how different agentic AI patterns can work together in a practical application. Instead of one agent trying to do everything, I created specialized agents that each focus on a specific aspect of code review. They work together to give you comprehensive feedback on your code.

## Key Features

Here's what makes this system useful:

- **Specialized Agents**: Each agent focuses on one area - syntax, security, performance, style, best practices, and documentation
- **Comprehensive Analysis**: Covers everything from basic syntax errors to architectural issues
- **Smart Issue Detection**: Finds bugs, security vulnerabilities, performance problems, and code smells
- **Actionable Suggestions**: Not just problems, but specific recommendations on how to fix them
- **Detailed Reports**: Generates well-formatted reports you can share with your team
- **Multiple Languages**: Works with Python, JavaScript, TypeScript, and more

## How It Works

The system uses six specialized agents, each with their own job:

- **Syntax Analyzer**: Catches syntax errors and basic structural problems before anything else
- **Security Agent**: Looks for vulnerabilities like SQL injection, hardcoded secrets, and other security risks
- **Performance Agent**: Identifies bottlenecks, inefficient algorithms, and optimization opportunities
- **Style Agent**: Checks your code against style guides and naming conventions
- **Best Practices Agent**: Reviews design patterns, SOLID principles, and architectural issues
- **Documentation Agent**: Evaluates how well your code is documented

An orchestrator coordinates all these agents, collects their findings, and puts everything together into a comprehensive report.

## Tech Stack

- **LangChain**: Agent framework
- **Gemini API**: LLM for code analysis
- **Streamlit**: Web interface
- **Python**: Core implementation

## Status

Ready for use. All core components implemented and tested.

## Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment:**

   Copy the example env and add your Gemini API key (do not commit the real `.env`):

   - Unix / macOS:
   ```bash
   cp .env.example .env
   ```

   - Windows (PowerShell):
   ```powershell
   Copy-Item .env.example .env
   ```

   Then edit `.env` and set `GEMINI_API_KEY` to your key.

   You can get an API key from [Gemini's platform](https://platform.Gemini.com/api-keys).

3. **Run the application:**
```bash
streamlit run frontend/streamlit_app.py
```

The app will open at `http://localhost:8501`

## Usage

Using the system is straightforward:

1. **Input your code** - Either paste it directly or upload a file
2. **Pick the language** - Select Python, JavaScript, TypeScript, or another supported language
3. **Choose which agents to run** - You can run all of them or just the ones you care about
4. **Start the review** - Click the button and wait a minute or two while the agents do their work
5. **Check the results** - Each agent's findings are organized in expandable sections
6. **Export the report** - Download everything as a Markdown, Text, or JSON file to share with your team

## Testing

Run tests without API key:
```bash
python test_review_dry_run.py
```

Run full test with API key:
```bash
python test_review.py
```

Security note: If you accidentally committed secrets (for example a real `.env` file), remove it from future commits with:

```bash
git rm --cached .env
git commit -m "remove sensitive .env"
```

To purge secrets from repository history you will need to rewrite history (for example using `git filter-repo` or the BFG Repo Cleaner) — take care, this rewrites commits and will require force-push.

##  Tech Stack

- **LangChain**: Agent framework and orchestration
- **Gemini API**: LLM for code analysis
- **Streamlit**: Web interface
- **Python 3.8+**: Core language

##  Use Cases

- **Code Quality Assurance**: Automated code review before commits
- **Security Auditing**: Detect security vulnerabilities automatically
- **Performance Optimization**: Identify performance bottlenecks
- **Best Practices**: Ensure code follows best practices
- **Documentation**: Evaluate and improve code documentation

##  Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


