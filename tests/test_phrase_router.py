"""
Tests for phrase router - natural language command interpretation
"""
import pytest
from orchestrator_toolkit.phrase_router import (
    route_intent, extract_owner_from_text, normalize_id
)


class TestRouteIntent:
    """Test the main routing logic."""

    def test_default_to_plan(self):
        """Ambiguous input defaults to PLAN."""
        cmd, target, text = route_intent("add authentication")
        assert cmd == "plan"
        assert target is None
        assert text == "authentication"

    def test_plan_with_filler_words(self):
        """Filler words are stripped correctly."""
        cmd, target, text = route_intent("please create a new task for login system")
        assert cmd == "plan"
        assert target is None
        assert text == "login system"

    def test_empty_input(self):
        """Empty input creates untitled plan."""
        cmd, target, text = route_intent("")
        assert cmd == "plan"
        assert target is None
        assert text == "Untitled"

    def test_only_filler_words(self):
        """Input with only filler words."""
        cmd, target, text = route_intent("please create a new the")
        assert cmd == "plan"
        assert target is None

    # SPEC tests
    def test_spec_for_plan_with_id(self):
        """SPEC for specific PLAN ID."""
        cmd, target, text = route_intent("spec for plan-123 authentication flow")
        assert cmd == "spec"
        assert target == "PLAN-123"
        assert text == "authentication flow"

    def test_spec_for_plan_full_id(self):
        """SPEC for full PLAN ID format."""
        cmd, target, text = route_intent("spec for PLAN-20251013-01T6N8 auth flow")
        assert cmd == "spec"
        assert target == "PLAN-20251013-01T6N8"
        assert text == "auth flow"

    def test_spec_verb_without_plan(self):
        """SPEC verb but no plan reference (will prompt)."""
        cmd, target, text = route_intent("design the authentication system")
        assert cmd == "spec"
        assert target is None
        assert text == "authentication system"

    def test_spec_blueprint_verb(self):
        """Blueprint as spec verb."""
        cmd, target, text = route_intent("blueprint the payment flow")
        assert cmd == "spec"
        assert target is None
        assert text == "payment flow"

    # EXECUTE tests
    def test_execute_with_spec_id(self):
        """Execute with explicit spec ID."""
        cmd, target, text = route_intent("execute spec-456")
        assert cmd == "execute"
        assert target == "SPEC-456"
        assert text == ""

    def test_execute_with_full_spec_id(self):
        """Execute with full spec ID format."""
        cmd, target, text = route_intent("execute SPEC-20251013-02NZ6Q-auth")
        assert cmd == "execute"
        assert target == "SPEC-20251013-02NZ6Q-AUTH"
        assert text == ""

    def test_build_with_spec_id(self):
        """Build as execute verb."""
        cmd, target, text = route_intent("build spec-789")
        assert cmd == "execute"
        assert target == "SPEC-789"
        assert text == ""

    def test_exec_shorthand(self):
        """Exec as shorthand for execute."""
        cmd, target, text = route_intent("exec SPEC-001")
        assert cmd == "execute"
        assert target == "SPEC-001"
        assert text == ""

    def test_execute_verb_without_spec(self):
        """Execute verb but no spec ID (will prompt)."""
        cmd, target, text = route_intent("execute the login system")
        assert cmd == "execute"
        assert target is None
        assert text == "login system"

    def test_run_verb_without_spec(self):
        """Run as execute verb without spec."""
        cmd, target, text = route_intent("run the tests")
        assert cmd == "execute"
        assert target is None
        assert text == "tests"

    # Priority tests
    def test_exec_beats_plan_keywords(self):
        """EXECUTE with ID has priority over plan keywords."""
        cmd, target, text = route_intent("plan to execute spec-123")
        assert cmd == "execute"
        assert target == "SPEC-123"

    def test_spec_beats_plan_keywords(self):
        """SPEC with plan ID has priority over plan keywords."""
        cmd, target, text = route_intent("task spec for plan-456 new feature")
        assert cmd == "spec"
        assert target == "PLAN-456"

    # Complex cases
    def test_mixed_case_handling(self):
        """Mixed case input is handled correctly."""
        cmd, target, text = route_intent("EXECUTE Spec-ABC123")
        assert cmd == "execute"
        assert target == "SPEC-ABC123"

    def test_multiple_spaces_normalized(self):
        """Multiple spaces are normalized."""
        cmd, target, text = route_intent("create    a    new    task")
        assert cmd == "plan"
        assert text in ["task", ""]  # Depends on filler word removal

    def test_spec_on_instead_of_for(self):
        """'on' works as well as 'for' for spec."""
        cmd, target, text = route_intent("spec on plan-111 database schema")
        assert cmd == "spec"
        assert target == "PLAN-111"
        assert text == "database schema"


class TestExtractOwner:
    """Test owner extraction from text."""

    def test_owner_colon_format(self):
        """Extract owner:name format."""
        owner, text = extract_owner_from_text("create task owner:alex")
        assert owner == "alex"
        assert text == "create task"

    def test_owner_flag_format(self):
        """Extract --owner name format."""
        owner, text = extract_owner_from_text("new feature --owner bob")
        assert owner == "bob"
        assert text == "new feature"

    def test_owner_at_format(self):
        """Extract @name format."""
        owner, text = extract_owner_from_text("fix bug @charlie")
        assert owner == "charlie"
        assert text == "fix bug"

    def test_no_owner_specified(self):
        """No owner in text."""
        owner, text = extract_owner_from_text("create new feature")
        assert owner is None
        assert text == "create new feature"

    def test_owner_in_middle(self):
        """Owner specified in middle of text."""
        owner, text = extract_owner_from_text("create @david authentication")
        assert owner == "david"
        assert text == "create authentication"


class TestNormalizeId:
    """Test ID normalization."""

    def test_normalize_short_number(self):
        """Short number gets prefix added."""
        assert normalize_id("123", "PLAN") == "PLAN-123"
        assert normalize_id("456", "SPEC") == "SPEC-456"

    def test_already_normalized(self):
        """Already normalized IDs unchanged."""
        assert normalize_id("PLAN-123", "PLAN") == "PLAN-123"
        assert normalize_id("SPEC-456", "SPEC") == "SPEC-456"

    def test_legacy_format_preserved(self):
        """Legacy T-XXX and P-XXX formats preserved."""
        assert normalize_id("T-001", "PLAN") == "T-001"
        assert normalize_id("P-002", "SPEC") == "P-002"

    def test_full_format_preserved(self):
        """Full format with ULID preserved."""
        full_id = "PLAN-20251013-01T6N8-auth"
        assert normalize_id(full_id, "PLAN") == full_id.upper()

    def test_case_normalization(self):
        """IDs are uppercased."""
        assert normalize_id("plan-abc", "PLAN") == "PLAN-ABC"
        assert normalize_id("spec-xyz", "SPEC") == "SPEC-XYZ"

    def test_empty_id(self):
        """Empty ID returns empty string."""
        assert normalize_id("", "PLAN") == ""
        assert normalize_id(None, "SPEC") == ""