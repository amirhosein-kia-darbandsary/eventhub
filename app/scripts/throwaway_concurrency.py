import asyncio

from sqlalchemy import Column, Integer, MetaData, Table, select, update
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "postgresql+asyncpg://myuser:drsweb12@65.21.24.13:5445/eventhub_test"

metadata = MetaData()
counters = Table(
    "throwaway_counters",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("remaining", Integer),
)


async def setup(engine):
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
        await conn.execute(counters.insert().values(id=1, remaining=10))
        await conn.commit()


async def buy_one_no_lock(engine, worker_id: int):
    async with engine.connect() as conn:
        result = await conn.execute(select(counters.c.remaining).where(counters.c.id == 1))
        remaining = result.scalar_one()

        if remaining <= 0:
            print(f"worker {worker_id}: موجودی تمام شده، رد می‌شه")
            return


        await asyncio.sleep(0.05)

        await conn.execute(
            update(counters).where(counters.c.id == 1).values(remaining=remaining - 1)
        )
        await conn.commit()
        print(f"worker {worker_id}: یک واحد خرید (موجودی قبلش: {remaining})")

async def buy_one_with_lock(engine, worker_id: int):
    
    async with engine.connect() as conn:
        async with conn.begin():
            result = await conn.execute(
                select(counters.c.remaining).where(counters.c.id == 1).with_for_update()
            )
            remaining = result.scalar_one()

            if remaining <= 0:
                print(f"worker {worker_id}: موجودی تمام شده، رد می‌شه")
                return

            await asyncio.sleep(0.05)

            await conn.execute(
                update(counters).where(counters.c.id == 1).values(remaining=remaining - 1)
            )
            print(f"worker {worker_id}: یک واحد خرید (موجودی قبلش: {remaining})")

async def buy_one_optimistic(engine, worker_id: int):
    async with engine.connect() as conn:
        result = await conn.execute(
            select(counters.c.remaining, counters.c.version).where(counters.c.id == 1)
        )
        remaining, seen_version = result.one()

        if remaining <= 0:
            print(f"worker {worker_id}: موجودی تمام شده")
            return

        await asyncio.sleep(0.05)

        
        result = await conn.execute(
            update(counters)
            .where(counters.c.id == 1, counters.c.version == seen_version)
            .values(remaining=remaining - 1, version=seen_version + 1)
        )
        await conn.commit()

        if result.rowcount == 0:
            print(f"worker {worker_id}: یکی دیگه زودتر تغییرش داد -- باید دوباره تلاش کنم")
        else:
            print(f"worker {worker_id}: موفق شد")
                
async def main():
    engine = create_async_engine(DATABASE_URL)
    await setup(engine)

    tasks = [buy_one_with_lock(engine, i) for i in range(20)]
    await asyncio.gather(*tasks)

    async with engine.connect() as conn:
        result = await conn.execute(select(counters.c.remaining).where(counters.c.id == 1))
        final = result.scalar_one()
        print(f"\nموجودی نهایی باید ۰ یا بیشتر باشه. واقعاً شد: {final}")


if __name__ == "__main__":
    asyncio.run(main())
