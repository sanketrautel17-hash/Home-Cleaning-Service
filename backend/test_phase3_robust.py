import asyncio
import httpx
import uuid
from datetime import datetime, timedelta, date
from dotenv import load_dotenv

load_dotenv()

import logging

# Configure logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.FileHandler("test_results.log", mode="w", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


def log(msg):
    logging.info(msg)


# Replace print with log
print = log

from database.database import connect_to_mongo, close_mongo_connection
from cruds.user_crud import user_crud

BASE_URL = "http://127.0.0.1:8001"
RUN_ID = str(uuid.uuid4())[:8]

CLEANER_EMAIL = f"cleaner_{RUN_ID}@test.com"
CUSTOMER_EMAIL = f"customer_{RUN_ID}@test.com"
PASSWORD = "SecurePass123!"


async def verify_user_in_db(email):
    user = await user_crud.get_user_by_email(email)
    if user:
        user.email_verified = True
        await user_crud.update_user(str(user.id), email_verified=True)
        print(f"Verified {email} in DB.")
        return True
    print(f"User {email} not found in DB.")
    return False


async def main():
    # Connect to DB for manual verification
    await connect_to_mongo()

    # Increase timeout to 60s for slow registration
    async with httpx.AsyncClient(timeout=60.0) as client:
        print(f"--- Starting Test Run {RUN_ID} ---")

        # 1. Register Users
        print(f"Registering Cleaner: {CLEANER_EMAIL}")
        resp = await client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": CLEANER_EMAIL,
                "password": PASSWORD,
                "full_name": "Test Cleaner",
                "role": "cleaner",
            },
        )
        print(f"Cleaner Reg: {resp.status_code}")

        print(f"Registering Customer: {CUSTOMER_EMAIL}")
        resp = await client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": CUSTOMER_EMAIL,
                "password": PASSWORD,
                "full_name": "Test Customer",
                "role": "customer",
            },
        )
        print(f"Customer Reg: {resp.status_code}")

        # 2. Verify Emails (Direct DB)
        await verify_user_in_db(CLEANER_EMAIL)
        await verify_user_in_db(CUSTOMER_EMAIL)

        # 3. Login
        print("Logging in Cleaner...")
        resp = await client.post(
            f"{BASE_URL}/api/auth/login",
            data={"username": CLEANER_EMAIL, "password": PASSWORD},
        )
        if resp.status_code != 200:
            print(f"Cleaner Login Failed: {resp.text}")
            return
        cleaner_token = resp.json()["tokens"]["access_token"]
        cleaner_headers = {"Authorization": f"Bearer {cleaner_token}"}

        print("Logging in Customer...")
        resp = await client.post(
            f"{BASE_URL}/api/auth/login",
            data={"username": CUSTOMER_EMAIL, "password": PASSWORD},
        )
        if resp.status_code != 200:
            print(f"Customer Login Failed: {resp.text}")
            return
        customer_token = resp.json()["tokens"]["access_token"]
        customer_headers = {"Authorization": f"Bearer {customer_token}"}

        # 4. Create Profile
        print("Creating Cleaner Profile...")
        resp = await client.post(
            f"{BASE_URL}/api/cleaners/profile",
            json={
                "bio": "Test Bio",
                "experience_years": 5,
                "base_hourly_rate": 50,
                "city": "Test City",
            },
            headers=cleaner_headers,
        )
        print(f"Profile Status: {resp.status_code}")
        if resp.status_code not in [200, 201]:
            print(f"Profile Error: {resp.text}")

        # 5. Create Service
        print("Creating Service...")
        resp = await client.post(
            f"{BASE_URL}/api/services/",
            json={
                "name": "Test Service",
                "description": "Test Description",
                "category": "deep",
                "price": 100.0,
                "duration_hours": 2.0,
            },
            headers=cleaner_headers,
        )

        if resp.status_code != 201:
            print(f"Service Creation Failed: {resp.text}")
            return

        service_data = resp.json()
        if "service" in service_data:
            service_id = service_data["service"]["id"]
            cleaner_id = service_data["service"]["cleaner_id"]
        else:
            # Depending on response wrapper
            service_id = service_data["id"]
            cleaner_id = service_data[
                "cleaner_id"
            ]  # clean_router example shows flat response in example but wrapped in "service"?
            # Let's check response text in case
            print(f"Service Created: {service_data}")

        # 6. Customer Booking
        print("Booking Service...")
        tomorrow = date.today() + timedelta(days=1)
        booking_payload = {
            "service_id": service_id,
            "cleaner_id": cleaner_id,
            "scheduled_date": tomorrow.isoformat(),
            "start_time": "14:00",
            "address": {
                "street": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "pincode": "123456",
            },
            "special_instructions": "Code 1234",
        }

        resp = await client.post(
            f"{BASE_URL}/api/bookings", json=booking_payload, headers=customer_headers
        )
        print(f"Booking Status: {resp.status_code}")
        if resp.status_code == 201:
            booking = resp.json()
            booking_id = booking["id"]
            print(f"Booking Success: {booking_id}")
        else:
            print(f"Booking Failed: {resp.text}")
            return

        # 7. Check Availability (Double Booking)
        print("Testing Double Booking...")
        resp = await client.post(
            f"{BASE_URL}/api/bookings", json=booking_payload, headers=customer_headers
        )
        if resp.status_code == 409:
            print("Double Booking Prevented (PASS)")
        else:
            print(f"Double Booking Check Failed: {resp.status_code} - {resp.text}")

        # 8. Cleaner Confirms
        print("Confirming Booking...")
        resp = await client.patch(
            f"{BASE_URL}/api/bookings/{booking_id}/status",
            json={"status": "confirmed"},
            headers=cleaner_headers,
        )
        if resp.status_code == 200:
            print("Booking Confirmed (PASS)")
        else:
            print(f"Confirm Failed: {resp.text}")

    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
