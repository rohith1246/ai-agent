-- Day 1: SELECT, WHERE, ORDER BY
-- Starting SQL sprint - June 8, 2026
-- Day 1: SELECT and WHERE

-- 1. Get all students
SELECT * FROM students;

-- 2. Get only name and marks
SELECT name, marks FROM students;

-- 3. Students who scored above 80
SELECT name, marks FROM students 
WHERE marks > 80;

-- 4. Students from Hyderabad
SELECT * FROM students 
WHERE city = 'Hyderabad';

-- 5. Students above 80 from Hyderabad
SELECT name, marks FROM students 
WHERE marks > 80 AND city = 'Hyderabad';