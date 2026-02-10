import asyncio
import httpx
import sys

BASE_URL = "http://127.0.0.1:8001"


async def test_login():
    async with httpx.AsyncClient() as client:
        # data = {"username": "cleaner_phase2_v4@example.com", "password": "CleanerPass123!"}
        # Explicitly encode just in case, but dict is better

        # Test 1: Standard Dict
        print("Test 1: Standard Dict")
        resp = await client.post(
            f"{BASE_URL}/api/auth/login",
            data={
                "username": "cleaner_phase2_v4@example.com",
                "password": "CleanerPass123!",
            },
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")

        # Test 2: Adding grant_type
        print("\nTest 2: Adding grant_type")
        resp = await client.post(
            f"{BASE_URL}/api/auth/login",
            data={
                "username": "cleaner_phase2_v4@example.com",
                "password": "CleanerPass123!",
                "grant_type": "password",
            },
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")

        # Test 3: Raw string
        print("\nTest 3: Raw string")
        resp = await client.post(
            f"{BASE_URL}/api/auth/login",
            content="username=cleaner_phase2_v4%40example.com&password=CleanerPass123%21",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")


if __name__ == "__main__":
    asyncio.run(test_login())
