import asyncio
import os
import random
import io

import asyncpg
from faker import Faker

IDENTITY_DB_URL = os.environ["IDENTITY_DB_URL"]
COURSE_DB_URL = os.environ["COURSE_DB_URL"]
ENROLLMENT_DB_URL = os.environ["ENROLLMENT_DB_URL"]
PAYMENT_DB_URL = os.environ["PAYMENT_DB_URL"]
NOTIFICATION_DB_URL = os.environ["NOTIFICATION_DB_URL"]

USER_COUNT = 50_000
COURSE_COUNT = 100_000
ENROLLMENT_COUNT = 200_000
PAYMENT_COUNT = 50_000
REVIEW_COUNT = 100_000
BATCH_SIZE = 5_000

# 80% students, 20% teachers
TEACHER_RATIO = 0.2
# 70% of teachers are verified
TEACHER_VERIFIED_RATIO = 0.7

fake = Faker()
# Pre-hash a single password for all seed users (bcrypt is slow, we don't need unique hashes for testing)
SEED_PASSWORD_HASH = "$2b$12$UATV7vr3iDCYLCAvv2bqquAgxLOUlKmIrXDGcowenuwxvFT0z.7Oa"


async def seed_users(pool: asyncpg.Pool) -> tuple[list[str], list[str], list[str]]:
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

    student_rows = await pool.fetch("SELECT id FROM users WHERE role = 'student'")
    student_ids = [str(row["id"]) for row in student_rows]

    all_rows = await pool.fetch("SELECT id FROM users")
    all_ids = [str(row["id"]) for row in all_rows]

    print(f"Seeded {len(all_ids)} users ({len(teacher_ids)} verified teachers, {len(student_ids)} students)")
    return all_ids, teacher_ids, student_ids


async def seed_courses(pool: asyncpg.Pool, teacher_ids: list[str]) -> list[tuple[str, bool, float]]:
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
            price = "\\N" if is_free else str(round(random.uniform(9.99, 199.99), 2))
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

    # Fetch course data for enrollments
    rows = await pool.fetch("SELECT id, is_free, price FROM courses")
    course_data = [(str(r["id"]), r["is_free"], float(r["price"] or 0)) for r in rows]
    print(f"Seeded {COURSE_COUNT} courses")
    return course_data


async def seed_modules_and_lessons(pool: asyncpg.Pool) -> None:
    """Seed modules and lessons for first 10K courses."""
    print("Seeding modules and lessons...")

    course_rows = await pool.fetch(
        "SELECT id FROM courses ORDER BY created_at LIMIT 10000"
    )
    course_ids = [str(r["id"]) for r in course_rows]

    module_titles = [
        "Введение", "Основы", "Продвинутые темы", "Практика", "Итоговый проект",
        "Теория", "Инструменты", "Архитектура",
    ]
    lesson_prefixes = [
        "Что такое", "Как работает", "Настройка", "Практикум:", "Разбор",
        "Основы", "Углублённо:", "Задание:",
    ]
    lesson_topics = [
        "переменные", "функции", "классы", "модули", "тестирование",
        "деплой", "базы данных", "API", "авторизация", "кэширование",
    ]

    total_modules = 0
    total_lessons = 0

    for batch_start in range(0, len(course_ids), 500):
        batch_courses = course_ids[batch_start:batch_start + 500]
        module_buf = io.BytesIO()
        modules_in_batch: list[tuple[str, str, int]] = []  # (module_placeholder, course_id, order)

        for course_id in batch_courses:
            num_modules = random.randint(3, 5)
            chosen_titles = random.sample(module_titles, min(num_modules, len(module_titles)))
            for order, mtitle in enumerate(chosen_titles):
                line = f"{course_id}\t{mtitle}\t{order}\n"
                module_buf.write(line.encode())
                total_modules += 1

        module_buf.seek(0)
        async with pool.acquire() as conn:
            await conn.copy_to_table(
                "modules", source=module_buf,
                columns=["course_id", "title", "order"], format="text",
            )

        # Now fetch these modules and seed lessons
        module_rows = await pool.fetch(
            'SELECT id, course_id FROM modules WHERE course_id = ANY($1::uuid[]) ORDER BY "order"',
            [r["id"] for r in course_rows[batch_start:batch_start + 500]],
        )

        lesson_buf = io.BytesIO()
        for mod_row in module_rows:
            num_lessons = random.randint(3, 8)
            for order in range(num_lessons):
                prefix = random.choice(lesson_prefixes)
                topic = random.choice(lesson_topics)
                ltitle = f"{prefix} {topic}"
                content = fake.paragraph(nb_sentences=5)
                duration = random.choice([10, 15, 20, 25, 30, 45, 60])
                line = f"{mod_row['id']}\t{ltitle}\t{content}\t\\N\t{duration}\t{order}\n"
                lesson_buf.write(line.encode())
                total_lessons += 1

        lesson_buf.seek(0)
        async with pool.acquire() as conn:
            await conn.copy_to_table(
                "lessons", source=lesson_buf,
                columns=["module_id", "title", "content", "video_url", "duration_minutes", "order"],
                format="text",
            )

        print(f"  Modules+Lessons: {min(batch_start + 500, len(course_ids))}/{len(course_ids)} courses")

    print(f"Seeded {total_modules} modules, {total_lessons} lessons")


