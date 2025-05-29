-- Creating Room Table
CREATE TABLE Room (
    room_no INT PRIMARY KEY,
    room_name VARCHAR(50),
    room_type VARCHAR(10) CHECK (room_type IN ('AC', 'NonAC')),
    charges DECIMAL(10, 2)
);

-- Creating Guest Table
CREATE TABLE Guest (
    Guest_code INT PRIMARY KEY,
    Gname VARCHAR(50),
    city VARCHAR(50)
);

-- Insert sample records into Room
INSERT INTO Room VALUES (1, 'Deluxe', 'AC', 12000);
INSERT INTO Room VALUES (2, 'Standard', 'NonAC', 8000);
INSERT INTO Room VALUES (3, 'Executive', 'AC', 15000);
INSERT INTO Room VALUES (4, 'Economy', 'NonAC', 5000);

-- Insert sample records into Guest
INSERT INTO Guest VALUES (101, 'John Doe', 'Pune');
INSERT INTO Guest VALUES (102, 'Jane Smith', 'Mumbai');
INSERT INTO Guest VALUES (103, 'Amit Shah', 'Delhi');
INSERT INTO Guest VALUES (104, 'Anjali Mehta', 'Pune');
