# 1-9 SQL 处理数列

关系模型的数据结构里，并没有“顺序”这一概念。因此，基于它实现的关系数据库中的表和视图的行和列也必然没有顺序。同样地，处理有序集合也并非SQL的直接用途。

## 生成连续编号

如果把数看成字符串，其实它就是由各个数位上的数字组成的集合。

那么可以先创建一个0-9的数字表：

```
+-----+
|digit|
+-----+
|0    |
|1    |
|2    |
|3    |
|4    |
|5    |
|6    |
|7    |
|8    |
|9    |
+-----+

```

可以通过对两个Digits集合求笛卡儿积而得出0～99的数字：

```mysql
select d1.digit + (d2.digit * 10) as 'number'
from digits d1
         cross join digits d2
order by 'number';
```

生成1-542的序列：

```MySQL
SELECT D1.digit + (D2.digit * 10) + (D3.digit * 100) AS seq
FROM Digits D1,
     Digits D2,
     Digits D3
WHERE D1.digit + (D2.digit * 10) + (D3.digit * 100) BETWEEN 1 AND 542
ORDER BY seq;
```

将这个解法和本书多次介绍过的冯·诺依曼型有序数的定义进行比较，可以很容易发现它们的区别。冯·诺依曼的方法使用递归集合定义自然数，先定义0然后得到1，定义1然后得到2，是有先后顺序的（因此这种方法适用于解决位次、累计值等与顺序相关的问题）。

通过将这个查询的结果存储在视图里，就可以在需要连续编号时通过简单的SELECT来获取需要的编号。

```MySQL
CREATE VIEW Sequence (seq)
AS SELECT D1.digit + (D2.digit * 10) + (D3.digit * 100)
     FROM Digits D1, Digits D2, Digits D3;

SELECT seq
  FROM Sequence
 WHERE seq BETWEEN 1 AND 100
ORDER BY seq;
```

## 求全部的缺失编号

如果使用前一道例题里的序列视图，很容易就可以满足上面的要求。因为我们可以任意地生成0～n的自然数集合，所以只需要和比较的对象表进行差集运算就可以了。

```
+---+
|seq|
+---+
|1  |
|2  |
|4  |
|5  |
|6  |
|7  |
|8  |
|11 |
|12 |
+---+

```

解答如下：

```mysql
select seq
from sequence
where seq between 1 and 12
  and seq not in (select seq from seqtbl);

-- 差集
SELECT seq
  FROM Sequence
 WHERE seq BETWEEN 1 AND 12
EXCEPT
SELECT seq FROM SeqTbl;
```

但是通过扩展BETWEEN谓词的参数，我们可以动态地指定目标表的最大值和最小值。

```MySQL
/* 动态地指定连续编号范围的SQL语句 */
SELECT seq
  FROM Sequence
 WHERE seq BETWEEN (SELECT MIN(seq) FROM SeqTbl)
               AND (SELECT MAX(seq) FROM SeqTbl)
EXCEPT
SELECT seq FROM SeqTbl;
```

## 车票相关问题

假设存在下面这样一张存储了火车座位预订情况的表。

