from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class StackType(str, Enum):
    NODEJS = "nodejs"
    PYTHON = "python"
    GO = "go"
    JAVA = "java"
    STATIC = "static"

class DatabaseType(str, Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    NONE = "none"

class ProjectProfile(BaseModel):
    name: str
    github_url: str
    stack: StackType
    version: Optional[str] = None
    database: DatabaseType = DatabaseType.NONE
    env_vars: List[str] = []
    build_command: Optional[str] = None
    start_command: str

class DeploymentStepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class DeploymentStep(BaseModel):
    id: str
    name: str
    command: str
    status: DeploymentStepStatus = DeploymentStepStatus.PENDING
    output: str = ""
    error: Optional[str] = None
    depends_on: List[str] = []

class DeploymentPlan(BaseModel):
    project_name: str
    steps: List[DeploymentStep]
