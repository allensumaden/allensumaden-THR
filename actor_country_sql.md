-- 1. Create the countries table
CREATE TABLE IF NOT EXISTS countries (
    country_id            serial PRIMARY KEY,
    country_name          varchar(70) NOT NULL,
    country_modified_date timestamp without time zone,
    country_delete_ind    boolean NOT NULL DEFAULT false
);

-- 2. Make sure actors matches the diagram
CREATE TABLE IF NOT EXISTS actors (
    actor_id            serial PRIMARY KEY,
    actor_fname         varchar(50),
    actor_lname         varchar(50),
    actor_modified_date timestamp without time zone,
    actor_delete_ind    boolean NOT NULL DEFAULT false
);
-- If the actors table already exists from my earlier suggestion, fix its columns:
ALTER TABLE actors DROP COLUMN IF EXISTS actor_name;
ALTER TABLE actors ADD COLUMN IF NOT EXISTS actor_fname varchar(50);
ALTER TABLE actors ADD COLUMN IF NOT EXISTS actor_lname varchar(50);
ALTER TABLE actors ADD COLUMN IF NOT EXISTS actor_modified_date timestamp without time zone;
ALTER TABLE actors ADD COLUMN IF NOT EXISTS actor_delete_ind boolean NOT NULL DEFAULT false;

-- 3. Update movies: replace the text country column with a foreign key
ALTER TABLE movies DROP COLUMN IF EXISTS movie_country;
ALTER TABLE movies ADD COLUMN IF NOT EXISTS country_id integer REFERENCES countries(country_id);
ALTER TABLE movies ADD COLUMN IF NOT EXISTS actor_id integer REFERENCES actors(actor_id);
ALTER TABLE movies ADD COLUMN IF NOT EXISTS language_id integer REFERENCES languages(language_id);

INSERT INTO countries (country_name) VALUES ('South Korea'), ('USA');

UPDATE movies
SET country_id = (SELECT country_id FROM countries WHERE country_name = 'South Korea')
WHERE movie_id = 1;

-- 4. Create the languages table
CREATE TABLE IF NOT EXISTS languages (
    language_id            serial PRIMARY KEY,
    language_name          varchar(70) NOT NULL,
    language_modified_date timestamp without time zone,
    language_delete_ind    boolean NOT NULL DEFAULT false
);

-- 5. Insert languages in language table
INSERT INTO languages (language_name) VALUES ('English'), ('Korean'), ('Filipino');

-- 6. Create users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    user_name VARCHAR(50) NOT NULL UNIQUE,
    user_password VARCHAR(256) NOT NULL,
    user_modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_delete_ind BOOLEAN NOT NULL DEFAULT FALSE
);