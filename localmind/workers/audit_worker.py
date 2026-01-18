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


# Default scoring parameters with weights
# Each parameter scored 0-10, weighted by importance
# Total weighted max = 100 (when all weights sum to 10.0)
DEFAULT_PARAMETERS = [
    {"name": "greeting", "max_score": 10, "weight": 0.7, "description": "Proper greeting and introduction"},
    {"name": "active_listening", "max_score": 10, "weight": 1.1, "description": "Demonstrates active listening skills"},
    {"name": "problem_identification", "max_score": 10, "weight": 1.1, "description": "Correctly identifies customer issue"},
    {"name": "solution_provided", "max_score": 10, "weight": 1.5, "description": "Provides appropriate solution"},
    {"name": "product_knowledge", "max_score": 10, "weight": 1.1, "description": "Demonstrates product knowledge"},
    {"name": "communication_clarity", "max_score": 10, "weight": 0.8, "description": "Clear and professional communication"},
    {"name": "empathy", "max_score": 10, "weight": 0.8, "description": "Shows empathy and understanding"},
    {"name": "call_control", "max_score": 10, "weight": 0.7, "description": "Maintains control of conversation"},
    {"name": "closing", "max_score": 10, "weight": 0.7, "description": "Proper call closing and next steps"},
    {"name": "compliance", "max_score": 10, "weight": 1.5, "description": "Follows required compliance scripts"},
]
# Total weights: 0.7+1.1+1.1+1.5+1.1+0.8+0.8+0.7+0.7+1.5 = 10.0
# Total weighted max score: 10 * 10.0 = 100


