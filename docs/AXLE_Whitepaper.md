**AXLE**

AI-Powered Linux Deployment Engine

Technical Whitepaper

Version 1.0

March 2026

+:---------------------------------------------------------------------:+
| **Deploy any full-stack application to AWS EC2 with zero manual       |
| configuration.**                                                      |
|                                                                       |
| AI handles Nginx, SSL, databases, dependencies, monitoring ---        |
| everything.                                                           |
+-----------------------------------------------------------------------+

**1. Executive Summary**

AXLE (AI-Powered Linux Deployment Engine) is an open-source, self-hosted
deployment framework that eliminates the complexity of configuring and
managing full-stack applications on AWS EC2 instances. By combining an
intelligent AI engine, automated server configuration, a real-time web
dashboard, and a secure secrets vault, AXLE allows developers to go from
a GitHub repository to a fully live, HTTPS-enabled production
environment in minutes --- without writing a single configuration file.

Unlike managed platforms such as Vercel or Heroku, AXLE runs entirely on
infrastructure owned by the developer. There are no per-seat fees, no
vendor lock-in, and no restrictions on backend workloads, long-running
processes, or database types. The developer retains full root access to
their EC2 machine while the AI handles all of the configuration
complexity automatically.

+-----------------------------------------------------------------------+
| **Core Value Proposition**                                            |
|                                                                       |
| AXLE gives developers the control of raw EC2 infrastructure combined  |
| with the simplicity of a managed platform --- without paying platform |
| fees or surrendering ownership of their infrastructure.               |
+-----------------------------------------------------------------------+

**2. The Problem**

**2.1 Manual EC2 Configuration Is Broken**

Deploying a production-grade full-stack application on a raw AWS EC2
instance currently requires a developer to manually complete dozens of
interdependent configuration steps. A typical deployment of a Node.js +
React + PostgreSQL application involves:

- Installing the correct runtime version (Node.js, Python, Java, etc.)

- Configuring Nginx as a reverse proxy with correct server blocks and
  path routing

- Obtaining and renewing SSL certificates via Certbot for HTTPS

- Installing, initialising, and securing a database server

- Running database migrations in the correct order

- Writing systemd service files for process management and auto-restart

- Managing environment variables securely without leaking secrets

- Setting up monitoring, log rotation, and anomaly alerting

Each of these steps is documented across dozens of different sources, is
highly version-sensitive, and breaks in different ways depending on the
Linux distribution, hardware specification, and application stack. A
single misconfigured Nginx block, missing SSL renewal cron job, or
incorrectly scoped database user can bring down a production
environment.

**2.2 Existing Solutions Fall Short**

  ---------------------- ---------------------- -------------------------
  **Solution**           **What it does well**  **Where it fails**

  Vercel / Netlify       Fast deploys for       No custom backends,
                         frontend apps          vendor lock-in, high cost
                                                at scale

  Raw EC2 + bash scripts Full control           Breaks constantly, not
                                                reusable, requires deep
                                                Linux expertise

  Ansible / Terraform    Infrastructure as code Steep learning curve,
                                                verbose, no AI or
                                                self-healing

  Docker / Kubernetes    Container              Massive operational
                         orchestration          overhead for small to
                                                mid-scale apps

  Heroku / Railway       Simple PaaS            Expensive, limited
                                                control, no custom server
                                                config
  ---------------------- ---------------------- -------------------------

**3. Solution --- What AXLE Does**

AXLE is a thin, intelligent middleware layer that sits between the
developer and their EC2 machine. It does not abstract away the
infrastructure --- it automates the configuration of it. The developer
retains full SSH access and root control at all times. AXLE simply
ensures that the server is correctly configured so they never have to do
it manually.

**3.1 Project Ingestion**

Developers submit their project to AXLE in one of three ways:

- Paste a GitHub or GitLab repository URL

- Connect via OAuth for private repository access

- Upload a ZIP archive of their project

AXLE\'s scanner immediately analyses the project files --- package.json,
requirements.txt, Dockerfile, composer.json, Gemfile, go.mod, and others
--- to automatically detect the full technology stack without any manual
input from the developer.

**3.2 AI-Powered Deployment Planning**

Once the stack is identified, AXLE\'s AI engine (supporting OpenAI,
Google Gemini, and locally-hosted Ollama models) constructs a complete,
ordered deployment plan tailored to both the project\'s requirements and
the EC2 instance\'s hardware specifications. The plan accounts for:

- Correct runtime and dependency versions

- Database type, version, and initial configuration

- Nginx server block structure and path routing rules

- SSL certificate acquisition and auto-renewal scheduling

- systemd service definitions for process management

- Memory and CPU limits based on available instance resources

