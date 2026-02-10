"""
Phase 2 Test Script (V7)
========================
Comprehensive test script for Cleaner Profiles and Service Packages.
Verify all Phase 2 endpoints work correctly.

Run this script while the server is running on port 8001.

Uses: rautramashwini02@gmail.com for cleaner
"""

import sys
import os
import asyncio
import httpx
import json
import subprocess
import urllib.parse
import time

# Fix Unicode encoding for Windows
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8001"

# Use timestamp for customer uniquely
ts = int(time.time())

# User provided cleaner email
CLEANER_USER = {
    "email": "rautramashwini02@gmail.com",
    "password": "CleanerPass123!",
    "full_name": "Ashwini Cleaner",
    "role": "cleaner",
    "phone": "+919876543211",
}

CUSTOMER_USER = {
    "email": f"customer_p2_{ts}@example.com",
    "password": "CustomerPass123!",
    "full_name": "Phase2 Customer",
    "role": "customer",
    "phone": "+919876543212",
}

cleaner_token = ""
customer_token = ""
cleaner_id = ""  # User ID, not profile ID


# Formatting
passed = 0
failed = 0
total = 0


def print_result(test_name: str, success: bool, response=None, error=None):
    global passed, failed, total
    total += 1
    if success:
        passed += 1
        status = "✅ PASS"
    else:
        failed += 1
        status = "❌ FAIL"

    print(f"\n{status} - {test_name}")
    if response:
        print(f"    Status: {response.status_code}")
        try:
            data = response.json()
            if len(str(data)) < 200:
                print(f"    Response: {data}")
            else:
                print(f"    Response: (truncated) {str(data)[:200]}...")
        except:
            print(f"    Response: {response.text[:200]}")
    if error:
        print(f"    Error: {error}")


def verify_email_manually(email: str):
    """Run verification script."""
    print(f"Manually verifying {email}...")
    try:
        subprocess.run(
            [sys.executable, "scripts/verify_user.py", email],
            check=True,
            capture_output=True,
            text=True,
        )
        print("Verification script executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Verification script failed: {e.stdout} {e.stderr}")


