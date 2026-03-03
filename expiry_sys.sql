-- Step 1: Create and select the database
CREATE DATABASE IF NOT EXISTS expiry_system;
USE expiry_system;
 
-- Step 2: Create USERS table
CREATE TABLE users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(100) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    role        ENUM("admin", "user") DEFAULT "user",
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
 
-- Step 3: Create PRODUCTS table
CREATE TABLE products (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    barcode      VARCHAR(100) NOT NULL UNIQUE,
    name         VARCHAR(200) NOT NULL,
    category     VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(200),
    mfg_date     DATE NOT NULL,
    exp_date     DATE NOT NULL,
    quantity     INT DEFAULT 1,
    unit         VARCHAR(50) DEFAULT "pcs",
    added_by     INT,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (added_by) REFERENCES users(id)
);
 
-- Step 4: Create SCAN_LOGS table
CREATE TABLE scan_logs (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT,
    product_id INT,
    scan_time  DATETIME DEFAULT CURRENT_TIMESTAMP,
    status     VARCHAR(50),
    FOREIGN KEY (user_id)    REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Insert users (passwords stored as plain text for demo)
INSERT INTO users (username, password, role) VALUES
("admin", "admin123", "admin"),
("john",  "user123",  "user");
 
-- Insert sample products
-- NOTE: Change the exp_date values to future/near-future dates
-- based on when you are running this project
 
INSERT INTO products
  (barcode, name, category, manufacturer, mfg_date, exp_date, quantity, unit, added_by)
VALUES
("8901030874543","Paracetamol 500mg","Medicine","Cipla Ltd","2024-01-01","2026-06-01",100,"strips",1),
("8906010200123","Cough Syrup 100ml","Medicine","Dabur India","2024-06-01","2025-02-10",50,"bottles",1),
("8901030000001","Vitamin C Tablets","Supplement","Himalaya","2023-12-01","2024-12-31",200,"strips",1),
("7310865004703","Hand Sanitizer 500ml","Hygiene","Dettol","2024-03-01","2026-03-01",30,"bottles",1),
("8901491500014","Antacid Syrup","Medicine","Abbott","2024-08-01","2025-02-15",60,"bottles",1),
("8906002450013","Multivitamin Capsules","Supplement","HealthKart","2024-09-01","2025-03-10",80,"strips",1),
("4902505222054","Face Mask N95","Hygiene","3M Company","2024-04-01","2025-04-01",500,"pcs",1),
("8901030123456","Glucose Powder 500g","Supplement","Heinz India","2024-07-01","2026-07-01",40,"packs",1);

