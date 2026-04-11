"""
Tests for axle.core.scanner — Project stack detection. (T-045)

Covers:
  - Node.js detection: Express, Next.js, with pg/mysql/mongo
  - Python detection: FastAPI, Django, Flask, with psycopg2/pymongo
  - Go detection: Gin, Fiber, with pgx
  - Static site detection: plain HTML
  - Database detection from dependencies
  - Build/start command inference
  - Env var scanning from .env.example
  - Error handling: missing dir, unknown project type
  - Version detection (.nvmrc, engines, .python-version)
"""
import json
import pytest
from pathlib import Path

from axle.core.scanner import scan_repository
from axle.core.models import (
    StackType,
    FrameworkType,
    DatabaseType,
)


# =============================================================================
# Node.js Tests
# =============================================================================

class TestNodejsDetection:

    def test_basic_express(self, tmp_dir):
        pkg = {"name": "my-api", "dependencies": {"express": "^4.18.0"},
               "scripts": {"start": "node server.js"}}
        (tmp_dir / "package.json").write_text(json.dumps(pkg))
        profile = scan_repository(str(tmp_dir))

        assert profile.stack == StackType.NODEJS
        assert profile.framework == FrameworkType.EXPRESS

    def test_nextjs_detection(self, tmp_dir):
        pkg = {"name": "my-next-app", "dependencies": {"next": "^14.0.0", "react": "^18.0.0"},
               "scripts": {"start": "next start", "build": "next build"}}
        (tmp_dir / "package.json").write_text(json.dumps(pkg))
        profile = scan_repository(str(tmp_dir))

        assert profile.framework == FrameworkType.NEXTJS
        assert profile.has_frontend is True
        assert profile.build_command == "next build"

    def test_nestjs_detection(self, tmp_dir):
        pkg = {"name": "nest-api", "dependencies": {"@nestjs/core": "^10.0.0"},
               "scripts": {"start": "nest start"}}
        (tmp_dir / "package.json").write_text(json.dumps(pkg))
        profile = scan_repository(str(tmp_dir))

        assert profile.framework == FrameworkType.NESTJS

    def test_postgresql_detection_via_pg(self, tmp_dir):
        pkg = {"name": "api", "dependencies": {"express": "^4.0.0", "pg": "^8.11.0"},
               "scripts": {"start": "node index.js"}}
        (tmp_dir / "package.json").write_text(json.dumps(pkg))
        profile = scan_repository(str(tmp_dir))

        assert profile.database == DatabaseType.POSTGRESQL

    def test_mysql_detection(self, tmp_dir):
        pkg = {"name": "api", "dependencies": {"express": "^4.0.0", "mysql2": "^3.0.0"},
               "scripts": {"start": "node index.js"}}
        (tmp_dir / "package.json").write_text(json.dumps(pkg))
        profile = scan_repository(str(tmp_dir))

        assert profile.database == DatabaseType.MYSQL

    def test_mongodb_detection(self, tmp_dir):
        pkg = {"name": "api", "dependencies": {"express": "^4.0.0", "mongoose": "^7.0.0"},
               "scripts": {"start": "node index.js"}}
        (tmp_dir / "package.json").write_text(json.dumps(pkg))
        profile = scan_repository(str(tmp_dir))

        assert profile.database == DatabaseType.MONGODB

    def test_node_version_from_nvmrc(self, tmp_dir):
        pkg = {"name": "app", "dependencies": {}, "scripts": {"start": "node index.js"}}
        (tmp_dir / "package.json").write_text(json.dumps(pkg))
        (tmp_dir / ".nvmrc").write_text("18")
        profile = scan_repository(str(tmp_dir))

        assert profile.version == "18"

    def test_node_version_from_engines(self, tmp_dir):
        pkg = {"name": "app", "dependencies": {}, "scripts": {"start": "node index.js"},
               "engines": {"node": ">=20"}}
        (tmp_dir / "package.json").write_text(json.dumps(pkg))
        profile = scan_repository(str(tmp_dir))

        assert profile.version == "20"

    def test_env_vars_scanned(self, tmp_dir):
        pkg = {"name": "app", "dependencies": {"express": "^4.0.0"},
               "scripts": {"start": "node index.js"}}
        (tmp_dir / "package.json").write_text(json.dumps(pkg))
        (tmp_dir / ".env.example").write_text("DATABASE_URL=postgres://...\nSECRET_KEY=abc\n# comment\n")
        profile = scan_repository(str(tmp_dir))

        assert "DATABASE_URL" in profile.env_vars
        assert "SECRET_KEY" in profile.env_vars
        assert len(profile.env_vars) == 2


# =============================================================================
# Python Tests
# =============================================================================

