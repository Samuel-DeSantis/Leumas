from pv_engine.validation.base import Severity, ValidationResult


def test_empty_result_is_valid():
    result = ValidationResult()
    assert result.is_valid
    assert bool(result) is True
    assert len(result) == 0


def test_warning_does_not_invalidate():
    result = ValidationResult()
    result.warning("some.code", "just a heads up")
    assert result.is_valid
    assert len(result.warnings) == 1
    assert len(result.errors) == 0


def test_error_invalidates():
    result = ValidationResult()
    result.error("some.code", "this is bad")
    assert not result.is_valid
    assert bool(result) is False
    assert len(result.errors) == 1


def test_extend_combines_issues():
    a = ValidationResult()
    a.error("a.code", "a message")
    b = ValidationResult()
    b.warning("b.code", "b message")

    a.extend(b)
    assert len(a) == 2
    assert len(a.errors) == 1
    assert len(a.warnings) == 1


def test_add_with_explicit_severity():
    result = ValidationResult()
    result.add(Severity.ERROR, "x.code", "x message", "SomeObject")
    issue = result.issues[0]
    assert issue.severity == Severity.ERROR
    assert issue.object_ref == "SomeObject"
