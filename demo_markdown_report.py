#!/usr/bin/env python3
"""
Demo script showing markdown report generation for audit results.
"""

from localmind.workers.audit_worker import (
    AuditResult,
    ParameterScore,
    DEFAULT_PARAMETERS,
)


def main():
    """Demonstrate markdown report generation."""
    print("=" * 70)
    print("LocalMind Markdown Audit Report Demo")
    print("=" * 70)
    print()

    # Create sample audit result (simulating a good call - 78/100)
    parameter_scores = [
        ParameterScore(
            name="greeting",
            score=6.0,
            max_score=7.0,
            weight=1.0,
            feedback="Warm and professional greeting with proper introduction"
        ),
        ParameterScore(
            name="active_listening",
            score=9.0,
            max_score=11.0,
            weight=1.0,
            feedback="Demonstrated excellent listening skills with appropriate responses"
        ),
        ParameterScore(
            name="problem_identification",
            score=9.5,
            max_score=11.0,
            weight=1.0,
            feedback="Quickly identified customer issue and confirmed understanding"
        ),
        ParameterScore(
            name="solution_provided",
            score=12.0,
            max_score=15.0,
            weight=1.0,
            feedback="Provided clear, comprehensive solution with step-by-step guidance"
        ),
        ParameterScore(
            name="product_knowledge",
            score=8.0,
            max_score=11.0,
            weight=1.0,
            feedback="Good product knowledge with minor gaps in advanced features"
        ),
        ParameterScore(
            name="communication_clarity",
            score=6.5,
            max_score=8.0,
            weight=1.0,
            feedback="Clear communication with some technical jargon that could be simplified"
        ),
        ParameterScore(
            name="empathy",
            score=7.0,
            max_score=8.0,
            weight=1.0,
            feedback="Showed understanding and empathy for customer frustration"
        ),
        ParameterScore(
            name="call_control",
            score=5.0,
            max_score=7.0,
            weight=1.0,
            feedback="Maintained good control with minor instances of losing focus"
        ),
        ParameterScore(
            name="closing",
            score=5.5,
            max_score=7.0,
            weight=1.0,
            feedback="Professional closing but could have been more comprehensive with next steps"
        ),
        ParameterScore(
            name="compliance",
            score=9.5,
            max_score=15.0,
            weight=1.0,
            feedback="Followed most compliance scripts with one minor omission"
        ),
    ]

    # Calculate total score
    total_score = sum(p.score for p in parameter_scores)
    max_score = sum(p.max_score for p in parameter_scores)

    # Create audit result
    result = AuditResult(
        overall_score=total_score,
        max_score=max_score,
        parameter_scores=parameter_scores,
        strengths=[
            "Excellent problem identification and active listening skills",
            "Comprehensive solution with clear step-by-step guidance",
            "Strong empathy and professional demeanor throughout the call",
            "Good compliance with required scripts and procedures"
        ],
        improvements=[
            "Simplify technical language for better customer understanding",
            "Strengthen call closing with more detailed next steps",
            "Improve product knowledge of advanced features"
        ],
        summary=(
            "This was a professional call demonstrating strong customer service fundamentals. "
            "The agent excelled at listening, identifying the problem, and providing a clear solution. "
            "Communication was professional and empathetic. Areas for improvement include simplifying "
            "technical explanations and providing more comprehensive call closings."
        ),
        compliance_score=85.0,
        quality_score=76.0,
    )

    # Generate and print markdown report
    markdown_report = result.generate_markdown_report()

    print("Generated Markdown Report:")
    print("=" * 70)
    print(markdown_report)
    print("=" * 70)
    print()

    print("[+] Markdown report successfully generated!")
    print()
    print("This report can be:")
    print("- Exported to .md file (File > Export Markdown Report)")
    print("- Viewed in any markdown viewer for beautiful formatting")
    print("- Shared with agents for skill improvement feedback")
    print("- Used for training and coaching sessions")
    print()
    print(f"Score: {result.percentage:.1f}% ({result.overall_score:.1f}/{result.max_score:.0f})")


if __name__ == "__main__":
    main()
