"""
AXLE OS — Task Runner (T-087 to T-092)

Executes deployment plans asynchronously.
Groups steps into parallel execution waves and executes them using asyncio.gather.
"""
import asyncio
import logging
import time
from typing import Dict, List, Optional

from axle.core.models import (
    DeploymentPlan,
    DeploymentStep,
    DeploymentStepStatus,
    DeploymentStatus,
)
from axle.core.planner import Planner
from axle.plugins.registry import PluginRegistry, create_default_registry
from axle.plugins.base import PluginResult

logger = logging.getLogger("axle.runner")


class TaskRunner:
    """Async execution orchestrator for deployment plans."""

    def __init__(self, registry: Optional[PluginRegistry] = None, planner: Optional[Planner] = None):
        self.registry = registry or create_default_registry()
        self.planner = planner or Planner(None)  # Planner without AI engine for local helpers
        self.log_stream = []  # Store live logs (T-090 support)

    async def execute_plan(self, plan: DeploymentPlan, context: dict) -> DeploymentPlan:
        """
        Execute an entire deployment plan wave by wave. (T-088)
        If a step fails, the plan stops.
        """
        # Reset step states
        for step in plan.steps:
            step.status = DeploymentStepStatus.PENDING
            step.output = ""
            step.error = None

        waves = self.planner.get_parallel_groups(plan.steps)
        logger.info(f"Executing {len(plan.steps)} steps across {len(waves)} waves.")

        for i, wave in enumerate(waves):
            self._log(f"Starting Wave {i+1} ({len(wave)} steps)")
            
            # Execute wave steps in parallel using asyncio.gather (T-089)
            # We use to_thread because plugin commands are synchronous and blocking
            tasks = [
                asyncio.to_thread(self._run_step_sync, step, context)
                for step in wave
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check for failures (T-092)
            has_failure = False
            for step, result in zip(wave, results):
                if isinstance(result, Exception):
                    step.status = DeploymentStepStatus.FAILED
                    step.error = f"Unhandled exceptions: {str(result)}"
                    has_failure = True
                elif not result.success:
                    has_failure = True

            if has_failure:
                self._log(f"Wave {i+1} failed. Halting deployment.", level="error")
                # T-092: Failure handling & rollback trigger
                await self.rollback_plan(plan, context)
                return plan

        return plan

    def _run_step_sync(self, step: DeploymentStep, context: dict) -> PluginResult:
        """Execute a single deployment step synchronously (runs in a thread)."""
        start_time = time.time()
        step.status = DeploymentStepStatus.RUNNING
        self._log(f"[RUNNING] {step.name}")

        plugin_name = step.plugin
        if not plugin_name:
            # Fallback to a generic shell execution if no plugin mapped
            step.status = DeploymentStepStatus.FAILED
            step.error = f"Missing plugin for step: {step.name}"
            self._log(f"[ERROR] {step.error}", level="error")
            return PluginResult(success=False, error=step.error)

        plugin = self.registry.get(plugin_name)
        if not plugin:
            step.status = DeploymentStepStatus.FAILED
            step.error = f"Plugin '{plugin_name}' not registered."
            self._log(f"[ERROR] {step.error}", level="error")
            return PluginResult(success=False, error=step.error)

        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                # 1. Validate
                val_result = plugin.validate(context)
                if not val_result.success:
                    step.status = DeploymentStepStatus.FAILED
                    step.error = f"Validation failed: {val_result.error}"
                    self._log(f"[FAILED] {step.name} -> {step.error}", level="error")
                    return val_result

                # 2. Configure
                cfg_result = plugin.configure(context)
                if not cfg_result.success:
                    if attempt < max_retries:
                        self._log(f"[WARN] {step.name} config failed. Retrying ({attempt}/{max_retries})...")
                        time.sleep(2)
                        continue
                    
                    step.status = DeploymentStepStatus.FAILED
                    step.error = f"Configuration failed: {cfg_result.error}"
                    step.output = cfg_result.output
                    self._log(f"[FAILED] {step.name} -> {step.error}", level="error")
                    return cfg_result

                # 3. Verify
                ver_result = plugin.verify(context)
                if not ver_result.success:
                    if attempt < max_retries:
                        self._log(f"[WARN] {step.name} verify failed. Retrying ({attempt}/{max_retries})...")
                        time.sleep(2)
                        continue
                    
                    step.status = DeploymentStepStatus.FAILED
                    step.error = f"Verification failed: {ver_result.error}"
                    step.output = ver_result.output
                    self._log(f"[FAILED] {step.name} -> {step.error}", level="error")
                    return ver_result

                # Success
                step.status = DeploymentStepStatus.COMPLETED
                step.output = cfg_result.output
                step.duration_seconds = round(time.time() - start_time, 2)
                self._log(f"[COMPLETED] {step.name} in {step.duration_seconds}s")
                return cfg_result

            except Exception as e:
                if attempt < max_retries:
                    self._log(f"[WARN] Exception in {step.name}. Retrying ({attempt}/{max_retries})...")
                    time.sleep(2)
                    continue
                step.status = DeploymentStepStatus.FAILED
                step.error = f"Unhandled plugin exception: {str(e)}"
                self._log(f"[ERROR] {step.name} -> {step.error}", level="error")
                return PluginResult(success=False, error=step.error)

    async def rollback_plan(self, plan: DeploymentPlan, context: dict):
        """Rollback all completed steps in reverse order. (T-092)"""
        self._log("Initiating rollback for completed steps...")
        
        # Collect all COMPLETED steps, then reverse them
        completed_steps = [s for s in plan.steps if s.status == DeploymentStepStatus.COMPLETED]
        completed_steps.reverse()
        
        for step in completed_steps:
            if not step.plugin:
                continue
            plugin = self.registry.get(step.plugin)
            if plugin:
                self._log(f"[ROLLBACK] Reverting '{step.name}' via {step.plugin}")
                # Run synchronously in thread
                await asyncio.to_thread(plugin.rollback, context)
                
        self._log("Rollback complete.")

    def _log(self, message: str, level: str = "info"):
        """Append to live log stream. (T-090)"""
        timestamp = time.strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}"
        self.log_stream.append(log_line)
        if level == "error":
            logger.error(log_line)
        else:
            logger.info(log_line)
        # Real-time streaming to CLI/Dashboard would read from self.log_stream