def create_audit_json_schema(parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create JSON schema for audit results based on parameters.

    This schema is used for constrained generation to guarantee valid JSON output.
    Each parameter is scored from 0 to max_score (typically 0-10).
    Weights are applied after scoring to calculate weighted total out of 100.
    """
    # Build parameter_scores schema with all parameter names
    parameter_properties = {}
    required_params = []

    for param in parameters:
        param_name = param["name"]
        max_score = param.get("max_score", 10)

        parameter_properties[param_name] = {
            "type": "object",
            "properties": {
                "score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": max_score,
                    "description": f"Score from 0 to {max_score}",
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


def create_single_shot_audit_prompt(parameters: List[Dict[str, Any]]) -> str:
    """Create single-shot audit prompt for powerful API models (GPT-4, Claude, etc.).

    Args:
        parameters: List of scoring parameters with max_score and weight

    Returns:
        Optimized single-shot prompt for API models
    """
    # Build parameter list
    param_list = "\n".join(
        f"- **{p['name']}** (0-{p.get('max_score', 10)}, weight: {p.get('weight', 1.0)}): {p['description']}"
        for p in parameters
    )

    return f"""You are an expert call quality auditor. Analyze and score this customer service call.

## PARAMETERS TO SCORE

{param_list}

## SCORING GUIDELINES

**Final weighted score ranges (out of 100):**
- **70-85/100 = GOOD** - Professional, competent service (most calls)
- **85-100/100 = EXCELLENT** - Exceptional service
- **50-65/100 = ACCEPTABLE** - Adequate but needs improvement
- **30-45/100 = BELOW AVERAGE** - Significant issues
- **0-25/100 = POOR** - Unacceptable performance

**How to score each parameter (0-10 scale):**
- 8-9 = Good professional performance
- 9-10 = Excellent/exceptional
- 6-7 = Acceptable with gaps
- 3-5 = Below average
- 0-2 = Poor/unacceptable

## OUTPUT FORMAT

Return valid JSON with:
- `parameter_scores`: Object with each parameter scored (score + feedback)
- `strengths`: Array of 2-4 key strengths observed
- `improvements`: Array of 2-4 areas for improvement
- `summary`: Brief overall assessment (2-3 sentences)

**Important**: Professional calls typically score 70-85/100 overall. Only score below 50 if there are serious issues."""


def create_cot_analysis_prompt() -> str:
    """Create Chain-of-Thought analysis prompt for reasoning phase.

    Returns:
        Prompt for LLM to analyze call before scoring
    """
    return """You are a call quality expert. Analyze this customer service call carefully.

## Your Task

Read the transcript and think through these questions step-by-step:

1. **Opening & Greeting**: How did the agent start the call? Was it professional and warm?

2. **Listening & Understanding**: Did the agent listen well? Did they understand the customer's needs?

3. **Problem Solving**: How well did they identify and solve the customer's issue?

4. **Communication**: Was the agent clear, professional, and easy to understand?

5. **Customer Experience**: How did the customer likely feel during this call?

6. **Closing**: How did the call end? Were next steps clear?

## Instructions

Write a detailed analysis covering what the agent did well and what needs improvement. Be specific with examples from the transcript.

Focus on observable behaviors, not assumptions. This analysis will be used to score the call accurately."""


def create_audit_prompt(parameters: List[Dict[str, Any]], analysis: str, model_name: str = "phi-3.5-mini") -> str:
    """Create universal audit prompt that works with all local LLMs.

    Args:
        parameters: List of scoring parameters with max_score and weight
        analysis: Chain-of-thought analysis from reasoning phase
        model_name: Name of the LLM model (informational only)

    Returns:
        Universal prompt string optimized for local LLMs
    """
    # Build parameter list with max scores and weights
    param_list = "\n".join(
        f"- **{p['name']}** (0-{p.get('max_score', 10)} scale, weight: {p.get('weight', 1.0)}): {p['description']}"
        for p in parameters
    )

    # Create realistic example scores for a GOOD professional call
    # Most parameters should score 7-9 out of 10 for good service
    example_scores = {}
    for p in parameters:
        max_score = p.get("max_score", 10)
        # Good professional service = 70-85% of max (7-8.5 out of 10)
        example_score = round(max_score * 0.8, 1)  # 8 out of 10 as baseline
        example_scores[p['name']] = {
            "score": example_score,
            "feedback": f"Professional performance with minor areas for improvement"
        }

    # Format example scores as JSON string
    example_scores_json = []
    for name, data in example_scores.items():
        example_scores_json.append(f'    "{name}": {{"score": {data["score"]}, "feedback": "{data["feedback"]}"}}')
    example_scores_str = ",\n".join(example_scores_json)

    return f"""You are a call quality auditor. Based on the analysis below, score each parameter.

## ANALYSIS FROM REASONING PHASE

{analysis}

## NOW SCORE BASED ON THIS ANALYSIS

## SCORING SYSTEM

Each parameter is scored 0-10, then weighted and combined for a final score out of 100.

**What each score means (final weighted score out of 100):**
- **70-80/100 = GOOD** ← Most professional calls score here
- **85-100/100 = EXCELLENT** - Exceptional service
- **50-60/100 = ACCEPTABLE** - Adequate but needs work
- **30-40/100 = BELOW AVERAGE** - Significant issues
- **0-20/100 = POOR** - Unacceptable, only for truly terrible calls

## PARAMETERS (scored 0 to max, weighted by importance)

{param_list}

## EXAMPLE: Good Professional Call (final score: ~80/100)

Score each parameter honestly, aiming for 7-9 out of 10 for professional service:

```json
{{
  "parameter_scores": {{
{example_scores_str}
  }},
  "strengths": ["Clear communication", "Good problem resolution", "Professional tone"],
  "improvements": ["Could probe deeper", "Closing could be stronger"],
  "summary": "Professional call with effective service delivery"
}}
```

**This example would score approximately 80/100 after weighting = GOOD professional service.**

## CRITICAL RULES

1. **Professional calls score 70-85 out of 100 overall** - NOT 10 out of 100!
2. **70-80 out of 100 = GOOD service** - This is the norm for competent agents
3. **10-20 out of 100 = TERRIBLE** - Only use for truly unacceptable calls
4. **Score realistically** - A good call with minor flaws should score 75-80 out of 100, not 10 out of 100!
5. **Provide specific feedback** for each parameter

## OUTPUT

Return ONLY valid JSON (no markdown, no explanations):

{{
  "parameter_scores": {{ ...all parameters with score and feedback... }},
  "strengths": ["strength 1", "strength 2"],
  "improvements": ["improvement 1", "improvement 2"],
  "summary": "brief assessment"
}}"""


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
        """Use LLM to audit the transcript.

        Uses Chain-of-Thought (CoT) for local models, single-shot for API models.
        """
        from localmind.llm import create_provider, LLMConfig

        self.report_progress(20, "Loading LLM provider...")

        provider = create_provider()
        await provider.initialize()

        # Detect provider type
        provider_name = provider.provider_name.lower()
        use_cot = provider_name == "local"

        if use_cot:
            # Local models benefit from Chain-of-Thought reasoning
            return await self._llm_audit_with_cot(provider)
        else:
            # API models (GPT-4, Claude, Groq) are powerful enough for single-shot
            return await self._llm_audit_single_shot(provider)

    async def _llm_audit_with_cot(self, provider) -> AuditResult:
        """Use Chain-of-Thought reasoning for local LLMs (2-phase approach)."""
        from localmind.llm import LLMConfig

        try:
            self.report_progress(30, "Analyzing transcript...")

            # Get model name
            model_name = getattr(provider, '_model', 'phi-3.5-mini')
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

            # ========== PHASE 1: Chain-of-Thought Analysis ==========
            self.report_progress(40, "Reasoning phase: Analyzing call quality...")

            cot_prompt = create_cot_analysis_prompt()
            cot_messages = [
                provider.create_system_message(cot_prompt),
                provider.create_user_message(f"Analyze this call transcript:\n\n{transcript}"),
            ]

            # Generate analysis with higher temperature for reasoning
            cot_config = LLMConfig(
                temperature=0.7,
                max_tokens=800,  # Detailed analysis
            )

            analysis_response = await provider.generate(cot_messages, cot_config)
            analysis = analysis_response.get("content", "No analysis generated")

            self.report_progress(55, "Analysis complete. Now scoring...")

            # ========== PHASE 2: Structured Scoring (based on analysis) ==========
            scoring_prompt = create_audit_prompt(self._parameters, analysis, model_name)
            scoring_messages = [
                provider.create_system_message(scoring_prompt),
                provider.create_user_message(
                    "Based on the analysis above, provide structured scores for each parameter."
                ),
            ]

            # Create JSON schema for constrained generation
            json_schema = create_audit_json_schema(self._parameters)

            # Use lower temperature for consistent scoring
            scoring_config = LLMConfig(
                temperature=0.3,
                max_tokens=1200,
                json_mode=True,
                json_schema=json_schema,
            )

            self.report_progress(70, "Generating scores (CoT-enhanced)...")

            response_data = await provider.generate_json(scoring_messages, scoring_config)

            self.report_progress(80, "Processing audit results...")

            # Parse parameter scores (now using points out of 100 total)
            parameter_scores = []
            param_data = response_data.get("parameter_scores", {})

            for param in self._parameters:
                name = param["name"]
                score_data = param_data.get(name, {})
                max_score = param.get("max_score", 10)
                weight = param.get("weight", 1.0)

                parameter_scores.append(ParameterScore(
                    name=name,
                    score=float(score_data.get("score", 0)),
                    max_score=float(max_score),
                    weight=float(weight),
                    feedback=score_data.get("feedback", ""),
                ))

            # Calculate overall scores using weighted system
            # Each score is multiplied by its weight, then summed
            total_score = sum(p.score * p.weight for p in parameter_scores)
            total_max = sum(p.max_score * p.weight for p in parameter_scores)

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

    async def _llm_audit_single_shot(self, provider) -> AuditResult:
        """Use single-shot prompting for powerful API models (GPT-4, Claude, etc.)."""
        from localmind.llm import LLMConfig

        try:
            self.report_progress(30, "Analyzing transcript...")

            # Get model name
            model_name = getattr(provider, '_model', 'gpt-4')
            transcript = self._merge_result.merged_text

            # Truncate long transcripts to fit context window
            max_transcript_chars = 10000  # ~2850 tokens

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

            # Single-shot prompt (no CoT analysis phase)
            # API models are powerful enough to reason internally
            system_prompt = create_single_shot_audit_prompt(self._parameters)
            messages = [
                provider.create_system_message(system_prompt),
                provider.create_user_message(
                    f"Analyze and score this call transcript:\n\n{transcript}"
                ),
            ]

            # Create JSON schema for constrained generation
            json_schema = create_audit_json_schema(self._parameters)

            # Use moderate temperature for API models
            config = LLMConfig(
                temperature=0.5,
                max_tokens=1536,
                json_mode=True,
                json_schema=json_schema,
            )

            self.report_progress(50, "Generating audit scores...")

            response_data = await provider.generate_json(messages, config)

            self.report_progress(80, "Processing audit results...")

            # Parse parameter scores
            parameter_scores = []
            param_data = response_data.get("parameter_scores", {})

            for param in self._parameters:
                name = param["name"]
                score_data = param_data.get(name, {})
                max_score = param.get("max_score", 10)
                weight = param.get("weight", 1.0)

                parameter_scores.append(ParameterScore(
                    name=name,
                    score=float(score_data.get("score", 0)),
                    max_score=float(max_score),
                    weight=float(weight),
                    feedback=score_data.get("feedback", ""),
                ))

            # Calculate overall scores using weighted system
            total_score = sum(p.score * p.weight for p in parameter_scores)
            total_max = sum(p.max_score * p.weight for p in parameter_scores)

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