**3.3 Automated EC2 Execution**

The async task runner executes all deployment steps in parallel wherever
dependencies allow, dramatically reducing total deployment time. The
following tasks are fully automated:

  -------------------- --------------------------------------------------
  **Task**             **What AXLE does automatically**

  Install dependencies apt, pip, npm, composer --- correct versions
                       detected from project files

  Configure Nginx      Writes server blocks, path routing, upstream proxy
                       config, validates before reload

  SSL via Certbot      Requests certificate, configures HTTPS redirect,
                       schedules auto-renewal

  Database setup       Installs PostgreSQL/MySQL/MongoDB, creates DB and
                       user, runs migrations

  Process management   Writes systemd unit files, enables auto-restart on
                       crash or reboot

  Build step           Runs npm run build, pip install, cargo build ---
                       framework-aware
  -------------------- --------------------------------------------------

**3.4 Secrets Vault --- Isolated Environment Management**

Environment variables and secrets are handled in a completely isolated,
encrypted vault that is architecturally separated from the AI engine and
the web chatbot. This design ensures that:

- The AI model never has access to secret values --- only to key names

- Secrets are encrypted at rest using AES-256

- Values are injected into the deployment process at runtime only

- No secret values ever appear in deployment logs or the dashboard UI

- Developers manage secrets in a dedicated section of the dashboard,
  separate from all other functionality

+-----------------------------------------------------------------------+
| **Security Design Principle**                                         |
|                                                                       |
| The secrets vault is a separate subsystem from the AI engine. The AI  |
| plans the deployment using key names only (e.g. DATABASE_URL,         |
| SECRET_KEY). It never sees the actual values. Secrets are decrypted   |
| and injected directly into the process environment at execution time, |
| and are never written to disk in plaintext.                           |
+-----------------------------------------------------------------------+

**3.5 Real-Time Dashboard**

Every deployment step streams its output to the web dashboard in real
time via WebSocket. Developers see exactly what is running, in what
order, with timestamps and exit codes. The dashboard is browser-based
and works identically across Windows, macOS, and Linux client machines.

- Live log stream --- every shell command and its output visible as it
  runs

- Step-by-step progress tracker --- visual status for each deployment
  task

- Deployment history --- full logs of every past deployment retained

- One-click rollback --- revert to any previous successful deployment
  state

**3.6 AI Monitor and Auto-Fix**

After deployment, AXLE\'s monitor runs a health check every 60 seconds.
It tracks CPU usage, memory consumption, disk I/O, HTTP response codes,
database connection pool status, and process uptime. When an anomaly is
detected, the AI engine diagnoses the root cause and either applies an
automated fix or surfaces a plain-English explanation in the web
chatbot.

- Process crash --- systemd restarts the process; AI logs the exit code
  and identifies the likely cause

- Memory exhaustion --- AI identifies the likely endpoint or query
  responsible and recommends a fix

- SSL expiry --- Certbot renewal is triggered automatically before
  expiry

- Database connection saturation --- AI identifies the pool
  configuration and suggests tuning values

**3.7 Web Chatbot Interface**

The dashboard includes a web-based chatbot powered by the same AI engine
used for deployment planning. The chatbot has full access to live server
metrics, deployment history, and log data. Developers can ask natural
language questions about their running deployment:

- \"Why is my app responding slowly right now?\"

- \"What changed in the last deployment?\"

- \"Why did my backend crash at 3am?\"

- \"How much disk space do I have left?\"

- \"Is my database running out of connections?\"

The chatbot answers using real data from the live server --- not generic
advice. It has context of the entire deployment history, the current
stack, and the live system metrics.

**4. System Architecture**

**4.1 High-Level Architecture**

AXLE is structured in four distinct zones, each with clear boundaries
and responsibilities:

  ------------------ --------------------------- -------------------------
  **Zone**           **Components**              **Responsibility**

  Project Input      GitHub/GitLab connector,    Accepts project source
                     ZIP uploader, Web chatbot   and passes to scanner
                     intake                      

  AI Engine          Project scanner, Plan       Analyses project,
                     generator, Secrets vault,   constructs plan, executes
                     Async task runner           tasks in parallel

  EC2 Execution      Nginx plugin, SSL plugin,   Configures server ---
                     Database plugin, systemd    installs, configures,
                     plugin                      starts all services

  Dashboard          Real-time log viewer, AI    Visibility, control, and
                     monitor, Web chatbot,       ongoing intelligence
                     Rollback manager            layer
  ------------------ --------------------------- -------------------------

**4.2 Single EC2 Machine Deployment**

AXLE fully supports --- and is optimised for --- running a complete
application stack (frontend, backend, and database) on a single EC2
instance. This is the most cost-effective topology for small to
medium-scale applications and is the primary deployment target for
AXLE\'s initial release.

