# Business Requirements Document
## Self-Hosted Server Monitoring Platform
*Internal infrastructure monitoring and alerting tool*

| Field | Detail |
|---|---|
| Document type | Business Requirements Document (BRD) |
| Project name | Server Monitoring Platform ("SMP") |
| Version | 1.0 (Draft) |
| Date | August 11, 2026 |
| Prepared for | Project owner / self-hosted infrastructure |
| Status | Draft — for review |

---

## 1. Executive Summary

This document defines the business and functional requirements for a self-hosted Server Monitoring Platform (SMP) — a lightweight alternative to tools such as Grafana and Checkmk, purpose-built to monitor the owner's own server infrastructure.

The platform will collect system-level metrics (CPU, memory, disk, network) and service-level checks from each monitored server, store them centrally, visualize them on a dashboard, and alert the owner when defined thresholds are breached. The initial release favors simplicity, security, and fast time-to-value over feature completeness, with a clear path to extend toward parity with commercial tools over time.

## 2. Business Objectives

- Gain real-time visibility into the health of all owned servers from a single dashboard.
- Detect and respond to infrastructure issues (high CPU, low disk space, downed services) before they cause outages.
- Avoid dependency on third-party SaaS monitoring tools and their recurring costs or data-sharing requirements.
- Establish a secure, low-maintenance monitoring foundation that can grow in scope without a rebuild.
- Keep operational overhead low — the tool should be easier to run than the infrastructure it monitors.

## 3. Project Scope

### 3.1 In Scope (Phase 1 — MVP)

- Lightweight monitoring agent installed on each server, collecting CPU, memory, disk, and network metrics.
- Central collector service that receives and stores metrics from all agents.
- Time-series storage of historical metric data.
- Web dashboard showing current status and historical trends per server.
- Threshold-based alerting with notification via webhook (Slack/Telegram) or email.
- Basic service checks (is a process running, is a port open, is disk space below a limit).

### 3.2 In Scope (Later Phases)

- Custom, user-defined checks and plugins (Checkmk-style extensibility).
- Multi-user access with role-based permissions.
- Anomaly detection / trend-based alerting, not just static thresholds.
- Optional agentless checks (SSH key-based) for devices that cannot run an agent, e.g. network appliances.
- Mobile-friendly dashboard and push notifications.

### 3.3 Out of Scope

- Multi-tenant SaaS offering for external customers.
- Storing or requesting server passwords for remote login-based monitoring.
- Log aggregation and full-text log search (may be considered as a separate future project).
- Application performance monitoring (APM) / distributed tracing.

## 4. Stakeholders

| Role | Responsibility |
|---|---|
| Project owner | Defines requirements, uses the platform daily, approves scope changes |
| System administrator (owner) | Installs agents, manages servers, responds to alerts |
| Developer (owner/contributor) | Builds and maintains the platform |

## 5. Assumptions and Constraints

### 5.1 Assumptions

- The owner has root or sudo access on all servers to be monitored.
- All monitored servers can reach the central collector over HTTPS (outbound access).
- Initial server count is small (single digits to low tens), so a single-node deployment is sufficient.

### 5.2 Constraints

- No server passwords will be stored centrally; agent-based, key-less push architecture is required for security.
- The system must run on modest hardware (e.g. a single small VPS or home server) with minimal ongoing cost.
- Development will use Python for the backend and agent, per stack preference.

## 6. Functional Requirements

Requirements are prioritized using MoSCoW: Must have, Should have, Could have, Won't have (this phase).

### 6.1 Data Collection (Agent)

| ID | Requirement | Priority |
|---|---|---|
| FR-1.1 | Agent collects CPU utilization, memory usage, disk usage, and network I/O at a configurable interval (default 30s). | Must |
| FR-1.2 | Agent runs as a background service and auto-starts on boot. | Must |
| FR-1.3 | Agent pushes metrics to the collector over HTTPS using an authenticated request (API key per agent). | Must |
| FR-1.4 | Agent supports basic service checks: process running, port open/closed, disk space below threshold. | Should |
| FR-1.5 | Agent buffers metrics locally and retries if the collector is temporarily unreachable. | Should |
| FR-1.6 | Agent supports user-defined custom check scripts. | Could |

### 6.2 Central Collector

| ID | Requirement | Priority |
|---|---|---|
| FR-2.1 | Collector exposes an authenticated API endpoint to receive metrics from agents. | Must |
| FR-2.2 | Collector validates incoming payloads and rejects malformed or unauthenticated requests. | Must |
| FR-2.3 | Collector writes metrics to persistent time-series storage. | Must |
| FR-2.4 | Collector supports registering new agents/servers with a unique identifier and API key. | Must |
| FR-2.5 | Collector exposes a read API for the dashboard to query historical and current data. | Must |

### 6.3 Dashboard

| ID | Requirement | Priority |
|---|---|---|
| FR-3.1 | Dashboard displays a list of all registered servers with current status (healthy / warning / critical / offline). | Must |
| FR-3.2 | Dashboard displays historical charts (CPU, memory, disk, network) per server over selectable time ranges. | Must |
| FR-3.3 | Dashboard highlights servers currently in an alert state. | Must |
| FR-3.4 | Dashboard supports viewing details for a single server (all metrics, recent alert history). | Should |
| FR-3.5 | Dashboard is accessible via browser and requires authentication to view. | Must |
| FR-3.6 | Dashboard is usable on mobile browsers. | Could |

