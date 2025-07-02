#### **(1) 查询每个部门的编号、名称、雇员人数、最低工资、平均工资、最高工资及工资总额**
```sql
SELECT 
    d.dept_no,
    d.dept_name,
    COUNT(e.emp_no) AS employee_count,
    MIN(s.salary) AS min_salary,
    AVG(s.salary) AS avg_salary,
    MAX(s.salary) AS max_salary,
    SUM(s.salary) AS sum_salary
FROM 
    kk.departments d
JOIN 
    kk.dept_emp de ON d.dept_no = de.dept_no
JOIN 
    kk.employees e ON de.emp_no = e.emp_no
JOIN 
    kk.salaries s ON e.emp_no = s.emp_no
GROUP BY 
    d.dept_no,d.dept_name
ORDER BY
    d.dept_no ASC;
```

---

#### **(2) 查询每个部门的编号、名称、及各个时间段担任该部门经理的雇员的编号和姓名**
```sql
SELECT
    d.dept_no,
    d.dept_name,
    e.emp_no,
    e.first_name || ' ' || e.last_name AS dept_manager_name,
    dm.from_date,
    dm.to_date
FROM 
    kk.departments d
JOIN
    kk.dept_manager dm ON dm.dept_no = d.dept_no
JOIN
    kk.employees e ON e.emp_no = dm.emp_no
ORDER BY
    d.dept_no,dm.from_date;
```

---

#### **(3) 查询每位雇员的编号、姓名、及各个时间段的工资额**
```sql
SELECT
    e.emp_no,
    e.first_name || ' ' || e.last_name AS employee_name,
    s.salary,
    s.from_date,
    s.to_date
FROM 
    kk.employees e
JOIN
    kk.salaries s ON s.emp_no = e.emp_no
ORDER BY
    e.emp_no,s.from_date;
    
```

---

#### **(4) 查询每位雇员的编号、姓名、及各个时间段担任的职务**
```sql
SELECT
    e.emp_no,
    e.first_name || ' ' || e.last_name AS employee_name,
    t.title,
    t.from_date,
    t.to_date
FROM 
    kk.employees e
JOIN
    kk.titles t ON t.emp_no = e.emp_no
ORDER BY
    e.emp_no,t.from_date;
```

---

#### **(5) 查询担任每种职务的雇员人数**
```sql
SELECT 
    title,
    COUNT(t.emp_no) AS title_count
FROM 
    kk.titles t
GROUP BY 
    title;
```

---

#### **(6) 查询每个部门中担任每种职务的雇员人数**
```sql
SELECT
    d.dept_no,
    d.dept_name,
    t.title,
    COUNT(t.emp_no)
FROM
    kk.departments d
JOIN
    kk.dept_emp de ON d.dept_no = de.dept_no
JOIN
    kk.titles t ON de.emp_no = t.emp_no
GROUP BY
    d.dept_no,d.dept_name,t.title
ORDER BY
    d.dept_no,t.title;

```

---

#### **(7) 查询所有曾经在 `Development` 工作过雇员的编号、姓名及时间段**
```sql
SELECT
    e.emp_no,
    e.first_name || ' ' || e.last_name AS employee_name,
    de.from_date,
    de.to_date
FROM 
    kk.employees e
JOIN
    kk.dept_emp de ON de.emp_no = e.emp_no
JOIN
    kk.departments d ON de.dept_no = d.dept_no
WHERE
    d.dept_name = 'Development';
```

---

#### **(8) 查询曾经在所有部门都工作过的雇员的编号、姓名**
```sql
SELECT
    e.emp_no,
    e.first_name || ' ' || e.last_name AS employee_name
FROM
    kk.employees e
WHERE
(
    SELECT
        COUNT(d.dept_no)
    FROM kk.departments d
)
= 
(
    SELECT 
        COUNT(de.dept_no)
    FROM kk.dept_emp de
    WHERE de.emp_no = e.emp_no
)
ORDER BY
    e.emp_no;

```

---

