"""Shared validation primitives for the engineering engine.

pv_engine must remain importable without Django installed (see
CLAUDE.md / Claude_Development_Specification, "Engineering Package").
Everything in this package is plain Python: dataclasses and functions.
"""

from dataclasses import dataclass, field
from enum import StrEnum


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class ValidationIssue:
    """A single validation finding.

    Attributes:
        severity: ERROR blocks the design from being considered valid;
            WARNING flags something worth an engineer's attention.
        code: a short, stable machine-readable identifier (e.g.
            "module_type.voc_below_vmpp") so callers/tests can match on it
            without parsing message text.
        message: a human-readable explanation.
        object_ref: a free-form label identifying the offending object
            (e.g. "ModuleType: JinkoSolar Tiger Neo 585")
    """

    severity: Severity
    code: str
    message: str
    object_ref: str = ""


@dataclass
class ValidationResult:
    """An ordered collection of validation issues with convenience helpers."""

    issues: list[ValidationIssue] = field(default_factory=list)

    def add(self, severity: Severity, code: str, message: str, object_ref: str = "") -> None:
        self.issues.append(ValidationIssue(severity, code, message, object_ref))

    def error(self, code: str, message: str, object_ref: str = "") -> None:
        self.add(Severity.ERROR, code, message, object_ref)

    def warning(self, code: str, message: str, object_ref: str = "") -> None:
        self.add(Severity.WARNING, code, message, object_ref)

    def extend(self, other: "ValidationResult") -> None:
        self.issues.extend(other.issues)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.WARNING]

    @property
    def is_valid(self) -> bool:
        """True if there are no ERROR-level issues (warnings are allowed)."""
        return len(self.errors) == 0

    def __bool__(self) -> bool:
        return self.is_valid

    def __iter__(self):
        return iter(self.issues)

    def __len__(self) -> int:
        return len(self.issues)
