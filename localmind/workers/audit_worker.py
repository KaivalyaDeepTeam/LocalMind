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


# Default scoring parameters
DEFAULT_PARAMETERS = [
    {"name": "greeting", "max_score": 10, "weight": 1.0, "description": "Proper greeting and introduction"},
    {"name": "active_listening", "max_score": 10, "weight": 1.5, "description": "Demonstrates active listening skills"},
    {"name": "problem_identification", "max_score": 10, "weight": 1.5, "description": "Correctly identifies customer issue"},
    {"name": "solution_provided", "max_score": 10, "weight": 2.0, "description": "Provides appropriate solution"},
    {"name": "product_knowledge", "max_score": 10, "weight": 1.5, "description": "Demonstrates product knowledge"},
    {"name": "communication_clarity", "max_score": 10, "weight": 1.0, "description": "Clear and professional communication"},
    {"name": "empathy", "max_score": 10, "weight": 1.0, "description": "Shows empathy and understanding"},
    {"name": "call_control", "max_score": 10, "weight": 1.0, "description": "Maintains control of conversation"},
    {"name": "closing", "max_score": 10, "weight": 1.0, "description": "Proper call closing and next steps"},
    {"name": "compliance", "max_score": 10, "weight": 2.0, "description": "Follows required compliance scripts"},
]


def create_audit_json_schema(parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create JSON schema for audit results based on parameters.

    This schema is used for constrained generation to guarantee valid JSON output.
    """
    # Build parameter_scores schema with all parameter names
    parameter_properties = {}
    required_params = []

    for param in parameters:
        param_name = param["name"]
        parameter_properties[param_name] = {
            "type": "object",
            "properties": {
                "score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": param["max_score"],
                    "description": f"Score from 0 to {param['max_score']}",
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


def create_audit_prompt(parameters: List[Dict[str, Any]]) -> str:
    """Create the audit system prompt based on parameters."""
    param_list = "\n".join(
        f"- {p['name']}: {p['description']} (Score 0-{p['max_score']})"
        for p in parameters
    )

    # Create realistic example scores (7-9 range for good performance)
    example_scores = {
        p['name']: f'{{"score": {7 + (hash(p["name"]) % 3)}, "feedback": "Good performance with minor areas for improvement"}}'
        for p in parameters
    }
    example_scores_str = ",\n    ".join(f'"{name}": {score}' for name, score in example_scores.items())

    return f"""You are a call quality auditor. Analyze the call transcript and provide scores.

SCORING PARAMETERS:
{param_list}

SCORING GUIDE - Use the FULL 0-10 scale:
• 9-10: Excellent - Exceptional performance, best practices followed
• 7-8: Good - Strong performance with minor improvements possible
• 5-6: Average - Acceptable but needs improvement
• 3-4: Below Average - Significant issues present
• 0-2: Poor - Major problems, unacceptable performance

IMPORTANT: Most typical customer service calls should score in the 6-8 range. Only use very low scores (0-3) for calls with serious problems like rudeness, incorrect information, or policy violations.

YOUR TASK:
1. Read the entire call transcript carefully
2. Score EACH parameter using the FULL 0-10 scale based on actual performance
3. Provide specific feedback explaining each score
4. Identify 2-4 concrete strengths observed in the call
5. Identify 2-4 specific areas for improvement
6. Write a brief overall summary

EXAMPLE - A typical good sales call might score:
{{
  "parameter_scores": {{
    "greeting": {{"score": 8, "feedback": "Professional greeting with name and company"}},
    "active_listening": {{"score": 7, "feedback": "Good acknowledgment but could ask more clarifying questions"}},
    "solution_provided": {{"score": 9, "feedback": "Comprehensive explanation of product benefits and features"}}
  }}
}}

OUTPUT FORMAT - Return ONLY valid JSON (no markdown, no explanations):

{{
  "parameter_scores": {{
    {example_scores_str}
  }},
  "strengths": ["Specific strength 1", "Specific strength 2", "Specific strength 3"],
  "improvements": ["Specific improvement 1", "Specific improvement 2", "Specific improvement 3"],
  "summary": "Brief overall assessment of the call quality and agent performance"
}}

CRITICAL:
- Use realistic scores (most calls score 5-9, not 0-2)
- Score based on ACTUAL performance, not idealized perfection
- Output ONLY the JSON object (no markdown, no extra text)
- All parameter names must match exactly as listed above"""


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

            system_prompt = create_audit_prompt(self._parameters)
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
                    f"Please audit this call transcript:\n\n{transcript}"
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

            # Parse parameter scores
            parameter_scores = []
            param_data = response_data.get("parameter_scores", {})

            for param in self._parameters:
                name = param["name"]
                score_data = param_data.get(name, {})

                parameter_scores.append(ParameterScore(
                    name=name,
                    score=float(score_data.get("score", 0)),
                    max_score=float(param["max_score"]),
                    weight=float(param["weight"]),
                    feedback=score_data.get("feedback", ""),
                ))

            # Calculate overall scores
            total_weighted = sum(p.weighted_score for p in parameter_scores)
            total_max_weighted = sum(p.weighted_max for p in parameter_scores)

            # Calculate compliance and quality subscores
            compliance_params = ["greeting", "closing", "compliance"]
            quality_params = ["active_listening", "problem_identification", "solution_provided",
                            "product_knowledge", "communication_clarity", "empathy", "call_control"]

            compliance_score = self._calculate_subscore(parameter_scores, compliance_params)
            quality_score = self._calculate_subscore(parameter_scores, quality_params)

            return AuditResult(
                overall_score=total_weighted,
                max_score=total_max_weighted,
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
