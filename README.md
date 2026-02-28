# 🤖 Personal AI Employee - Bronze & Silver Tier Implementation

**Building Autonomous FTEs (Full-Time Equivalent) in 2026**
*Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Bronze Tier Features](# bronze-tier-features)
- [Silver Tier Features](#silver-tier-features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Tech Stack](#tech-stack)
- [License](#license)

## 🌟 Overview

This project implements a fully autonomous AI Employee that operates as your digital full-time equivalent. It proactively manages personal affairs (Gmail, WhatsApp) and business operations (Social Media, Payments) using Claude Code as the reasoning engine and Obsidian as the management dashboard.

**Key Vision:** Transform your AI from a chatbot into a proactive business partner that provides "Monday Morning CEO Briefing" - autonomously auditing bank transactions and tasks to report revenue and bottlenecks.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │ Gmail Watcher│ │WhatsApp Watch│ │Finance Watcher│            │
│  │  (Python)    │ │ (Playwright) │ │   (Python)   │            │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘            │
└─────────┼────────────────┼────────────────┼────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  REASONING LAYER (Claude Code)                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  ┌─────────────────────────────────────────────────┐  │    │
│  │  │     Dashboard.md (Real-time Summary)          │  │    │
│  │  └─────────────────────────────────────────────────┘  │    │
│  │  ┌─────────────────────────────────────────────────┐  │    │
│  │  │   Company_Handbook.md (Rules of Engagement)   │  │    │
│  │  └─────────────────────────────────────────────────┘  │    │
│  │  ┌─────────────────────────────────────────────────┐  │    │
│  │  │         Plan.md (Multi-step Tasks)            │  │    │
│  │  └─────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ACTION LAYER (MCP)                           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │  Gmail MCP   │ │LinkedIn MCP  │ │Human Approval│            │
│  │  (Email Send)│ │(Post Automation││   (Workflow) │            │
│  └──────────────┘ └──────────────┘ └──────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

## ⭐ Bronze Tier Features

### ✅ Foundation (Minimum Viable Deliverable)
- [x] **Obsidian Vault** with `Dashboard.md` and `Company_Handbook.md`
- [x] **One working Watcher script** (Gmail OR file system monitoring)
- [x] **Claude Code** successfully reading from and writing to the vault
- [x] **Basic folder structure**: `/Inbox`, `/Needs_Action`, `/Done`
- [x] **All AI functionality** implemented as [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

### 📁 Basic File Structure
```
AI_Employee_Vault/
├── Dashboard.md
├── Company_Handbook.md
├── Inbox/
├── Needs_Action/
├── Done/
└── Logs/
```

## 🥈 Silver Tier Features

### ✅ Functional Assistant
- [x] **Two or more Watcher scripts** (Gmail + WhatsApp + LinkedIn)
- [x] **Automatically Post on LinkedIn** about business to generate sales
- [x] **Claude reasoning loop** that creates Plan.md files
- [x] **One working MCP server** for external action (e.g., sending emails)
- [x] **Human-in-the-loop approval workflow** for sensitive actions
- [x] **Basic scheduling** via cron or Task Scheduler
- [x] **All AI functionality** as Agent Skills

### 🚀 Enhanced Capabilities
- **Real-time monitoring** with configurable intervals
- **Keyword-based filtering** for urgent messages
- **Persistent browser sessions** for WhatsApp Web
- **Automated LinkedIn posting** with approval gating
- **Intelligent action file creation** with metadata

## 🔧 Tech Stack

### Core Components
| Component | Purpose |
|:----------|:--------|
| [Claude Code](https://claude.com/product/claude-code) | Primary reasoning engine |
| [Obsidian](https://obsidian.md/download) | Knowledge base & dashboard (v1.10.6+) |
| [Python](https://www.python.org/downloads/) | Sentinel scripts & orchestration (3.13+) |
| [Node.js](http://Node.js) | MCP servers & automation (v24+ LTS) |
| [Playwright](https://playwright.dev/) | Browser automation for WhatsApp & LinkedIn |

### File System Architecture
- **Dashboard.md**: Real-time summary of bank balance, pending messages, and active business projects
- **Company_Handbook.md**: "Rules of Engagement" (e.g., "Always be polite on WhatsApp")
- **/Inbox/**: Raw inputs from watchers
- **/Needs_Action/**: Items requiring attention
- **/Needs_Approval/**: Sensitive actions awaiting human approval
- **/Done/**: Completed tasks
- **/Logs/**: Operational logs

## ⚙️ Installation

### Prerequisites
- Python 3.13 or higher
- Node.js v24+ LTS
- Claude Code subscription
- Obsidian v1.10.6+

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Create Python virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies (if MCP servers required):**
   ```bash
   npm install  # If MCP servers exist
   ```

5. **Set up Obsidian vault:**
   - Create a new vault named "AI_Employee_Vault"
   - Copy the provided vault structure

## 🔐 Configuration

### Environment Setup
Create a `.env` file in the root directory:

```env
# Gmail API Configuration
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
GMAIL_CREDENTIALS_PATH=path/to/credentials

# LinkedIn Configuration
LINKEDIN_EMAIL=your-linkedin-email
LINKEDIN_PASSWORD=your-password
LINKEDIN_CLIENT_ID=your-client-id
LINKEDIN_CLIENT_SECRET=your-client-secret
LINKEDIN_REDIRECT_URI=http://localhost:3000

# WhatsApp Configuration
WHATSAPP_SESSION_PATH=./whatsapp_session

# Claude Code Configuration
CLAUDE_CODE_API_KEY=your-claude-api-key

# General Configuration
VAULT_PATH=AI_Employee_Vault
DEV_MODE=true
```

### OAuth Setup (Gmail)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Create credentials (OAuth 2.0 client ID)
5. Download credentials JSON to the specified path

## 🚀 Usage

### Running the AI Employee

#### 1. Start the Gmail Watcher (Continuous Monitoring)
```bash
export $(grep -v '^#' .env | xargs) && python simple_gmail_watcher.py --interval 300
```

#### 2. Start the WhatsApp Watcher (Real-time Monitoring)
```bash
export $(grep -v '^#' .env | xargs) && python whatsapp_watcher.py --vault-dir AI_Employee_Vault --interval 300
```

#### 3. Start the LinkedIn Automation Server
```bash
cd mcp && export $(grep -v '^#' .env | xargs) && python linkedin-mcp-server.py
```

### Watcher Architecture

#### Gmail Watcher
- Monitors Gmail for new messages
- Filters for keywords: urgent, asap, invoice, payment, help
- Creates action files in `/Needs_Action/`

#### WhatsApp Watcher
- Uses Playwright for WhatsApp Web automation
- Maintains persistent browser session
- Real-time monitoring with JavaScript injection
- Creates action files for keyword matches

#### LinkedIn Automation
- Posts business-related content automatically
- Requires human approval for sensitive actions
- Integrates with Claude Code for content generation

### Human-in-the-Loop Workflow
1. AI detects sensitive action requiring approval
2. Creates file in `/Needs_Approval/`
3. Human reviews and moves to `/Approved/` or `/Rejected/`
4. AI processes approved actions

## 📁 File Structure

```
AI_Employee_Hackathon/
├── .env                    # Environment variables
├── .gitignore             # Git ignore rules
├── AI_Employee_Vault/     # Obsidian vault
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── Inbox/
│   ├── Needs_Action/
│   ├── Needs_Approval/
│   ├── Done/
│   └── Logs/
├── mcp/                   # Model Context Protocol servers
│   ├── linkedin-mcp-server.py
│   ├── email-mcp-server.py
│   └── browser-mcp-server.py
├── scripts/               # Automation scripts
│   ├── run_ai_employee.py
│   ├── ai_employee_scheduler.py
│   └── automated_linkedin_poster.py
├── .claude/skills/        # Claude Agent Skills
│   ├── gmail-send/
│   ├── human-approval/
│   ├── linkedin-post/
│   └── vault-file-manager/
├── simple_gmail_watcher.py
├── whatsapp_watcher.py
├── README.md
└── requirements.txt
```

## 🤖 Agent Skills

### Available Skills
- **gmail-send**: Send emails via Gmail API
- **human-approval**: Request and process human approval
- **linkedin-post**: Automate LinkedIn posting
- **vault-file-manager**: Manage vault file operations

### Skill Integration
Each skill follows the structure:
```
.claude/skills/[skill-name]/
├── SKILL.md          # Skill definition
└── scripts/
    └── [script-name].py
```

## 📊 Performance Metrics

| Metric | Bronze Tier | Silver Tier |
|:-------|:------------|:------------|
| Ramp-up Time | 3–6 Months | Instant (via SKILL.md) |
| Consistency | 85–95% accuracy | 99%+ consistency |
| Scaling | Linear (Hire 10 for 10x) | Exponential (Instant duplication) |
| Cost per Task | ~$3.00–$6.00 | ~$0.25–$0.50 |
| Annual Hours | ~2,000 hours | ~8,760 hours |

> **The 'Aha!' Moment**: A Digital FTE works nearly 9,000 hours a year vs a human's 2,000. The cost per task reduction (from ~$5.00 to ~$0.50) is an 85–90% cost saving—usually the threshold where a CEO approves a project without further debate.

## 🛡️ Security & Privacy

- **Local-first approach**: All sensitive data stored locally
- **Credential isolation**: Secrets never synced across systems
- **Approval gating**: Sensitive actions require human approval
- **Audit trail**: Complete action logging in vault
- **Session management**: Secure browser session handling

## 🔄 Continuous vs. Scheduled Operations

| Operation Type | Example Task | Trigger |
|:---------------|:-------------|:--------|
| **Scheduled** | Daily Briefing: Summarize business tasks at 8:00 AM | cron (Mac/Linux) or Task Scheduler (Win) |
| **Continuous** | Lead Capture: Watch WhatsApp for keywords like "Pricing" | Python watchdog script monitoring |
| **Project-Based** | Q1 Tax Prep: Categorize 3 months of business expenses | Manual drag-and-drop of file |

## 🏁 Silver Tier Completion

### ✅ All Requirements Met:
- [x] Enhanced Gmail watcher with continuous monitoring
- [x] Real-time WhatsApp watcher with persistent session
- [x] Automated LinkedIn posting capability
- [x] Claude reasoning loops creating Plan.md files
- [x] MCP servers for external actions
- [x] Human-in-the-loop approval workflows
- [x] Basic scheduling capabilities
- [x] All AI functionality as Agent Skills

## 📈 Future Enhancements (Gold Tier)

- **Cloud deployment** with 24/7 operation
- **Work-zone specialization** (cloud vs local responsibilities)
- **Delegation via Synced Vault** with claim-by-move rules
- **Security hardening** with separate domains
- **Odoo integration** for accounting automation

## 📜 License

This project is part of the Personal AI Employee Hackathon and is intended for educational and research purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🆘 Support

For issues and questions:
- Check the existing documentation
- Create an issue in the repository
- Join the hackathon community for discussions

---

**Built with ❤️ for the Personal AI Employee Hackathon 0**
*Transforming AI from assistants to autonomous business partners*