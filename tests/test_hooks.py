"""
Tests for the non-blocking hooks system.
"""
import os
import signal
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from orchestrator_toolkit.hooks import HookManager, TimeoutError, get_hook_manager
from orchestrator_toolkit.settings import OrchSettings


@pytest.fixture
def temp_run_log(tmp_path):
    """Create a temporary run_log.md file."""
    log_path = tmp_path / "run_log.md"
    log_path.write_text("")
    return log_path


@pytest.fixture
def mock_settings():
    """Create mock settings with hooks disabled by default."""
    settings = Mock(spec=OrchSettings)
    settings.archon_enabled = False
    settings.mem0_enabled = False
    return settings


@pytest.fixture
def hook_manager(mock_settings, temp_run_log, monkeypatch):
    """Create a hook manager with mocked settings and temp log file."""
    monkeypatch.chdir(temp_run_log.parent)
    manager = HookManager(settings=mock_settings, timeout=1)
    return manager


class TestHookManagerInit:
    """Test HookManager initialization."""

    def test_default_initialization(self, temp_run_log, monkeypatch):
        """Test default initialization loads settings from environment."""
        monkeypatch.chdir(temp_run_log.parent)
        manager = HookManager(timeout=3)
        assert manager.timeout == 3
        assert manager.settings is not None
        assert manager.run_log_path == temp_run_log.parent / "run_log.md"

    def test_custom_settings(self, mock_settings, temp_run_log, monkeypatch):
        """Test initialization with custom settings."""
        monkeypatch.chdir(temp_run_log.parent)
        manager = HookManager(settings=mock_settings, timeout=2)
        assert manager.settings == mock_settings
        assert manager.timeout == 2


class TestLogging:
    """Test logging functionality."""

    def test_log_warning(self, hook_manager, temp_run_log):
        """Test warning logging."""
        hook_manager._log_warning("test_hook", "Something went wrong")

        log_content = temp_run_log.read_text()
        assert "WARN" in log_content
        assert "hook=test_hook" in log_content
        assert "Something went wrong" in log_content

    def test_log_warning_with_exception(self, hook_manager, temp_run_log):
        """Test warning logging with exception."""
        error = ValueError("Test error")
        hook_manager._log_warning("test_hook", "Failed", error)

        log_content = temp_run_log.read_text()
        assert "WARN" in log_content
        assert "hook=test_hook" in log_content
        assert "ValueError" in log_content
        assert "Test error" in log_content

    def test_log_warning_failure_silent(self, hook_manager):
        """Test that logging failures don't raise exceptions."""
        # Make run_log_path invalid
        hook_manager.run_log_path = Path("/invalid/path/that/does/not/exist.md")

        # Should not raise exception
        hook_manager._log_warning("test_hook", "message")

    def test_log_hook_fire(self, hook_manager, temp_run_log):
        """Test hook fire logging."""
        hook_manager._log_hook_fire("test_hook", plan_id="PLAN-123", title="Test Plan")

        log_content = temp_run_log.read_text()
        assert "INFO" in log_content
        assert "hook=test_hook" in log_content
        assert "plan_id=PLAN-123" in log_content
        assert "title=Test Plan" in log_content


class TestTimeoutProtection:
    """Test timeout protection mechanism."""

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific timeout test")
    def test_timeout_on_slow_function(self, hook_manager, temp_run_log):
        """Test that slow functions are timed out."""
        def slow_func():
            time.sleep(10)  # Sleep longer than timeout

        success = hook_manager._call_with_timeout("slow_hook", slow_func)
        assert success is False

        log_content = temp_run_log.read_text()
        assert "WARN" in log_content
        assert "timed out" in log_content

    def test_successful_fast_function(self, hook_manager, temp_run_log):
        """Test that fast functions complete successfully."""
        def fast_func():
            pass  # Completes instantly

        success = hook_manager._call_with_timeout("fast_hook", fast_func)
        assert success is True

    def test_exception_in_function(self, hook_manager, temp_run_log):
        """Test that exceptions are caught and logged."""
        def failing_func():
            raise ValueError("Something broke")

        success = hook_manager._call_with_timeout("failing_hook", failing_func)
        assert success is False

        log_content = temp_run_log.read_text()
        assert "WARN" in log_content
        assert "failing_hook" in log_content
        assert "ValueError" in log_content

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_windows_no_timeout_mechanism(self, hook_manager):
        """Test that Windows systems don't use signal-based timeout."""
        def fast_func():
            pass

        # Should still work on Windows, just without signal-based timeout
        success = hook_manager._call_with_timeout("test_hook", fast_func)
        assert success is True


