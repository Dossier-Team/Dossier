# Dossier voice agent: Lambrou emergency line

Someone calls the Twilio number. Twilio asks this server what to do (`POST /twiml`), and the server streams the call's audio over a WebSocket (`/media`) to a Deepgram voice agent, which answers as Lambrou Real Estate's emergency maintenance line. When the call ends, Gemini pulls the caller's details out of the transcript, and the transcript and details are posted to getdossier.org. There the request is classified, routed to a team and logged, and it appears on the Live page (getdossier.org/demo/live).

This is the `lambrou-emergency-line` branch. `main` is the scam-call version.

## How a call goes

- **Greeting:** "Thanks for calling Lambrou Real Estate's emergency maintenance line. I'm an automated assistant, and this call is transcribed. How can I help you?"
- **Script** (`src/agent/prompts.py`): what's wrong, the address and unit, the caller's name, whether the number they called from is the best one, and an optional email that the agent reads back to confirm. A gas smell, smoke, fire, a CO alarm, sparks or an injury gets "get everyone out and call 911" first. The agent never promises a time or a cost.
- **Hanging up:** the agent says goodbye, then calls an `end_call` function. The bridge waits until Twilio confirms the goodbye has played, then closes the stream, and the `<Hangup />` after `<Connect>` ends the call.
- **After the call** (`src/extraction/service.py`): Gemini 3.7 Flash fills in `MaintenanceCall` (name, address, callback number, problem, email, whether the email was confirmed). The call is posted to `CALL_INTAKE_URL` with `CALL_INTAKE_TOKEN` as a Bearer token, with two retries. If extraction fails, the transcript is sent without details. If sending fails, the transcript is written to the log so it isn't lost.
- **Models:** Deepgram Flux listens, Gemini 2.5 Flash (through Deepgram) writes the replies, and Deepgram Aura-2 Thalia speaks (`src/agent/settings.py`).

## Security

- `/twiml` checks Twilio's `X-Twilio-Signature` against `TWILIO_AUTH_TOKEN`, over the URL `https://PUBLIC_HOST_NAME/twiml`. Anything else gets a 403.
- `/twiml` gives each call a stream token. `/media` accepts only a stream carrying the right token for its call, and checks it before opening a Deepgram session, so nobody else can run up the Deepgram bill.

## Settings (`.env`)

| Name | What it is |
| --- | --- |
| `DEEPGRAM_API_KEY` | Deepgram console > API Keys |
| `GEMINI_API_KEY` | Google AI Studio > API keys. Used for the after-call extraction |
| `PUBLIC_HOST_NAME` | The host Twilio reaches, without `https://`: `voice.getdossier.org` |
| `TWILIO_AUTH_TOKEN` | Twilio console > Account info > Auth Token |
| `CALL_INTAKE_TOKEN` | A long random string (`openssl rand -hex 32`). The same value is the `CALL_INTAKE_TOKEN` secret on the getdossier.org Worker |
| `CALL_INTAKE_URL` | Optional. Defaults to `https://getdossier.org/demo/api/inbound/call` |

The server won't start without the first five.

## Deploying on AWS

One EC2 instance runs the app and [Caddy](https://caddyserver.com), which gets the HTTPS certificate and passes the WebSocket through (`docker-compose.yml`, `Caddyfile`). Lambda doesn't fit: each call holds a WebSocket open to Twilio and another to Deepgram for the whole call.

1. **Launch the instance.** EC2 > Launch instance. Choose Ubuntu Server 24.04 LTS (x86), `t3.small`, and a key pair you can SSH with. Under Network settings, allow SSH from My IP, and allow HTTP and HTTPS from the internet (Twilio connects from any address). Use 16 GB of storage.
2. **Give it a fixed address.** EC2 > Elastic IPs > Allocate, then Associate it with the instance.
3. **Point the name at it.** Cloudflare > getdossier.org > DNS > Add record: type `A`, name `voice`, the Elastic IP, Proxy status **DNS only** (grey cloud), so Caddy can get its certificate.
4. **Install Docker.** SSH in (`ssh -i your-key.pem ubuntu@<elastic-ip>`), then:
   ```bash
   sudo apt-get update && sudo apt-get install -y docker.io docker-compose-v2 git
   ```
5. **Get the code and settings.**
   ```bash
   git clone -b lambrou-emergency-line https://github.com/Dossier-Team/Dossier.git && cd Dossier
   cp .env.example .env && nano .env
   ```
6. **Start it.**
   ```bash
   sudo docker compose up -d --build
   ```
7. **Check it.** `curl https://voice.getdossier.org/` should print `{"status":"ok"}`. The first request can take a few seconds while Caddy gets the certificate.

To update after a push: `git pull && sudo docker compose up -d --build`. To watch calls: `sudo docker compose logs -f app`.

## Twilio

The account must be upgraded. On a trial account, `<Connect><Stream>` plays the trial notice and then hangs up. Under Phone Numbers > Active numbers > your number > Voice configuration:

| Setting | Value |
| --- | --- |
| A call comes in | Webhook, `https://voice.getdossier.org/twiml`, HTTP POST |
| Primary handler fails | `https://getdossier.org/demo/api/phone/voice`, HTTP POST |

The fallback is getdossier.org's own scripted phone line, which asks the same questions one at a time. It answers if this server is down. For its signature check, the Worker needs `TWILIO_AUTH_TOKEN` too.

## Running locally

```bash
python3.14 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest
.venv/bin/uvicorn app:app --port 8000
```

For a real call against your laptop, run `ngrok http 8000`, set `PUBLIC_HOST_NAME` to the ngrok host, and point the number's "A call comes in" at `https://<ngrok-host>/twiml`. A free ngrok URL changes each time ngrok restarts.

## What's been tested

The tests use a fake Twilio socket and a fake Deepgram agent. They cover:

- Signatures, checked against Twilio's own test vector.
- Rejecting a stream with a forged token.
- Hanging up only after the goodbye has played, including when Twilio never confirms it.
- A caller hanging up.
- Sending to getdossier.org with retries, and sending the transcript when extraction fails.

The Docker image builds and answers `/twiml` like Twilio expects. A finished call was posted to the live getdossier.org endpoint and logged.

Two things haven't been tested yet, because they need real keys: a real call through Deepgram, and Gemini extraction.
