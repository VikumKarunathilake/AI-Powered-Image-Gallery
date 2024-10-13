CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    img_id VARCHAR(50) UNIQUE,
    title VARCHAR(255),
    url_viewer VARCHAR(255),
    url VARCHAR(255),
    display_url VARCHAR(255),
    width INTEGER,
    height INTEGER,
    size INTEGER,
    upload_time TIMESTAMP,
    expiration INTEGER,
    filename VARCHAR(255),
    mime_type VARCHAR(50),
    delete_url VARCHAR(255),
    approved BOOLEAN DEFAULT FALSE
);
