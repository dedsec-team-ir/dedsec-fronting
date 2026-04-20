Domain‑Fronting HTTP/HTTPS Proxy

A lightweight Python‑based proxy that attempts domain fronting by routing outbound traffic through google.com while rewriting the Host header to the intended target domain.
It supports standard HTTP methods and a basic CONNECT tunnel for HTTPS (with important limitations).


🚀 Features
HTTP proxy supporting
GET
POST
PUT
DELETE
HEAD
OPTIONS
CONNECT tunneling for HTTPS (with limitations due to SNI)
Threaded server (handles multiple clients at once)
Request logging to console


⚠️ Important Notes
This proxy is for educational and research purposes only.
Modern CDNs and services (including Google) block most domain‑fronting attempts because of SNI mismatch.
HTTPS tunneling is unlikely to work reliably due to required SNI matching during TLS handshake.
Do not use this tool for any unauthorized, malicious, or harmful activities.


📦 Requirements
Python 3.8+
Standard library only (no external packages)


📜 How It Works (High‑Level)
The client sends an HTTP request to the proxy.
The proxy extracts the real target host from the URL.
Instead of connecting directly to the target, the proxy creates a connection to google.com.
It rewrites the Host header to the original destination.
Google receives the request but routes it based on SNI/Host behavior (usually blocked nowadays).

For CONNECT (HTTPS):
The proxy opens a TCP connection to google.com:443.
Raw TLS traffic is forwarded between client and Google.
Because TLS SNI still reveals the target host, domain‑fronting will likely fail.
