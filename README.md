# Intelligent Code Review Agent

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
- **OpenAI API**: LLM for code analysis
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
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

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

