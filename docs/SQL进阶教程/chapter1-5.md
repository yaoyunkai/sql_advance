# 1-5 外连接的用法

> TODO: SQL IF的使用

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



## 在交叉表里制作嵌套式表侧栏

表TblPop是一张按照县、年龄层级和性别统计的人口分布表，要求根据表TblPop生成交叉表“包含嵌套式表侧栏的统计表”:

```
年龄层级表: 
+---------+---------+
|age_class|age_range|
+---------+---------+
|1        |21岁～30岁  |
|2        |31岁～40岁  |
|3        |41岁～50岁  |
+---------+---------+

性别表：
+------+---+
|sex_cd|sex|
+------+---+
|f     |女  |
|m     |男  |
+------+---+

人口分布表: 
+---------+---------+------+----------+
|pref_name|age_class|sex_cd|population|
+---------+---------+------+----------+
|东京       |1        |f     |1500      |
|东京       |1        |m     |900       |
|东京       |3        |f     |1200      |
|千叶       |1        |f     |1000      |
|千叶       |1        |m     |900       |
|千叶       |3        |f     |900       |
|秋田       |1        |f     |800       |
|秋田       |1        |m     |400       |
|秋田       |3        |f     |1000      |
|秋田       |3        |m     |1000      |
|青森       |1        |f     |500       |
|青森       |1        |m     |700       |
|青森       |3        |f     |800       |
+---------+---------+------+----------+

```

这个问题的要点在于，虽然表TblPop中没有一条年龄层级为2的数据，但是返回结果还是要包含这个年龄层级，固定输出6行.

目标表的侧栏是年龄层级和性别，所以我们需要使用表TblAge和表TblSex作为主表。

```SQL
-- 先将原始的数据表分组
select age_class,
       sex_cd,
       SUM(IF(pref_name IN ('青森', '秋田'), population, NULL)) AS pop_tohoku,
       SUM(IF(pref_name IN ('东京', '千叶'), population, NULL)) AS pop_kanto
from tblpop
group by age_class, sex_cd;

SELECT MASTER1.age_class AS age_class,
       MASTER2.sex_cd    AS sex_cd,
       DATA.pop_tohoku   AS pop_tohoku,
       DATA.pop_kanto    AS pop_kanto
FROM (SELECT age_class,
             sex_cd,
             SUM(IF(pref_name IN ('青森', '秋田'), population, NULL)) AS pop_tohoku,
             SUM(IF(pref_name IN ('东京', '千叶'), population, NULL)) AS pop_kanto
      FROM TblPop
      GROUP BY age_class, sex_cd) DATA
         RIGHT OUTER JOIN TblAge MASTER1
                          ON MASTER1.age_class = DATA.age_class
         RIGHT OUTER JOIN TblSex MASTER2
                          ON MASTER2.sex_cd = DATA.sex_cd;
```

实际上，与年龄层级主表外连接之后，结果里是包含年龄层级为2的数据的：

```SQL
SELECT MASTER1.age_class AS age_class,
       DATA.age_class    as data_age_class,
       DATA.sex_cd       AS sex_cd,
       DATA.pop_tohoku   AS pop_tohoku,
       DATA.pop_kanto    AS pop_kanto
FROM (SELECT age_class,
             sex_cd,
             SUM(IF(pref_name IN ('青森', '秋田'), population, NULL)) AS pop_tohoku,
             SUM(IF(pref_name IN ('东京', '千叶'), population, NULL)) AS pop_kanto

      FROM TblPop
      GROUP BY age_class, sex_cd) DATA
         RIGHT OUTER JOIN TblAge MASTER1
                          ON MASTER1.age_class = DATA.age_class;

/*
+---------+--------------+------+----------+---------+
|age_class|data_age_class|sex_cd|pop_tohoku|pop_kanto|
+---------+--------------+------+----------+---------+
|1        |1             |f     |1300      |2500     |
|1        |1             |m     |1100      |1800     |
|2        |null          |null  |null      |null     |
|3        |3             |f     |1800      |2100     |
|3        |3             |m     |1000      |null     |
+---------+--------------+------+----------+---------+

*/
```