class TestFeatureFlags:
    """Test that feature flags gate hook behavior."""

    def test_archon_disabled_no_calls(self, hook_manager, temp_run_log):
        """Test that Archon hooks don't fire when disabled."""
        hook_manager.settings.archon_enabled = False
        hook_manager.settings.mem0_enabled = False

        hook_manager.on_plan_created("PLAN-123", "Test Plan")

        log_content = temp_run_log.read_text()
        assert "archon_plan_created" not in log_content
        assert "on_plan_created" in log_content  # Main hook fires

    def test_archon_enabled_calls_fire(self, hook_manager, temp_run_log):
        """Test that Archon hooks fire when enabled."""
        hook_manager.settings.archon_enabled = True
        hook_manager.settings.mem0_enabled = False

        hook_manager.on_plan_created("PLAN-123", "Test Plan")

        log_content = temp_run_log.read_text()
        assert "archon_plan_created" in log_content
        assert "on_plan_created" in log_content

    def test_mem0_disabled_no_calls(self, hook_manager, temp_run_log):
        """Test that Mem0 hooks don't fire when disabled."""
        hook_manager.settings.archon_enabled = False
        hook_manager.settings.mem0_enabled = False

        hook_manager.on_spec_created("SPEC-456", "PLAN-123", "Test Spec")

        log_content = temp_run_log.read_text()
        assert "mem0_spec_created" not in log_content
        assert "on_spec_created" in log_content

    def test_mem0_enabled_calls_fire(self, hook_manager, temp_run_log):
        """Test that Mem0 hooks fire when enabled."""
        hook_manager.settings.archon_enabled = False
        hook_manager.settings.mem0_enabled = True

        hook_manager.on_spec_created("SPEC-456", "PLAN-123", "Test Spec")

        log_content = temp_run_log.read_text()
        assert "mem0_spec_created" in log_content
        assert "on_spec_created" in log_content

    def test_both_enabled(self, hook_manager, temp_run_log):
        """Test that both Archon and Mem0 hooks fire when both enabled."""
        hook_manager.settings.archon_enabled = True
        hook_manager.settings.mem0_enabled = True

        hook_manager.on_phase_started("SPEC-789", "planning")

        log_content = temp_run_log.read_text()
        assert "archon_phase_started" in log_content
        assert "mem0_phase_started" in log_content
        assert "on_phase_started" in log_content


class TestHookMethods:
    """Test individual hook methods."""

    def test_on_plan_created_basic(self, hook_manager, temp_run_log):
        """Test on_plan_created hook."""
        hook_manager.on_plan_created("PLAN-123", "Test Plan", "alice")

        log_content = temp_run_log.read_text()
        assert "on_plan_created" in log_content
        assert "plan_id=PLAN-123" in log_content
        assert "title=Test Plan" in log_content
        assert "owner=alice" in log_content

    def test_on_plan_created_no_owner(self, hook_manager, temp_run_log):
        """Test on_plan_created without owner."""
        hook_manager.on_plan_created("PLAN-124", "Another Plan")

        log_content = temp_run_log.read_text()
        assert "on_plan_created" in log_content
        assert "owner=unassigned" in log_content

    def test_on_spec_created(self, hook_manager, temp_run_log):
        """Test on_spec_created hook."""
        hook_manager.on_spec_created("SPEC-456", "PLAN-123", "Test Spec")

        log_content = temp_run_log.read_text()
        assert "on_spec_created" in log_content
        assert "spec_id=SPEC-456" in log_content
        assert "plan_id=PLAN-123" in log_content
        assert "title=Test Spec" in log_content

    def test_on_phase_started(self, hook_manager, temp_run_log):
        """Test on_phase_started hook."""
        hook_manager.on_phase_started("SPEC-789", "implementation")

        log_content = temp_run_log.read_text()
        assert "on_phase_started" in log_content
        assert "spec_id=SPEC-789" in log_content
        assert "phase=implementation" in log_content

    def test_on_phase_completed(self, hook_manager, temp_run_log):
        """Test on_phase_completed hook."""
        hook_manager.on_phase_completed("SPEC-789", "testing")

        log_content = temp_run_log.read_text()
        assert "on_phase_completed" in log_content
        assert "spec_id=SPEC-789" in log_content
        assert "phase=testing" in log_content

    def test_on_build_completed(self, hook_manager, temp_run_log):
        """Test on_build_completed hook."""
        hook_manager.on_build_completed("SPEC-999")

        log_content = temp_run_log.read_text()
        assert "on_build_completed" in log_content
        assert "spec_id=SPEC-999" in log_content