On a single machine, AXLE configures the following service topology:

- Nginx on ports 80/443 --- terminates SSL, serves static frontend
  files, proxies /api/ to backend

- Backend application on localhost:3000 or :8000 --- managed by systemd,
  never exposed to internet

- Database on local socket --- no TCP overhead, fastest possible
  connection, not network-accessible

- All processes restarted automatically by systemd on crash or reboot

**4.3 Recommended EC2 Instance Sizing**

  --------------------------- --------------------- ---------------------
  **Use case**                **Recommended         **RAM**
                              instance**            

  Personal project / MVP      t3.small              2 GB

  Small production            t3.medium             4 GB
  application                                       

  Medium traffic application  t3.large              8 GB

  Heavy backend with large DB t3.xlarge             16 GB
  --------------------------- --------------------- ---------------------

**4.4 Project Structure**

The AXLE codebase is organised into clearly separated modules:

+-----------------------------------------------------------------------+
| **Repository Layout**                                                 |
|                                                                       |
| axle/ core/ scanner.py --- Detects stack from project files           |
| planner.py --- AI-powered deployment plan builder runner.py --- Async |
| parallel task executor plugins/ nginx.py --- Nginx config writer and  |
| validator ssl.py --- Certbot automation database.py --- DB setup and  |
| migrations systemd.py --- Service management secrets/ vault.py ---    |
| Encrypted env store, isolated from AI monitor/ health.py ---          |
| 60-second checks and AI anomaly detection web/ dashboard/ ---         |
| Real-time log viewer and status UI chatbot/ --- AI chat interface for |
| live deployments api.py --- REST and WebSocket server ai/ engine.py   |
| --- OpenAI, Gemini, Ollama multi-provider config/ settings.py ---     |
| Configuration management                                              |
+-----------------------------------------------------------------------+

**5. Cross-Platform Support**

AXLE supports Windows, macOS, and Ubuntu/Linux as client operating
systems. The EC2 agent always runs on Linux (Ubuntu 22.04 LTS
recommended), but the developer-facing tools and dashboard work
identically across all three client platforms.

**5.1 Installation per Platform**

  -------------- ---------------------------------------------------------
  **Platform**   **Installation method**

  Windows        Download axle-setup.exe --- one-click installer, no
                 prerequisites required

  macOS          brew install axle-deploy --- or download axle.dmg

  Ubuntu / Linux curl -fsSL https://axle.sh/install \| bash
  -------------- ---------------------------------------------------------

After installation on any platform, AXLE runs a lightweight background
service and places an icon in the system tray (Windows) or menu bar
(macOS). Clicking the icon opens the web dashboard in the default
browser at localhost:4000. From that point, the experience is identical
across all operating systems --- the dashboard is fully browser-based.

**5.2 Technology Stack for Cross-Platform Support**

  ------------------ -------------------------- --------------------------
  **Layer**          **Technology**             **Reason**

  Core CLI and agent Python 3.10+               Runs identically on all
                                                platforms

  Web dashboard      React + Flask              Browser-based, OS-agnostic

  Windows packaging  PyInstaller + Inno Setup   Bundles Python runtime
                                                into .exe

  macOS packaging    PyInstaller + create-dmg   Native .dmg with no
                                                prerequisites

  Linux packaging    apt package / curl script  Native, zero overhead

  System tray        pystray library            Cross-platform tray
                                                support

  SSH to EC2         paramiko (Python SSH)      No OpenSSH dependency on
                                                Windows
  ------------------ -------------------------- --------------------------

**6. Comparison to Existing Solutions**

  --------------------------- --------------------- ---------------------
  **Feature**                 **AXLE**              **Vercel**

  Infrastructure ownership    Your own EC2          Vercel\'s servers

  Cost model                  AWS instance cost     Per-seat and usage
                              only                  billing

  Backend applications        Any --- Node, Python, Serverless functions
                              Java, Go, PHP         only

  Long-running processes      Full support via      Not supported
                              systemd               

  Custom databases            Installed directly on External only
                              EC2                   

  Custom Nginx rules          Full control          Not possible

  AI configuration            Core feature          None

  Self-healing monitor        Built-in, every 60    None
                              seconds               

  Private / internal apps     Fully self-hosted     Requires paid plan

  Secrets management          Encrypted vault,      Environment variables
                              AI-isolated           in UI
  --------------------------- --------------------- ---------------------

**7. Security Model**

**7.1 Secrets Isolation**

The secrets vault is the most security-sensitive component of AXLE and
is designed with strict isolation in mind. Environment variable values
are encrypted at rest using AES-256 and are never passed to the AI
engine, the chatbot, or any external service. The AI receives only the
key names when building a deployment plan.

