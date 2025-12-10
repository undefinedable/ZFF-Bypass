# ZFF-Bypass - Free Fire Emulator Bypass
A lightweight mitmproxy-based interceptor that modifies Protobuf login requests to study and bypass emulator-detection behavior during research and debugging.

## Table of Contents

1. [Introduction](#1-introduction)
2. [Features](#2-features)
3. [Architecture Overview](#3-architecture-overview)
4. [How the System Works](#4-how-the-system-works)

   * [Request Handling](#request-handling)
   * [Response Handling](#response-handling)
   * [UID / Bypass Logic](#uid-validation-logic)
   * [Discord Bot](#discord-bot)
5. [Installation](#5-installation)
6. [Configuration](#6-configuration)

   * [Setting Up mitmproxy](#61-setting-up-mitmproxy)
7. [Running the System](#7-running-the-system)
8. [Project Structure](#8-project-structure)

   * [Code Structure Overview](#8-code-structure-overview)
9. [Disclaimer](#9-disclaimer)
10. [References](#references)

---

## 1. Introduction

The **ZFF-Bypass** is a modular interception framework built around **mitmproxy**, the **Zeppelin API**, Discord webhook integrations, and an optional **Discord bot**.

Its primary purpose is to **intercept, analyze, modify, and forward client traffic**—specifically targeting endpoints such as `/MajorLogin`.
By transforming Protobuf payloads and altering specific request fields, the system is able to **simulate legitimate device behavior**, allowing developers to study **how emulator-detection mechanisms operate** and how requests are processed by the server.

This tool is designed for **research and debugging** scenarios, enabling controlled modification of network flows without altering the original application. Developers can easily extend the logic, inject custom handlers, or integrate additional monitoring components.

---

## 2. Features

* **HTTP Traffic Interception** via mitmproxy
* **Automatic Protobuf Payload Modification** using an external API
* **UID Extraction and Validation** against a local database
* **Custom Error Response Injection** when UID is invalid
* **Discord Webhook Logging** for UID events
* **Optional Discord Bot Integration** running in parallel

---

## 3. Architecture Overview

The system consists of several modular components:

* **mitmproxy** — Acts as the HTTP proxy that captures and routes traffic.
* **MajorLoginInterceptor** — Main addon responsible for request/response handling.
* **ZeppelinAPI** — Communicates with the backend service for Protobuf modification and UID extraction.
* **UIDService** — Handles UID existence checks using internal storage.
* **Webhook Sender** — Pushes UID logs to Discord.
* **Discord Bot (optional)** — Runs independently to provide bot-related functionality.

### High-Level Workflow

1. A client sends a request through the proxy.
2. The interceptor checks for matches (e.g., `/MajorLogin`).
3. Request payload is transformed using the external API.
4. Response payload is analyzed to extract the UID.
5. The UID is validated against the local database.
6. If invalid → the proxy injects a custom error response.
7. If valid → optional webhook logging is triggered.

---

## 4. How the System Works

### Request Handling

If a request matches the configured path:

* Its content is converted to hex
* Sent to the API for modification
* Replaced with the API response (converted back to bytes)

### Response Handling

The response body is:

* Parsed and converted to hex
* Sent to the API to extract the UID
* Validated using `UIDService`

### UID Validation Logic

* **UID not found:**

  * Response body is replaced with a styled message
  * Response status code is changed to `400`
* **UID valid:**

  * Processing continues normally
  * Webhook notification is sent (if enabled)

### Discord Bot

If enabled, the bot runs in a background thread and operates independently of the proxy.

---

## 5. Installation

Install required Python packages:

```bash
pip install -r requirements.txt
```

Install mitmproxy:

```bash
pip install mitmproxy
```

---

## 6. Configuration

Configuration is managed through:

```
config.json
```

Example configuration:

```json
{
  "api_url": "https://api.example.com",
  "proxy_port": 8080,
  "use_webhook": true,
  "use_bot": false,
  "discord": {
    "bot_token": "YOUR_BOT_TOKEN",
    "webhook_url": "YOUR_WEBHOOK_URL"
  }
}
```

---

## 6.1 Setting Up mitmproxy

For full, official, and always up-to-date instructions, refer to the mitmproxy documentation:

**[https://docs.mitmproxy.org](https://docs.mitmproxy.org)**

Below is a concise summary:
Below is a step-by-step guide for setting up mitmproxy, installing its certificate, and configuring HTTP proxy.

### Step 1 — Verify mitmproxy Installation

Check if mitmdump/mitmproxy is installed:

```
mitmdump --version
```

If not installed:

```
pip install mitmproxy
```

### Step 2 — Start mitmproxy

Run your interceptor normally:

```
python main.py
```

### Step 3 — Configure Proxy (Android via ADB)

You can set the device's global HTTP proxy directly using **ADB**:

**Set Proxy:**

```
adb shell settings put global http_proxy <your_ip>:<port>
```

Example:

```
adb shell settings put global http_proxy 192.168.1.10:8080
```

**Clear Proxy:**

```
adb shell settings put global http_proxy :0
```

This sets the proxy for the entire device without manual configuration.

### Step 4 — Certificate Installation (Important)

To intercept HTTPS traffic from any application, you **must install the mitmproxy certificate** on the device or environment being tested.

Details vary depending on platform (Android, Windows, iOS, macOS, Linux).
Users should refer to the official documentation or search for the correct method themselves:

**[https://docs.mitmproxy.org/stable/concepts/certificates/](https://docs.mitmproxy.org/stable/concepts/certificates/)**

> Without installing and trusting the certificate, HTTPS interception will not work.

### Step 6 — Validate Setup — Validate Setup

Open any HTTPS website. If mitmproxy logs traffic, setup is correct.

---

## 7. Running the System

Start the proxy (and bot, if enabled):

```bash
python main.py
```

The proxy will launch on the port specified in `proxy_port`.

---

## 8. Project Structure

```
C:.
│   main.py
│   requirements.txt
│
├───config
│       config.json
│       config.py
│
├───database
│       uids.json
│
└───libs
        api.py
        bot.py
        services.py
        webhook.py
```

## 8. Code Structure Overview

### MajorLoginInterceptor

* `__init__()` – Initializes paths and API client
* `_match()` – Verifies whether a request targets the configured endpoint
* `request()` – Modifies request payload based on API output
* `response()` – Extracts UID and validates it; injects error responses if needed

### ZLabs

* `run_proxy()` – Starts mitmdump with this script as an addon
* `run_bot()` – Runs the Discord bot in a separate thread

---

## 9. Disclaimer

> [!WARNING]
>
> This project is a **research-oriented, unofficial reverse‑engineering utility** intended solely for protocol analysis, debugging, and controlled testing environments. It is **not affiliated with, endorsed by, or associated with any game publisher, service provider, or platform**, including but not limited to Garena, Free Fire.
>
> Usage of traffic interception, protocol manipulation on systems you do not own or do not have explicit authorization to test may violate Terms of Service, contractual agreements, or applicable laws.
> The developer **assumes no liability** for misuse, damage, account penalties, bans, or legal consequences arising from improper use of this software.
>
> This tool is provided **as‑is**, without warranties of any kind.
> Use responsibly, ethically, and within the boundaries of lawful testing.

---

## 10. References

This project references external materials strictly for **technical study**, **interoperability research**, and **understanding protocol structures**.
No external project is affiliated with, endorses, or maintains this repository.

### **Primary References**

1. **FreeFire-Api (Protobuf Structure Reference Only)**
   Source used exclusively for understanding request/response binary layouts and Protobuf message structures.
   > [https://github.com/0xMe/FreeFire-Api](https://github.com/0xMe/FreeFire-Api)

2. **mitmproxy Official Documentation**
   Comprehensive documentation for certificate setup, interception workflows, and addon development.
   > [https://docs.mitmproxy.org](https://docs.mitmproxy.org)

## 11. Demo Video

You can see a short demonstration of the interceptor in action here:

➡️ https://www.youtube.com/shorts/nJKmzTGr3Rs