class TestPythonDetection:

    def test_fastapi_from_requirements(self, tmp_dir):
        (tmp_dir / "requirements.txt").write_text("fastapi==0.100.0\nuvicorn==0.23.0\n")
        (tmp_dir / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()")
        profile = scan_repository(str(tmp_dir))

        assert profile.stack == StackType.PYTHON
        assert profile.framework == FrameworkType.FASTAPI
        assert "uvicorn" in profile.start_command
        assert "main:app" in profile.start_command

    def test_django_detection(self, tmp_dir):
        (tmp_dir / "requirements.txt").write_text("django==4.2\npsycopg2-binary==2.9.9\n")
        (tmp_dir / "manage.py").write_text("#!/usr/bin/env python\nimport django")
        profile = scan_repository(str(tmp_dir))

        assert profile.framework == FrameworkType.DJANGO
        assert profile.database == DatabaseType.POSTGRESQL
        assert "manage.py" in profile.start_command

    def test_flask_detection(self, tmp_dir):
        (tmp_dir / "requirements.txt").write_text("Flask==3.0.0\n")
        (tmp_dir / "app.py").write_text("from flask import Flask\napp = Flask(__name__)")
        profile = scan_repository(str(tmp_dir))

        assert profile.framework == FrameworkType.FLASK
        assert profile.port == 5000

    def test_postgresql_via_psycopg2(self, tmp_dir):
        (tmp_dir / "requirements.txt").write_text("fastapi\npsycopg2-binary\n")
        (tmp_dir / "main.py").write_text("")
        profile = scan_repository(str(tmp_dir))

        assert profile.database == DatabaseType.POSTGRESQL

    def test_mongodb_via_pymongo(self, tmp_dir):
        (tmp_dir / "requirements.txt").write_text("flask\npymongo\n")
        (tmp_dir / "app.py").write_text("")
        profile = scan_repository(str(tmp_dir))

        assert profile.database == DatabaseType.MONGODB

    def test_python_version_from_file(self, tmp_dir):
        (tmp_dir / "requirements.txt").write_text("flask\n")
        (tmp_dir / ".python-version").write_text("3.11.5")
        (tmp_dir / "app.py").write_text("")
        profile = scan_repository(str(tmp_dir))

        assert profile.version == "3.11.5"

    def test_build_command_with_requirements(self, tmp_dir):
        (tmp_dir / "requirements.txt").write_text("flask\n")
        (tmp_dir / "app.py").write_text("")
        profile = scan_repository(str(tmp_dir))

        assert profile.build_command == "pip install -r requirements.txt"


# =============================================================================
# Go Tests
# =============================================================================

class TestGoDetection:

    def test_basic_go(self, tmp_dir):
        (tmp_dir / "go.mod").write_text("module github.com/test/app\n\ngo 1.22\n")
        (tmp_dir / "main.go").write_text("package main\nfunc main() {}")
        profile = scan_repository(str(tmp_dir))

        assert profile.stack == StackType.GO
        assert profile.version == "1.22"
        assert profile.start_command == "./app"
        assert "go build" in profile.build_command

    def test_gin_framework(self, tmp_dir):
        go_mod = "module app\n\ngo 1.22\n\nrequire github.com/gin-gonic/gin v1.9.0\n"
        (tmp_dir / "go.mod").write_text(go_mod)
        (tmp_dir / "main.go").write_text("package main")
        profile = scan_repository(str(tmp_dir))

        assert profile.framework == FrameworkType.GIN

    def test_fiber_framework(self, tmp_dir):
        go_mod = "module app\n\ngo 1.22\n\nrequire github.com/gofiber/fiber v2.0.0\n"
        (tmp_dir / "go.mod").write_text(go_mod)
        (tmp_dir / "main.go").write_text("package main")
        profile = scan_repository(str(tmp_dir))

        assert profile.framework == FrameworkType.FIBER

    def test_postgresql_via_pgx(self, tmp_dir):
        go_mod = "module app\n\ngo 1.22\n\nrequire github.com/jackc/pgx v5.0.0\n"
        (tmp_dir / "go.mod").write_text(go_mod)
        (tmp_dir / "main.go").write_text("package main")
        profile = scan_repository(str(tmp_dir))

        assert profile.database == DatabaseType.POSTGRESQL


# =============================================================================
# Static Site Tests
# =============================================================================

class TestStaticDetection:

    def test_basic_static(self, tmp_dir):
        (tmp_dir / "index.html").write_text("<!DOCTYPE html><html><body>Hello</body></html>")
        profile = scan_repository(str(tmp_dir))

        assert profile.stack == StackType.STATIC
        assert profile.has_frontend is True
        assert profile.has_backend is False
        assert profile.database == DatabaseType.NONE
        assert profile.build_command is None

    def test_static_with_dist_dir(self, tmp_dir):
        (tmp_dir / "index.html").write_text("<html></html>")
        dist = tmp_dir / "dist"
        dist.mkdir()
        (dist / "index.html").write_text("<html>built</html>")
        profile = scan_repository(str(tmp_dir))

        assert profile.static_dir == "dist"


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestScannerErrors:

    def test_nonexistent_directory(self):
        with pytest.raises(FileNotFoundError):
            scan_repository("/nonexistent/path/xyz")

    def test_unknown_project_type(self, tmp_dir):
        (tmp_dir / "random.txt").write_text("nothing useful")
        with pytest.raises(ValueError, match="Cannot detect project type"):
            scan_repository(str(tmp_dir))

    def test_file_not_directory(self, tmp_dir):
        file_path = tmp_dir / "file.txt"
        file_path.write_text("hello")
        with pytest.raises(ValueError, match="not a directory"):
            scan_repository(str(file_path))


# =============================================================================
# Priority Tests (Node > Python > Go > Static)
# =============================================================================

class TestDetectionPriority:

    def test_node_takes_priority_over_static(self, tmp_dir):
        """If both package.json and index.html exist, detect as Node."""
        pkg = {"name": "app", "dependencies": {"express": "^4.0.0"}, "scripts": {"start": "node index.js"}}
        (tmp_dir / "package.json").write_text(json.dumps(pkg))
        (tmp_dir / "index.html").write_text("<html></html>")
        profile = scan_repository(str(tmp_dir))

        assert profile.stack == StackType.NODEJS

    def test_node_takes_priority_over_python(self, tmp_dir):
        """If both package.json and requirements.txt exist, detect as Node."""
        pkg = {"name": "app", "dependencies": {"express": "^4.0.0"}, "scripts": {"start": "node index.js"}}
        (tmp_dir / "package.json").write_text(json.dumps(pkg))
        (tmp_dir / "requirements.txt").write_text("flask\n")
        profile = scan_repository(str(tmp_dir))

        assert profile.stack == StackType.NODEJS