核心点在这里：虽然年龄层级2确实可以通过外连接从表TblAge获取，但是在表TblPop里，与之相应的“性别编号”列却是NULL。原因也不难理解。表TblPop里本来就没有年龄层级为2的数据，自然也没有相应的性别信息m或f，于是“性别编号”列只能是NULL。因此与性别主表进行外连接时，连接条件会变成ON MASTER2.sex_cd =NULL，结果是unknown（这个真值的意思请参考1-3节）。因此，最终结果里永远不会出现年龄层级为2的数据，即使改变两次外连接的先后顺序，结果也还是一样的。

```SQL
SELECT MASTER.age_class AS age_class,
       MASTER.sex_cd    AS sex_cd,
       DATA.pop_tohoku  AS pop_tohoku,
       DATA.pop_kanto   AS pop_kanto
FROM (SELECT age_class, sex_cd
      FROM TblAge
               CROSS JOIN TblSex) MASTER -- 使用交叉表生成笛卡尔积
         LEFT OUTER JOIN
     (SELECT age_class,
             sex_cd,
             SUM(IF(pref_name IN ('青森', '秋田'), population, NULL)) AS pop_tohoku,
             SUM(IF(pref_name IN ('东京', '千叶'), population, NULL)) AS pop_kanto
      FROM TblPop
      GROUP BY age_class, sex_cd) DATA
     ON MASTER.age_class = DATA.age_class
         AND MASTER.sex_cd = DATA.sex_cd;

select * from tblage cross join tblsex;
/*
+---------+---------+------+---+
|age_class|age_range|sex_cd|sex|
+---------+---------+------+---+
|1        |21岁～30岁  |f     |女  |
|1        |21岁～30岁  |m     |男  |
|2        |31岁～40岁  |f     |女  |
|2        |31岁～40岁  |m     |男  |
|3        |41岁～50岁  |f     |女  |
|3        |41岁～50岁  |m     |男  |
+---------+---------+------+---+
*/
```

## 作为乘法运算的连接

TO: [1-4节的专栏“关系除法运算”](./chapter1-4.md)

接下来，我们将以下面的商品主表和商品销售历史管理表为例:

```
+-------+----+
|item_no|item|
+-------+----+
|10     |FD  |
|20     |CD-R|
|30     |MO  |
|40     |DVD |
+-------+----+

+----------+-------+--------+
|sale_date |item_no|quantity|
+----------+-------+--------+
|2007-10-01|10     |4       |
|2007-10-01|20     |10      |
|2007-10-01|30     |3       |
|2007-10-03|10     |32      |
|2007-10-03|30     |12      |
|2007-10-04|20     |22      |
|2007-10-04|30     |7       |
+----------+-------+--------+

```

先使用这两张表生成一张统计表，以商品为单位汇总出各自的销量。

```sql
SELECT I.item_no, SH.total_qty
FROM Items I
         LEFT OUTER JOIN
     (SELECT item_no, SUM(quantity) AS total_qty
      FROM SalesHistory
      GROUP BY item_no) SH
     ON I.item_no = SH.item_no;
     
/*
+-------+--------+
|item_no|quantity|
+-------+--------+
|10     |36      |
|20     |32      |
|30     |22      |
|40     |null    |
+-------+--------+
*/
```

这条语句首先在连接前按商品编号对销售记录表进行聚合，进而生成了一张以item_no为主键的临时视图。接下来，通过“item_no”列对商品主表和这个视图进行连接操作后，商品主表和临时视图就成为了在主键上进行的一对一连接。

但是，如果从性能角度考虑，这条SQL语句还是有些问题的。比如临时视图SH的数据需要临时存储在内存里，还有就是虽然通过聚合将item_no变成了主键，但是SH上却不存在主键索引，因此我们也就无法利用索引优化查询。

要改善这个查询，关键在于导入“把连接看作乘法运算”这种视点。商品主表Items和视图SH确实是一对一的关系，但其实从“item_no”列看，表Items和表SalesHistory是一对多的关系。而且，当连接操作的双方是一对多关系时，结果的行数并不会增加。这就像普通乘法里任意数乘以1后，结果不会变化一样。

```SQL
-- 解答(2)：先进行一对多的连接再聚合
SELECT I.item_no, SUM(SH.quantity) AS total_qty
FROM Items I LEFT OUTER JOIN SalesHistory SH ON I.item_no = SH.item_no
GROUP BY I.item_no;
```

