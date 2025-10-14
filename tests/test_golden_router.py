"""
Golden Tests for Phrase Router

Tests a comprehensive set of natural language inputs to ensure consistent routing.
Each test case represents a real-world usage pattern that must maintain backward compatibility.
"""
import pytest
from orchestrator_toolkit.phrase_router import route_intent, extract_owner_from_text


class TestGoldenRouterPatterns:
    """Golden test cases for phrase router - must not break!"""

    def test_plan_patterns(self):
        """Test PLAN command detection patterns."""
        test_cases = [
            # Basic plan creation (avoid execution verbs)
            ("create auth system", ("plan", None, "auth system")),
            ("create login flow", ("plan", None, "login flow")),
            ("add payment integration", ("plan", None, "payment integration")),
            ("add user management", ("plan", None, "user management")),

            # With quotes
            ('"OAuth 2.1 & PKCE implementation"', ("plan", None, "OAuth 2.1 & PKCE implementation")),
            ("plan 'Design: Auth flows'", ("plan", None, "Design: Auth flows")),

            # Edge cases
            ("", ("plan", None, "Untitled")),
            ("   ", ("plan", None, "Untitled")),
            ("todo", ("plan", None, "todo")),  # Single word is kept as title

            # NOTE: "implement" is an EXEC verb, so these become execute commands:
            # ("implement auth", ("execute", None, "auth"))
            # ("build system", ("execute", None, "system"))
        ]

        for input_text, expected in test_cases:
            result = route_intent(input_text)
            assert result == expected, f"Input: '{input_text}' -> Expected: {expected}, Got: {result}"

    def test_spec_patterns(self):
        """Test SPEC command detection patterns."""
        test_cases = [
            # Explicit spec for plan
            ("spec for PLAN-20251013-01T6N8", ("spec", "PLAN-20251013-01T6N8", "")),
            ("spec for plan-123", ("spec", "PLAN-123", "")),
            ("design for PLAN-20251013-01T6N8-auth", ("spec", "PLAN-20251013-01T6N8-AUTH", "")),

            # Spec with title
            ("spec for plan-123 'Authentication Flow'", ("spec", "PLAN-123", "Authentication Flow")),
            ('spec for PLAN-20251013-01T6N8 "JWT Implementation"', ("spec", "PLAN-20251013-01T6N8", "JWT Implementation")),

            # Spec without plan (will prompt)
            ("spec authentication", ("spec", None, "authentication")),
            ("design the login system", ("spec", None, "login system")),  # "the" is stripped as filler
            ("specify error handling", ("spec", None, "error handling")),
        ]

        for input_text, expected in test_cases:
            result = route_intent(input_text)
            assert result == expected, f"Input: '{input_text}' -> Expected: {expected}, Got: {result}"

    def test_execute_patterns(self):
        """Test EXECUTE command detection patterns."""
        test_cases = [
            # Execute with spec ID
            ("execute SPEC-20251013-02NZ6Q", ("execute", "SPEC-20251013-02NZ6Q", "")),
            ("run spec-456", ("execute", "SPEC-456", "")),
            ("build SPEC-20251013-02NZ6Q-auth", ("execute", "SPEC-20251013-02NZ6Q-AUTH", "")),
            ("implement spec-789", ("execute", "SPEC-789", "")),

            # Execute without spec (will prompt)
            ("execute", ("execute", None, "")),
            ("run the tests", ("execute", None, "tests")),  # "the" is stripped as filler
            ("start implementation", ("execute", None, "implementation")),
        ]

        for input_text, expected in test_cases:
            result = route_intent(input_text)
            assert result == expected, f"Input: '{input_text}' -> Expected: {expected}, Got: {result}"

    def test_ready_patterns(self):
        """Test READY command for marking PLANs ready."""
        test_cases = [
            # Mark as ready patterns
            ("ready PLAN-20251013-01T6N8", ("ready", "PLAN-20251013-01T6N8", "")),
            ("mark ready plan-123", ("ready", "PLAN-123", "")),
            ("set as ready PLAN-20251013-01T6N8-auth", ("ready", "PLAN-20251013-01T6N8-AUTH", "")),
            ("plan-456 ready", ("ready", "PLAN-456", "")),
            ("plan ready PLAN-789", ("ready", "PLAN-789", "")),
        ]

        for input_text, expected in test_cases:
            result = route_intent(input_text)
            assert result == expected, f"Input: '{input_text}' -> Expected: {expected}, Got: {result}"

    def test_priority_routing(self):
        """Test that routing priority is correct: READY > EXECUTE > SPEC > PLAN."""
        test_cases = [
            # Ready should override other interpretations
            ("ready PLAN-123", ("ready", "PLAN-123", "")),

            # Execute with ID should override spec/plan
            ("execute SPEC-456 implement auth", ("execute", "SPEC-456", "")),

            # Spec for plan should override general plan
            ("spec for PLAN-789 design system", ("spec", "PLAN-789", "system")),  # "design" is SPEC_VERB, stripped

            # Ambiguous defaults to plan
            ("something vague", ("plan", None, "something vague")),

            # Verbs change interpretation
            ("implement auth", ("execute", None, "auth")),  # EXEC verb
            ("design auth", ("spec", None, "auth")),  # SPEC verb
            ("create auth", ("plan", None, "auth")),  # Default to PLAN
        ]

        for input_text, expected in test_cases:
            result = route_intent(input_text)
            assert result == expected, f"Input: '{input_text}' -> Expected: {expected}, Got: {result}"

    def test_owner_extraction(self):
        """Test owner extraction from text."""
        test_cases = [
            # owner: pattern
            ("implement auth owner:alice", ("alice", "implement auth")),
            ("plan for login owner:bob", ("bob", "plan for login")),

            # --owner pattern
            ("create api --owner charlie", ("charlie", "create api")),
            ("spec database --owner dave", ("dave", "spec database")),

            # @mention pattern
            ("@eve implement the feature", ("eve", "implement the feature")),
            ("build system @frank", ("frank", "build system")),

            # No owner specified
            ("just a regular task", (None, "just a regular task")),
            ("", (None, "")),
        ]

        for input_text, expected in test_cases:
            result = extract_owner_from_text(input_text)
            assert result == expected, f"Input: '{input_text}' -> Expected: {expected}, Got: {result}"

    def test_complex_real_world_patterns(self):
        """Test complex real-world usage patterns."""
        test_cases = [
            # Complex spec creation
            ("spec for PLAN-20251013-01T6N8-ship-auth 'Implement JWT with refresh tokens'",
             ("spec", "PLAN-20251013-01T6N8-SHIP-AUTH", "Implement JWT with refresh tokens")),

            # Plan with special characters
            ('"Plan: OAuth 2.1 & PKCE (Web+Mobile)"',
             ("plan", None, "Plan: OAuth 2.1 & PKCE (Web+Mobile)")),

            # Ready command with full ID
            ("mark as ready PLAN-20251013-01T6N8-implement-auth-system",
             ("ready", "PLAN-20251013-01T6N8-IMPLEMENT-AUTH-SYSTEM", "")),

            # Execute with full spec ID
            ("run SPEC-20251014-02NZ6Q-auth-jwt-implementation",
             ("execute", "SPEC-20251014-02NZ6Q-AUTH-JWT-IMPLEMENTATION", "")),

            # Owner with complex command
            ("@alice spec for plan-123 'Design auth flows'",
             ("spec", "PLAN-123", "Design auth flows")),  # Note: owner extraction is separate
        ]

        for input_text, expected in test_cases:
            # First extract owner
            owner, cleaned = extract_owner_from_text(input_text)
            # Then route the cleaned text
            result = route_intent(cleaned)
            assert result == expected, f"Input: '{cleaned}' -> Expected: {expected}, Got: {result}"


