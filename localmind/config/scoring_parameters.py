"""
LocalMind Scoring Parameters

Manages scoring parameters with profiles for different use cases.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class ParameterCategory(Enum):
    """Categories for scoring parameters."""
    COMPLIANCE = "compliance"
    QUALITY = "quality"
    COMMUNICATION = "communication"
    CUSTOM = "custom"


@dataclass
class ScoringParameter:
    """A single scoring parameter."""
    name: str
    display_name: str
    description: str
    max_score: float = 10.0
    weight: float = 1.0
    category: ParameterCategory = ParameterCategory.QUALITY
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "max_score": self.max_score,
            "weight": self.weight,
            "category": self.category.value,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScoringParameter":
        """Create from dictionary."""
        category = data.get("category", "quality")
        if isinstance(category, str):
            category = ParameterCategory(category)

        return cls(
            name=data["name"],
            display_name=data.get("display_name", data["name"].replace("_", " ").title()),
            description=data.get("description", ""),
            max_score=float(data.get("max_score", 10.0)),
            weight=float(data.get("weight", 1.0)),
            category=category,
            enabled=data.get("enabled", True),
        )


@dataclass
class ScoringProfile:
    """A complete scoring profile with multiple parameters."""
    name: str
    description: str = ""
    parameters: List[ScoringParameter] = field(default_factory=list)
    created_at: str = ""
    modified_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [p.to_dict() for p in self.parameters],
            "created_at": self.created_at,
            "modified_at": self.modified_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScoringProfile":
        """Create from dictionary."""
        parameters = [
            ScoringParameter.from_dict(p) for p in data.get("parameters", [])
        ]
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            parameters=parameters,
            created_at=data.get("created_at", ""),
            modified_at=data.get("modified_at", ""),
        )

    def get_enabled_parameters(self) -> List[ScoringParameter]:
        """Get only enabled parameters."""
        return [p for p in self.parameters if p.enabled]

    def get_total_weight(self) -> float:
        """Get total weight of enabled parameters."""
        return sum(p.weight for p in self.get_enabled_parameters())

    def get_max_possible_score(self) -> float:
        """Get maximum possible weighted score."""
        return sum(p.max_score * p.weight for p in self.get_enabled_parameters())


# Default parameters for call quality auditing
DEFAULT_PARAMETERS = [
    ScoringParameter(
        name="greeting",
        display_name="Greeting & Introduction",
        description="Agent properly greets the customer and introduces themselves and the company",
        max_score=10.0,
        weight=1.0,
        category=ParameterCategory.COMPLIANCE,
    ),
    ScoringParameter(
        name="active_listening",
        display_name="Active Listening",
        description="Agent demonstrates active listening through acknowledgments and paraphrasing",
        max_score=10.0,
        weight=1.5,
        category=ParameterCategory.QUALITY,
    ),
    ScoringParameter(
        name="problem_identification",
        display_name="Problem Identification",
        description="Agent correctly identifies and understands the customer's issue",
        max_score=10.0,
        weight=1.5,
        category=ParameterCategory.QUALITY,
    ),
    ScoringParameter(
        name="solution_provided",
        display_name="Solution Provided",
        description="Agent provides an appropriate and effective solution",
        max_score=10.0,
        weight=2.0,
        category=ParameterCategory.QUALITY,
    ),
    ScoringParameter(
        name="product_knowledge",
        display_name="Product Knowledge",
        description="Agent demonstrates adequate knowledge of products/services",
        max_score=10.0,
        weight=1.5,
        category=ParameterCategory.QUALITY,
    ),
    ScoringParameter(
        name="communication_clarity",
        display_name="Communication Clarity",
        description="Agent communicates clearly and professionally",
        max_score=10.0,
        weight=1.0,
        category=ParameterCategory.COMMUNICATION,
    ),
    ScoringParameter(
        name="empathy",
        display_name="Empathy & Rapport",
        description="Agent shows empathy and builds rapport with the customer",
        max_score=10.0,
        weight=1.0,
        category=ParameterCategory.COMMUNICATION,
    ),
    ScoringParameter(
        name="call_control",
        display_name="Call Control",
        description="Agent maintains control of the conversation professionally",
        max_score=10.0,
        weight=1.0,
        category=ParameterCategory.QUALITY,
    ),
    ScoringParameter(
        name="closing",
        display_name="Call Closing",
        description="Agent properly closes the call with next steps and verification",
        max_score=10.0,
        weight=1.0,
        category=ParameterCategory.COMPLIANCE,
    ),
    ScoringParameter(
        name="compliance",
        display_name="Script Compliance",
        description="Agent follows required compliance scripts and disclosures",
        max_score=10.0,
        weight=2.0,
        category=ParameterCategory.COMPLIANCE,
    ),
]


def get_default_profile() -> ScoringProfile:
    """Get the default scoring profile."""
    from datetime import datetime
    now = datetime.now().isoformat()

    return ScoringProfile(
        name="Default",
        description="Standard call quality scoring parameters",
        parameters=DEFAULT_PARAMETERS.copy(),
        created_at=now,
        modified_at=now,
    )


class ScoringProfileManager:
    """Manages scoring profiles with persistence."""

    def __init__(self, profiles_dir: Optional[Path] = None):
        """Initialize profile manager.

        Args:
            profiles_dir: Directory for storing profiles.
        """
        if profiles_dir is None:
            from localmind.config import get_settings_manager
            profiles_dir = get_settings_manager().config_dir / "profiles"

        self._profiles_dir = profiles_dir
        self._profiles_dir.mkdir(parents=True, exist_ok=True)
        self._current_profile: Optional[ScoringProfile] = None

        # Ensure default profile exists
        self._ensure_default_profile()

    def _ensure_default_profile(self) -> None:
        """Ensure the default profile exists."""
        default_path = self._profiles_dir / "default.json"
        if not default_path.exists():
            profile = get_default_profile()
            self.save_profile(profile)

    def list_profiles(self) -> List[str]:
        """List all available profile names."""
        profiles = []
        for path in self._profiles_dir.glob("*.json"):
            profiles.append(path.stem)
        return sorted(profiles)

    def load_profile(self, name: str) -> ScoringProfile:
        """Load a profile by name.

        Args:
            name: Profile name (without .json extension).

        Returns:
            Loaded profile.
        """
        path = self._profiles_dir / f"{name}.json"
        if not path.exists():
            raise FileNotFoundError(f"Profile not found: {name}")

        with open(path, "r") as f:
            data = json.load(f)

        self._current_profile = ScoringProfile.from_dict(data)
        return self._current_profile

    def save_profile(self, profile: ScoringProfile) -> None:
        """Save a profile.

        Args:
            profile: Profile to save.
        """
        from datetime import datetime
        profile.modified_at = datetime.now().isoformat()

        path = self._profiles_dir / f"{profile.name.lower().replace(' ', '_')}.json"
        with open(path, "w") as f:
            json.dump(profile.to_dict(), f, indent=2)

        self._current_profile = profile

    def delete_profile(self, name: str) -> None:
        """Delete a profile.

        Args:
            name: Profile name to delete.
        """
        if name.lower() == "default":
            raise ValueError("Cannot delete the default profile")

        path = self._profiles_dir / f"{name}.json"
        if path.exists():
            path.unlink()

    def duplicate_profile(self, source_name: str, new_name: str) -> ScoringProfile:
        """Duplicate an existing profile.

        Args:
            source_name: Name of profile to duplicate.
            new_name: Name for the new profile.

        Returns:
            New duplicated profile.
        """
        source = self.load_profile(source_name)

        from datetime import datetime
        now = datetime.now().isoformat()

        new_profile = ScoringProfile(
            name=new_name,
            description=f"Copy of {source.name}",
            parameters=[ScoringParameter.from_dict(p.to_dict()) for p in source.parameters],
            created_at=now,
            modified_at=now,
        )

        self.save_profile(new_profile)
        return new_profile

    def export_profile(self, name: str, export_path: Path) -> None:
        """Export a profile to a file.

        Args:
            name: Profile name to export.
            export_path: Path to export to.
        """
        profile = self.load_profile(name)
        with open(export_path, "w") as f:
            json.dump(profile.to_dict(), f, indent=2)

    def import_profile(self, import_path: Path) -> ScoringProfile:
        """Import a profile from a file.

        Args:
            import_path: Path to import from.

        Returns:
            Imported profile.
        """
        with open(import_path, "r") as f:
            data = json.load(f)

        profile = ScoringProfile.from_dict(data)
        self.save_profile(profile)
        return profile

    def get_current_profile(self) -> ScoringProfile:
        """Get the current profile, loading default if none loaded."""
        if self._current_profile is None:
            self._current_profile = self.load_profile("default")
        return self._current_profile

    def reset_to_default(self) -> ScoringProfile:
        """Reset current profile to default values."""
        self._current_profile = get_default_profile()
        self.save_profile(self._current_profile)
        return self._current_profile


# Global profile manager instance
_profile_manager: Optional[ScoringProfileManager] = None


def get_profile_manager() -> ScoringProfileManager:
    """Get the global profile manager instance."""
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = ScoringProfileManager()
    return _profile_manager
