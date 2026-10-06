# SMP Agent - Server Monitoring Daemon

Lightweight Python agent for the **Server Monitoring Platform (SMP)**. Collects CPU, memory, disk, network metrics, and service checks using `psutil`, pushing data securely over HTTPS.

---

## 1. Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Running the Agent
```bash
python main.py --server http://YOUR_SMP_COLLECTOR_URL:8000 --api-key smp_YOUR_API_KEY --interval 30
```

---

## 2. Configuration File (`config.json`)

You can create a `config.json` file for daemon configuration:
```json
{
  "server_url": "http://localhost:8000",
  "api_key": "smp_xxxxxxxxxxxxxxxxxxxxxxxx",
  "interval": 30,
  "buffer_db_path": "agent_buffer.db",
  "process_checks": ["nginx", "mysqld", "docker"],
  "port_checks": [80, 443, 3306]
}
```

Run with configuration file:
```bash
python main.py --config config.json
```

---

## 3. Systemd Daemon Installation (Linux)

Create `/etc/systemd/system/smp-agent.service`:
```ini
[Unit]
Description=Server Monitoring Platform Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/smp-agent
ExecStart=/usr/bin/python3 /opt/smp-agent/main.py --config /opt/smp-agent/config.json
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable & start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable smp-agent
sudo systemctl start smp-agent
```
