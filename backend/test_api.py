"""
API Test Script
===============
Tests all Phase 1 endpoints to verify they work correctly.
Run this script while the server is running.
"""

import httpx
import asyncio
import json


BASE_URL = "http://127.0.0.1:8000"

# Test data
TEST_USER = {
    "email": "testuser@example.com",
    "password": "TestPass123!",
    "full_name": "Test User",
    "role": "customer",
    "phone": "+919876543210",
}


def print_result(test_name: str, success: bool, response=None, error=None):
    """Print formatted test result."""
    status = "✅ PASS" if success else "❌ FAIL"
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


async def run_tests():
    """Run all API tests."""
    print("=" * 60)
    print("HOME CLEANING SERVICE API - PHASE 1 TESTS")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=30.0) as client:
        all_passed = True
        access_token = None

        # =================================================================
        # TEST 1: Root endpoint
        # =================================================================
        try:
            response = await client.get(f"{BASE_URL}/")
            success = (
                response.status_code == 200 and "Home Cleaning Service" in response.text
            )
            print_result("GET / - Root endpoint", success, response)
            all_passed = all_passed and success
        except Exception as e:
            print_result("GET / - Root endpoint", False, error=str(e))
            all_passed = False

        # =================================================================
        # TEST 2: Health check
        # =================================================================
        try:
            response = await client.get(f"{BASE_URL}/health")
            success = (
                response.status_code == 200
                and response.json().get("status") == "healthy"
            )
            print_result("GET /health - Health check", success, response)
            all_passed = all_passed and success
        except Exception as e:
            print_result("GET /health - Health check", False, error=str(e))
            all_passed = False

        # =================================================================
        # TEST 3: Register new user
        # =================================================================
        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/register", json=TEST_USER
            )
            # Could be 201 (created) or 400 (already exists)
            success = response.status_code in [201, 400]
            print_result("POST /api/auth/register - Register user", success, response)
            all_passed = all_passed and success
        except Exception as e:
            print_result("POST /api/auth/register - Register user", False, error=str(e))
            all_passed = False

        # =================================================================
        # TEST 4: Login
        # =================================================================
        try:
            login_data = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"],
            }
            response = await client.post(f"{BASE_URL}/api/auth/login", json=login_data)
            success = response.status_code == 200
            if success:
                data = response.json()
                access_token = data.get("tokens", {}).get("access_token")
                success = access_token is not None
            print_result("POST /api/auth/login - Login", success, response)
            all_passed = all_passed and success
        except Exception as e:
            print_result("POST /api/auth/login - Login", False, error=str(e))
            all_passed = False

        # =================================================================
        # TEST 5: Get current user (auth required)
        # =================================================================
        if access_token:
            try:
                headers = {"Authorization": f"Bearer {access_token}"}
                response = await client.get(f"{BASE_URL}/api/auth/me", headers=headers)
                success = response.status_code == 200
                print_result(
                    "GET /api/auth/me - Get current user (authenticated)",
                    success,
                    response,
                )
                all_passed = all_passed and success
            except Exception as e:
                print_result("GET /api/auth/me - Get current user", False, error=str(e))
                all_passed = False
        else:
            print_result(
                "GET /api/auth/me - Get current user", False, error="No access token"
            )
            all_passed = False

        # =================================================================
        # TEST 6: Get user profile via /users/me
        # =================================================================
        if access_token:
            try:
                headers = {"Authorization": f"Bearer {access_token}"}
                response = await client.get(f"{BASE_URL}/api/users/me", headers=headers)
                success = response.status_code == 200
                print_result("GET /api/users/me - Get user profile", success, response)
                all_passed = all_passed and success
            except Exception as e:
                print_result(
                    "GET /api/users/me - Get user profile", False, error=str(e)
                )
                all_passed = False

        # =================================================================
        # TEST 7: Update user profile
        # =================================================================
        if access_token:
            try:
                headers = {"Authorization": f"Bearer {access_token}"}
                update_data = {"full_name": "Updated Test User"}
                response = await client.put(
                    f"{BASE_URL}/api/users/me", json=update_data, headers=headers
                )
                success = response.status_code == 200
                print_result("PUT /api/users/me - Update profile", success, response)
                all_passed = all_passed and success
            except Exception as e:
                print_result("PUT /api/users/me - Update profile", False, error=str(e))
                all_passed = False

        # =================================================================
        # TEST 8: List users
        # =================================================================
        try:
            response = await client.get(f"{BASE_URL}/api/users/?limit=5")
            success = response.status_code == 200 and "users" in response.json()
            print_result("GET /api/users/ - List users", success, response)
            all_passed = all_passed and success
        except Exception as e:
            print_result("GET /api/users/ - List users", False, error=str(e))
            all_passed = False

        # =================================================================
        # TEST 9: Forgot password
        # =================================================================
        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/forgot-password",
                json={"email": TEST_USER["email"]},
            )
            success = response.status_code == 200
            print_result(
                "POST /api/auth/forgot-password - Forgot password", success, response
            )
            all_passed = all_passed and success
        except Exception as e:
            print_result("POST /api/auth/forgot-password", False, error=str(e))
            all_passed = False

        # =================================================================
        # TEST 10: Token refresh
        # =================================================================
        try:
            # First login to get refresh token
            login_data = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"],
            }
            login_response = await client.post(
                f"{BASE_URL}/api/auth/login", json=login_data
            )
            if login_response.status_code == 200:
                refresh_token = (
                    login_response.json().get("tokens", {}).get("refresh_token")
                )
                if refresh_token:
                    response = await client.post(
                        f"{BASE_URL}/api/auth/refresh",
                        json={"refresh_token": refresh_token},
                    )
                    success = response.status_code == 200
                    print_result(
                        "POST /api/auth/refresh - Token refresh", success, response
                    )
                    all_passed = all_passed and success
                else:
                    print_result(
                        "POST /api/auth/refresh", False, error="No refresh token"
                    )
            else:
                print_result("POST /api/auth/refresh", False, error="Login failed")
        except Exception as e:
            print_result("POST /api/auth/refresh", False, error=str(e))
            all_passed = False

        # =================================================================
        # SUMMARY
        # =================================================================
        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 ALL TESTS PASSED!")
        else:
            print("⚠️  SOME TESTS FAILED - Check above for details")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_tests())
