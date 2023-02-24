# 1-5 外连接的用法

## 用外连接进行行列转换(1)（行→列）：制作交叉表

例如，这里有一张用于管理员工学习过的培训课程的表，如下所示。

```
+----+------+
|name|course|
+----+------+
|吉田  |UNIX基础|
|工藤  |Java中级|
|工藤  |SQL入门 |
|渡边  |SQL入门 |
|赤井  |SQL入门 |
|赤井  |UNIX基础|
|铃木  |SQL入门 |
+----+------+

```

首先让我们利用上面这张表生成下面这样一张交叉表（“课程学习记录一览表”）:

```SQL
SELECT C0.name as c0_name, c1.name as c1_name, c2.name as c2_name, c3.name as c3_name
FROM (SELECT DISTINCT name FROM Courses) C0
         left outer join (select name from courses where course = 'SQL入门') c1 on c0.name = c1.name
         left outer join (select name from courses where course = 'UNIX基础') c2 on c0.name = c2.name
         left outer join (select name from courses where course = 'Java中级') c3 on c0.name = c3.name;
         
/*
c0: 所有不重复名字的集合
c1: 所有course为 `SQL入门`的name集合
c2: ...

+-------+-------+-------+-------+
|c0_name|c1_name|c2_name|c3_name|
+-------+-------+-------+-------+
|吉田     |null   |吉田     |null   |
|工藤     |工藤     |null   |工藤     |
|渡边     |渡边     |null   |null   |
|赤井     |赤井     |赤井     |null   |
|铃木     |铃木     |null   |null   |
+-------+-------+-------+-------+

*/

SELECT C0.name,
       CASE WHEN C1.name IS NOT NULL THEN '○' ELSE NULL END AS "SQL入门",
       CASE WHEN C2.name IS NOT NULL THEN '○' ELSE NULL END AS "UNIX基础",
       CASE WHEN C3.name IS NOT NULL THEN '○' ELSE NULL END AS "Java中级"
  FROM  (SELECT DISTINCT name FROM  Courses) C0
    LEFT OUTER JOIN
    (SELECT name FROM Courses WHERE course = 'SQL入门' ) C1
    ON  C0.name = C1.name
      LEFT OUTER JOIN
        (SELECT name FROM Courses WHERE course = 'UNIX基础' ) C2
        ON  C0.name = C2.name
          LEFT OUTER JOIN
            (SELECT name FROM Courses WHERE course = 'Java中级' ) C3
            ON  C0.name = C3.name;

/*
使用子查询，根据源表Courses生成C0～C3这4个子集。

*/
```

使用子查询，根据源表Courses生成C0～C3这4个子集。

因为目标表格的表头是3列，所以进行了3次外连接。列数增加时原理也是一样的，只需要增加外连接操作就可以了。想生成置换了表头和表侧栏的交叉表时，我们也可以用同样的思路。这种做法具有比较直观和易于理解的优点，但是因为大量用到了内嵌视图和连接操作，代码会显得很臃肿。而且，随着表头列数的增加，性能也会恶化。

一般情况下，外连接都可以用标量子查询替代，因此可以像下面这样写：

```SQL
/* 水平展开（2）：使用标量子查询 */
SELECT C0.name,
       (SELECT 'o'
        FROM Courses C1
        WHERE course = 'SQL入门'
          AND C1.name = C0.name) AS "SQL入门",
       (SELECT 'o'
        FROM Courses C2
        WHERE course = 'UNIX基础'
          AND C2.name = C0.name) AS "UNIX基础",
       (SELECT 'o'
        FROM Courses C3
        WHERE course = 'Java中级'
          AND C3.name = C0.name) AS "Java中级"
FROM (SELECT DISTINCT name FROM Courses) C0;
```

接下来介绍第三种方法，即嵌套使用CASE表达式：

```SQL
/* 水平展开（3）：嵌套使用CASE表达式 */
SELECT  name,
        CASE WHEN SUM(CASE WHEN course = 'SQL入门' THEN 1 ELSE NULL END) >= 1
             THEN 'o' ELSE NULL END AS "SQL入门",
        CASE WHEN SUM(CASE WHEN course = 'UNIX基础' THEN 1 ELSE NULL END) >= 1
             THEN 'o' ELSE NULL END AS "UNIX基础",
        CASE WHEN SUM(CASE WHEN course = 'Java中级' THEN 1 ELSE NULL END) >= 1
             THEN 'o' ELSE NULL END AS "Java中级"
  FROM Courses
 GROUP BY name;
 
/*
group by 将 courses 分成多个子集，然后按每种course求和


*/
```

如果不使用聚合，那么返回结果的行数会是表Courses的行数，所以这里以参加培训课程的员工为单位进行聚合。关于将聚合函数的返回值用于条件判断的写法，如果大家不习惯，可能会有点疑惑。但是，其实在SELECT子句里，聚合函数的执行结果也是标量值，因此可以像常量和普通列一样使用。

## 用外连接进行行列转换(2)（列→行）：汇总重复项于一列

......

## 在交叉表里制作嵌套式表侧栏

