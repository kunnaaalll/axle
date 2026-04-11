"""
AXLE OS — Core Data Models

All Pydantic models used across the AXLE system:
  - Enums: StackType, FrameworkType, DatabaseType, DeploymentStepStatus
  - Profiles: ProjectProfile, ServerProfile
  - Deployment: DeploymentStep, DeploymentPlan, DeploymentHistory
  - Monitoring: HealthMetrics
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime


# =============================================================================
# Enums
# =============================================================================

class StackType(str, Enum):
    """Primary programming language/runtime of the project."""
    NODEJS = "nodejs"
    PYTHON = "python"
    GO = "go"
    JAVA = "java"
    STATIC = "static"


class FrameworkType(str, Enum):
    """Detected web framework within the stack. (T-032)"""
    # Node.js frameworks
    EXPRESS = "express"
    NEXTJS = "nextjs"
    NUXTJS = "nuxtjs"
    NESTJS = "nestjs"
    FASTIFY = "fastify"
    # Python frameworks
    DJANGO = "django"
    FASTAPI = "fastapi"
    FLASK = "flask"
    # Go frameworks
    GIN = "gin"
    FIBER = "fiber"
    ECHO = "echo"
    # Java frameworks
    SPRING = "spring"
    # Static / none
    NONE = "none"


class DatabaseType(str, Enum):
    """Database type detected in the project."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    SQLITE = "sqlite"
    NONE = "none"


class DeploymentStepStatus(str, Enum):
    """Status of an individual deployment step."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class DeploymentStatus(str, Enum):
    """Overall status of a deployment."""
    PLANNING = "planning"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


# =============================================================================
# Project & Server Profiles
# =============================================================================

class ProjectProfile(BaseModel):
    """
    Result of scanning a project repository.
    Contains everything AXLE needs to generate a deployment plan.
    """
    name: str
    github_url: str = ""
    stack: StackType
    framework: FrameworkType = FrameworkType.NONE
    version: Optional[str] = None
    database: DatabaseType = DatabaseType.NONE
    env_vars: List[str] = Field(default_factory=list)
    build_command: Optional[str] = None
    start_command: str
    port: int = 3000
    has_frontend: bool = False
    has_backend: bool = True
    static_dir: Optional[str] = None


class ServerProfile(BaseModel):
    """
    Hardware and OS profile of the target EC2 instance. (T-033)
    Used by the AI planner to tailor deployment steps.
    """
    hostname: str = "axle-os"
    os_name: str = "Ubuntu 22.04 LTS"
    cpu_count: int = 2
    ram_total_mb: int = 4096
    disk_total_gb: int = 30
    architecture: str = "x86_64"
    ip_address: str = "0.0.0.0"


# =============================================================================
# Deployment Models
# =============================================================================

class DeploymentStep(BaseModel):
    """A single step within a deployment plan."""
    id: str
    name: str
    command: str
    plugin: Optional[str] = None  # which plugin handles this step
    status: DeploymentStepStatus = DeploymentStepStatus.PENDING
    output: str = ""
    error: Optional[str] = None
    depends_on: List[str] = Field(default_factory=list)
    duration_seconds: Optional[float] = None


class DeploymentPlan(BaseModel):
    """An ordered, parallelizable plan for deploying a project."""
    project_name: str
    profile: Optional[ProjectProfile] = None
    server: Optional[ServerProfile] = None
    steps: List[DeploymentStep] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DeploymentHistory(BaseModel):
    """
    Record of a completed (or failed) deployment. (T-034)
    Stored in AXLE's internal SQLite database.
    """
    id: str
    project_name: str
    github_url: str = ""
    status: DeploymentStatus = DeploymentStatus.COMPLETED
    plan: Optional[DeploymentPlan] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None
    rollback_available: bool = False


# =============================================================================
# Monitoring Models
# =============================================================================

class HealthMetrics(BaseModel):
    """
    System health metrics collected every 60 seconds. (T-035)
    Used by the AI monitor for anomaly detection.
    """
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cpu_percent: float = 0.0
    ram_used_mb: float = 0.0
    ram_total_mb: float = 0.0
    disk_used_gb: float = 0.0
    disk_total_gb: float = 0.0
    network_rx_bytes: int = 0
    network_tx_bytes: int = 0
    process_running: bool = True
    http_status_code: Optional[int] = None
    http_response_time_ms: Optional[float] = None
    db_connections_active: Optional[int] = None
    ssl_days_remaining: Optional[int] = None

    @property
    def ram_percent(self) -> float:
        if self.ram_total_mb == 0:
            return 0.0
        return (self.ram_used_mb / self.ram_total_mb) * 100

    @property
    def disk_percent(self) -> float:
        if self.disk_total_gb == 0:
            return 0.0
        return (self.disk_used_gb / self.disk_total_gb) * 100
