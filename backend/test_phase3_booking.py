import asyncio
import httpx
import sys
from datetime import datetime, timedelta, date

BASE_URL = "http://127.0.0.1:8001"

# Test Data
CLEANER_EMAIL = "cleaner_p3@example.com"
CLEANER_PASS = "SecurePass123!"
CUSTOMER_EMAIL = "customer_p3@example.com"
CUSTOMER_PASS = "SecurePass123!"


async def register_user(client, email, password, role, name):
    print(f"--- Registering {role}: {email} ---")
    resp = await client.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": name,
            "role": role,
            "phone": "1234567890",
        },
    )

    if resp.status_code == 201:
        print("Registered successfully.")
        return True
    elif resp.status_code == 400 and "already exists" in resp.text:
        print("User already exists.")
        return True
    else:
        print(f"Registration failed: {resp.text}")
        return False


async def login(client, email, password):
    print(f"--- Logging in {email} ---")
    resp = await client.post(
        f"{BASE_URL}/api/auth/login", data={"username": email, "password": password}
    )

    if resp.status_code == 200:
        token = resp.json()["tokens"]["access_token"]
        # Verify email manually for test (since we don't have email service)
        # But wait, login requires verification now?
        # Yes, controller checks email_verified.
        # We need a hack or manual verification.
        print("Login successful.")
        return token
    elif resp.status_code == 403 and "Email not verified" in resp.text:
        print("Email not verified. Attempting to verify...")
        # We need to manually verify via DB or backdoor.
        # For this test, let's assume we can use a helper script or specific endpoint.
        # Actually, let's use the 'verify_email' endpoint if we can get the token.
        # But we can't extract the token easily without logs.
        # Plan B: We'll likely fail here if not verified.
        # Let's use the crud directly in a separate setup step if needed.
        return None
    else:
        print(f"Login failed: {resp.text}")
        return None


async def main():
    # 1. Setup Users (Direct DB manipulation for verification to speed up)
    # We will use a subprocess to verify emails
    import subprocess

    subprocess.run([sys.executable, "manual_verify_p3.py"], capture_output=True)

    async with httpx.AsyncClient() as client:
        # Register if not exists
        await register_user(
            client, CLEANER_EMAIL, CLEANER_PASS, "cleaner", "Phase3 Cleaner"
        )
        await register_user(
            client, CUSTOMER_EMAIL, CUSTOMER_PASS, "customer", "Phase3 Customer"
        )

        # Verify emails (Hack: run verification script)
        subprocess.run([sys.executable, "manual_verify_p3.py"])

        # Login
        cleaner_token = await login(client, CLEANER_EMAIL, CLEANER_PASS)
        customer_token = await login(client, CUSTOMER_EMAIL, CUSTOMER_PASS)

        if not cleaner_token or not customer_token:
            print("Failed to login. Exiting.")
            return

        cleaner_headers = {"Authorization": f"Bearer {cleaner_token}"}
        customer_headers = {"Authorization": f"Bearer {customer_token}"}

        # 2. Cleaner Setup: Profile & Service
        print("\n--- Setting up Cleaner Profile & Service ---")
        # Create Profile
        await client.post(
            f"{BASE_URL}/api/cleaners/profile",
            json={
                "bio": "Expert Cleaner",
                "experience_years": 5,
                "base_hourly_rate": 50,
            },
            headers=cleaner_headers,
        )

        # Create Service
        print("Creating Service...")
        resp = await client.post(
            f"{BASE_URL}/api/services",
            json={
                "name": "Phase 3 Deep Clean",
                "description": "Thorough deep cleaning",
                "category": "deep",
                "price": 100.0,
                "duration_hours": 2.0,
            },
            headers=cleaner_headers,
        )

        if resp.status_code != 201:
            print(f"Failed to create service: {resp.text}")
            return

        service_id = resp.json()["id"]
        cleaner_id = resp.json()["cleaner_id"]
        print(f"Service Created: {service_id}")

        # 3. Customer Booking
        print("\n--- Customer Booking ---")
        tomorrow = date.today() + timedelta(days=1)
        booking_data = {
            "service_id": service_id,
            "cleaner_id": cleaner_id,
            "scheduled_date": tomorrow.isoformat(),
            "start_time": "10:00",
            "address": {
                "street": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "pincode": "123456",
            },
            "special_instructions": "Door code is 1234",
        }

        resp = await client.post(
            f"{BASE_URL}/api/bookings", json=booking_data, headers=customer_headers
        )
        print(f"Booking Request Status: {resp.status_code}")
        if resp.status_code == 201:
            booking = resp.json()
            booking_id = booking["id"]
            print(f"Booking Created! ID: {booking_id}")
            print(f"Total Price: {booking['total_price']}")
        else:
            print(f"Booking Failed: {resp.text}")
            return

        # 4. Check Cleaner Availability (Try to book same slot)
        print("\n--- Testing Double Booking (Should Fail) ---")
        resp = await client.post(
            f"{BASE_URL}/api/bookings", json=booking_data, headers=customer_headers
        )
        print(f"Double Booking Status: {resp.status_code} (Expected 409)")
        if resp.status_code == 409:
            print("PASS: Prevented double booking.")
        else:
            print(f"FAIL: Unexpected status {resp.status_code}")

        # 5. Cleaner Actions
        print("\n--- Cleaner Actions ---")
        # Get Bookings
        resp = await client.get(f"{BASE_URL}/api/bookings", headers=cleaner_headers)
        bookings = resp.json()["bookings"]
        print(f"Cleaner has {len(bookings)} bookings.")

        # Confirm Booking
        print(f"Confirming booking {booking_id}...")
        resp = await client.patch(
            f"{BASE_URL}/api/bookings/{booking_id}/status",
            json={"status": "confirmed"},
            headers=cleaner_headers,
        )
        print(f"Update Status: {resp.status_code}")
        if resp.status_code == 200 and resp.json()["status"] == "confirmed":
            print("PASS: Booking Confirmed.")
        else:
            print(f"FAIL: Could not confirm. {resp.text}")

        print("\n--- Phase 3 Test Complete ---")


if __name__ == "__main__":
    asyncio.run(main())
