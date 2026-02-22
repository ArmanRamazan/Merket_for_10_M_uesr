CREATE INDEX IF NOT EXISTS idx_courses_teacher_id ON courses (teacher_id);
CREATE INDEX IF NOT EXISTS idx_courses_created_at ON courses (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_modules_course_id ON modules (course_id);
CREATE INDEX IF NOT EXISTS idx_lessons_module_id ON lessons (module_id);
CREATE INDEX IF NOT EXISTS idx_reviews_course_id ON reviews (course_id);