async def seed_reviews(pool: asyncpg.Pool, student_ids: list[str]) -> None:
    """Seed reviews for courses."""
    print(f"Seeding ~{REVIEW_COUNT} reviews...")

    course_rows = await pool.fetch("SELECT id FROM courses")
    course_ids = [str(r["id"]) for r in course_rows]

    seen: set[tuple[str, str]] = set()
    written = 0

    for batch_start in range(0, REVIEW_COUNT, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, REVIEW_COUNT)
        buf = io.BytesIO()
        batch_written = 0

        for _ in range(batch_start, batch_end):
            student_id = random.choice(student_ids)
            course_id = random.choice(course_ids)
            key = (student_id, course_id)
            if key in seen:
                continue
            seen.add(key)

            rating = random.choices([1, 2, 3, 4, 5], weights=[5, 5, 15, 35, 40])[0]
            comment = fake.sentence() if random.random() < 0.7 else ""
            line = f"{student_id}\t{course_id}\t{rating}\t{comment}\n"
            buf.write(line.encode())
            batch_written += 1

        if batch_written == 0:
            continue

        buf.seek(0)
        async with pool.acquire() as conn:
            await conn.copy_to_table(
                "reviews", source=buf,
                columns=["student_id", "course_id", "rating", "comment"],
                format="text",
            )
        written += batch_written
        print(f"  Reviews: {written}/{REVIEW_COUNT}")

    # Update avg_rating and review_count on courses
    await pool.execute("""
        UPDATE courses c SET
            avg_rating = sub.avg_rating,
            review_count = sub.cnt
        FROM (
            SELECT course_id, AVG(rating)::NUMERIC(3,2) as avg_rating, count(*) as cnt
            FROM reviews GROUP BY course_id
        ) sub
        WHERE c.id = sub.course_id
    """)

    print(f"Seeded {written} reviews, updated course ratings")


async def seed_payments(
    pool: asyncpg.Pool,
    student_ids: list[str],
    paid_courses: list[tuple[str, float]],
) -> list[tuple[str, str, str]]:
    """Seed payments and return (payment_id, student_id, course_id) tuples."""
    print(f"Seeding {PAYMENT_COUNT} payments...")

    payment_records: list[tuple[str, str, str]] = []

    for batch_start in range(0, PAYMENT_COUNT, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, PAYMENT_COUNT)
        buf = io.BytesIO()

        for _ in range(batch_start, batch_end):
            student_id = random.choice(student_ids)
            course_id, price = random.choice(paid_courses)
            line = f"{student_id}\t{course_id}\t{price}\tcompleted\n"
            buf.write(line.encode())

        buf.seek(0)

        async with pool.acquire() as conn:
            await conn.copy_to_table(
                "payments",
                source=buf,
                columns=["student_id", "course_id", "amount", "status"],
                format="text",
            )

        print(f"  Payments: {batch_end}/{PAYMENT_COUNT}")

    rows = await pool.fetch("SELECT id, student_id, course_id FROM payments")
    payment_records = [(str(r["id"]), str(r["student_id"]), str(r["course_id"])) for r in rows]
    print(f"Seeded {len(payment_records)} payments")
    return payment_records


