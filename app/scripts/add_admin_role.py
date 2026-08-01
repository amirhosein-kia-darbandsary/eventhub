from app.db.session import async_session_factory
from app.models.user import User, UserRole
from sqlalchemy import select
import asyncio

async def assign_role_to_admin():
    async with async_session_factory.begin() as session:
        result = await session.execute(
            select(User).order_by(User.id).limit(1)
        )

        user = result.scalar_one_or_none()

        if user is None:
            print("No users found.")
            return

        user.role = UserRole.admin

        print(f"{user.email} promoted to admin.")
    
    
    
if __name__ == "__main__":
    asyncio.run(assign_role_to_admin())