**7.2 Network Security**

- The AXLE dashboard is accessible only from localhost by default --- it
  is not exposed to the internet

- The backend application process binds to localhost only --- Nginx is
  the only internet-facing service

- The database binds to a local Unix socket --- it is not accessible
  over any network interface

- SSL certificates are obtained automatically via Let\'s Encrypt and
  renewed before expiry

**7.3 EC2 Access**

- AXLE connects to EC2 using the SSH key provided by the developer
  during setup

- The SSH key is stored locally on the developer\'s machine and is never
  transmitted to any AXLE service

- All communication between the AXLE client and the EC2 agent is over
  SSH

**8. System Requirements**

**8.1 EC2 Server Requirements**

- Operating system: Ubuntu 22.04 LTS (recommended) or Ubuntu 20.04 LTS

- Minimum RAM: 2 GB (t3.small or equivalent)

- Minimum disk: 20 GB

- Root or sudo access required for initial AXLE agent installation

- Inbound ports: 22 (SSH), 80 (HTTP), 443 (HTTPS)

**8.2 Client Machine Requirements**

- Windows 10/11, macOS 12+, or Ubuntu 20.04+

- 4 GB RAM minimum on client machine

- Modern browser (Chrome, Firefox, Safari, Edge)

- SSH key pair for EC2 access

**8.3 AI Provider Requirements**

- At least one AI provider configured: OpenAI API key, Google Gemini API
  key, or Ollama running locally

- Ollama requires no API key --- runs entirely locally on the
  developer\'s machine

**9. Roadmap**

  ------------ -----------------------------------------------------------
  **Phase**    **Features**

  Phase 1 ---  GitHub/GitLab ingestion, ZIP upload, AI deployment planner,
  Core (v1.0)  Nginx + SSL automation, PostgreSQL and MySQL support,
               systemd process management, real-time log dashboard,
               secrets vault

  Phase 2 ---  60-second health monitor, AI anomaly detection, auto-fix
  Monitor      for common issues, deployment history and rollback, web
  (v1.5)       chatbot with live server context

  Phase 3 ---  MongoDB and Redis support, multi-server deployments,
  Scale (v2.0) blue-green deployment strategy, CI/CD webhook triggers
               (push to deploy), Windows and macOS packaged installers

  Phase 4 ---  Team access controls, audit logging, custom domain
  Enterprise   management, multi-region EC2 support, Slack and email alert
  (v3.0)       integrations
  ------------ -----------------------------------------------------------

**10. Conclusion**

AXLE addresses a genuine and widespread problem: the gap between the
simplicity of managed deployment platforms and the control of raw cloud
infrastructure. Developers who choose EC2 for cost, compliance, or
architectural reasons currently face hours of manual configuration work
for every new deployment. AXLE eliminates that work entirely.

By combining intelligent stack detection, AI-powered configuration,
parallel async execution, an isolated secrets vault, real-time log
streaming, and continuous AI monitoring, AXLE delivers a deployment
experience that rivals managed platforms --- without surrendering any
infrastructure ownership or incurring platform fees.

AXLE is designed to be the deployment framework that developers reach
for when they need real control of real servers, and want the machine to
handle the configuration so they can focus on building their product.

+-----------------------------------------------------------------------+
| **Get Started**                                                       |
|                                                                       |
| Install AXLE on your EC2 instance with a single command: curl -fsSL   |
| https://axle.sh/install \| bash Then open http://your-ec2-ip:4000 to  |
| access the dashboard.                                                 |
+-----------------------------------------------------------------------+

**Appendix A --- Glossary**

  ------------- ---------------------------------------------------------
  **Term**      **Definition**

  AXLE          AI-Powered Linux Deployment Engine --- the framework
                described in this document

  EC2           Amazon Elastic Compute Cloud --- virtual server instances
                provided by AWS

  Nginx         High-performance web server and reverse proxy, used by
                AXLE to route traffic

  Certbot       Let\'s Encrypt client tool used by AXLE to obtain and
                renew SSL certificates

  systemd       Linux init system used by AXLE to manage application
                processes

  Ollama        Tool for running large language models locally, supported
                as an AI provider by AXLE

  Reverse proxy A server that forwards client requests to a backend
                service --- Nginx acts as this in AXLE

  Secrets vault AXLE\'s encrypted, AI-isolated store for environment
                variables and API keys

  paramiko      Python SSH library used by AXLE to connect to EC2 from
                Windows clients

  AES-256       Advanced Encryption Standard with 256-bit keys --- used
                by AXLE\'s secrets vault
  ------------- ---------------------------------------------------------
