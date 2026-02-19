import asyncio
import os
import random
import io

import asyncpg
from faker import Faker

IDENTITY_DB_URL = os.environ["IDENTITY_DB_URL"]
CATALOG_DB_URL = os.environ["CATALOG_DB_URL"]

USER_COUNT = 50_000
PRODUCT_COUNT = 100_000
BATCH_SIZE = 5_000

fake = Faker()
# Pre-hash a single password for all seed users (bcrypt is slow, we don't need unique hashes for testing)
SEED_PASSWORD_HASH = "$2b$12$LJ3m4ys3Lk0TSwHCbmQ0oOzHPCFDMBSVOGwpMkgiMfOFMkyNrtfjO"


async def seed_users(pool: asyncpg.Pool) -> list[str]:
    print(f"Seeding {USER_COUNT} users...")
    user_ids = []

    for batch_start in range(0, USER_COUNT, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, USER_COUNT)
        records = []
        for i in range(batch_start, batch_end):
            records.append((
                f"user{i}@example.com",
                SEED_PASSWORD_HASH,
                fake.name(),
            ))

        buf = io.BytesIO()
        for email, pwd_hash, name in records:
            line = f"{email}\t{pwd_hash}\t{name}\n"
            buf.write(line.encode())
        buf.seek(0)

        async with pool.acquire() as conn:
            await conn.copy_to_table(
                "users",
                source=buf,
                columns=["email", "password_hash", "name"],
                format="text",
            )

        print(f"  Users: {batch_end}/{USER_COUNT}")

    rows = await pool.fetch("SELECT id FROM users")
    user_ids = [str(row["id"]) for row in rows]
    print(f"Seeded {len(user_ids)} users")
    return user_ids


async def seed_products(pool: asyncpg.Pool, user_ids: list[str]) -> None:
    print(f"Seeding {PRODUCT_COUNT} products...")

    categories = [
        "Electronics", "Clothing", "Home & Garden", "Sports", "Books",
        "Toys", "Beauty", "Automotive", "Food", "Health",
    ]
    adjectives = [
        "Premium", "Vintage", "Modern", "Classic", "Professional",
        "Compact", "Wireless", "Organic", "Handmade", "Limited Edition",
    ]

    for batch_start in range(0, PRODUCT_COUNT, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, PRODUCT_COUNT)
        buf = io.BytesIO()

        for _ in range(batch_start, batch_end):
            seller_id = random.choice(user_ids)
            adj = random.choice(adjectives)
            cat = random.choice(categories)
            title = f"{adj} {fake.word().title()} {cat} {fake.word().title()}"
            description = fake.paragraph(nb_sentences=3)
            price = round(random.uniform(1.0, 9999.99), 2)
            stock = random.randint(0, 1000)
            line = f"{seller_id}\t{title}\t{description}\t{price}\t{stock}\n"
            buf.write(line.encode())

        buf.seek(0)

        async with pool.acquire() as conn:
            await conn.copy_to_table(
                "products",
                source=buf,
                columns=["seller_id", "title", "description", "price", "stock"],
                format="text",
            )

        print(f"  Products: {batch_end}/{PRODUCT_COUNT}")

    print(f"Seeded {PRODUCT_COUNT} products")


async def main() -> None:
    identity_pool = await asyncpg.create_pool(IDENTITY_DB_URL, min_size=2, max_size=5)
    catalog_pool = await asyncpg.create_pool(CATALOG_DB_URL, min_size=2, max_size=5)

    try:
        # Check if already seeded
        count = await identity_pool.fetchval("SELECT count(*) FROM users")
        if count >= USER_COUNT:
            print(f"Already seeded ({count} users). Skipping.")
            return

        user_ids = await seed_users(identity_pool)
        await seed_products(catalog_pool, user_ids)
        print("Seeding complete!")
    finally:
        await identity_pool.close()
        await catalog_pool.close()


if __name__ == "__main__":
    asyncio.run(main())
