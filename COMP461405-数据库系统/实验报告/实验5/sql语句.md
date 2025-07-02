## 3.1.1 创建
(1) 创建模式 sche1，然后创建表空间 example1，创建分区表 sche1.students(包括学号 id，
姓名，年龄)，并基于年龄（<18、18~20、20~25、25~40），将分区表划分 4 个分区 P1、P2、
P3、P4。

```sql

CREATE SCHEMA IF NOT EXISTS sche1;


create tablespace example1 relative location 'example1';


CREATE TABLE sche1.students (
    id    VARCHAR(10) PRIMARY KEY,
    name  VARCHAR(50),
    age   INT
) TABLESPACE example1
PARTITION BY RANGE (age)
(
    PARTITION P1 VALUES LESS THAN(18),
    PARTITION P2 VALUES LESS THAN(21),
    PARTITION P3 VALUES LESS THAN(26),
    PARTITION P4 VALUES LESS THAN(41)
)
ENABLE ROW MOVEMENT;

```

## 3.1.2 增删改查
(1) 向分区表 sche1.students 中加入增加一些记录(“1001”,“aerf”,10)、(“1021”,“beu”,19)、
(“1031”,“cekf”,11)；

```sql
INSERT INTO sche1.students VALUES('1001','aerf',10), ('1021','beu',19), ('1031','cekf',11);
```

(2) 查询分区 P1 的所有信息；

```sql
SELECT * FROM sche1.students PARTITION(P1);
```

(3) 删除分区表 sche1.students 和表空间 example1，并删除模式 sche1。

```sql
DROP TABLE IF EXISTS sche1.students;
DROP TABLESPACE IF EXISTS example1;
DROP SCHEMA IF EXISTS sche1 CASCADE;
```

## 3.2.1 练习更新、删除主表数据（针对主键属性且子表中可能有参照外键数据）
(1) 找出学号为“1437120165”的同学，将她的学号更新为“1001”，并更新和参照外键数据；
(2) 学号更新完之后，删除学号为“1001”同学的相关信息。

```sql
-- 配置xk表级联约束（需执行一次）
ALTER TABLE kk.xk DROP CONSTRAINT IF EXISTS xk_fkey_1;
ALTER TABLE kk.xk ADD CONSTRAINT xk_fkey_1 
FOREIGN KEY (xh) REFERENCES kk.xs(xh)
ON UPDATE CASCADE ON DELETE CASCADE;
```

```sql

UPDATE kk.xs SET xh = '1001' WHERE xh = '1437120165';
DELETE FROM xs WHERE xh = '1001';

```


## 3.2.2 练习更新、删除主表数据（针对非主键属性）
(1) 寻找性别为“NULL”的数据，并将其赋值为“男”；
(2) 寻找出生日期为“NULL”的数据，删除这些同学的信息，以及他们的选课信息。

```sql
UPDATE kk.xs SET xb = '男' WHERE xb IS NULL;

-- 由于 xk.xh 已经设了 ON DELETE CASCADE，下面一条就能同时删子表
DELETE FROM kk.xs WHERE chrq IS NULL;

```

## 3.2.3 练习先删除子表数据，再删除主表数据
(1) 删除设计与艺术学院（zy）的相关信息，并把属于设计与艺术学院的同学，老师，授课
信息以及同学的选课信息删除。

```sql

DELETE FROM kk.xk
WHERE xh IN (
  SELECT xh FROM kk.xs WHERE ydh = 'zy'
);

DELETE FROM kk.xk
WHERE (kcbh, jsbh) IN (
    SELECT kcbh, bh
    FROM kk.sk
    WHERE bh IN (
        SELECT jsbh FROM kk.js WHERE ydh = 'zy'
    )
);


DELETE FROM kk.sk
WHERE bh IN (
  SELECT jsbh FROM kk.js WHERE ydh = 'zy'
);


DELETE FROM kk.xs
WHERE ydh = 'zy';


DELETE FROM kk.js
WHERE ydh = 'zy';


DELETE FROM kk.xyb
WHERE ydh = 'zy';

```

