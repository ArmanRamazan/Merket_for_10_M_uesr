CREATE TABLE IF NOT EXISTS categories (
    id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE
);

INSERT INTO categories (name, slug) VALUES
    ('Programming', 'programming'),
    ('Design', 'design'),
    ('Business', 'business'),
    ('Marketing', 'marketing'),
    ('Data Science', 'data-science'),
    ('Languages', 'languages'),
    ('Music', 'music'),
    ('Other', 'other')
ON CONFLICT (slug) DO NOTHING;

ALTER TABLE courses ADD COLUMN IF NOT EXISTS category_id UUID REFERENCES categories(id);
CREATE INDEX IF NOT EXISTS idx_courses_category_id ON courses(category_id);