### 6.4 Alerting

| ID | Requirement | Priority |
|---|---|---|
| FR-4.1 | System supports defining threshold rules per metric (e.g. CPU > 90% for 5 minutes). | Must |
| FR-4.2 | System evaluates alert rules on a regular schedule against incoming/stored data. | Must |
| FR-4.3 | System sends notifications via webhook (Slack/Telegram) or email when a rule is triggered. | Must |
| FR-4.4 | System sends a recovery notification when a triggered alert condition clears. | Should |
| FR-4.5 | System suppresses duplicate/repeat notifications for an already-active alert. | Should |
| FR-4.6 | System flags a server as offline if no metrics are received within a configurable window. | Must |

### 6.5 Administration

| ID | Requirement | Priority |
|---|---|---|
| FR-5.1 | Owner can add, rename, and remove monitored servers. | Must |
| FR-5.2 | Owner can configure alert thresholds per server or globally. | Must |
| FR-5.3 | Owner can revoke an agent's API key (e.g. decommissioned server). | Should |
| FR-5.4 | System supports multiple user accounts with distinct logins. | Could |

## 7. Non-Functional Requirements

| Category | Requirement |
|---|---|
| Security | No server credentials (passwords or SSH keys granting broad access) are stored centrally. Agent-to-collector traffic is authenticated (API key) and encrypted (HTTPS/TLS). |
| Security | Dashboard access requires authentication; sessions expire after a period of inactivity. |
| Reliability | Collector should tolerate brief agent disconnects without data loss (agent-side buffering and retry). |
| Performance | Dashboard queries for a 24-hour view should return in under 2 seconds for up to 50 monitored servers. |
| Scalability | Architecture should support growing from a handful of servers to 50+ without a redesign, though Phase 1 targets low tens. |
| Maintainability | Codebase should be modular (agent, collector, alerting, dashboard as separable components) to ease future extension. |
| Cost | Entire system should run on a single small VPS or home server (e.g. 1-2 vCPU, 2-4GB RAM) at Phase 1 scale. |
| Portability | Agent should run on common Linux distributions at minimum; Windows support is a later consideration. |

## 8. Proposed Technical Approach

The system follows an agent-based (push) model rather than an agentless (pull/SSH) model. Each monitored server runs a lightweight Python agent that collects its own metrics and pushes them to a central collector — no server passwords or broadly-scoped SSH keys are ever stored centrally, which significantly reduces the security blast radius of the monitoring system itself.

| Component | Proposed technology | Notes |
|---|---|---|
| Agent | Python + psutil | Runs as a systemd service; pushes JSON metrics over HTTPS |
| Collector API | Python + FastAPI | Authenticated ingest endpoint; validates and persists metrics |
| Storage | MySQL (Phase 1) | Indexed on (server_id, timestamp); revisit engine choice if scale requires a dedicated time-series store |
| Alert engine | Scheduled job within the collector service | Evaluates threshold rules; sends webhook/email notifications |
| Dashboard | FastAPI + lightweight frontend (charts) | Can later be swapped for Grafana pointed at the same database |

## 9. Success Criteria

1. All owned servers report metrics to the dashboard within 1 minute of agent installation.
2. A simulated resource spike (e.g. CPU pegged, disk filled) triggers a notification within the configured evaluation window.
3. The owner can determine server health at a glance without needing to SSH into individual machines.
4. No server passwords or unscoped credentials are stored anywhere in the system.
5. The system runs unattended for 30+ days without manual intervention beyond planned maintenance.

## 10. Rollout Plan

| Phase | Deliverable | Target outcome |
|---|---|---|
| Phase 1 — MVP | Agent, collector, storage, basic dashboard, threshold alerting | Core visibility and alerting across all servers |
| Phase 2 — Hardening | Auth improvements, alert suppression/recovery, offline detection | Reduced noise, more trustworthy alerts |
| Phase 3 — Extensibility | Custom checks/plugins, multi-user access | Feature parity approaching Checkmk-style flexibility |
| Phase 4 — Polish | Mobile-friendly UI, push notifications, optional agentless checks | Broader device coverage and usability |

## 11. Risks

| Risk | Mitigation |
|---|---|
| Single point of failure: if the collector goes down, all monitoring stops. | Keep the collector lightweight enough to redeploy quickly; consider a simple external heartbeat/dead-man's-switch check in a later phase. |
| Alert fatigue from poorly tuned thresholds. | Start with conservative defaults; add alert suppression and recovery notifications early. |
| Agent compromise on a monitored server. | Scope agent API keys to write-only metric submission; agent should not accept inbound commands from the collector in Phase 1. |
| Scope creep toward full Grafana/Checkmk feature parity slows MVP delivery. | Hold strictly to the Phase 1 scope in Section 3.1 before considering later-phase items. |

## 12. Open Questions

- Should alert notification channel(s) (Slack, Telegram, email) be finalized before Phase 1, or configurable per deployment?
- What is the target retention period for historical metric data (e.g. 30, 90, 365 days)?
- Is a single central collector acceptable long-term, or should high availability be considered in Phase 2?