## 3.2.4 使用子查询方式更新、删除数据
(1) 找出挂过科的同学（至少有一名课程成绩在小于 60），将他们的班级信息更新为
“08012048”；
(2) 找出挂过科的同学，并删除他们的对应数据；与此同时，对应的选课信息也被删除。

```sql
UPDATE kk.xs
SET bj = '08012048'
WHERE xh IN (
  SELECT DISTINCT xh
  FROM kk.xk
  WHERE cj < 60
);

DELETE FROM kk.xs
WHERE xh IN (
  SELECT DISTINCT xh
  FROM kk.xk
  WHERE cj < 60
);

```


## 3.3.1 使用 create index 创建索引
(1) 对学生表(xs)中的学号(xh)列创建单列索引 stu_index；
(2) 对学生表(xs)中的姓名(xm)和班级(bj)列创建复合索引 ad_index;
(3) 对学生表(xs)中的出生日期(chrq)（00/00/0000）的年份创建表达式索引;
(4) 对学院表(xyb)中的学院编号(ydh)列创建唯一索引；
(5) 对学院表(xyb)中的学院编号(ydh)列创建部分索引（只索引单号的部门 ID）；

```sql
CREATE INDEX IF NOT EXISTS stu_index
ON kk.xs(xh);

CREATE INDEX IF NOT EXISTS ad_index
ON kk.xs(xm, bj);

CREATE INDEX IF NOT EXISTS year_index
ON kk.xs ((EXTRACT(YEAR FROM chrq)));

CREATE UNIQUE INDEX IF NOT EXISTS ydh_index
ON kk.xyb(ydh);

CREATE INDEX IF NOT EXISTS odd_ydh_index
ON kk.xyb(ydh)
WHERE (ydh ~ '^[0-9]+$' AND (ydh::int % 2) = 1);
```

## 3.3.2 使用 alter table 添加索引
(1) 对学生表(xs)中的出生日期列添加一个唯一索引 date_index，姓名(xm)和性别(xb)列添加一个复合索引 name_sex_index；
(2) 对学生选课表(xk)中的教师编号(jsbh)列创建外键索引。

数据集无法给出生日期、姓名性别创建唯一索引。且opengauss的alter table不支持创建普通索引。
```sql
CREATE INDEX IF NOT EXISTS date_index
  ON kk.xs(chrq);

CREATE INDEX IF NOT EXISTS name_sex_index
  ON kk.xs(xm, xb);

CREATE INDEX IF NOT EXISTS idx_xk_jsbh
    ON kk.xk(jsbh);

```

## 3.3.3 在创建表的同时创建索引
(1) 创建 game 表（比赛编号，比赛名称、比赛时间、学分）（每列的数据类型及长度等信
息自定），并对比赛编号列创建主键索引 game_pkey，在学分列创建唯一索引 game_cre_index。
```sql
CREATE TABLE IF NOT EXISTS kk.game (
  game_id    VARCHAR(10)   NOT NULL,
  game_name  VARCHAR(100),
  game_time  TIMESTAMP     NOT NULL,
  xf         DECIMAL(5,1)  NOT NULL,
  CONSTRAINT game_pkey      PRIMARY KEY (game_id),
  CONSTRAINT game_cre_index UNIQUE     (xf)
);
```


## 3.3.4 查询计划
(1) 通过查询计划（EXPLAIN）查询学生表中出生年份在 1998 的学生信息。
```sql
EXPLAIN ANALYZE
SELECT *
FROM kk.xs
WHERE EXTRACT(YEAR FROM chrq) = 1998;

SET enable_indexscan  = OFF;
SET enable_bitmapscan = OFF;

EXPLAIN ANALYZE
SELECT *
FROM kk.xs
WHERE EXTRACT(YEAR FROM chrq) = 1998;

SET enable_indexscan  = ON;
SET enable_bitmapscan = ON;
```

## 3.3.5 删除索引
(1) 使用 drop index 删除索引 stu_index、ad_index

```sql
DROP INDEX IF EXISTS kk.stu_index;
DROP INDEX IF EXISTS kk.ad_index;
```