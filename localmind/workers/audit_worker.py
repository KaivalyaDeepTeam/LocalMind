"""
LocalMind Audit Worker

Background worker for quality auditing using LLM.
"""

import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

from localmind.workers.base import BaseWorker
from localmind.workers.merge_worker import MergeResult


@dataclass
class ParameterScore:
    """Score for a single parameter."""
    name: str
    score: float
    max_score: float
    weight: float = 1.0
    feedback: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "score": self.score,
            "max_score": self.max_score,
            "weight": self.weight,
            "feedback": self.feedback,
        }

    @property
    def weighted_score(self) -> float:
        """Get weighted score."""
        return self.score * self.weight

    @property
    def weighted_max(self) -> float:
        """Get weighted max score."""
        return self.max_score * self.weight


@dataclass
class AuditResult:
    """Result of quality audit."""
    overall_score: float
    max_score: float
    parameter_scores: List[ParameterScore] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    summary: str = ""
    compliance_score: float = 0.0
    quality_score: float = 0.0
    transcript: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "overall_score": self.overall_score,
            "max_score": self.max_score,
            "percentage": self.percentage,
            "normalized_score": self.percentage,  # Alias for clarity
            "compliance_score": self.compliance_score,
            "quality_score": self.quality_score,
            "parameter_scores": {p.name: p.to_dict() for p in self.parameter_scores},
            "strengths": self.strengths,
            "improvements": self.improvements,
            "summary": self.summary,
            "transcript": self.transcript,
            "markdown_report": self.generate_markdown_report(),  # Add markdown report
            "feedback": {
                "summary": self.summary,
                "strengths": self.strengths,
                "improvements": self.improvements,
            },
            "scores": {p.name: {"score": p.score, "max": p.max_score, "weight": p.weight}
                      for p in self.parameter_scores},
        }

    @property
    def percentage(self) -> float:
        """Get score as percentage."""
        if self.max_score == 0:
            return 0.0
        return (self.overall_score / self.max_score) * 100

    def generate_markdown_report(self) -> str:
        """Generate a beautiful markdown report for the audit results.

        Creates a human-readable report with scores, feedback, and improvement suggestions.
        Goal: Help users read and improve their calls/selling/support skills.

        Returns:
            Formatted markdown string with complete audit feedback.
        """
        percentage = self.percentage

        # Determine performance level and emoji
        if percentage >= 85:
            level = "Excellent Performance"
            emoji = "🌟"
        elif percentage >= 70:
            level = "Good Performance"
            emoji = "✅"
        elif percentage >= 55:
            level = "Acceptable Performance"
            emoji = "👍"
        elif percentage >= 40:
            level = "Below Average"
            emoji = "⚠️"
        else:
            level = "Needs Improvement"
            emoji = "❌"

        # Build markdown report
        lines = [
            "# 📞 Call Quality Audit Report",
            "",
            f"**Overall Score: {self.overall_score:.1f}/{self.max_score:.0f}** ({percentage:.1f}%)",
            f"**Performance Level: {emoji} {level}**",
            "",
        ]

        # Add compliance and quality subscores if available
        if self.compliance_score > 0 or self.quality_score > 0:
            lines.extend([
                "## 📊 Score Breakdown",
                "",
            ])
            if self.compliance_score > 0:
                lines.append(f"- **Compliance Score:** {self.compliance_score:.1f}%")
            if self.quality_score > 0:
                lines.append(f"- **Quality Score:** {self.quality_score:.1f}%")
            lines.append("")

        # Parameter scores section
        lines.extend([
            "## 📋 Detailed Parameter Scores",
            "",
        ])

        for param in self.parameter_scores:
            param_percentage = (param.score / param.max_score * 100) if param.max_score > 0 else 0

            # Choose emoji based on parameter score
            if param_percentage >= 85:
                param_emoji = "🌟"
            elif param_percentage >= 70:
                param_emoji = "✅"
            elif param_percentage >= 55:
                param_emoji = "👍"
            else:
                param_emoji = "⚠️"

            # Format parameter name (capitalize and replace underscores)
            param_name = param.name.replace("_", " ").title()

            lines.extend([
                f"### {param_emoji} {param_name}: {param.score:.1f}/{param.max_score:.0f} ({param_percentage:.0f}%)",
                "",
            ])

            if param.feedback:
                lines.extend([
                    f"**Feedback:** {param.feedback}",
                    "",
                ])

        # Strengths section
        if self.strengths:
            lines.extend([
                "## ✨ Key Strengths",
                "",
            ])
            for strength in self.strengths:
                lines.append(f"- {strength}")
            lines.append("")

        # Improvements section
        if self.improvements:
            lines.extend([
                "## 🎯 Areas for Improvement",
                "",
            ])
            for improvement in self.improvements:
                lines.append(f"- {improvement}")
            lines.append("")

        # Summary section
        if self.summary:
            lines.extend([
                "## 📝 Summary",
                "",
                self.summary,
                "",
            ])

        # Footer with encouragement
        lines.extend([
            "---",
            "",
            "_This report is generated to help you improve your communication skills._",
            "_Focus on the areas for improvement while building on your strengths._",
        ])

        return "\n".join(lines)


