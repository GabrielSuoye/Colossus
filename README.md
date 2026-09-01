# Colossus Command & Control (C2) Distributed Telemetry Architecture

A secure, enterprise-grade distributed surveillance and log ingestion architecture. The pipeline integrates a low-level Linux hardware implant, a symmetric cryptographic transit shield, a high-throughput asynchronous FastAPI data matrix server, and a Streamlit operational visualization panel.

## 🛠️ Architecture & Core Components

### 1. Edge Agent Implant (`client.py`)
- **Kernel-Level Hooking**: Intercepts character blocks directly from Linux subsystem files (`/dev/input/`), bypassing application-isolation security wrappers on modern **Wayland** and X11 display servers.
- **Asynchronous Execution**: Built on `asyncio` and `evdev` event loops to monitor input actions cleanly without causing CPU processing spikes or core hangs.
- **Background Exfiltration Tasks**: Uses `asyncio.create_task()` to schedule outbound HTTP transmissions in the background, ensuring target typing performance is never throttled during high network latency.

### 2. Cryptographic Transit Shield (`crypto_vault.py`)
- **Symmetric Cipher**: Implements **Fernet (AES-128 in CBC mode with an HMAC-SHA256 signature)** via the `cryptography` library.
- **Integrity Enforcement**: Guarantees secure data transport; payloads intercepted mid-transit trigger an instantaneous `InvalidToken` error rather than rendering corrupt or manipulated strings.

### 3. Central Management Matrix (`server.py`)
- **Asynchronous Routing**: Powered by **FastAPI** to enable high-velocity concurrent ingestion pipelines across multiple reporting target nodes.
- **Dependency Injection Security**: Enforces custom perimeter security checks (`X-Argus-Token` headers) to completely drop invalid or unauthenticated scanning traffic.
- **Modern Lifespan Management**: Employs SQLAlchemy 2.0 async context engines and `aiosqlite` thread pools to separate disk operations from the web routing loops.

### 4. Operations Control Console (`dashboard.py`)
- **Rapid-Response UI**: Built with **Streamlit** and **Pandas DataFrames** to rapidly transform raw incoming JSON datastores into categorized, readable operational summaries.
- **Isolated UI Refreshing**: Features optimized `@st.fragment` rendering decorators to auto-pull updates every 3 seconds without causing global browser page flashing.

---

## 📦 System Dependencies & Installation

### Core System Requirements (Fedora / RHEL Modules)
Since the agent communicates directly with system hardware lines, ensure Python headers and input tools are present:
```bash
sudo dnf install python3-devel kbd
```

### Installation Workflow
1. Navigate to the project layout root directory:
   ```bash
   cd ~/Projects/Colossus
   ```
2. Build your local Python virtual environment configuration wrapper and activate it:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install the full engineering requirements sheet:
   ```bash
   pip install fastapi uvicorn sqlalchemy aiosqlite cryptography httpx pydantic-settings streamlit pandas
   ```

---

## 🚀 Execution & Deployment Manual

### 1. Initialize Server Environment Securely
Create a local, untracked environment variables tracking profile:
```bash
touch .env
```
Populate `.env` with your centralized secret variables mapping keys:
```ini
COLOSSUS_SHARED_KEY=PpGmRJE1b_16XobS-LVv2_mG7F8k7UendeG1exLxw3A=
ARGUS_API_TOKEN=super_secret_agent_password_123
```
Launch the central broker engine:
```bash
uvicorn server:app --reload --port 8000
```
*API interactive swagger docs are dynamically accessible at `http://127.0.0`.*

### 2. Run the Streamlit Management Console
Fire up the real-time visual control dashboard in a separate tab session:
```bash
streamlit run dashboard.py
```
*The panel automatically launches on host browser port `http://localhost:8501`.*

### 3. Deploy the Edge Monitoring Agent
Execute the input listener agent on the target machine utilizing hardware access privileges:
```bash
sudo env "PATH=$PATH" python3 client.py
```
*To run this persistently in production environments, compile the agent using **PyInstaller / PyArmor** and configure it as a native background daemon system loop (`/etc/systemd/system/argus.service`).*

---

## 📊 Live System Log Output Model
When user input streams are committed and flushed over the network pipeline, the telemetry dashboard displays clean chronologically-tracked messaging cards:

```text
🎯 Active Targets Monitored: 2          📊 Total Data Logs Intercepted: 6

🤖 Agent: linux-fedora
🕒 2026-08-25 21:10:42
Captured Keystrokes:
testing the secure api token hpf[BACKSPACE][BACKSPACE]nctionality; it works successfully.
```

---

## ⚠️ Compliance & Security Affirmation
This project architecture is constructed explicitly for authorized endpoint monitoring simulations, academic security engineering courses, or credentialed penetration testing frameworks. Unauthorized execution or tracking on computing equipment without explicit administrative ownership consent is unlawful and unethical.
