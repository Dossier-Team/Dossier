# Dossier Prototype

Someone dials a Twilio number → Twilio hits your server → your server registers
the call with ElevenLabs → an ElevenLabs agent picks up and talks.

**This is just to prove calls get answer**

## Prerequisites

- ElevenLabs account
- Twilio account, **upgraded (not trial)** — see gotcha #4 below
- Python 3.10+
- [ngrok](https://ngrok.com) account + CLI installed

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

Fill in `ELEVENLABS_API_KEY` in `.env` — create it in the ElevenLabs dashboard
under Profile → API Keys, and make sure **Conversational AI** access is
enabled with **write** permission (not just read). See gotcha #1.

## Provision the agent

Create an agent in the ELEVEN LABS dashboard and copy the agent id into `.env` as `ELEVENLABS_AGENT_ID`.

## Run it

Three things need to be running at once, in separate terminals:

```bash
python server.py          # 1. your server, port 8000
ngrok http 8000            # 2. public tunnel to it
```

3. Copy ngrok's `https://...ngrok-free.dev` forwarding URL, append
   `/twilio/inbound`, and paste the full thing into **Twilio Console → Phone
   Numbers → Manage → Active Numbers → your number → Voice Configuration →
   "A call comes in"** (Webhook, method POST). See gotcha #2.

Call the number. The agent should pick up.

## Gotchas (check these first)

1. **401 `missing_permissions` / `convai_write`** — your ElevenLabs API key
   was created without Conversational AI write access. Make a new key with
   that permission enabled, swap it into `.env`, restart `server.py`.

2. **404 on the webhook** — the URL in Twilio must include the path:
   `.../twilio/inbound`, not just the bare ngrok domain.

3. **ngrok URL changes every restart** (free tier). If you restart ngrok,
   you must re-paste the new URL into Twilio's Voice Configuration, or
   nothing will reach your server.

4. **Call answers, plays a trial disclaimer, then hangs up** — this is a
   Twilio **trial account** restriction. `<Connect><Stream>` (what bridges
   the call to ElevenLabs) doesn't fully work on trial. Upgrade the Twilio
   account (add a payment method).

5.**`.env` changes require a `server.py` restart** — it's only read once,
   at startup.