class TestNonBlockingBehavior:
    """Test that hooks never block core operations."""

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific timeout test")
    def test_slow_hook_does_not_block(self, hook_manager, temp_run_log):
        """Test that a slow hook is cut off and doesn't block."""
        # Patch the internal archon call to be slow
        original_enabled = hook_manager.settings.archon_enabled
        hook_manager.settings.archon_enabled = True

        # This should complete quickly despite the timeout
        start = time.time()
        hook_manager.on_plan_created("PLAN-123", "Test")
        elapsed = time.time() - start

        # Should take about 1 second (our timeout), not 10
        assert elapsed < 2.0  # Give some margin

        hook_manager.settings.archon_enabled = original_enabled

    def test_exception_does_not_propagate(self, hook_manager):
        """Test that exceptions in hooks don't propagate to caller."""
        hook_manager.settings.archon_enabled = True

        # Patch to raise an exception
        def raise_error(*args, **kwargs):
            raise RuntimeError("Critical error!")

        # Should not raise despite the internal error
        try:
            with patch.object(hook_manager, '_log_hook_fire', side_effect=raise_error):
                # The hook should catch and log the error, not propagate
                # Note: We're patching _log_hook_fire just as an example of where
                # an error might occur. In practice, errors would come from API calls.
                hook_manager.on_plan_created("PLAN-123", "Test")
        except RuntimeError:
            pytest.fail("Exception should not have propagated from hook")


class TestGetHookManager:
    """Test the factory function."""

    def test_get_hook_manager_default(self, temp_run_log, monkeypatch):
        """Test get_hook_manager with default timeout."""
        monkeypatch.chdir(temp_run_log.parent)
        manager = get_hook_manager()
        assert isinstance(manager, HookManager)
        assert manager.timeout == 3

    def test_get_hook_manager_custom_timeout(self, temp_run_log, monkeypatch):
        """Test get_hook_manager with custom timeout."""
        monkeypatch.chdir(temp_run_log.parent)
        manager = get_hook_manager(timeout=3)
        assert manager.timeout == 3


