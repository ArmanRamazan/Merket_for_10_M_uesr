DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
        CREATE TYPE user_role AS ENUM ('student', 'teacher');
    END IF;
END$$;

ALTER TABLE users ADD COLUMN IF NOT EXISTS role user_role NOT NULL DEFAULT 'student';
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN NOT NULL DEFAULT false;
