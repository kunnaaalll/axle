"""
AXLE OS — Project Scanner (T-037 to T-044)

Scans a local project directory (or cloned repo) to detect:
  - Primary stack (Node.js, Python, Go, Java, static)
  - Framework (Express, Django, FastAPI, Next.js, etc.)
  - Database type (PostgreSQL, MySQL, MongoDB, etc.)
  - Build and start commands
  - Environment variable keys
  - Frontend / backend separation

Usage:
    from axle.core.scanner import scan_repository, clone_and_scan
    profile = scan_repository("/path/to/project")
    profile = clone_and_scan("https://github.com/user/repo")
"""
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

from axle.core.models import (
    DatabaseType,
    FrameworkType,
    ProjectProfile,
    StackType,
)


# =============================================================================
# Framework Detection Maps
# =============================================================================

# Node.js: package name → FrameworkType
NODE_FRAMEWORK_MAP = {
    "express": FrameworkType.EXPRESS,
    "next": FrameworkType.NEXTJS,
    "nuxt": FrameworkType.NUXTJS,
    "@nestjs/core": FrameworkType.NESTJS,
    "fastify": FrameworkType.FASTIFY,
}

# Python: package name → FrameworkType
PYTHON_FRAMEWORK_MAP = {
    "django": FrameworkType.DJANGO,
    "fastapi": FrameworkType.FASTAPI,
    "flask": FrameworkType.FLASK,
    "Flask": FrameworkType.FLASK,
    "Django": FrameworkType.DJANGO,
    "FastAPI": FrameworkType.FASTAPI,
}

# Node.js: package name → DatabaseType
NODE_DB_MAP = {
    "pg": DatabaseType.POSTGRESQL,
    "postgres": DatabaseType.POSTGRESQL,
    "sequelize": DatabaseType.POSTGRESQL,  # default assumption
    "prisma": DatabaseType.POSTGRESQL,     # default assumption
    "@prisma/client": DatabaseType.POSTGRESQL,
    "mysql": DatabaseType.MYSQL,
    "mysql2": DatabaseType.MYSQL,
    "mongoose": DatabaseType.MONGODB,
    "mongodb": DatabaseType.MONGODB,
    "redis": DatabaseType.REDIS,
    "ioredis": DatabaseType.REDIS,
}

# Python: package name → DatabaseType
PYTHON_DB_MAP = {
    "psycopg2": DatabaseType.POSTGRESQL,
    "psycopg2-binary": DatabaseType.POSTGRESQL,
    "asyncpg": DatabaseType.POSTGRESQL,
    "psycopg": DatabaseType.POSTGRESQL,
    "mysqlclient": DatabaseType.MYSQL,
    "pymysql": DatabaseType.MYSQL,
    "PyMySQL": DatabaseType.MYSQL,
    "pymongo": DatabaseType.MONGODB,
    "motor": DatabaseType.MONGODB,
    "redis": DatabaseType.REDIS,
    "sqlalchemy": DatabaseType.POSTGRESQL,  # default assumption
    "SQLAlchemy": DatabaseType.POSTGRESQL,
}


# =============================================================================
# Core Scanner Functions
# =============================================================================

def scan_repository(path: str) -> ProjectProfile:
    """
    Scan a local project directory and return a ProjectProfile.

    Detection order:
      1. Check for package.json → Node.js
      2. Check for requirements.txt / pyproject.toml → Python
      3. Check for go.mod → Go
      4. Check for index.html (alone) → Static
      5. Fallback → raise ValueError

    Args:
        path: Absolute or relative path to the project directory.

    Returns:
        ProjectProfile with detected stack, framework, database, and commands.

    Raises:
        ValueError: If the project type cannot be detected.
        FileNotFoundError: If the path does not exist.
    """
    project_dir = Path(path)
    if not project_dir.exists():
        raise FileNotFoundError(f"Project directory not found: {path}")
    if not project_dir.is_dir():
        raise ValueError(f"Path is not a directory: {path}")

    project_name = project_dir.name

    # --- Node.js (T-038) ---
    package_json = project_dir / "package.json"
    if package_json.exists():
        return _scan_nodejs(project_dir, project_name)

    # --- Python (T-039) ---
    requirements_txt = project_dir / "requirements.txt"
    pyproject_toml = project_dir / "pyproject.toml"
    if requirements_txt.exists() or pyproject_toml.exists():
        return _scan_python(project_dir, project_name)

    # --- Go (T-040) ---
    go_mod = project_dir / "go.mod"
    if go_mod.exists():
        return _scan_go(project_dir, project_name)

    # --- Static Site (T-041) ---
    index_html = project_dir / "index.html"
    if index_html.exists():
        return _scan_static(project_dir, project_name)

    raise ValueError(
        f"Cannot detect project type in '{path}'. "
        "Expected package.json, requirements.txt, pyproject.toml, go.mod, or index.html."
    )


