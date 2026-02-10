import asyncio
from database.database import connect_to_mongo, close_mongo_connection
from cruds.user_crud import user_crud

EMAILS = ["cleaner_p3@example.com", "customer_p3@example.com"]


async def main():
    await connect_to_mongo()
    for email in EMAILS:
        try:
            user = await user_crud.get_user_by_email(email)
            if user:
                user.email_verified = True
                await user_crud.update_user(str(user.id), email_verified=True)
                print(f"Verified {email}")
            else:
                print(f"User {email} not found")
        except Exception as e:
            print(f"Error verifies {email}: {e}")
    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