async def seed_enrollments(
    pool: asyncpg.Pool,
    student_ids: list[str],
    course_data: list[tuple[str, bool, float]],
    payment_records: list[tuple[str, str, str]],
) -> None:
    print(f"Seeding {ENROLLMENT_COUNT} enrollments...")

    # Build payment lookup: (student_id, course_id) -> payment_id
    payment_lookup: dict[tuple[str, str], str] = {}
    for pid, sid, cid in payment_records:
        payment_lookup[(sid, cid)] = pid

    seen: set[tuple[str, str]] = set()
    free_course_ids = [cid for cid, is_free, _ in course_data if is_free]
    paid_course_ids = [cid for cid, is_free, _ in course_data if not is_free]

    for batch_start in range(0, ENROLLMENT_COUNT, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, ENROLLMENT_COUNT)
        buf = io.BytesIO()
        written = 0

        for _ in range(batch_start, batch_end):
            student_id = random.choice(student_ids)
            # 60% free, 40% paid
            if random.random() < 0.6 and free_course_ids:
                course_id = random.choice(free_course_ids)
                payment_id = "\\N"
            elif paid_course_ids:
                course_id = random.choice(paid_course_ids)
                payment_id = payment_lookup.get((student_id, course_id), "\\N")
            else:
                course_id = random.choice(free_course_ids)
                payment_id = "\\N"

            key = (student_id, course_id)
            if key in seen:
                continue
            seen.add(key)

            line = f"{student_id}\t{course_id}\t{payment_id}\tenrolled\n"
            buf.write(line.encode())
            written += 1

        if written == 0:
            continue

        buf.seek(0)

        async with pool.acquire() as conn:
            await conn.copy_to_table(
                "enrollments",
                source=buf,
                columns=["student_id", "course_id", "payment_id", "status"],
                format="text",
            )

        print(f"  Enrollments: {min(batch_end, len(seen))}/{ENROLLMENT_COUNT}")

    print(f"Seeded {len(seen)} enrollments")


async def main() -> None:
    identity_pool = await asyncpg.create_pool(IDENTITY_DB_URL, min_size=2, max_size=5)
    course_pool = await asyncpg.create_pool(COURSE_DB_URL, min_size=2, max_size=5)
    enrollment_pool = await asyncpg.create_pool(ENROLLMENT_DB_URL, min_size=2, max_size=5)
    payment_pool = await asyncpg.create_pool(PAYMENT_DB_URL, min_size=2, max_size=5)

    try:
        # Check if already seeded
        count = await identity_pool.fetchval("SELECT count(*) FROM users")
        if count >= USER_COUNT:
            print(f"Already seeded ({count} users). Skipping.")
            return

        # Insert admin user before bulk COPY
        await identity_pool.execute(
            """
            INSERT INTO users (email, password_hash, name, role, is_verified)
            VALUES ($1, $2, $3, 'admin', true)
            ON CONFLICT (email) DO NOTHING
            """,
            "admin@eduplatform.com",
            SEED_PASSWORD_HASH,
            "Admin",
        )

        all_ids, teacher_ids, student_ids = await seed_users(identity_pool)
        course_data = await seed_courses(course_pool, teacher_ids)
        await seed_modules_and_lessons(course_pool)
        await seed_reviews(course_pool, student_ids)

        paid_courses = [(cid, price) for cid, is_free, price in course_data if not is_free]
        payment_records = await seed_payments(payment_pool, student_ids, paid_courses)
        await seed_enrollments(enrollment_pool, student_ids, course_data, payment_records)
        print("Seeding complete!")
    finally:
        await identity_pool.close()
        await course_pool.close()
        await enrollment_pool.close()
        await payment_pool.close()


if __name__ == "__main__":
    asyncio.run(main())
