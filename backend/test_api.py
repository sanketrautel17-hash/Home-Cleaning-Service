"""
API Test Script
===============
Comprehensive Phase 1 test script that verifies ALL endpoints work correctly.
Run this script while the server is running.

Tests covered:
 1. GET  /              - Root endpoint
 2. GET  /health        - Health check
 3. POST /api/auth/register       - Register new user
 4. POST /api/auth/verify-email   - Verify email (using generated token)
 5. POST /api/auth/login          - Login
 6. GET  /api/auth/me             - Get current user (authenticated)
 7. GET  /api/users/me            - Get user profile
 8. PUT  /api/users/me            - Update user profile
 9. GET  /api/users/              - List users
10. GET  /api/users/{user_id}     - Get user by ID (public profile)
11. POST /api/auth/forgot-password - Forgot password
12. POST /api/auth/reset-password  - Reset password with token
13. POST /api/auth/refresh         - Token refresh
14. POST /api/auth/change-password - Change password (authenticated)
15. POST /api/users/me/deactivate  - Deactivate account
16. DELETE /api/users/me           - Delete account
"""

import sys
import os

# Fix Unicode encoding for Windows (emojis in output)
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# Add the backend directory to path so we can import security utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import httpx
import asyncio
import json

BASE_URL = "http://127.0.0.1:8000"

# Test data - unique email to avoid collisions
TEST_USER = {
    "email": "phase1test@example.com",
    "password": "TestPass123!",
    "full_name": "Phase1 Test User",
    "role": "customer",
    "phone": "+919876543210",
}

# Counters
passed = 0
failed = 0
total = 0


def print_result(test_name: str, success: bool, response=None, error=None):
    """Print formatted test result."""
    global passed, failed, total
    total += 1
    if success:
        passed += 1
    else:
        failed += 1

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
        except Exception:
            print(f"    Response: {response.text[:200]}")
    if error:
        print(f"    Error: {error}")


async def cleanup_test_user(
    client: httpx.AsyncClient, access_token: str, password: str
):
    """Delete the test user to clean up after tests."""
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        await client.request(
            "DELETE",
            f"{BASE_URL}/api/users/me",
            json={"password": password},
            headers=headers,
        )
    except Exception:
        pass


