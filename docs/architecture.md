# AXLE OS Architecture

This document describes the technical architecture of AXLE OS.

## High-Level Overview

AXLE OS follows a three-layer appliance architecture:

1.  **Layer 1: Ubuntu 22.04 LTS Base** - Core operating system.
2.  **Layer 2: Server Stack** - Pre-installed services (Nginx, PostgreSQL, Runtime environments).
3.  **Layer 3: AXLE Appliance** - The intelligent management layer (AI Engine, Task Runner, Dashboard).

## Component Breakdown

### AI Engine
Abstracts multiple LLM providers (OpenAI, Gemini, Ollama) to provide deployment planning and diagnostic capabilities.

### Project Scanner
Analyzes repository contents to detect stacks and requirements without manual input.

### Async Task Runner
Executes multi-step deployment plans in parallel with live log streaming.

### Secrets Vault
An AES-256 encrypted store for environment variables, strictly isolated from the AI inference context.

### Web Dashboard
A real-time React-based interface for management, monitoring, and AI chat.
