# SQL经典实例

## 1. 检索记录

### 1.7 拼接列值

将多列的值作为一列返回：

```SQL
select concat(ename, ' works as a', job) 
from emp
where deptn=10
```

### 1.10 从表中随机返回

```SQL
select ename, job from emp order by rand() limit 5;
```

### 1.12 将NULL值转换为实际的值

```SQL
select case when comm is not null then comm else 0 end as comm
from emp;

-- 使用coalesce函数
select coalesce(comm, 0) as comm
from emp;
```

## 2. 查询结果排序

### 2.5 排序时处理NULL值

你想按照 COMM 对来自 EMP 表的查询结果进行排序，但这一列的值可能为 NULL，因此需要指定是否将 COMM 列为 NULL 的行排在最后面。

```SQL
select ename, sal, comm
from emp
order by comm;

/**
+------+----+----+
|ename |sal |comm|
+------+----+----+
|SMITH |800 |null|
|JONES |2975|null|
|BLAKE |2850|null|
|CLARK |2450|null|
|SCOTT |3000|null|
|KING  |5000|null|
|ADAMS |1100|null|
|JAMES |950 |null|
|FORD  |3000|null|
|MILLER|1300|null|
|TURNER|1500|0   |
|ALLEN |1600|300 |
|WARD  |1250|500 |
|MARTIN|1250|1400|
+------+----+----+


**/

-- 先制作一个视图
select ename,
       sal,
       comm,
       case when comm is null then 0 else 1 end as is_null
from emp
order by comm;

select ename,
       sal,
       comm,
       case when comm is null then 0 else 1 end as is_null
from emp
order by is_null desc , comm;
```

```SQL
select ename, sal, comm
from (select ename,
             sal,
             comm,
             case when comm is null then 0 else 1 end as is_null
      from emp) x
order by is_null desc, COMM desc 
```

## 3. 使用多张表

### 3.2 合并相关的行

你想执行基于相同列或相同列值的连接，以返回多张表中的行。例如，你想显示所有部门编号为 10 的员工的姓名以及每位员工所属部门的位置，但这些数据存储在两张表中。

```SQL
select e.ename, d.loc
from emp e
         inner join dept d on e.DEPTNO = d.DEPTNO
where e.DEPTNO = 10;

/*
+------+--------+
|ename |loc     |
+------+--------+
|CLARK |NEW YORK|
|KING  |NEW YORK|
|MILLER|NEW YORK|
+------+--------+

*/
```

### 3.3 查找两张表中相同的行

你想找出两张表中相同的行，但需要连接多列。

```SQL
create view V as
select ename, job, sal
from emp
where job = 'CLERK';

select *
from V;

/*
+------+-----+----+
|ename |job  |sal |
+------+-----+----+
|SMITH |CLERK|800 |
|ADAMS |CLERK|1100|
|JAMES |CLERK|950 |
|MILLER|CLERK|1300|
+------+-----+----+


*/
```

生成笛卡尔积：

```SQL
select * from t_blog cross join t_type;

select * from t_blog inner join t_type;

select * from t_blog, t_type;
```

基于必要的列将表连接起来，以返回正确的结果。

也可以使用集合运算 INTERSECT来返回两张表的交集（两张表中相同的行），这样可以避免执行连接操作。

```SQL
select e.empno, e.ename, e.job, e.sal, e.DEPTNO
from emp e,
     V v
where e.ename = v.ename
  and e.job = v.job
  and e.sal = v.sal;

```

集合运算 INTERSECT 会返回两个数据源中相同的行。使用 INTERSECT 时，必须对两张表中数据类型相同的列进行比较。别忘了，集合运算默认不会返回重复的行。

```SQL
SELECT *
FROM emp
WHERE (ename, job, sal) IN 
    (SELECT ename,
		 job,
		 sal
    FROM emp intersectSELECT ename,
		 job,
		 sal
    FROM V)
```

### 3.4 从一张表中检索没有出现在另一张表中的值

你想找出一张表（源表）中没有出现在目标表中的值。例如，你想找出 DEPT 表中都有哪些部门没有出现在 EMP 表中。

使用集合运算的差集运算：

```SQL
select deptno
from dept
except
select deptno
from emp;
```

使用子查询将 EMP 表中所有的 DEPTNO 都返回给外部查询，而外部查询在 DEPT 表中查找 DEPTO 没有出现在子查询返回结果中的行。

```mysql
select deptno
from dept
where deptno not in (select deptno from emp);

-- null的情况
select 1 not in (4, 2, 3, null)
```

使用not in时，需要注意null值。为了避免 NULL 给 NOT IN 带来的问题，可以结合使用关联子查询和 NOT EXISTS。

```sql
select d.deptno from dept d where not exists(
    select e.deptno from emp e where d.deptno = e.deptno
    )
```

### 3.5 从一张表中检索在另一张表中没有对应行的行

有两张包含相同键的表，你想从一张表中找出在另一张表中没有与之匹配的行。例如，你想确定哪个部门没有员工：

使用外连接并执行基于 NULL 的筛选（关键字 OUTER 是可选的）。

```SQL
select d.*
from dept d
         left outer join emp e on d.DEPTNO = e.DEPTNO
where e.DEPTNO is null

```

## 4. 插入 更新和删除

### 4.5 复制表定义

DB2:

```SQL
create table dept_2 like dept
```

mysql:

```SQL
create table dept_2
as
select *
  from dept
where 1 = 0
```

## 5. 元数据查询

### 5.1 列出某个数据库的所有表

```SQL
select TABLE_SCHEMA, table_name
from information_schema.tables
where TABLE_SCHEMA = 'demo2_basic';

/*
+------------+-------------+
|TABLE_SCHEMA|TABLE_NAME   |
+------------+-------------+
|demo2_basic |dept         |
|demo2_basic |emp          |
|demo2_basic |productsum   |
|demo2_basic |productsumjim|
|demo2_basic |t1           |
|demo2_basic |t10          |
|demo2_basic |t100         |
+------------+-------------+

*/
```

### 5.2 列出表中的列column

信息：information_schema.columns

```SQL
select *
from information_schema.columns
where TABLE_SCHEMA = 'demo2_basic'
  and TABLE_NAME = 'emp';
```

### 5.3 列出表的索引列

```SQL
select *
from information_schema.STATISTICS
where TABLE_SCHEMA like 'demo1%';

show index from emp;
```

### 5.4 列出表的约束

你想列出给表定义的约束以及这些约束是在哪些列上定义的。例如，你想获悉 EMP 表的约束以及这些约束是在哪些列上定义的。

```SQL
select *
from information_schema.TABLE_CONSTRAINTS
where TABLE_SCHEMA like 'demo1%'

-- information_schema.key_column_usage
```

## 6. 处理字符串

