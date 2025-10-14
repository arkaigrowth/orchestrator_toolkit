"""
Non-blocking hooks system for external integrations.

Provides safe, timeout-protected calls to external systems (Archon, Mem0)
that never block core operations. All hook failures are logged but don't
propagate exceptions to callers.
"""
from __future__ import annotations

import os
import random
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional, Set

from orchestrator_toolkit.settings import OrchSettings


class TimeoutError(Exception):
    """Raised when a hook call times out."""
    pass


class HookManager:
    """
    Manages non-blocking hooks to external systems.

    All hook methods are safe to call - they will never raise exceptions
    or block indefinitely. Failures are logged to run_log.md.

    Feature flags control which hooks are active:
    - OTK_ARCHON_ENABLED: Enable Archon API calls
    - OTK_MEM0_ENABLED: Enable Mem0 API calls
    """

    def __init__(self, settings: Optional[OrchSettings] = None, timeout: int = 3):
        """
        Initialize hook manager.

        Args:
            settings: Configuration settings. If None, loads from environment.
            timeout: Timeout in seconds for hook calls (default: 3)
        """
        self.settings = settings or OrchSettings.load()
        self.timeout = timeout
        self.max_retries = 2  # 2 retries = 3 total attempts
        self.run_log_path = Path.cwd() / "run_log.md"
        self._muted_hooks: Set[str] = set()  # Track failed hooks to prevent log spam

    def _log_warning(self, hook_name: str, message: str, error: Optional[Exception] = None) -> None:
        """
        Log a warning to run_log.md without raising exceptions.

        Args:
            hook_name: Name of the hook that failed
            message: Warning message
            error: Optional exception that caused the warning
        """
        try:
            timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
            log_entry = f"[{timestamp}] WARN hook={hook_name} {message}"
            if error:
                log_entry += f" error={type(error).__name__}:{str(error)}"
            log_entry += "\n"

            # Append to run_log.md atomically
            with open(self.run_log_path, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception:
            # If we can't even log, silently ignore
            pass

    def _timeout_handler(self, signum: int, frame: Any) -> None:
        """Signal handler for timeout."""
        raise TimeoutError("Hook call exceeded timeout")

    def _jittered_delay(self) -> float:
        """
        Return a random delay between 250-750ms for retry backoff.

        Returns:
            Delay in seconds (0.25 to 0.75)
        """
        return random.uniform(0.25, 0.75)

    def _log_event(self, event: str, ids: dict, outcome: str) -> None:
        """
        Log a single-line structured event to run_log.md.

        Format: ISO_timestamp · event · ids · outcome

        Args:
            event: Event name (e.g., "archon_plan_created")
            ids: Dictionary of relevant IDs (e.g., {"plan_id": "PLAN-xxx"})
            outcome: Result (e.g., "success", "timeout", "failed", "muted")
        """
        try:
            timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
            ids_str = " ".join(f"{k}={v}" for k, v in ids.items())
            log_entry = f"[{timestamp}] · {event} · {ids_str} · {outcome}\n"

            with open(self.run_log_path, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception:
            pass  # Silent failure on logging

    def _call_with_timeout(self, hook_name: str, func: Callable[[], None]) -> bool:
        """
        Execute a function with timeout protection.

        Args:
            hook_name: Name of the hook (for logging)
            func: Function to execute

        Returns:
            True if successful, False if failed or timed out
        """
        # On non-Unix systems, just call directly without timeout
        if sys.platform == "win32":
            try:
                func()
                return True
            except Exception as e:
                self._log_warning(hook_name, "Hook execution failed", e)
                return False

        # Unix systems: use signal.alarm for timeout
        old_handler = signal.signal(signal.SIGALRM, self._timeout_handler)
        try:
            signal.alarm(self.timeout)
            func()
            signal.alarm(0)  # Cancel alarm
            return True
        except TimeoutError:
            self._log_warning(hook_name, f"Hook timed out after {self.timeout}s")
            return False
        except Exception as e:
            self._log_warning(hook_name, "Hook execution failed", e)
            return False
        finally:
            signal.alarm(0)  # Ensure alarm is cancelled
            signal.signal(signal.SIGALRM, old_handler)  # Restore handler

    def _call_with_retry(self, hook_name: str, func: Callable[[], None], ids: dict) -> bool:
        """
        Execute a function with timeout and retry protection.

        Implements:
        - 3 total attempts (initial + 2 retries)
        - 250-750ms jittered delay between retries
        - Muted hooks tracking (log once per run to avoid spam)
        - Structured logging: ISO timestamp · event · ids · outcome

        Args:
            hook_name: Name of the hook (for logging)
            func: Function to execute
            ids: Dictionary of relevant IDs for structured logging

        Returns:
            True if successful, False if failed after all retries
        """
        # Return early if hook is muted (already failed in this run)
        if hook_name in self._muted_hooks:
            self._log_event(hook_name, ids, "muted")
            return False

        # Try up to 3 times (initial + 2 retries)
        for attempt in range(self.max_retries + 1):
            success = self._call_with_timeout(hook_name, func)

            if success:
                self._log_event(hook_name, ids, "success")
                return True

            # If not the last attempt, add jittered delay
            if attempt < self.max_retries:
                delay = self._jittered_delay()
                time.sleep(delay)

        # All retries exhausted - mute this hook and log failure
        self._muted_hooks.add(hook_name)
        self._log_event(hook_name, ids, "failed_muted")
        return False

    def _log_hook_fire(self, hook_name: str, **params: Any) -> None:
        """
        Log that a hook was fired (for debugging).

        Args:
            hook_name: Name of the hook
            **params: Hook parameters to log
        """
        try:
            timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
            param_str = " ".join(f"{k}={v}" for k, v in params.items())
            log_entry = f"[{timestamp}] INFO hook={hook_name} {param_str}\n"

            with open(self.run_log_path, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception:
            pass

    def on_plan_created(self, plan_id: str, title: str, owner: Optional[str] = None) -> None:
        """
        Hook called when a new plan is created.

        Args:
            plan_id: The newly created plan ID (e.g., "PLAN-20251013-01T6N8")
            title: Plan title
            owner: Optional owner name
        """
        try:
            self._log_hook_fire("on_plan_created", plan_id=plan_id, title=title, owner=owner or "unassigned")
        except Exception:
            pass  # Never fail on logging

        def _archon_call() -> None:
            if self.settings.archon_enabled:
                # TODO: Actual Archon API call would go here
                # For now, just log that it would be called
                self._log_hook_fire("archon_plan_created", plan_id=plan_id)

        def _mem0_call() -> None:
            if self.settings.mem0_enabled:
                # TODO: Actual Mem0 API call would go here
                self._log_hook_fire("mem0_plan_created", plan_id=plan_id)

        # Execute hooks with retry protection
        if self.settings.archon_enabled:
            self._call_with_retry("archon_plan_created", _archon_call, {"plan_id": plan_id})

        if self.settings.mem0_enabled:
            self._call_with_retry("mem0_plan_created", _mem0_call, {"plan_id": plan_id})

    def on_spec_created(self, spec_id: str, plan_id: str, title: str) -> None:
        """
        Hook called when a new spec is created.

        Args:
            spec_id: The newly created spec ID (e.g., "SPEC-20251013-02NZ6Q")
            plan_id: Parent plan ID
            title: Spec title
        """
        try:
            self._log_hook_fire("on_spec_created", spec_id=spec_id, plan_id=plan_id, title=title)
        except Exception:
            pass  # Never fail on logging

        def _archon_call() -> None:
            if self.settings.archon_enabled:
                self._log_hook_fire("archon_spec_created", spec_id=spec_id, plan_id=plan_id)

        def _mem0_call() -> None:
            if self.settings.mem0_enabled:
                self._log_hook_fire("mem0_spec_created", spec_id=spec_id)

        if self.settings.archon_enabled:
            self._call_with_retry("archon_spec_created", _archon_call, {"spec_id": spec_id, "plan_id": plan_id})

        if self.settings.mem0_enabled:
            self._call_with_retry("mem0_spec_created", _mem0_call, {"spec_id": spec_id})

    def on_phase_started(self, spec_id: str, phase: str) -> None:
        """
        Hook called when a spec phase starts.

        Args:
            spec_id: Spec ID
            phase: Phase name (e.g., "planning", "implementation", "testing")
        """
        try:
            self._log_hook_fire("on_phase_started", spec_id=spec_id, phase=phase)
        except Exception:
            pass  # Never fail on logging

        def _archon_call() -> None:
            if self.settings.archon_enabled:
                self._log_hook_fire("archon_phase_started", spec_id=spec_id, phase=phase)

        def _mem0_call() -> None:
            if self.settings.mem0_enabled:
                self._log_hook_fire("mem0_phase_started", spec_id=spec_id, phase=phase)

        if self.settings.archon_enabled:
            self._call_with_retry("archon_phase_started", _archon_call, {"spec_id": spec_id, "phase": phase})

        if self.settings.mem0_enabled:
            self._call_with_retry("mem0_phase_started", _mem0_call, {"spec_id": spec_id, "phase": phase})

    def on_phase_completed(self, spec_id: str, phase: str) -> None:
        """
        Hook called when a spec phase completes.

        Args:
            spec_id: Spec ID
            phase: Phase name
        """
        try:
            self._log_hook_fire("on_phase_completed", spec_id=spec_id, phase=phase)
        except Exception:
            pass  # Never fail on logging

        def _archon_call() -> None:
            if self.settings.archon_enabled:
                self._log_hook_fire("archon_phase_completed", spec_id=spec_id, phase=phase)

        def _mem0_call() -> None:
            if self.settings.mem0_enabled:
                self._log_hook_fire("mem0_phase_completed", spec_id=spec_id, phase=phase)

        if self.settings.archon_enabled:
            self._call_with_retry("archon_phase_completed", _archon_call, {"spec_id": spec_id, "phase": phase})

        if self.settings.mem0_enabled:
            self._call_with_retry("mem0_phase_completed", _mem0_call, {"spec_id": spec_id, "phase": phase})

    def on_build_completed(self, spec_id: str) -> None:
        """
        Hook called when a build completes.

        Args:
            spec_id: Spec ID that was built
        """
        try:
            self._log_hook_fire("on_build_completed", spec_id=spec_id)
        except Exception:
            pass  # Never fail on logging

        def _archon_call() -> None:
            if self.settings.archon_enabled:
                self._log_hook_fire("archon_build_completed", spec_id=spec_id)

        def _mem0_call() -> None:
            if self.settings.mem0_enabled:
                self._log_hook_fire("mem0_build_completed", spec_id=spec_id)

        if self.settings.archon_enabled:
            self._call_with_retry("archon_build_completed", _archon_call, {"spec_id": spec_id})

        if self.settings.mem0_enabled:
            self._call_with_retry("mem0_build_completed", _mem0_call, {"spec_id": spec_id})


def get_hook_manager(timeout: int = 3) -> HookManager:
    """
    Get a configured hook manager instance.

    Args:
        timeout: Timeout in seconds for hook calls (default: 3)

    Returns:
        Configured HookManager instance
    """
    return HookManager(timeout=timeout)


def fire_hook(
    artifact_type: str,
    artifact_id: str,
    old_status: Optional[str],
    new_status: str,
    timeout: int = 3
) -> None:
    """
    Generic hook firing function for state transitions.

    This is a simplified interface that replaces per-event methods
    with a single generic function for all state changes.

    Args:
        artifact_type: Type of artifact (plan, spec, task)
        artifact_id: ID of the artifact (e.g., PLAN-*, SPEC-*, T-*)
        old_status: Previous status (None for creation)
        new_status: New status
        timeout: Timeout in seconds for hook calls (default: 3)

    Note:
        This function never raises exceptions. All failures are logged
        to run_log.md but don't propagate to callers.
    """
    try:
        hook_mgr = get_hook_manager(timeout)

        # Determine hook type based on artifact type and status change
        if old_status is None:
            # Creation event
            if artifact_type == "plan":
                hook_mgr.on_plan_created(artifact_id, title="", owner=None)
            elif artifact_type == "spec":
                hook_mgr.on_spec_created(artifact_id, plan_id="", title="")
        else:
            # State transition event
            if artifact_type == "spec" and new_status in ["planning", "implementation", "testing"]:
                hook_mgr.on_phase_started(artifact_id, phase=new_status)
            elif artifact_type == "spec" and old_status in ["planning", "implementation", "testing"]:
                hook_mgr.on_phase_completed(artifact_id, phase=old_status)
            elif artifact_type == "spec" and new_status == "done":
                hook_mgr.on_build_completed(artifact_id)

    except Exception:
        # Never fail on hook errors
        pass
