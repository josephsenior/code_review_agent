"""
Main Streamlit Application for the Code Review Agent System.
"""

import sys
from pathlib import Path

import streamlit as st

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path.parent))

# Import at top level to avoid E402
from backend.core.orchestrator import CodeReviewOrchestrator  # noqa: E402
from backend.core.report_generator import ReportGenerator  # noqa: E402

# Page configuration
st.set_page_config(
    page_title="Code Review Agent",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "orchestrator" not in st.session_state:
    try:
        st.session_state.orchestrator = CodeReviewOrchestrator()
        st.session_state.review_result = None
    except Exception as e:
        st.error(f"Failed to initialize orchestrator: {str(e)}")
        st.info("Make sure GEMINI_API_KEY is set in your .env file")
        st.stop()


def main():
    """Main application function."""
    st.title("Intelligent Code Review Agent")
    st.markdown("Get comprehensive code reviews using multiple specialized AI agents.")

    # Sidebar
    with st.sidebar:
        st.header("Configuration")

        language = st.selectbox(
            "Programming Language",
            ["python", "javascript", "typescript", "java", "cpp", "go"],
            key="language_selector",
        )

        st.divider()

        st.subheader("Select Agents")
        agent_options = {
            "syntax": st.checkbox("Syntax Analyzer", value=True, key="agent_syntax"),
            "security": st.checkbox("Security Agent", value=True, key="agent_security"),
            "performance": st.checkbox(
                "Performance Agent", value=True, key="agent_performance"
            ),
            "style": st.checkbox("Style Agent", value=True, key="agent_style"),
            "best_practices": st.checkbox(
                "Best Practices Agent", value=True, key="agent_best_practices"
            ),
            "documentation": st.checkbox(
                "Documentation Agent", value=True, key="agent_documentation"
            ),
        }

        selected_agents = [name for name, selected in agent_options.items() if selected]

        st.divider()

        st.subheader("About")
        st.info("""
        This system uses specialized AI agents to review your code:
        
        - **Syntax**: Basic errors and structure
        - **Security**: Vulnerabilities and risks
        - **Performance**: Bottlenecks and optimization
        - **Style**: Code conventions
        - **Best Practices**: Design patterns
        - **Documentation**: Docstrings and comments
        """)

    # Main content
    tab1, tab2, tab3 = st.tabs(["Code Input", "Review Results", "Report"])

    with tab1:
        render_code_input(selected_agents, language)

    with tab2:
        render_review_results()

    with tab3:
        render_report()


def render_code_input(selected_agents: list, language: str):
    """Render code input interface."""
    st.header("Input Code for Review")

    # Input method selection
    input_method = st.radio(
        "Input Method",
        ["Text Input", "File Upload"],
        horizontal=True,
        key="input_method",
    )

    code = ""

    if input_method == "Text Input":
        code = st.text_area(
            "Paste your code here",
            height=400,
            placeholder="def example():\n    pass",
            key="code_input",
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload code file",
            type=["py", "js", "ts", "java", "cpp", "go", "txt"],
            key="file_upload",
        )

        if uploaded_file:
            code = uploaded_file.read().decode("utf-8")
            st.code(code[:500] + "..." if len(code) > 500 else code, language=language)

    # Review button
    if st.button("Start Code Review", type="primary", use_container_width=True):
        if not code or not code.strip():
            st.warning("Please enter or upload code to review.")
            return

        if not selected_agents:
            st.warning("Please select at least one agent to run.")
            return

        with st.spinner("Reviewing code... This may take a few minutes."):
            try:
                result = st.session_state.orchestrator.review(
                    code=code, language=language, include_agents=selected_agents
                )

                st.session_state.review_result = result
                st.success("Code review complete!")
                st.rerun()

            except Exception as e:
                st.error(f"Review failed: {str(e)}")
                st.exception(e)

                error_msg = str(e).lower()
                if "api key" in error_msg:
                    st.info(
                        "Tip: Make sure your Gemini API key is set in the .env file."
                    )
                elif "timeout" in error_msg:
                    st.info(
                        "Tip: The request timed out. Try again or simplify your code."
                    )
                elif "rate limit" in error_msg:
                    st.info(
                        "Tip: API rate limit exceeded. Please wait a moment and try again."
                    )


def render_review_results():
    """Render review results."""
    st.header("Review Results")

    if not st.session_state.review_result:
        st.info("No review results yet. Go to 'Code Input' tab to start a review.")
        return

    result = st.session_state.review_result
    summary = result.get("summary", {})

    # Overall summary
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Overall Score", f"{summary.get('overall_score', 0):.1f}/10")

    with col2:
        st.metric("Total Issues", summary.get("total_issues", 0))

    with col3:
        st.metric("Critical Issues", summary.get("critical_issues", 0))

    with col4:
        st.metric("High Issues", summary.get("high_issues", 0))

    st.divider()

    # Agent results
    agent_results = result.get("agent_results", {})

    # Syntax
    if "syntax" in agent_results and not agent_results["syntax"].get("skipped"):
        with st.expander("Syntax Analysis", expanded=True):
            syntax = agent_results["syntax"]
            if syntax.get("syntax_valid"):
                st.success("Syntax is valid")
            else:
                st.error("Syntax errors detected")
                for issue in syntax.get("issues", [])[:10]:
                    st.write(
                        f"**Line {issue.get('line', '?')}:** {issue.get('message', 'Unknown error')}"
                    )

    # Security
    if "security" in agent_results and not agent_results["security"].get("skipped"):
        with st.expander("Security Analysis", expanded=True):
            security = agent_results["security"]
            score = security.get("security_score", 0)
            st.metric("Security Score", f"{score:.1f}/10")

            vulns = security.get("vulnerabilities", [])
            if vulns:
                st.warning(f"Found {len(vulns)} security vulnerabilities")
                for vuln in vulns[:10]:
                    severity = vuln.get("severity", "medium")
                    severity_color = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢",
                    }.get(severity, "⚪")

                    st.write(
                        f"{severity_color} **{severity.upper()}:** {vuln.get('message', 'Unknown')}"
                    )
                    if vuln.get("line"):
                        st.caption(f"Line {vuln['line']}")
            else:
                st.success("No security vulnerabilities detected")

    # Performance
    if "performance" in agent_results and not agent_results["performance"].get(
        "skipped"
    ):
        with st.expander("Performance Analysis"):
            performance = agent_results["performance"]
            score = performance.get("performance_score", 0)
            st.metric("Performance Score", f"{score:.1f}/10")

            issues = performance.get("issues", [])
            if issues:
                for issue in issues[:10]:
                    impact = issue.get("impact", "medium")
                    st.write(
                        f"**{impact.upper()} Impact:** {issue.get('message', 'Unknown')}"
                    )
                    if issue.get("line"):
                        st.caption(f"Line {issue['line']}")
            else:
                st.success("No performance issues detected")

    # Style
    if "style" in agent_results and not agent_results["style"].get("skipped"):
        with st.expander("Style Review"):
            style = agent_results["style"]
            score = style.get("style_score", 0)
            st.metric("Style Score", f"{score:.1f}/10")

            issues = style.get("issues", [])
            if issues:
                for issue in issues[:10]:
                    severity = issue.get("severity", "minor")
                    st.write(
                        f"**{severity.upper()}:** {issue.get('message', 'Unknown')}"
                    )
                    if issue.get("line"):
                        st.caption(f"Line {issue['line']}")
            else:
                st.success("Code style is good")

    # Best Practices
    if "best_practices" in agent_results and not agent_results["best_practices"].get(
        "skipped"
    ):
        with st.expander("Best Practices Review"):
            bp = agent_results["best_practices"]
            score = bp.get("best_practices_score", 0)
            st.metric("Best Practices Score", f"{score:.1f}/10")

            issues = bp.get("issues", [])
            if issues:
                for issue in issues[:10]:
                    st.write(
                        f"**{issue.get('category', 'General')}:** {issue.get('message', 'Unknown')}"
                    )
                    if issue.get("line"):
                        st.caption(f"Line {issue['line']}")
            else:
                st.success("Code follows best practices")

    # Documentation
    if "documentation" in agent_results and not agent_results["documentation"].get(
        "skipped"
    ):
        with st.expander("Documentation Review"):
            doc = agent_results["documentation"]
            score = doc.get("documentation_score", 0)
            st.metric("Documentation Score", f"{score:.1f}/10")

            doc_stats = doc.get("docstring_stats", {})
            if doc_stats:
                coverage = doc_stats.get("coverage_percentage", 0)
                st.metric("Docstring Coverage", f"{coverage:.1f}%")

            issues = doc.get("issues", [])
            if issues:
                for issue in issues[:10]:
                    st.write(
                        f"**{issue.get('severity', 'medium').upper()}:** {issue.get('message', 'Unknown')}"
                    )
                    if issue.get("line"):
                        st.caption(f"Line {issue['line']}")
            else:
                st.success("Documentation is adequate")


