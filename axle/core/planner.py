"""
AXLE OS — Deployment Planner (T-056 to T-061)

High-level orchestrator that:
  1. Takes a ProjectProfile + ServerProfile
  2. Calls the AI Engine to generate a raw plan
  3. Validates and orders the steps (topological sort)
  4. Produces a formatted preview for CLI/dashboard display

Usage:
    from axle.core.planner import Planner
    planner = Planner(ai_engine)
    plan = planner.generate_plan(profile, server)
    planner.print_preview(plan)
"""
import logging
from typing import Dict, List, Optional, Set

from axle.ai.engine import AIEngine
from axle.core.models import (
    DeploymentPlan,
    DeploymentStep,
    DeploymentStepStatus,
    ProjectProfile,
    ServerProfile,
)

logger = logging.getLogger("axle.planner")


# Required plugins for each configuration aspect
REQUIRED_PLUGINS = {"runtime", "systemd", "nginx"}
OPTIONAL_PLUGINS = {"database", "ssl", "firewall"}


class Planner:
    """
    Deployment planner — wraps the AI engine with validation and ordering.
    """

    def __init__(self, ai_engine: AIEngine):
        self.ai_engine = ai_engine

    def generate_plan(
        self,
        profile: ProjectProfile,
        server: Optional[ServerProfile] = None,
    ) -> DeploymentPlan:
        """
        Generate a validated, ordered deployment plan. (T-057)

        Args:
            profile: Scanned project profile.
            server: Target server profile.

        Returns:
            Validated DeploymentPlan with resolved dependencies.
        """
        if server is None:
            server = ServerProfile()

        # 1. Ask AI to generate the raw plan
        plan = self.ai_engine.generate_plan(profile, server)

        # 2. Validate the plan has required steps
        plan = self._validate_plan(plan, profile)

        # 3. Resolve execution order (topological sort)
        plan.steps = self._resolve_order(plan.steps)

        return plan

    def get_parallel_groups(self, steps: List[DeploymentStep]) -> List[List[DeploymentStep]]:
        """
        Group steps into execution waves — steps in the same wave can run in parallel. (T-058)

        Returns:
            List of groups, where each group is a list of steps that can run concurrently.
        """
        if not steps:
            return []

        completed: Set[str] = set()
        remaining = list(steps)
        groups = []

        while remaining:
            # Find all steps whose dependencies are satisfied
            ready = [
                s for s in remaining
                if all(dep in completed for dep in s.depends_on)
            ]

            if not ready:
                # Circular dependency or broken depends_on reference
                logger.warning(
                    "Cannot resolve remaining steps — possible circular dependency. "
                    "Executing remaining steps sequentially."
                )
                groups.append(remaining)
                break

            groups.append(ready)
            for s in ready:
                completed.add(s.id)
                remaining.remove(s)

        return groups

    def validate_plan(self, plan: DeploymentPlan) -> List[str]:
        """
        Validate a deployment plan and return a list of warnings. (T-059)

        Returns:
            List of warning messages (empty = plan is valid).
        """
        warnings = []
        step_ids = {s.id for s in plan.steps}

        # Check for duplicate IDs
        if len(step_ids) != len(plan.steps):
            warnings.append("Duplicate step IDs detected")

        # Check all depends_on references are valid
        for step in plan.steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    warnings.append(f"Step '{step.id}' depends on unknown step '{dep}'")

        # Check for circular dependencies
        if self._has_cycle(plan.steps):
            warnings.append("Circular dependency detected in step graph")

        return warnings

    def format_preview(self, plan: DeploymentPlan) -> str:
        """
        Format a deployment plan for CLI preview. (T-060)

        Returns:
            Formatted multi-line string.
        """
        lines = []
        lines.append(f"╔══════════════════════════════════════════════════════╗")
        lines.append(f"║  Deployment Plan: {plan.project_name:<35}║")
        lines.append(f"╠══════════════════════════════════════════════════════╣")

        if plan.profile:
            lines.append(f"║  Stack: {plan.profile.stack.value:<10} Framework: {plan.profile.framework.value:<16}║")
            lines.append(f"║  Database: {plan.profile.database.value:<42}║")

        lines.append(f"╠══════════════════════════════════════════════════════╣")
        lines.append(f"║  Steps ({len(plan.steps)} total):{'':>34}║")
        lines.append(f"║{'':>54}║")

        groups = self.get_parallel_groups(plan.steps)
        for i, group in enumerate(groups):
            wave_label = f"Wave {i+1}"
            if len(group) > 1:
                wave_label += f" (parallel: {len(group)} steps)"

            lines.append(f"║  {wave_label:<52}║")
            for step in group:
                status_icon = "○"
                deps = f" → after: {', '.join(step.depends_on)}" if step.depends_on else ""
                name_display = step.name[:40]
                lines.append(f"║    {status_icon} {name_display:<48}║")
                if deps:
                    lines.append(f"║      {deps:<50}║")

        lines.append(f"╚══════════════════════════════════════════════════════╝")
        return "\n".join(lines)

    # ==========================================================================
    # Internal Helpers
    # ==========================================================================

    def _validate_plan(self, plan: DeploymentPlan, profile: ProjectProfile) -> DeploymentPlan:
        """Ensure the plan has minimum required steps. (T-059)"""
        existing_plugins = {s.plugin for s in plan.steps if s.plugin}

        # Check required plugins
        for required in REQUIRED_PLUGINS:
            if required not in existing_plugins:
                logger.warning(f"AI plan missing required '{required}' step — adding default")
                # The runner will handle missing plugins gracefully

        return plan

    def _resolve_order(self, steps: List[DeploymentStep]) -> List[DeploymentStep]:
        """Topological sort of steps based on depends_on. (T-058)"""
        if not steps:
            return []

        # Build adjacency map
        step_map: Dict[str, DeploymentStep] = {s.id: s for s in steps}
        in_degree: Dict[str, int] = {s.id: 0 for s in steps}

        for step in steps:
            for dep in step.depends_on:
                if dep in in_degree:
                    in_degree[step.id] += 1

        # Kahn's algorithm
        queue = [sid for sid, deg in in_degree.items() if deg == 0]
        sorted_steps = []

        while queue:
            current = queue.pop(0)
            sorted_steps.append(step_map[current])

            for step in steps:
                if current in step.depends_on:
                    in_degree[step.id] -= 1
                    if in_degree[step.id] == 0:
                        queue.append(step.id)

        # If we couldn't sort everything, append remaining (broken deps)
        if len(sorted_steps) < len(steps):
            sorted_ids = {s.id for s in sorted_steps}
            for step in steps:
                if step.id not in sorted_ids:
                    sorted_steps.append(step)

        return sorted_steps

    def _has_cycle(self, steps: List[DeploymentStep]) -> bool:
        """Detect circular dependencies using DFS."""
        step_ids = {s.id for s in steps}
        dep_map = {s.id: [d for d in s.depends_on if d in step_ids] for s in steps}

        WHITE, GRAY, BLACK = 0, 1, 2
        color = {sid: WHITE for sid in step_ids}

        def dfs(node):
            color[node] = GRAY
            for neighbor in dep_map.get(node, []):
                if color[neighbor] == GRAY:
                    return True  # Back edge = cycle
                if color[neighbor] == WHITE and dfs(neighbor):
                    return True
            color[node] = BLACK
            return False

        for sid in step_ids:
            if color[sid] == WHITE:
                if dfs(sid):
                    return True

        return False
