"""
Script untuk update credentials di Langflow flow via API.
Jalankan SETELAH Langflow sudah hidup di port 7860.

Usage:
    python scripts/update_langflow_credentials.py
"""
import asyncio
import json
import os
import sys
import httpx
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

LANGFLOW_BASE = "http://127.0.0.1:7860"
FLOW_ID = "741990f6-cf6e-4039-bcb6-1bf774dd91d7"
API_KEY = "***REMOVED***"

ASTRA_TOKEN = "***REMOVED***"
ASTRA_ENDPOINT = "https://7977b6ab-38ac-4425-8825-0e014bddf4ff-us-east-2.apps.astra.datastax.com"
GOOGLE_API_KEY = "***REMOVED***"


async def update_flow_credentials():
    headers = {"x-api-key": API_KEY}

    async with httpx.AsyncClient(timeout=30.0, base_url=LANGFLOW_BASE) as client:
        # 1. Cek apakah Langflow hidup
        print("Checking Langflow health...")
        try:
            r = await client.get("/api/v1/version")
            print(f"Langflow version: {r.json()}")
        except Exception as e:
            print(f"ERROR: Langflow tidak bisa diakses: {e}")
            print("Pastikan Langflow sudah running di port 7860!")
            return False

        # 2. Ambil flow
        print(f"\nFetching flow {FLOW_ID}...")
        try:
            r = await client.get(f"/api/v1/flows/{FLOW_ID}", headers=headers)
        except Exception as e:
            # Coba tanpa API key (auto-login mode)
            r = await client.get(f"/api/v1/flows/{FLOW_ID}")

        if r.status_code == 401:
            print("401 Unauthorized - mencoba login...")
            login_r = await client.post(
                "/api/v1/login",
                data={"username": "langflow", "password": "admin"},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            if login_r.status_code == 200:
                token = login_r.json().get("access_token")
                headers["Authorization"] = f"Bearer {token}"
                r = await client.get(f"/api/v1/flows/{FLOW_ID}", headers=headers)
            else:
                print(f"Login gagal: {login_r.status_code} {login_r.text[:200]}")
                return False

        if r.status_code != 200:
            print(f"ERROR fetching flow: {r.status_code} {r.text[:200]}")
            return False

        flow = r.json()
        print(f"Flow found: {flow.get('name')}")

        # 3. Update credentials di nodes
        data = flow.get("data", {})
        updated = 0
        for node in data.get("nodes", []):
            template = node.get("data", {}).get("node", {}).get("template", {})

            # Update Astra DB token
            if "token" in template:
                template["token"]["value"] = ASTRA_TOKEN
                template["token"]["load_from_db"] = False
                updated += 1
                print(f"  ✓ Updated Astra token in: {node['data'].get('id', '?')}")

            # Update Astra DB endpoint
            if "api_endpoint" in template:
                template["api_endpoint"]["value"] = ASTRA_ENDPOINT
                updated += 1
                print(f"  ✓ Updated api_endpoint in: {node['data'].get('id', '?')}")

            # Update Google API key di Agent node
            if "api_key" in template and node.get("data", {}).get("type") == "Agent":
                template["api_key"]["value"] = GOOGLE_API_KEY
                template["api_key"]["load_from_db"] = False
                updated += 1
                print(f"  ✓ Updated Google API key in: {node['data'].get('id', '?')}")

        print(f"\nTotal updates: {updated}")

        # 4. Save flow
        print("Saving flow...")
        save_r = await client.patch(
            f"/api/v1/flows/{FLOW_ID}",
            json={"data": data},
            headers=headers
        )
        if save_r.status_code in (200, 201):
            print("✓ Flow saved successfully!")
        else:
            print(f"WARNING: Save returned {save_r.status_code}: {save_r.text[:200]}")

        # 5. Test run
        print("\nTesting flow with simple message...")
        test_r = await client.post(
            f"/api/v1/run/{FLOW_ID}",
            json={
                "output_type": "chat",
                "input_type": "chat",
                "input_value": "halo, tes koneksi",
                "session_id": "test-credentials-update"
            },
            headers=headers,
            timeout=120.0
        )
        if test_r.status_code == 200:
            result = test_r.json()
            try:
                text = result["outputs"][0]["outputs"][0]["results"]["message"]["text"]
                print(f"✓ Flow test BERHASIL! Response: {text[:150]}")
                return True
            except (KeyError, IndexError):
                print(f"Flow responded but couldn't parse: {str(result)[:200]}")
                return True
        else:
            print(f"Flow test gagal: {test_r.status_code} {test_r.text[:300]}")
            return False


if __name__ == "__main__":
    success = asyncio.run(update_flow_credentials())
    sys.exit(0 if success else 1)