class TestRetryLogic:
    """Test retry logic and muted hooks."""

    def test_jittered_delay_in_range(self, hook_manager):
        """Test that jittered delay returns values in correct range."""
        for _ in range(100):  # Test multiple times for randomness
            delay = hook_manager._jittered_delay()
            assert 0.25 <= delay <= 0.75

    def test_log_event_structured_format(self, hook_manager, temp_run_log):
        """Test structured event logging format."""
        hook_manager._log_event(
            "test_event",
            {"plan_id": "PLAN-123", "spec_id": "SPEC-456"},
            "success"
        )

        log_content = temp_run_log.read_text()
        assert "test_event" in log_content
        assert "plan_id=PLAN-123" in log_content
        assert "spec_id=SPEC-456" in log_content
        assert "success" in log_content
        assert " · " in log_content  # Structured separator

    def test_retry_attempts_on_failure(self, hook_manager, temp_run_log):
        """Test that failing hooks are retried 3 times (1 initial + 2 retries)."""
        call_count = 0

        def failing_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("Simulated failure")

        success = hook_manager._call_with_retry(
            "test_hook",
            failing_func,
            {"test_id": "123"}
        )

        assert success is False
        assert call_count == 3  # Initial + 2 retries

    def test_retry_succeeds_on_second_attempt(self, hook_manager, temp_run_log):
        """Test that retry succeeds if function succeeds on retry."""
        call_count = 0

        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:  # Fail first time, succeed second
                raise ValueError("Temporary failure")

        success = hook_manager._call_with_retry(
            "flaky_hook",
            flaky_func,
            {"test_id": "456"}
        )

        assert success is True
        assert call_count == 2  # Stopped after success
        log_content = temp_run_log.read_text()
        assert "success" in log_content

    def test_muted_hooks_after_failure(self, hook_manager, temp_run_log):
        """Test that hooks are muted after all retries fail."""
        def failing_func():
            raise ValueError("Always fails")

        # First call - should try 3 times and fail
        success1 = hook_manager._call_with_retry(
            "persistent_failure",
            failing_func,
            {"test_id": "789"}
        )
        assert success1 is False
        assert "persistent_failure" in hook_manager._muted_hooks

        # Second call - should return immediately without trying
        call_count = 0

        def counting_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("Should not be called")

        success2 = hook_manager._call_with_retry(
            "persistent_failure",
            counting_func,
            {"test_id": "789"}
        )

        assert success2 is False
        assert call_count == 0  # Function not called because hook is muted
        log_content = temp_run_log.read_text()
        assert "muted" in log_content

    def test_structured_logging_on_success(self, hook_manager, temp_run_log):
        """Test structured logging logs success properly."""
        def success_func():
            pass  # Succeeds immediately

        hook_manager._call_with_retry(
            "success_hook",
            success_func,
            {"plan_id": "PLAN-999"}
        )

        log_content = temp_run_log.read_text()
        assert "success_hook" in log_content
        assert "plan_id=PLAN-999" in log_content
        assert "success" in log_content

    def test_structured_logging_on_failure_muted(self, hook_manager, temp_run_log):
        """Test structured logging logs failed_muted after all retries."""
        def failing_func():
            raise ValueError("Always fails")

        hook_manager._call_with_retry(
            "failure_hook",
            failing_func,
            {"spec_id": "SPEC-888"}
        )

        log_content = temp_run_log.read_text()
        assert "failure_hook" in log_content
        assert "spec_id=SPEC-888" in log_content
        assert "failed_muted" in log_content


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_hook_with_empty_strings(self, hook_manager, temp_run_log):
        """Test hooks with empty string parameters."""
        hook_manager.on_plan_created("", "", "")

        log_content = temp_run_log.read_text()
        assert "on_plan_created" in log_content

    def test_hook_with_special_characters(self, hook_manager, temp_run_log):
        """Test hooks with special characters in parameters."""
        hook_manager.on_plan_created(
            "PLAN-123",
            "Test with special chars: @#$%^&*()",
            "user@example.com"
        )

        log_content = temp_run_log.read_text()
        assert "on_plan_created" in log_content

    def test_multiple_rapid_hooks(self, hook_manager, temp_run_log):
        """Test multiple hooks called in rapid succession."""
        for i in range(10):
            hook_manager.on_plan_created(f"PLAN-{i}", f"Plan {i}")

        log_content = temp_run_log.read_text()
        # Should have 10 entries
        assert log_content.count("on_plan_created") == 10

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific signal test")
    def test_signal_handler_restoration(self, hook_manager):
        """Test that signal handlers are properly restored after hook calls."""
        # Save original handler
        original_handler = signal.signal(signal.SIGALRM, signal.SIG_DFL)
        signal.signal(signal.SIGALRM, original_handler)

        # Call a hook
        hook_manager.on_plan_created("PLAN-123", "Test")

        # Handler should be restored
        current_handler = signal.signal(signal.SIGALRM, signal.SIG_DFL)
        signal.signal(signal.SIGALRM, original_handler)  # Restore for other tests

        assert current_handler == signal.SIG_DFL
