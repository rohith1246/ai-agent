-- Day 2: ORDER BY, LIMIT, DISTINCT

-- 1. Students ordered by marks highest first
SELECT name, marks FROM students 
ORDER BY marks DESC;

-- 2. Top 5 students only
SELECT name, marks FROM students 
ORDER BY marks DESC 
LIMIT 5;

-- 3. Lowest scorer
SELECT name, marks FROM students 
ORDER BY marks ASC 
LIMIT 1;

-- 4. All unique cities students are from
SELECT DISTINCT city FROM students;

-- 5. Top 3 students from Hyderabad
SELECT name, marks FROM students 
WHERE city = 'Hyderabad' 
ORDER BY marks DESC 
LIMIT 3;