如果表Items里的“items_no”列内存在重复行，就属于多对多连接了，因而这种做法就不能再使用。这时，需要先把某张表聚合一下，使两张表变成一对多的关系.

一对一或一对多关系的两个集合，在进行连接操作后行数不会（异常地）增加。

这个技巧在需要使用连接和聚合来解决问题时非常有用，请熟练掌握。

## 全外连接

本节的前半部分主要从应用的角度介绍了外连接的一些内容。后半部分将换个角度，从面向集合的角度介绍一下外连接本身的一些性质。

标准SQL的三种外连接：

- left outer join
- full outer join
- right outer join

## 用外连接进行集合运算

前面介绍了交集和并集，下面来介绍一下差集的求法。注意一下前面有关全外连接的例题会发现，伊集院在A班里存在而在B班里不存在，“B_name”列的值是NULL；相反，西园寺在B班里存在而在A班里不存在，“A_name”列的值是NULL。于是，我们可以通过判断连接后的相关字段是否为NULL来求得差集。

### 用外连接求差集：A－B

```SQL
SELECT A.id AS id, A.name AS A_name
FROM Class_A A
         LEFT OUTER JOIN Class_B B
                         ON A.id = B.id
WHERE B.name IS NULL;
```

### 用外连接求差集：B－A

```SQL
SELECT B.id AS id, B.name AS B_name
FROM Class_A A
         RIGHT OUTER JOIN Class_B B
                          ON A.id = B.id
WHERE A.name IS NULL;
```

对于不支持差集运算的数据库来说，这也可以作为NOT IN和NOT EXISTS之外的另一种解法，而且它可能是差集运算中效率最高的，这也是它的优点。

### 用全外连接求异或集

接下来我们考虑一下如何求两个集合的异或集。SQL没有定义求异或集的运算符，如果用集合运算符，可以有两种方法。一种是(A UNION B) EXCEPT (A INTERSECT B)，另一种是(A EXCEPT B) UNION (B EXCEPT A)。两种方法都比较麻烦，性能开销也会增大。

```SQL
SELECT COALESCE(A.id, B.id) AS id,
      COALESCE(A.name , B.name ) AS name
  FROM Class_A  A  FULL OUTER JOIN Class_B  B
    ON A.id = B.id
 WHERE A.name IS NULL
    OR B.name IS NULL;
```

## 小结

OUTER也是可以省略的，所以我们也可以写成LEFT JOIN和FULL JOIN（标准SQL也是允许的）。但是为了区分是内连接和外连接，最好还是写上。

1．SQL不是用来生成报表的语言，所以不建议用它来进行格式转换。

2．必要时考虑用外连接或CASE表达式来解决问题。

3．生成嵌套式表侧栏时，如果先生成主表的笛卡儿积再进行连接，很容易就可以完成。

4．从行数来看，表连接可以看成乘法。因此，当表之间是一对多的关系时，连接后行数不会增加。

5．外连接的思想和集合运算很像，使用外连接可以实现各种集合运算。

## 练习题

### 1-5-1 先连接还是先聚合

在“在交叉表里制作嵌套式表侧栏”部分里，我们通过聚合将DATA视图和MASTER视图转换为一对一的关系之后进行了连接操作。采用这种做法时，代码的确比较好理解，但是这就需要创建两个临时视图，性能并不是很好。请想办法改善一下代码，尽量减少临时视图。

```SQL
SELECT MASTER.age_class                                         AS age_class,
       MASTER.sex_cd                                            AS sex_cd,
       SUM(IF(pref_name IN ('青森', '秋田'), population, NULL)) AS pop_tohoku,
       SUM(IF(pref_name IN ('东京', '千叶'), population, NULL)) AS pop_kanto
FROM (SELECT age_class, sex_cd
      FROM TblAge
               CROSS JOIN TblSex) MASTER
         LEFT OUTER JOIN TblPop DATA /* 关键在于理解DATA其实就是TblPop */
                         ON MASTER.age_class = DATA.age_class
                             AND MASTER.sex_cd = DATA.sex_cd
GROUP BY MASTER.age_class, MASTER.sex_cd;
```
