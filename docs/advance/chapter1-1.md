# CASE 语句的用法

case表达式从SQL92标准引入。

## CASE表达式概述

CASE表达式有简单CASE表达式（simple case expression）和搜索CASE表达式（searched case expression）两种写法.

> TODO: 简单case和搜索case的区别???

```sql
--简单CASE表达式
CASE sex
  WHEN '1' THEN ’男’
  WHEN '2' THEN ’女’
ELSE ’其他’ END

--搜索CASE表达式
CASE WHEN sex ='1'THEN’男’
    WHEN sex ='2'THEN’女’
ELSE ’其他’ END
```

在编写SQL语句的时候需要注意，在发现为真的WHEN子句时，CASE表达式的真假值判断就会中止，而剩余的WHEN子句会被忽略。

使用CASE时需要注意：

- 任何分支的返回类型需要统一。
- 不要忘记写 `END`
- 与END不同，ELSE子句是可选的，不写也不会出错。不写ELSE子句时，CASE表达式的执行结果是NULL。

## 将已有编号方式转换为新的方式并统计

在进行非定制化统计时，我们经常会遇到将已有编号方式转换为另外一种便于分析的方式并进行统计的需求。

demo1, 例如现在有一张表要转换为按各个地区的方式来统计：

```
+---------+----------+
|pref_name|population|
+---------+----------+
|东京       |400       |
|佐贺       |100       |
|德岛       |100       |
|爱媛       |150       |
|福冈       |300       |
|群马       |50        |
|长崎       |200       |
|香川       |200       |
|高知       |200       |
+---------+----------+

table name: PopTbl
```

```
+--------+---------------+
|district|SUM(population)|
+--------+---------------+
|其他      |450            |
|九州      |600            |
|四国      |650            |
+--------+---------------+
```

使用CASE语句，将县名的条件按地区来区分：

```SQL
SELECT 
    CASE pref_name
        WHEN '德岛' THEN '四国'
        WHEN '香川' THEN '四国'
        WHEN '爱媛' THEN '四国'
        WHEN '高知' THEN '四国'
        WHEN '福冈' THEN '九州'
        WHEN '佐贺' THEN '九州'
        WHEN '长崎' THEN '九州'
        ELSE '其他'
    END AS district,
    SUM(population)
FROM
    poptbl
GROUP BY CASE pref_name
    WHEN '德岛' THEN '四国'
    WHEN '香川' THEN '四国'
    WHEN '爱媛' THEN '四国'
    WHEN '高知' THEN '四国'
    WHEN '福冈' THEN '九州'
    WHEN '佐贺' THEN '九州'
    WHEN '长崎' THEN '九州'
    ELSE '其他'
END;
```

这里的关键在于将SELECT子句里的CASE表达式复制到GROUP BY子句里。需要注意的是，如果对转换前的列“pref_name”进行GROUP BY，就得不到正确的结果（因为这并不会引起语法错误，所以容易被忽视）。

demo2, 也可以按人口数量等级来进行区分：

```SQL
SELECT 
    CASE
        WHEN population < 100 THEN '01'
        WHEN population >= 100 AND population < 200 THEN '02'
        WHEN population >= 200 AND population < 300 THEN '03'
        WHEN population >= 300 THEN '04'
        ELSE NULL
    END AS pop_class,
    COUNT(*) AS cnt
FROM
    poptbl
GROUP BY CASE
    WHEN population < 100 THEN '01'
    WHEN population >= 100 AND population < 200 THEN '02'
    WHEN population >= 200 AND population < 300 THEN '03'
    WHEN population >= 300 THEN '04'
    ELSE NULL
END;
```

在这两个SQL中，我们的GROUP BY 的写法必须和CASE的写法一样，但是在MySQL和postgresql中可以用如下写法(非标准SQL)：

但是严格来说，这种写法是违反标准SQL的规则的。因为GROUP BY子句比SELECT语句先执行，所以在GROUP BY子句中引用在SELECT子句里定义的别称是不被允许的。

![image-20230214163755880](.assets/image-20230214163755880.png)

```mysql
SELECT 
    CASE
        WHEN population < 100 THEN '01: 小于100'
        WHEN population >= 100 AND population < 200 THEN '02: 在100到200之间'
        WHEN population >= 200 AND population < 300 THEN '03: 在200到300之间'
        WHEN population >= 300 THEN '04: 大于等于300'
        ELSE NULL
    END AS pop_class,
    COUNT(*) AS cnt
FROM
    PopTbl
GROUP BY pop_class
```

## 用一条SQL语句进行不同条件的统计

例如，我们需要往存储各县人口数量的表PopTbl里添加上“性别”列，然后求按性别、县名汇总的人数。

```
+---------+---+----------+
|pref_name|sex|population|
+---------+---+----------+
|东京       |1  |250       |
|东京       |2  |150       |
|佐贺       |1  |20        |
|佐贺       |2  |80        |
|德岛       |1  |60        |
|德岛       |2  |40        |
|爱媛       |1  |100       |
|爱媛       |2  |50        |
|福冈       |1  |100       |
|福冈       |2  |200       |
|长崎       |1  |125       |
|长崎       |2  |125       |
|香川       |1  |100       |
|香川       |2  |100       |
|高知       |1  |100       |
|高知       |2  |100       |
+---------+---+----------+

tablename: poptbl2
```

```
+---------+-------+---------+
|pref_name|Man Pop|Women Pop|
+---------+-------+---------+
|东京       |250    |150      |
|佐贺       |20     |80       |
|德岛       |60     |40       |
|爱媛       |100    |50       |
|福冈       |100    |200      |
|长崎       |125    |125      |
|香川       |100    |100      |
|高知       |100    |100      |
+---------+-------+---------+
```

使用case表达式和聚合函数来使用：

```SQL
SELECT 
    pref_name,
    SUM(CASE
        WHEN sex = '1' THEN population
        ELSE 0
    END) AS 'Man Pop',
    SUM(CASE
        WHEN sex = '2' THEN population
        ELSE 0
    END) AS 'Women Pop'
FROM
    poptbl2
GROUP BY pref_name
```

这里是将“行结构”的数据转换成了“列结构”的数据。除了SUM, COUNT、AVG等聚合函数也都可以用于将行结构的数据转换成列结构的数据。

这个技巧可贵的地方在于，它能将SQL的查询结果转换为二维表的格式。

新手用WHERE子句进行条件分支，高手用**SELECT子句**进行条件分支。