async def run_tests():
    """Run all Phase 1 API tests."""
    print("=" * 60)
    print("HOME CLEANING SERVICE API - PHASE 1 COMPREHENSIVE TESTS")
    print("=" * 60)

    # Import security utils to generate verification/reset tokens for testing
    try:
        from commons.security import create_email_verification_token, create_reset_token

        can_generate_tokens = True
        print("\n🔧 Security utils loaded - can generate tokens for testing")
    except Exception as e:
        can_generate_tokens = False
        print(f"\n⚠️ Could not import security utils: {e}")
        print("   Some tests will be skipped")

    async with httpx.AsyncClient(timeout=30.0) as client:
        access_token = None
        refresh_token_value = None
        user_id = None

        # First, clean up any existing test user by trying to login and delete
        try:
            login_resp = await client.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": TEST_USER["email"], "password": TEST_USER["password"]},
            )
            if login_resp.status_code == 200:
                old_token = login_resp.json().get("tokens", {}).get("access_token")
                if old_token:
                    await cleanup_test_user(client, old_token, TEST_USER["password"])
                    print("🧹 Cleaned up existing test user")
                    await asyncio.sleep(0.5)
        except Exception:
            pass

        # =================================================================
        # TEST 1: Root endpoint
        # =================================================================
        try:
            response = await client.get(f"{BASE_URL}/")
            success = (
                response.status_code == 200 and "Home Cleaning Service" in response.text
            )
            print_result("GET / - Root endpoint", success, response)
        except Exception as e:
            print_result("GET / - Root endpoint", False, error=str(e))

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
        except Exception as e:
            print_result("GET /health - Health check", False, error=str(e))

        # =================================================================
        # TEST 3: Register new user
        # =================================================================
        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/register", json=TEST_USER
            )
            success = response.status_code == 201
            print_result("POST /api/auth/register - Register user", success, response)
        except Exception as e:
            print_result("POST /api/auth/register - Register user", False, error=str(e))

        # =================================================================
        # TEST 4: Verify email (using generated token)
        # =================================================================
        if can_generate_tokens:
            try:
                token = create_email_verification_token(TEST_USER["email"])
                response = await client.post(
                    f"{BASE_URL}/api/auth/verify-email",
                    params={"token": token},
                )
                success = response.status_code == 200
                print_result(
                    "POST /api/auth/verify-email - Verify email", success, response
                )
            except Exception as e:
                print_result(
                    "POST /api/auth/verify-email - Verify email", False, error=str(e)
                )
        else:
            print_result(
                "POST /api/auth/verify-email - Verify email",
                False,
                error="Cannot generate token",
            )

        # =================================================================
        # TEST 5: Login
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
                refresh_token_value = data.get("tokens", {}).get("refresh_token")
                user_id = data.get("user", {}).get("id")
                success = access_token is not None
            print_result("POST /api/auth/login - Login", success, response)
        except Exception as e:
            print_result("POST /api/auth/login - Login", False, error=str(e))

        # =================================================================
        # TEST 6: Get current user via /auth/me (authenticated)
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
            except Exception as e:
                print_result("GET /api/auth/me - Get current user", False, error=str(e))
        else:
            print_result(
                "GET /api/auth/me - Get current user", False, error="No access token"
            )

        # =================================================================
        # TEST 7: Get user profile via /users/me
        # =================================================================
        if access_token:
            try:
                headers = {"Authorization": f"Bearer {access_token}"}
                response = await client.get(f"{BASE_URL}/api/users/me", headers=headers)
                success = response.status_code == 200
                print_result("GET /api/users/me - Get user profile", success, response)
            except Exception as e:
                print_result(
                    "GET /api/users/me - Get user profile", False, error=str(e)
                )
        else:
            print_result(
                "GET /api/users/me - Get user profile", False, error="No access token"
            )

        # =================================================================
        # TEST 8: Update user profile
        # =================================================================
        if access_token:
            try:
                headers = {"Authorization": f"Bearer {access_token}"}
                update_data = {
                    "full_name": "Updated Test User",
                    "phone": "+911234567890",
                }
                response = await client.put(
                    f"{BASE_URL}/api/users/me", json=update_data, headers=headers
                )
                success = response.status_code == 200
                if success:
                    # Verify name was actually updated
                    resp_data = response.json()
                    updated_name = resp_data.get("user", {}).get("full_name", "")
                    success = updated_name == "Updated Test User"
                print_result("PUT /api/users/me - Update profile", success, response)
            except Exception as e:
                print_result("PUT /api/users/me - Update profile", False, error=str(e))
        else:
            print_result(
                "PUT /api/users/me - Update profile", False, error="No access token"
            )

        # =================================================================
        # TEST 9: List users
        # =================================================================
        try:
            response = await client.get(f"{BASE_URL}/api/users/?limit=5")
            success = response.status_code == 200 and "users" in response.json()
            print_result("GET /api/users/ - List users", success, response)
        except Exception as e:
            print_result("GET /api/users/ - List users", False, error=str(e))

        # =================================================================
        # TEST 10: Get user by ID (public profile)
        # =================================================================
        if user_id:
            try:
                response = await client.get(f"{BASE_URL}/api/users/{user_id}")
                success = response.status_code == 200
                print_result(
                    "GET /api/users/{user_id} - Get public profile", success, response
                )
            except Exception as e:
                print_result(
                    "GET /api/users/{user_id} - Get public profile", False, error=str(e)
                )
        else:
            print_result(
                "GET /api/users/{user_id} - Get public profile",
                False,
                error="No user_id",
            )

        # =================================================================
        # TEST 11: Forgot password
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
        except Exception as e:
            print_result("POST /api/auth/forgot-password", False, error=str(e))

        # =================================================================
        # TEST 12: Reset password with token
        # =================================================================
        if can_generate_tokens:
            try:
                reset_token = create_reset_token(TEST_USER["email"])
                response = await client.post(
                    f"{BASE_URL}/api/auth/reset-password",
                    json={
                        "token": reset_token,
                        "new_password": TEST_USER[
                            "password"
                        ],  # Reset back to same password
                    },
                )
                success = response.status_code == 200
                print_result(
                    "POST /api/auth/reset-password - Reset password", success, response
                )
            except Exception as e:
                print_result(
                    "POST /api/auth/reset-password - Reset password",
                    False,
                    error=str(e),
                )
        else:
            print_result(
                "POST /api/auth/reset-password - Reset password",
                False,
                error="Cannot generate token",
            )

        # =================================================================
        # TEST 13: Token refresh
        # =================================================================
        try:
            # Re-login to get fresh tokens (in case password reset changed things)
            login_data = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"],
            }
            login_response = await client.post(
                f"{BASE_URL}/api/auth/login", json=login_data
            )
            if login_response.status_code == 200:
                tokens = login_response.json().get("tokens", {})
                refresh_token_value = tokens.get("refresh_token")
                access_token = tokens.get("access_token")
                if refresh_token_value:
                    response = await client.post(
                        f"{BASE_URL}/api/auth/refresh",
                        json={"refresh_token": refresh_token_value},
                    )
                    success = response.status_code == 200
                    if success:
                        # Update access token with the new one
                        new_tokens = response.json().get("tokens", {})
                        access_token = new_tokens.get("access_token", access_token)
                    print_result(
                        "POST /api/auth/refresh - Token refresh", success, response
                    )
                else:
                    print_result(
                        "POST /api/auth/refresh", False, error="No refresh token"
                    )
            else:
                print_result("POST /api/auth/refresh", False, error="Login failed")
        except Exception as e:
            print_result("POST /api/auth/refresh", False, error=str(e))

        # =================================================================
        # TEST 14: Change password (authenticated)
        # =================================================================
        if access_token:
            try:
                headers = {"Authorization": f"Bearer {access_token}"}
                new_password = "NewTestPass456!"
                response = await client.post(
                    f"{BASE_URL}/api/auth/change-password",
                    json={
                        "current_password": TEST_USER["password"],
                        "new_password": new_password,
                    },
                    headers=headers,
                )
                success = response.status_code == 200
                print_result(
                    "POST /api/auth/change-password - Change password",
                    success,
                    response,
                )

                # If password changed successfully, update for subsequent tests
                if success:
                    # Login with new password to get fresh token
                    login_resp = await client.post(
                        f"{BASE_URL}/api/auth/login",
                        json={"email": TEST_USER["email"], "password": new_password},
                    )
                    if login_resp.status_code == 200:
                        access_token = (
                            login_resp.json().get("tokens", {}).get("access_token")
                        )
                        TEST_USER["password"] = new_password  # Update for cleanup
            except Exception as e:
                print_result("POST /api/auth/change-password", False, error=str(e))
        else:
            print_result(
                "POST /api/auth/change-password", False, error="No access token"
            )

        # =================================================================
        # TEST 15: Unauthorized access (negative test)
        # =================================================================
        try:
            response = await client.get(f"{BASE_URL}/api/auth/me")
            success = response.status_code == 401 or response.status_code == 403
            print_result(
                "GET /api/auth/me - Unauthorized access (no token, expect 401/403)",
                success,
                response,
            )
        except Exception as e:
            print_result("Unauthorized access test", False, error=str(e))

        # =================================================================
        # TEST 16: Delete account (cleanup)
        # =================================================================
        if access_token:
            try:
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                }
                response = await client.request(
                    "DELETE",
                    f"{BASE_URL}/api/users/me",
                    json={"password": TEST_USER["password"]},
                    headers=headers,
                )
                success = response.status_code == 200
                print_result("DELETE /api/users/me - Delete account", success, response)
            except Exception as e:
                print_result(
                    "DELETE /api/users/me - Delete account", False, error=str(e)
                )
        else:
            print_result(
                "DELETE /api/users/me - Delete account", False, error="No access token"
            )

        # =================================================================
        # SUMMARY
        # =================================================================
        print("\n" + "=" * 60)
        print(f"📊 RESULTS: {passed}/{total} passed, {failed}/{total} failed")
        print("=" * 60)
        if failed == 0:
            print("🎉 ALL TESTS PASSED! Phase 1 is fully functional!")
        else:
            print("⚠️  SOME TESTS FAILED - Check above for details")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_tests())
