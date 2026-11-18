-- Run once against the configured database before starting a version with Google sign-in.
ALTER TABLE users ADD COLUMN google_sub VARCHAR(255) NULL;
CREATE UNIQUE INDEX uq_users_google_sub ON users (google_sub);