async def setup_users(client: httpx.AsyncClient):
    """Create test users and get tokens."""
    global cleaner_token, customer_token, cleaner_id

    # -------------------------------------------------------------------------
    # CLEANER SETUP
    # -------------------------------------------------------------------------
    print(f"\n--- Setup: Creating Cleaner ({CLEANER_USER['email']}) ---")
    resp = await client.post(f"{BASE_URL}/api/auth/register", json=CLEANER_USER)
    if resp.status_code == 201:
        print("Cleaner registered.")
        verify_email_manually(CLEANER_USER["email"])
    elif resp.status_code == 400 and "exists" in resp.text:
        print("Cleaner already exists.")
        verify_email_manually(CLEANER_USER["email"])
    else:
        print(f"Failed to register cleaner: {resp.status_code} {resp.text}")
        return False

    # Login Cleaner
    print("Logging in Cleaner...")
    payload = f"username={urllib.parse.quote(CLEANER_USER['email'])}&password={urllib.parse.quote(CLEANER_USER['password'])}"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        resp = await client.post(
            f"{BASE_URL}/api/auth/login", content=payload, headers=headers
        )
        if resp.status_code == 200:
            data = resp.json()
            if "tokens" in data:
                cleaner_token = data["tokens"]["access_token"]
            else:
                cleaner_token = data["access_token"]

            if "user" in data:
                cleaner_id = data["user"]["id"]
            else:
                pass

            print(f"Cleaner logged in.")

            # Fetch /me to get ID if needed
            if not cleaner_id:
                me_resp = await client.get(
                    f"{BASE_URL}/api/users/me",
                    headers={"Authorization": f"Bearer {cleaner_token}"},
                )
                if me_resp.status_code == 200:
                    cleaner_id = me_resp.json()["user"]["id"]
                    print(f"Cleaner ID fetched: {cleaner_id}")
                else:
                    print("Failed to fetch cleaner ID")
                    return False
        else:
            print(f"Cleaner login failed: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        print(f"Login exception: {e}")
        return False

    # -------------------------------------------------------------------------
    # CUSTOMER SETUP
    # -------------------------------------------------------------------------
    print("\n--- Setup: Creating Customer ---")
    resp = await client.post(f"{BASE_URL}/api/auth/register", json=CUSTOMER_USER)
    if resp.status_code == 201:
        print("Customer registered.")
        verify_email_manually(CUSTOMER_USER["email"])
    elif resp.status_code == 400 and "exists" in resp.text:
        print("Customer already exists.")
        verify_email_manually(CUSTOMER_USER["email"])
    else:
        print(f"Failed to register customer: {resp.status_code} {resp.text}")
        return False

    # Login Customer
    print("Logging in Customer...")
    payload = f"username={urllib.parse.quote(CUSTOMER_USER['email'])}&password={urllib.parse.quote(CUSTOMER_USER['password'])}"

    resp = await client.post(
        f"{BASE_URL}/api/auth/login", content=payload, headers=headers
    )
    if resp.status_code == 200:
        data = resp.json()
        if "tokens" in data:
            customer_token = data["tokens"]["access_token"]
        else:
            customer_token = data["access_token"]
        print("Customer logged in.")
    else:
        print(f"Customer login failed: {resp.status_code} {resp.text}")
        return False

    return True


async def test_cleaner_profile(client: httpx.AsyncClient):
    """Test cleaner profile endpoints."""
    print("\n=== Testing Cleaner Profiles ===")

    headers = {"Authorization": f"Bearer {cleaner_token}"}
    cust_headers = {"Authorization": f"Bearer {customer_token}"}

    # 1. Create Profile (Cleaner)
    profile_data = {
        "bio": "Expert home cleaner",
        "experience_years": 3,
        "specializations": ["regular", "deep"],
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400001",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "service_radius_km": 15.0,
    }
    resp = await client.post(
        f"{BASE_URL}/api/cleaners/profile", json=profile_data, headers=headers
    )

    if resp.status_code == 409:
        print("Profile already exists (expected prior run).")
        # Check if profile is active/valid
        resp = await client.get(f"{BASE_URL}/api/cleaners/profile/me", headers=headers)
        print_result("Get Existing Profile", resp.status_code == 200, resp)
    else:
        print_result("Create Cleaner Profile", resp.status_code == 201, resp)

    # 2. Create Profile (Customer) - Should Fail
    resp = await client.post(
        f"{BASE_URL}/api/cleaners/profile", json=profile_data, headers=cust_headers
    )
    print_result("Customer Create Profile (Fail)", resp.status_code == 403, resp)

    # 3. Get Own Profile
    resp = await client.get(f"{BASE_URL}/api/cleaners/profile/me", headers=headers)
    print_result("Get Own Profile", resp.status_code == 200, resp)
    if resp.status_code == 200:
        city = resp.json()["profile"]["city"]
        if city != "Mumbai":
            print(f"    Warning: City is {city}, expected Mumbai")

    # 4. Update Profile
    update_data = {
        "bio": "Updated Bio",
        "is_available": True,
    }  # Keep available for search
    resp = await client.put(
        f"{BASE_URL}/api/cleaners/profile/me", json=update_data, headers=headers
    )
    print_result("Update Profile", resp.status_code == 200, resp)
    if resp.status_code == 200:
        bio = resp.json()["profile"]["bio"]
        if bio != "Updated Bio":
            print(f"    Warning: Bio is {bio}, expected Updated Bio")

    # 5. Get Public Profile (No Auth)
    resp = await client.get(f"{BASE_URL}/api/cleaners/{cleaner_id}")
    print_result("Get Public Profile", resp.status_code == 200, resp)

    # 6. Search Cleaners
    # Wait a bit for indexing? usually near instant
    resp = await client.get(f"{BASE_URL}/api/cleaners/search?city=Mumbai")
    print_result("Search Cleaners (City)", resp.status_code == 200, resp)
    if resp.status_code == 200:
        cleaners = resp.json()["cleaners"]
        print(f"    Found {len(cleaners)} cleaners in search")

    # 7. Nearby Search
    # 10km radius from 19.0760, 72.8777
    resp = await client.get(
        f"{BASE_URL}/api/cleaners/nearby?latitude=19.0760&longitude=72.8777&radius_km=10"
    )
    print_result("Nearby Search", resp.status_code == 200, resp)
    if resp.status_code == 200:
        cleaners = resp.json()["cleaners"]
        print(f"    Found {len(cleaners)} nearby cleaners")


async def test_services(client: httpx.AsyncClient):
    """Test service package endpoints."""
    print("\n=== Testing Services ===")

    headers = {"Authorization": f"Bearer {cleaner_token}"}
    cust_headers = {"Authorization": f"Bearer {customer_token}"}
    service_id = ""

    # 1. Create Service
    service_data = {
        "name": "Standard Cleaning V7",
        "description": "Basic home cleaning",
        "price": 500.0,
        "category": "regular",
        "price_type": "flat",
        "duration_hours": 2.0,
    }
    resp = await client.post(
        f"{BASE_URL}/api/services/", json=service_data, headers=headers
    )
    print_result("Create Service", resp.status_code == 201, resp)
    if resp.status_code == 201:
        service_id = resp.json()["service"]["id"]
    else:
        print("    Skipping subsequent tests because service creation failed")
        return

    # 2. Create Service (Customer) - Should Fail
    resp = await client.post(
        f"{BASE_URL}/api/services/", json=service_data, headers=cust_headers
    )
    print_result("Customer Create Service (Fail)", resp.status_code == 403, resp)

    # 3. Get My Services
    resp = await client.get(f"{BASE_URL}/api/services/me", headers=headers)
    print_result("Get My Services", resp.status_code == 200, resp)

    # 4. Update Service
    if service_id:
        update_data = {"price": 600.0}
        resp = await client.put(
            f"{BASE_URL}/api/services/{service_id}", json=update_data, headers=headers
        )
        print_result("Update Service", resp.status_code == 200, resp)

    # 5. Search Services
    resp = await client.get(f"{BASE_URL}/api/services/search?category=regular")
    search_res = resp.json()
    print_result("Search Services", resp.status_code == 200, resp)
    if resp.status_code == 200:
        services = search_res["services"]
        print(f"    Found {len(services)} services")

    # 6. Get Cleaner's Services (Public)
    resp = await client.get(f"{BASE_URL}/api/services/cleaner/{cleaner_id}")
    print_result("Get Cleaner's Services", resp.status_code == 200, resp)

    # 7. Delete Service
    if service_id:
        # Customer Try Delete (Fail)
        resp = await client.delete(
            f"{BASE_URL}/api/services/{service_id}", headers=cust_headers
        )
        print_result("Customer Delete Service (Fail)", resp.status_code == 403, resp)

        # Cleaner Delete (Success)
        resp = await client.delete(
            f"{BASE_URL}/api/services/{service_id}", headers=headers
        )
        print_result("Delete Service", resp.status_code == 200, resp)


async def main():
    print(f"Connecting to {BASE_URL}...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(f"{BASE_URL}/health")
            if resp.status_code != 200:
                print(f"Health check failed: {resp.status_code}")
                return
            print("Server is healthy.")
        except Exception as e:
            print(f"Server not reachable at {BASE_URL}: {e}")
            return

        if await setup_users(client):
            await test_cleaner_profile(client)
            await test_services(client)

    print(f"\nTotal: {total}, Passed: {passed}, Failed: {failed}")


if __name__ == "__main__":
    asyncio.run(main())
