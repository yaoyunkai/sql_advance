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