def clone_and_scan(github_url: str, branch: str = "main") -> ProjectProfile:
    """
    Clone a GitHub repo to a temp directory, scan it, and return a ProjectProfile. (T-044)

    Args:
        github_url: Full GitHub URL (https://github.com/user/repo)
        branch: Branch to clone (default: main)

    Returns:
        ProjectProfile with github_url set.
    """
    with tempfile.TemporaryDirectory(prefix="axle-scan-") as tmp_dir:
        clone_path = os.path.join(tmp_dir, "repo")
        result = subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", branch, github_url, clone_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            # Try without specifying branch (might be 'master')
            result = subprocess.run(
                ["git", "clone", "--depth", "1", github_url, clone_path],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                raise RuntimeError(f"Failed to clone {github_url}: {result.stderr}")

        profile = scan_repository(clone_path)
        profile.github_url = github_url

        # Try to extract project name from URL
        repo_name = github_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        profile.name = repo_name

        return profile


# =============================================================================
# Stack-Specific Scanners
# =============================================================================

def _scan_nodejs(project_dir: Path, name: str) -> ProjectProfile:
    """Scan a Node.js project (T-038)."""
    pkg_path = project_dir / "package.json"
    try:
        pkg = json.loads(pkg_path.read_text())
    except (json.JSONDecodeError, UnicodeDecodeError):
        pkg = {}

    all_deps = {}
    all_deps.update(pkg.get("dependencies", {}))
    all_deps.update(pkg.get("devDependencies", {}))

    # Detect framework
    framework = FrameworkType.NONE
    for pkg_name, fw_type in NODE_FRAMEWORK_MAP.items():
        if pkg_name in all_deps:
            framework = fw_type
            break

    # Detect database (T-042)
    database = DatabaseType.NONE
    for pkg_name, db_type in NODE_DB_MAP.items():
        if pkg_name in all_deps:
            database = db_type
            break

    # Detect commands (T-043)
    scripts = pkg.get("scripts", {})
    start_command = _infer_node_start(scripts, framework)
    build_command = scripts.get("build")

    # Detect port
    port = _detect_port_from_scripts(scripts)

    # Detect frontend
    has_frontend = framework == FrameworkType.NEXTJS or "react" in all_deps or "vue" in all_deps
    has_backend = framework != FrameworkType.NONE or "express" in all_deps or "http" in str(scripts)

    # Detect env vars
    env_vars = _scan_env_files(project_dir)

    # Detect Node version
    version = _detect_node_version(pkg, project_dir)

    return ProjectProfile(
        name=name,
        stack=StackType.NODEJS,
        framework=framework,
        version=version,
        database=database,
        env_vars=env_vars,
        build_command=build_command,
        start_command=start_command,
        port=port,
        has_frontend=has_frontend,
        has_backend=has_backend,
    )


def _scan_python(project_dir: Path, name: str) -> ProjectProfile:
    """Scan a Python project (T-039)."""
    deps = _read_python_deps(project_dir)

    # Detect framework
    framework = FrameworkType.NONE
    for dep_name, fw_type in PYTHON_FRAMEWORK_MAP.items():
        if dep_name.lower() in [d.lower() for d in deps]:
            framework = fw_type
            break

    # Detect database (T-042)
    database = DatabaseType.NONE
    for dep_name, db_type in PYTHON_DB_MAP.items():
        if dep_name.lower() in [d.lower() for d in deps]:
            database = db_type
            break

    # Detect start command (T-043)
    start_command = _infer_python_start(framework, project_dir)
    build_command = "pip install -r requirements.txt" if (project_dir / "requirements.txt").exists() else None

    # Detect port
    port = 8000 if framework in (FrameworkType.FASTAPI, FrameworkType.DJANGO) else 5000

    env_vars = _scan_env_files(project_dir)

    # Detect Python version
    version = _detect_python_version(project_dir)

    return ProjectProfile(
        name=name,
        stack=StackType.PYTHON,
        framework=framework,
        version=version,
        database=database,
        env_vars=env_vars,
        build_command=build_command,
        start_command=start_command,
        port=port,
        has_frontend=False,
        has_backend=True,
    )


def _scan_go(project_dir: Path, name: str) -> ProjectProfile:
    """Scan a Go project (T-040)."""
    go_mod = (project_dir / "go.mod").read_text()

    # Detect framework
    framework = FrameworkType.NONE
    if "github.com/gin-gonic/gin" in go_mod:
        framework = FrameworkType.GIN
    elif "github.com/gofiber/fiber" in go_mod:
        framework = FrameworkType.FIBER
    elif "github.com/labstack/echo" in go_mod:
        framework = FrameworkType.ECHO

    # Detect database
    database = DatabaseType.NONE
    if "github.com/lib/pq" in go_mod or "github.com/jackc/pgx" in go_mod:
        database = DatabaseType.POSTGRESQL
    elif "github.com/go-sql-driver/mysql" in go_mod:
        database = DatabaseType.MYSQL
    elif "go.mongodb.org/mongo-driver" in go_mod:
        database = DatabaseType.MONGODB

    # Detect Go version
    version_match = re.search(r"^go\s+(\d+\.\d+)", go_mod, re.MULTILINE)
    version = version_match.group(1) if version_match else None

    env_vars = _scan_env_files(project_dir)

    return ProjectProfile(
        name=name,
        stack=StackType.GO,
        framework=framework,
        version=version,
        database=database,
        env_vars=env_vars,
        build_command="go build -o app .",
        start_command="./app",
        port=8080,
        has_frontend=False,
        has_backend=True,
    )


def _scan_static(project_dir: Path, name: str) -> ProjectProfile:
    """Scan a static HTML site (T-041)."""
    static_dir = "."
    # Check for common build output directories
    for candidate in ["dist", "build", "public", "out"]:
        if (project_dir / candidate / "index.html").exists():
            static_dir = candidate
            break

    return ProjectProfile(
        name=name,
        stack=StackType.STATIC,
        framework=FrameworkType.NONE,
        database=DatabaseType.NONE,
        build_command=None,
        start_command="nginx",  # served by Nginx directly
        port=80,
        has_frontend=True,
        has_backend=False,
        static_dir=static_dir,
    )


# =============================================================================
# Helper Functions
# =============================================================================

def _infer_node_start(scripts: dict, framework: FrameworkType) -> str:
    """Infer the start command for a Node.js project. (T-043)"""
    if "start" in scripts:
        return f"npm run start"
    if framework == FrameworkType.NEXTJS:
        return "npm run start"
    if "server.js" in scripts.get("start", ""):
        return "node server.js"
    return "node index.js"


def _infer_python_start(framework: FrameworkType, project_dir: Path) -> str:
    """Infer the start command for a Python project. (T-043)"""
    if framework == FrameworkType.FASTAPI:
        # Look for the main file
        for candidate in ["main.py", "app.py", "api.py"]:
            if (project_dir / candidate).exists():
                module = candidate.replace(".py", "")
                return f"uvicorn {module}:app --host 0.0.0.0 --port 8000"
        return "uvicorn main:app --host 0.0.0.0 --port 8000"

    if framework == FrameworkType.DJANGO:
        # Find manage.py
        if (project_dir / "manage.py").exists():
            return "python manage.py runserver 0.0.0.0:8000"
        return "gunicorn app.wsgi:application --bind 0.0.0.0:8000"

    if framework == FrameworkType.FLASK:
        for candidate in ["app.py", "main.py", "wsgi.py"]:
            if (project_dir / candidate).exists():
                module = candidate.replace(".py", "")
                return f"gunicorn {module}:app --bind 0.0.0.0:5000"
        return "gunicorn app:app --bind 0.0.0.0:5000"

    # Fallback: look for common entry points
    for candidate in ["main.py", "app.py", "server.py", "run.py"]:
        if (project_dir / candidate).exists():
            return f"python {candidate}"

    return "python main.py"


def _read_python_deps(project_dir: Path) -> list:
    """Read Python dependencies from requirements.txt or pyproject.toml."""
    deps = []

    req_file = project_dir / "requirements.txt"
    if req_file.exists():
        for line in req_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-"):
                # Extract package name (before ==, >=, ~=, etc.)
                pkg = re.split(r"[=<>~!;@\[]", line)[0].strip()
                if pkg:
                    deps.append(pkg)

    pyproject = project_dir / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()
        # Simple regex extraction of deps from pyproject.toml
        dep_match = re.findall(r'"([a-zA-Z0-9_-]+)', content)
        deps.extend(dep_match)

    return deps


def _detect_node_version(pkg: dict, project_dir: Path) -> Optional[str]:
    """Detect Node.js version from package.json or .nvmrc."""
    # Check .nvmrc
    nvmrc = project_dir / ".nvmrc"
    if nvmrc.exists():
        return nvmrc.read_text().strip()

    # Check engines in package.json
    engines = pkg.get("engines", {})
    node_version = engines.get("node", "")
    if node_version:
        # Extract major version (e.g., ">=18" → "18")
        match = re.search(r"(\d+)", node_version)
        return match.group(1) if match else None

    return "20"  # Default to LTS


def _detect_python_version(project_dir: Path) -> Optional[str]:
    """Detect Python version from .python-version or runtime.txt."""
    py_version = project_dir / ".python-version"
    if py_version.exists():
        return py_version.read_text().strip()

    runtime = project_dir / "runtime.txt"
    if runtime.exists():
        content = runtime.read_text().strip()
        match = re.search(r"(\d+\.\d+)", content)
        return match.group(1) if match else None

    return "3.12"  # Default


def _detect_port_from_scripts(scripts: dict) -> int:
    """Try to detect the port from npm scripts."""
    start_script = scripts.get("start", "") + scripts.get("dev", "")
    port_match = re.search(r"(?:--port|PORT[=\s]|:)(\d{4,5})", start_script)
    if port_match:
        return int(port_match.group(1))
    return 3000  # Node default


def _scan_env_files(project_dir: Path) -> list:
    """Scan .env.example or .env.sample for variable names. (T-042 partial)"""
    env_keys = []
    for env_file_name in [".env.example", ".env.sample", ".env.template"]:
        env_file = project_dir / env_file_name
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key = line.split("=", 1)[0].strip()
                    if key:
                        env_keys.append(key)
    return env_keys