def render_report():
    """Render generated report."""
    st.header("Review Report")

    if not st.session_state.review_result:
        st.info("No review results yet. Go to 'Code Input' tab to start a review.")
        return

    result = st.session_state.review_result

    # Report format selection
    col1, col2 = st.columns([3, 1])

    with col2:
        report_format = st.selectbox(
            "Report Format", ["Markdown", "Text", "JSON"], key="report_format"
        )

    # Generate report
    report_generator = ReportGenerator()
    format_map = {"Markdown": "markdown", "Text": "text", "JSON": "json"}
    report = report_generator.generate_report(
        result, format_type=format_map[report_format]
    )

    # Display report
    if report_format == "JSON":
        st.json(result)
    elif report_format == "Markdown":
        st.markdown(report)
    else:
        st.text(report)

    # Download button
    st.download_button(
        label=f"Download Report as {report_format}",
        data=report,
        file_name=f"code_review_report.{report_format.lower()}",
        mime="text/plain" if report_format != "JSON" else "application/json",
        use_container_width=True,
    )

    # Metrics display
    st.divider()
    st.subheader("Code Metrics")

    metrics = result.get("metrics", {})
    if metrics:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Lines", metrics.get("total_lines", 0))

        with col2:
            st.metric("Code Lines", metrics.get("code_lines", 0))

        with col3:
            st.metric("Comment Lines", metrics.get("comment_lines", 0))

        with col4:
            st.metric("Avg Line Length", f"{metrics.get('average_line_length', 0):.1f}")


if __name__ == "__main__":
    main()
