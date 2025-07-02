## （1）
在 employees 表中，为员工 emp_no 为 10003 的员工新增一条工作经历记录到 dept_emp 
表，同时在 titles 表中为其添加一个新的职位记录。请编写一个事务，确保这两个操作要么 
都成功提交，要么都不生效，并通过 SELECT 给出事务提交前后查询相关数据的 SQL 语句 
及预期结果。 
```sql
-- 事务前数据验证
SELECT * FROM kk.dept_emp WHERE emp_no = 10003;
SELECT * FROM kk.titles WHERE emp_no = 10003;

-- 开始事务
BEGIN;

-- 向dept_emp表插入新记录
INSERT INTO kk.dept_emp (emp_no, dept_no, from_date, to_date)
VALUES (10003, 'd005', '2025-01-01', '2025-12-31');

-- 向titles表插入新记录
INSERT INTO kk.titles (emp_no, title, from_date, to_date)
VALUES (10003, 'wsp Engineer', '2025-01-01', '2025-12-31');

-- 提交事务（确保两个操作同时生效）
COMMIT;

-- 事务后数据验证
SELECT * FROM kk.dept_emp WHERE emp_no = 10003;
SELECT * FROM kk.titles WHERE emp_no = 10003;
```

## （2）
需要完成一个事务，要对 salaries 表中 emp_no 为 10001 的员工薪资进行调整，先将 
薪资提高 20%，然后模拟一个错误操作（如将 to_date 设置为一个不合理的过去时间），使 
用事务回滚确保数据库数据不受错误操作影响。请编写完整的事务代码，并给出事务回滚前 
后查询该员工薪资数据的 SQL 语句及预期结果。 

```sql
SELECT * FROM kk.salaries WHERE emp_no = 10001;
-- 开始事务
BEGIN;

UPDATE kk.salaries 
SET salary = salary * 1.2  
WHERE emp_no = 10001 AND to_date = '9999-01-01';

SAVEPOINT s1;

UPDATE kk.salaries 
SET to_date = '9988-01-01'  
WHERE emp_no = 10001 AND to_date = '9999-01-01';

ROLLBACK TO SAVEPOINT s1;

-- 事务后数据验证
SELECT * FROM kk.salaries WHERE emp_no = 10001;

COMMIT;
```

## （3）
在 departments 表中，要对部门信息进行一系列操作。首先插入一个新部门记录，设置 
保存点；接着尝试修改一个不存在的部门编号（模拟错误操作）；然后回滚到保存点，再插 
入另一个新部门记录，最后提交事务。请编写完整的事务代码，并给出各个关键步骤（设置 
保存点、回滚到保存点、提交事务）前后查询 departments 表数据的 SQL 语句及预期结果。 

```sql
-- 开始事务
BEGIN;

SELECT * FROM kk.departments;

INSERT INTO kk.departments (dept_no, dept_name) VALUES ('d010', 'New Department');


SAVEPOINT sp1;

UPDATE kk.departments 
SET dept_name = 'Invalid Update'
WHERE dept_no = 'd999'; 

SELECT * FROM kk.departments;

ROLLBACK TO SAVEPOINT sp1;

-- 插入第二个新部门
INSERT INTO kk.departments (dept_no, dept_name) VALUES ('d011', 'Another Department');

SELECT * FROM kk.departments;
-- 提交事务
COMMIT;

```
## （4）
基于 employ 数据库，设置两个用户连接，同时并发对同一个数据库（employ 数据库） 
进行操作，设置实验进行下列验证： 
a）READ COMMITTED（默认级别）下不会发生脏读。 
事务A：
```sql
BEGIN;
SELECT dept_name FROM kk.departments WHERE dept_no = 'd001';
```

事务B：
```sql
BEGIN;
UPDATE kk.departments SET dept_name = 'sbs' WHERE dept_no = 'd001'; 
```

事务A：
```sql
SELECT dept_name FROM kk.departments WHERE dept_no = 'd001';
COMMIT;
```

b) READ COMMITTED 下会发生不可重复读。 

事务A：
```sql
BEGIN;
SELECT dept_name FROM kk.departments WHERE dept_no = 'd001';
```

事务B：
```sql
BEGIN;
UPDATE kk.departments SET dept_name = 'sbs' WHERE dept_no = 'd001'; 
COMMIT;
```

事务A：
```sql
SELECT dept_name FROM kk.departments WHERE dept_no = 'd001';
COMMIT;
```
c) 设置隔离级别 REPEATABLE READ，解决不可重复读问题。

事务A：
```sql
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT dept_name FROM kk.departments WHERE dept_no = 'd001';
```

事务B：
```sql
BEGIN;
UPDATE kk.departments SET dept_name = 'wwwwwwwww' WHERE dept_no = 'd001'; 
COMMIT;
```

事务A：
```sql
SELECT dept_name FROM kk.departments WHERE dept_no = 'd001';
COMMIT;
```
CREATE USER user7 WITH PASSWORD 'Password123!';
CREATE DATABASE db77 OWNER user7;
## 在 openGauss 中，使用物理备份工具和逻辑备份工具： 
### 1）逻辑备份 employ 数据库，以目录形式输出到 /home/omm/logic/team。 
gs_dump -U user7 -W "Password123!" -p 5432 -F d -f /home/omm/logical/backup/db77 db77
### 2）逻辑备份 employees 员工表，以自定义形式输出到 /home/omm/logic/employees.dump。 
gs_dump -U user7 -W "Password123!" -p 5432 -F c -t kk.employees -f /home/omm/logical/backup/employees.dump db77
### 3）对 openGauss 的所有数据库数据进行一次性逻辑备份，并且以文本形式输出到 /home/omm/logic/database.bak。 
gs_dumpall -U user7 -W "Password123!" -p 5432 -f /home/omm/logical/backup/database.bak
### 4）将 1）导出的 employ 数据库目录恢复成原本的数据库。【先将数据库删除】
gs_restore -U user7 -W "Password123!" -p 5432 -d db77 -F d /home/omm/logical/backup/db77
### 5）将 1）导出的 emoloyees 员工表导入 employ 数据库中。【先将表删除】
gs_restore -U user7 -W "Password123!" -p 5432 -F c -d db77 /home/omm/logical/backup/employees.dump 
### 6）将 employ 数据库进行全量物理备份，输出到目录 /home/opengauss/physic/gs_bak。 【注意先初始化备份目录、添加备份实例】 
gs_probackup init -B /home/omm/physical/gs_bak
gs_probackup add-instance -B /home/omm/physical/gs_bak -D /var/lib/opengauss/data --instance=gs_bak_list
gs_probackup backup -B /home/omm/physical/gs_bak --instance=gs_bak_list -b FULL
### 7）将 employ 数据库进行增量物理备份，输出到目录 /home/opengauss/physic/gs_bak。 
ALTER SYSTEM SET enable_cbm_tracking=on;
gs_probackup backup -B /home/omm/physical/gs_bak --instance=gs_bak_list -b PTRACK
### 8）对 employ 数据库进行增量恢复。【先将整个数据库目录删除】
gs_probackup restore -B /home/omm/physical/gs_bak --instance=gs_bak_list -i SX4J92