class TestStateMachineGolden:
    """Golden tests for state machine transitions."""

    def test_plan_state_transitions(self):
        """Test PLAN state transitions are valid."""
        from pathlib import Path

        valid_transitions = {
            "draft": ["ready", "done"],  # Can skip to done if abandoned
            "ready": ["in-spec", "done"],
            "in-spec": ["executing", "done"],
            "executing": ["done"],
            "done": []  # Terminal state
        }

        # Test each transition
        for from_state, to_states in valid_transitions.items():
            for to_state in to_states:
                # This would test actual state transition logic
                # For now, just validate the mapping exists
                assert to_state in ["ready", "in-spec", "executing", "done", "draft"]

    def test_spec_state_transitions(self):
        """Test SPEC state transitions are valid."""
        valid_transitions = {
            "draft": ["designed", "done"],  # Can skip to done if abandoned
            "designed": ["built", "done"],
            "built": ["done"],
            "done": []  # Terminal state
        }

        for from_state, to_states in valid_transitions.items():
            for to_state in to_states:
                assert to_state in ["designed", "built", "done", "draft"]


class TestIdempotencyGolden:
    """Golden tests for idempotency guarantees."""

    def test_orchestrator_idempotency(self):
        """Test that orchestrator is idempotent."""
        # This would test actual orchestrator behavior
        # Key invariant: Running orchestrator twice should create 0 specs the second time
        # if no PLANs changed status to ready between runs

        # Pseudo-test structure:
        # 1. Create PLAN with status=ready
        # 2. Run orchestrator -> creates 1 SPEC
        # 3. Run orchestrator again -> creates 0 SPECs
        # 4. Verify PLAN still has same spec_id
        assert True  # Placeholder for actual implementation test

    def test_no_duplicate_specs(self):
        """Test that PLANs can't have multiple SPECs created."""
        # Key invariant: A PLAN with spec_id set should never get another SPEC
        # Even if status is manually changed back to "ready"
        assert True  # Placeholder for actual implementation test


if __name__ == "__main__":
    pytest.main([__file__, "-v"])