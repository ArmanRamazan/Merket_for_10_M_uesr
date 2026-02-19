import asyncio
import os
import random
import io

import asyncpg
from faker import Faker

IDENTITY_DB_URL = os.environ["IDENTITY_DB_URL"]
COURSE_DB_URL = os.environ["COURSE_DB_URL"]

USER_COUNT = 50_000
COURSE_COUNT = 100_000
BATCH_SIZE = 5_000

# 80% students, 20% teachers
TEACHER_RATIO = 0.2
# 70% of teachers are verified
TEACHER_VERIFIED_RATIO = 0.7

fake = Faker()
# Pre-hash a single password for all seed users (bcrypt is slow, we don't need unique hashes for testing)
SEED_PASSWORD_HASH = "$2b$12$LJ3m4ys3Lk0TSwHCbmQ0oOzHPCFDMBSVOGwpMkgiMfOFMkyNrtfjO"


async def seed_users(pool: asyncpg.Pool) -> tuple[list[str], list[str]]:
    print(f"Seeding {USER_COUNT} users...")
    teacher_count = int(USER_COUNT * TEACHER_RATIO)

    for batch_start in range(0, USER_COUNT, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, USER_COUNT)
        buf = io.BytesIO()

        for i in range(batch_start, batch_end):
            is_teacher = i < teacher_count
            role = "teacher" if is_teacher else "student"
            is_verified = "true" if (is_teacher and random.random() < TEACHER_VERIFIED_RATIO) else "false"
            email = f"user{i}@example.com"
            name = fake.name()
            line = f"{email}\t{SEED_PASSWORD_HASH}\t{name}\t{role}\t{is_verified}\n"
            buf.write(line.encode())

        buf.seek(0)

        async with pool.acquire() as conn:
            await conn.copy_to_table(
                "users",
                source=buf,
                columns=["email", "password_hash", "name", "role", "is_verified"],
                format="text",
            )

        print(f"  Users: {batch_end}/{USER_COUNT}")

    # Get teacher IDs (verified only) for course creation
    teacher_rows = await pool.fetch(
        "SELECT id FROM users WHERE role = 'teacher' AND is_verified = true"
    )
    teacher_ids = [str(row["id"]) for row in teacher_rows]

    all_rows = await pool.fetch("SELECT id FROM users")
    all_ids = [str(row["id"]) for row in all_rows]

    print(f"Seeded {len(all_ids)} users ({len(teacher_ids)} verified teachers)")
    return all_ids, teacher_ids


async def seed_courses(pool: asyncpg.Pool, teacher_ids: list[str]) -> None:
    print(f"Seeding {COURSE_COUNT} courses...")

    subjects = [
        "Python", "JavaScript", "Machine Learning", "Data Science", "Web Development",
        "Mobile Development", "DevOps", "Cloud Computing", "Cybersecurity", "Algorithms",
    ]
    adjectives = [
        "Complete", "Advanced", "Practical", "Modern", "Professional",
        "Beginner-Friendly", "Intensive", "Hands-On", "Comprehensive", "Essential",
    ]
    levels = ["beginner", "intermediate", "advanced"]

    for batch_start in range(0, COURSE_COUNT, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, COURSE_COUNT)
        buf = io.BytesIO()

        for _ in range(batch_start, batch_end):
            teacher_id = random.choice(teacher_ids)
            adj = random.choice(adjectives)
            subj = random.choice(subjects)
            title = f"{adj} {subj}: {fake.bs().title()}"
            description = fake.paragraph(nb_sentences=3)
            is_free = random.random() < 0.3
            price = "" if is_free else str(round(random.uniform(9.99, 199.99), 2))
            duration_minutes = random.choice([30, 60, 90, 120, 180, 240, 360, 480, 600])
            level = random.choice(levels)
            line = f"{teacher_id}\t{title}\t{description}\t{is_free}\t{price}\t{duration_minutes}\t{level}\n"
            buf.write(line.encode())

        buf.seek(0)

        async with pool.acquire() as conn:
            await conn.copy_to_table(
                "courses",
                source=buf,
                columns=["teacher_id", "title", "description", "is_free", "price", "duration_minutes", "level"],
                format="text",
            )

        print(f"  Courses: {batch_end}/{COURSE_COUNT}")

    print(f"Seeded {COURSE_COUNT} courses")


async def main() -> None:
    identity_pool = await asyncpg.create_pool(IDENTITY_DB_URL, min_size=2, max_size=5)
    course_pool = await asyncpg.create_pool(COURSE_DB_URL, min_size=2, max_size=5)

    try:
        # Check if already seeded
        count = await identity_pool.fetchval("SELECT count(*) FROM users")
        if count >= USER_COUNT:
            print(f"Already seeded ({count} users). Skipping.")
            return

        all_ids, teacher_ids = await seed_users(identity_pool)
        await seed_courses(course_pool, teacher_ids)
        print("Seeding complete!")
    finally:
        await identity_pool.close()
        await course_pool.close()


if __name__ == "__main__":
    asyncio.run(main())
