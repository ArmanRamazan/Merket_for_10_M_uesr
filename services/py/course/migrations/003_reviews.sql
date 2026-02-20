CREATE TABLE IF NOT EXISTS reviews (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL,
    course_id  UUID NOT NULL,
    rating     SMALLINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment    TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(student_id, course_id)
);

ALTER TABLE courses ADD COLUMN IF NOT EXISTS avg_rating NUMERIC(3,2);
ALTER TABLE courses ADD COLUMN IF NOT EXISTS review_count INTEGER NOT NULL DEFAULT 0;