#### **(9) 在 `dept_emp` 表中插入适当数据使得至少 3 个以上雇员满足上一题的查询要求**
```sql
INSERT INTO kk.employees (emp_no, birth_date, first_name, last_name, gender, hire_date)
VALUES
    (222, '2020-01-01', 'wsp', 'spw', 'M', '2019-01-01'),
    (122, '2020-01-01', 'wssp', 'sspw', 'M', '2019-01-01'),
    (322, '2020-01-01', 'wsssp', 'ssspw', 'M', '2019-01-01');




INSERT INTO kk.dept_emp (emp_no, dept_no, from_date, to_date)
VALUES 
    (222, 'd001', '2020-01-01', '2025-01-01'),
    (222, 'd002', '2020-01-01', '2025-01-01'),
    (222, 'd003', '2020-01-01', '2025-01-01'),
    (222, 'd004', '2020-01-01', '2025-01-01'),
    (222, 'd005', '2020-01-01', '2025-01-01'),
    (222, 'd006', '2020-01-01', '2025-01-01'),
    (222, 'd007', '2020-01-01', '2025-01-01'),
    (222, 'd008', '2020-01-01', '2025-01-01'),
    (222, 'd009', '2020-01-01', '2025-01-01'),
    (122, 'd001', '2020-01-01', '2025-01-01'),
    (122, 'd002', '2020-01-01', '2025-01-01'),
    (122, 'd003', '2020-01-01', '2025-01-01'),
    (122, 'd004', '2020-01-01', '2025-01-01'),
    (122, 'd005', '2020-01-01', '2025-01-01'),
    (122, 'd006', '2020-01-01', '2025-01-01'),
    (122, 'd007', '2020-01-01', '2025-01-01'),
    (122, 'd008', '2020-01-01', '2025-01-01'),
    (122, 'd009', '2020-01-01', '2025-01-01'),
    (322, 'd001', '2020-01-01', '2025-01-01'),
    (322, 'd002', '2020-01-01', '2025-01-01'),
    (322, 'd003', '2020-01-01', '2025-01-01'),
    (322, 'd004', '2020-01-01', '2025-01-01'),
    (322, 'd005', '2020-01-01', '2025-01-01'),
    (322, 'd006', '2020-01-01', '2025-01-01'),
    (322, 'd007', '2020-01-01', '2025-01-01'),
    (322, 'd008', '2020-01-01', '2025-01-01'),
    (322, 'd009', '2020-01-01', '2025-01-01');
```

---

#### **(10) 添加一个部门 `Learning`**
```sql
INSERT INTO kk.departments (dept_no, dept_name)
VALUES ('d010', 'Learning');
```

---

#### **(11) 删除 `Sales` 部门**
```sql
DELETE FROM kk.departments WHERE dept_name = 'Sales';
```

---

#### **(12) 删除工资低于 7w 的员工**
```sql
DELETE FROM kk.employees
WHERE emp_no IN (
    SELECT emp_no
    FROM kk.salaries
    WHERE salary < 70000
);
```

---

#### **(13) 修改 `Learning` 部门的编号为 `d01`**
```sql
UPDATE kk.departments
SET dept_no = 'd01'
WHERE dept_name = 'Learning';
```
以下是针对你描述的需求，逐步完成的 SQL 操作脚本。假设你已经进入 OpenGauss 的 `gsql` 客户端，并且已经连接到目标数据库。

---


#### (1) 创建用户 `user1`、`user2`
```sql
CREATE USER user1 WITH PASSWORD 'user1_password';
CREATE USER user2 WITH PASSWORD 'user2_password';
```

#### (2) 在 `user1` 下创建数据库 `db1`、`db2`
```sql
CREATE DATABASE db1 OWNER user1;
CREATE DATABASE db2 OWNER user1;
```

#### (3) 创建模式 `sche1`、`sche2`
```sql
-- 切换到 db1
\c db1
CREATE SCHEMA sche1;
CREATE SCHEMA sche2;
```

#### (4) 在 `db1` 的 `sche1` 下创建表 `students`，在 `sche2` 下创建表 `teachers`
```sql
-- 在 sche1 下创建 students 表
CREATE TABLE sche1.students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    age INT
);

-- 在 sche2 下创建 teachers 表
CREATE TABLE sche2.teachers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    subject VARCHAR(100)
);
```

#### (5) 分配给用户 `user1` 对于 `db1`、`db2` 的所有权限
```sql
GRANT ALL PRIVILEGES ON DATABASE db1 TO user1;
GRANT ALL PRIVILEGES ON DATABASE db2 TO user1;
```

#### (6) 把模式 `sche1` 授予用户 `user1`，`sche2` 授予用户 `user2`
```sql
GRANT USAGE ON SCHEMA sche1 TO user1;
GRANT USAGE ON SCHEMA sche2 TO user2;
```

#### (7) 撤销对 `db2` 的所有权限，并删除 `user2`、`db2`、`sche2`、`teachers` 表
```sql
-- 撤销 user1 对 db2 的所有权限
REVOKE ALL PRIVILEGES ON DATABASE db2 FROM user1;

-- 删除 teachers 表
DROP TABLE sche2.teachers;

-- 删除 sche2 模式
DROP SCHEMA sche2;

-- 删除 db2 数据库
DROP DATABASE db2;

-- 删除 user2 用户
DROP USER user2;
```

#### (8) 向表 `students` 中添加一列，名为 `column1`，数据类型为 `INT`，并删除
```sql
-- 添加列
ALTER TABLE sche1.students ADD COLUMN column1 INT;

-- 删除列
ALTER TABLE sche1.students DROP COLUMN column1;
```

---

