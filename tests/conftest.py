"""
Shared test fixtures for AXLE OS test suite.
"""
import pytest
import os
import tempfile
from pathlib import Path


@pytest.fixture
def tmp_dir():
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def sample_node_project(tmp_dir):
    """Create a minimal Node.js + Express project structure."""
    pkg = {
        "name": "test-app",
        "version": "1.0.0",
        "scripts": {
            "start": "node server.js",
            "build": "echo 'no build step'"
        },
        "dependencies": {
            "express": "^4.18.0",
            "pg": "^8.11.0"
        }
    }
    import json
    (tmp_dir / "package.json").write_text(json.dumps(pkg, indent=2))
    (tmp_dir / "server.js").write_text("const express = require('express');")
    return tmp_dir


@pytest.fixture
def sample_python_project(tmp_dir):
    """Create a minimal Python + FastAPI project structure."""
    (tmp_dir / "requirements.txt").write_text(
        "fastapi==0.100.0\nuvicorn==0.23.0\npsycopg2-binary==2.9.9\n"
    )
    (tmp_dir / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()")
    return tmp_dir


@pytest.fixture
def sample_static_project(tmp_dir):
    """Create a minimal static HTML site."""
    (tmp_dir / "index.html").write_text("<!DOCTYPE html><html><body>Hello</body></html>")
    (tmp_dir / "style.css").write_text("body { margin: 0; }")
    return tmp_dir


@pytest.fixture
def sample_go_project(tmp_dir):
    """Create a minimal Go project structure."""
    (tmp_dir / "go.mod").write_text("module github.com/test/app\n\ngo 1.22\n")
    (tmp_dir / "main.go").write_text('package main\n\nfunc main() {}\n')
    return tmp_dir
