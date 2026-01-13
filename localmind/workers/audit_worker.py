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


def create_audit_prompt(parameters: List[Dict[str, Any]]) -> str:
    """Create the audit system prompt based on parameters."""
    param_list = "\n".join(
        f"- {p['name']} (max: {p['max_score']}, weight: {p['weight']}): {p['description']}"
        for p in parameters
    )

    return f"""You are an expert call quality auditor. Analyze the provided call transcript and score it based on the following parameters:

{param_list}

For each parameter, provide:
1. A score from 0 to the max score
2. Brief feedback explaining the score

Also provide:
- Overall strengths (list of 2-4 items)
- Areas for improvement (list of 2-4 items)
- A brief summary of the call quality

Output your analysis as a JSON object with this structure:
{{
  "parameter_scores": {{
    "greeting": {{"score": 8, "feedback": "Good greeting but missed company name"}},
    "active_listening": {{"score": 9, "feedback": "Excellent paraphrasing and acknowledgment"}},
    ...
  }},
  "strengths": ["Strength 1", "Strength 2"],
  "improvements": ["Improvement 1", "Improvement 2"],
  "summary": "Brief overall assessment"
}}

Be fair but rigorous in your assessment. Provide constructive feedback."""


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

            messages = [
                provider.create_system_message(system_prompt),
                provider.create_user_message(
                    f"Please audit this call transcript:\n\n{transcript}"
                ),
            ]

            config = LLMConfig(temperature=0.3, json_mode=True)

            self.report_progress(50, "Generating audit scores...")

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