# Default scoring parameters - Total points = 100
# Each parameter has points allocated based on importance
DEFAULT_PARAMETERS = [
    {"name": "greeting", "points": 7, "description": "Proper greeting and introduction"},
    {"name": "active_listening", "points": 11, "description": "Demonstrates active listening skills"},
    {"name": "problem_identification", "points": 11, "description": "Correctly identifies customer issue"},
    {"name": "solution_provided", "points": 15, "description": "Provides appropriate solution"},
    {"name": "product_knowledge", "points": 11, "description": "Demonstrates product knowledge"},
    {"name": "communication_clarity", "points": 8, "description": "Clear and professional communication"},
    {"name": "empathy", "points": 8, "description": "Shows empathy and understanding"},
    {"name": "call_control", "points": 7, "description": "Maintains control of conversation"},
    {"name": "closing", "points": 7, "description": "Proper call closing and next steps"},
    {"name": "compliance", "points": 15, "description": "Follows required compliance scripts"},
]
# Total: 7+11+11+15+11+8+8+7+7+15 = 100 points


def create_audit_json_schema(parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create JSON schema for audit results based on parameters.

    This schema is used for constrained generation to guarantee valid JSON output.
    Scores are out of the points allocated to each parameter (total = 100).
    """
    # Build parameter_scores schema with all parameter names
    parameter_properties = {}
    required_params = []

    for param in parameters:
        param_name = param["name"]
        max_points = param.get("points", param.get("max_score", 10))  # Support both formats

        parameter_properties[param_name] = {
            "type": "object",
            "properties": {
                "score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": max_points,
                    "description": f"Score from 0 to {max_points} points",
                },
                "feedback": {
                    "type": "string",
                    "description": "Brief explanation of the score",
                },
            },
            "required": ["score", "feedback"],
        }
        required_params.append(param_name)

    # Complete JSON schema
    schema = {
        "type": "object",
        "properties": {
            "parameter_scores": {
                "type": "object",
                "properties": parameter_properties,
                "required": required_params,
                "additionalProperties": False,
            },
            "strengths": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 2,
                "maxItems": 4,
                "description": "List of 2-4 strengths",
            },
            "improvements": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 2,
                "maxItems": 4,
                "description": "List of 2-4 areas for improvement",
            },
            "summary": {
                "type": "string",
                "description": "Brief overall assessment of call quality",
            },
        },
        "required": ["parameter_scores", "strengths", "improvements", "summary"],
        "additionalProperties": False,
    }

    return schema


def create_audit_prompt(parameters: List[Dict[str, Any]], model_name: str = "phi-3.5-mini") -> str:
    """Create optimized audit prompt based on parameters and model.

    Args:
        parameters: List of scoring parameters with points allocated
        model_name: Name of the LLM model for optimization

    Returns:
        Optimized prompt string for the specific model
    """
    # Calculate total points
    total_points = sum(p.get("points", p.get("max_score", 10)) for p in parameters)

    # Build parameter list with points
    param_list = "\n".join(
        f"- **{p['name']}**: {p['description']} "
        f"(Max: {p.get('points', p.get('max_score', 10))} points)"
        for p in parameters
    )

    # Create realistic example scores for a good call (70-85% range)
    example_scores = {}
    for p in parameters:
        max_pts = p.get("points", p.get("max_score", 10))
        # Good performance = 75-85% of max points
        example_score = int(max_pts * 0.8)  # 80% as baseline
        example_scores[p['name']] = f'{{"score": {example_score}, "feedback": "Good performance with room for improvement"}}'

    example_scores_str = ",\n    ".join(f'"{name}": {score}' for name, score in example_scores.items())

    # Model-specific optimizations and chat format
    if "qwen" in model_name.lower():
        chat_start = "<|system|>"
        chat_end = "<|end|>"
        format_note = "Note: Qwen models excel at JSON output - use your strength!"
    elif "mistral" in model_name.lower():
        chat_start = "[INST]"
        chat_end = "[/INST]"
        format_note = "CRITICAL: Mistral, score realistically! A good professional call scores 70-85%, NOT 10%!"
    else:  # phi-3.5-mini and others
        chat_start = "<|system|>"
        chat_end = "<|end|>"
        format_note = "Note: Return ONLY the JSON object, no code blocks or explanations"

    return f"""{chat_start}
You are a professional call quality auditor. Your task is to score a customer service call.

## SCORING SYSTEM

**Total Points Available: {total_points}**

Each parameter below has a maximum point allocation. Score honestly based on actual performance.

### Parameters:
{param_list}

## SCORING GUIDELINES

**Overall Target Ranges:**
- 85-100: Excellent (exceptional service, minimal issues)
- 70-84: Good (professional, effective service)
- 55-69: Acceptable (adequate but needs improvement)
- 40-54: Below Average (significant issues present)
- 0-39: Poor (unacceptable performance)

**How to Score Each Parameter:**
1. Award **full points** if performance is excellent
2. Award **75-85%** of points for good professional performance
3. Award **50-70%** for acceptable but flawed performance
4. Award **25-50%** for below average performance
5. Award **0-25%** for poor/unacceptable performance

## REALISTIC EXAMPLE

A professional sales call with good rapport and service should score **70-85%** overall:

```json
{{
  "parameter_scores": {{
    {example_scores_str}
  }},
  "strengths": ["Clear product explanation", "Addressed customer concerns", "Professional tone throughout"],
  "improvements": ["Could ask more qualifying questions", "Closing could be stronger"],
  "summary": "Professional call with good product knowledge and customer engagement"
}}
```

## COMMON MISTAKE TO AVOID

**WRONG (10% = terrible service):**
```json
{{
  "parameter_scores": {{
    "greeting": {{"score": 1, "feedback": "..."}},
    "active_listening": {{"score": 1, "feedback": "..."}},
    "problem_identification": {{"score": 1, "feedback": "..."}},
    ...
  }}
}}
```
This is 10/100 = 10% = UNACCEPTABLE SERVICE. Only use this for truly terrible calls.

**CORRECT (80% = good professional service):**
```json
{{
  "parameter_scores": {{
    "greeting": {{"score": 6, "feedback": "Professional greeting"}},
    "active_listening": {{"score": 9, "feedback": "Good listening"}},
    "problem_identification": {{"score": 9, "feedback": "Identified issue"}},
    ...
  }}
}}
```
This is 80/100 = 80% = GOOD SERVICE. Use this range for professional calls.

## OUTPUT REQUIREMENTS

{format_note}

Return ONLY this JSON structure:

{{
  "parameter_scores": {{
    "greeting": {{"score": X, "feedback": "..."}},
    "active_listening": {{"score": X, "feedback": "..."}},
    ...all {len(parameters)} parameters...
  }},
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "improvements": ["improvement 1", "improvement 2"],
  "summary": "brief overall assessment"
}}

**Critical Rules:**
- Scores must be realistic (professional calls score 70-85%, NOT 10%)
- DO NOT score everything as 1 point - that means 10% which is TERRIBLE
- A good call should get 6-7 points out of 7, 9-11 out of 11, 12-15 out of 15
- If the call is professional, score it 70-85% of each parameter's max
- Each score reflects actual performance vs. maximum points
- Provide specific, actionable feedback for each parameter
- List 2-4 concrete strengths and improvements

REMEMBER: Professional calls = 70-85% overall, NOT 10%!
{chat_end}"""


class AuditWorker(BaseWorker):
    """Worker for auditing call quality."""

    def __init__(
        self,
        merge_result: MergeResult,
        parameters: Optional[List[Dict[str, Any]]] = None,
        parent=None,
    ):
        """Initialize audit worker.

        Args:
            merge_result: Merged transcript result.
            parameters: Scoring parameters (uses defaults if None).
            parent: Parent QObject.
        """
        super().__init__(parent)
        self._merge_result = merge_result
        self._parameters = parameters or DEFAULT_PARAMETERS
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def do_work(self) -> AuditResult:
        """Perform quality audit."""
        self.report_progress(0, "Preparing audit...")

        if self.check_stop():
            return None

        self.report_progress(10, "Initializing LLM for audit...")
        self.check_pause()

        if self.check_stop():
            return None

        # Run async LLM call in sync context
        self._loop = asyncio.new_event_loop()
        try:
            result = self._loop.run_until_complete(self._llm_audit())
        finally:
            self._loop.close()
            self._loop = None

        self.report_progress(100, "Audit complete")
        return result

    async def _llm_audit(self) -> AuditResult:
        """Use LLM to audit the transcript."""
        from localmind.llm import create_provider, LLMConfig

        self.report_progress(20, "Loading LLM provider...")

        provider = create_provider()
        await provider.initialize()

        try:
            self.report_progress(30, "Analyzing transcript...")

            # Get model name for optimized prompt
            model_name = getattr(provider, '_model', 'phi-3.5-mini')
            system_prompt = create_audit_prompt(self._parameters, model_name)
            transcript = self._merge_result.merged_text

            # Truncate long transcripts to fit context window
            # Estimate ~3.5 chars per token, leave room for prompt
            max_transcript_chars = 10000  # ~2850 tokens (safe for 4K-8K context models)

            if len(transcript) > max_transcript_chars:
                # Sample beginning (greeting), middle (main), end (closing)
                part_size = max_transcript_chars // 3

                begin = transcript[:part_size]
                middle_start = (len(transcript) - part_size) // 2
                middle = transcript[middle_start:middle_start + part_size]
                end = transcript[-part_size:]

                transcript = (
                    f"[CALL BEGINNING]\n{begin}\n\n"
                    f"[CALL MIDDLE - Representative Sample]\n{middle}\n\n"
                    f"[CALL ENDING]\n{end}"
                )
                self.report_progress(35, "Long call - sampling key sections...")

            messages = [
                provider.create_system_message(system_prompt),
                provider.create_user_message(
                    f"<|user|>\nPlease audit this call transcript:\n\n{transcript}\n<|end|>"
                ),
            ]

            # Create JSON schema for constrained generation
            json_schema = create_audit_json_schema(self._parameters)

            config = LLMConfig(
                temperature=0.3,
                json_mode=True,
                json_schema=json_schema,  # Use schema-based constrained generation
            )

            self.report_progress(50, "Generating audit scores (schema-constrained)...")

            response_data = await provider.generate_json(messages, config)

            self.report_progress(80, "Processing audit results...")

            # Parse parameter scores (now using points out of 100 total)
            parameter_scores = []
            param_data = response_data.get("parameter_scores", {})

            for param in self._parameters:
                name = param["name"]
                score_data = param_data.get(name, {})
                max_points = param.get("points", param.get("max_score", 10))

                parameter_scores.append(ParameterScore(
                    name=name,
                    score=float(score_data.get("score", 0)),
                    max_score=float(max_points),
                    weight=1.0,  # No weighting needed since points already allocated
                    feedback=score_data.get("feedback", ""),
                ))

            # Calculate overall scores (simple sum since points are out of 100)
            total_score = sum(p.score for p in parameter_scores)
            total_max = sum(p.max_score for p in parameter_scores)

            # Calculate compliance and quality subscores
            compliance_params = ["greeting", "closing", "compliance"]
            quality_params = ["active_listening", "problem_identification", "solution_provided",
                            "product_knowledge", "communication_clarity", "empathy", "call_control"]

            compliance_score = self._calculate_subscore(parameter_scores, compliance_params)
            quality_score = self._calculate_subscore(parameter_scores, quality_params)

            return AuditResult(
                overall_score=total_score,
                max_score=total_max,
                parameter_scores=parameter_scores,
                strengths=response_data.get("strengths", []),
                improvements=response_data.get("improvements", []),
                summary=response_data.get("summary", ""),
                compliance_score=compliance_score,
                quality_score=quality_score,
                transcript=transcript,
            )

        finally:
            await provider.close()

    def _calculate_subscore(
        self,
        scores: List[ParameterScore],
        param_names: List[str],
    ) -> float:
        """Calculate subscore for a group of parameters."""
        relevant = [s for s in scores if s.name in param_names]
        if not relevant:
            return 0.0

        total = sum(s.score for s in relevant)
        max_total = sum(s.max_score for s in relevant)

        if max_total == 0:
            return 0.0

        return (total / max_total) * 100
