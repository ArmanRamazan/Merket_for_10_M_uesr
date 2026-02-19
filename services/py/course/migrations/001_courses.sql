DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'course_level') THEN
        CREATE TYPE course_level AS ENUM ('beginner', 'intermediate', 'advanced');
    END IF;
END$$;

CREATE TABLE IF NOT EXISTS courses (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_id       UUID NOT NULL,
    title            VARCHAR(500) NOT NULL,
    description      TEXT NOT NULL DEFAULT '',
    is_free          BOOLEAN NOT NULL DEFAULT true,
    price            NUMERIC(12,2),
    duration_minutes INTEGER NOT NULL DEFAULT 0,
    level            course_level NOT NULL DEFAULT 'beginner',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
