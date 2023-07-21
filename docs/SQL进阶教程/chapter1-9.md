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

```
+----+------+
|seat|status|
+----+------+
|1   |已预订   |
|2   |已预订   |
|3   |未预定   |
|4   |未预定   |
|5   |未预定   |
|6   |已预订   |
|7   |未预定   |
|8   |未预定   |
|9   |未预定   |
|10  |未预定   |
|11  |未预定   |
|12  |已预订   |
|13  |已预订   |
|14  |未预定   |
|15  |未预定   |
+----+------+

```

问题是，从1～15的座位编号中，找出连续3个空位的全部组合。

```mysql
select s1.seat as start_seat, '~', s2.seat as end_start
from seats s1,
     seats s2
where s2.seat = s1.seat + (3 - 1)
  and not exists(
        select * from seats s3 where s3.seat between s1.seat and s2.seat and s3.status <> '未预定'
    )
```

1，通过自连接生成生成长度为3的序列

2，序列内的点要满足状态都是 “未预定”

接下来我们看一下这道例题的升级版，即发生换排的情况。假设这列火车每一排有5个座位。我们在表中加上表示行编号“row_id”列。

```
+----+------+------+
|seat|row_id|status|
+----+------+------+
|1   |A     |已预订   |
|2   |A     |已预订   |
|3   |A     |未预订   |
|4   |A     |未预订   |
|5   |A     |未预订   |
|6   |B     |已预订   |
|7   |B     |已预订   |
|8   |B     |未预订   |
|9   |B     |未预订   |
|10  |B     |未预订   |
|11  |C     |未预订   |
|12  |C     |未预订   |
|13  |C     |未预订   |
|14  |C     |已预订   |
|15  |C     |未预订   |
+----+------+------+

```

更新描述起点到终点之间所有的点需要满足的条件

```mysql
select s1.seat as start_seat, '~', s2.seat as end_start
from seats2 s1,
     seats2 s2
where s2.seat = s1.seat + (3 - 1)
  and not exists(
        select *
        from seats2 s3
        where s3.seat between s1.seat and s2.seat and (s3.status <> '未预订' or s3.row_id <> s1.row_id)
    )
```

接下来的例题和上一道刚好相反。这次要查询的是“按现在的空位状况，最多能坐下多少人”。换句话说，要求的是最长的序列。我们使用下面这张表Seats3。

```
+----+------+
|seat|status|
+----+------+
|1   |已预订   |
|2   |未预定   |
|3   |未预定   |
|4   |未预定   |
|5   |未预定   |
|6   |已预订   |
|7   |未预定   |
|8   |已预订   |
|9   |未预定   |
|10  |未预定   |
+----+------+

```

为了便于解答这道例题，我们可以先生成一张存储了所有可能序列的视图。有了这个视图之后，我们只需从中查找出最长的序列就可以了。

```mysql
/* 第一阶段：生成存储了所有序列的视图 */
CREATE VIEW Sequences (start_seat, end_seat, seat_cnt) AS
SELECT S1.seat               AS start_seat,
       S2.seat               AS end_seat,
       S2.seat - S1.seat + 1 AS seat_cnt
FROM Seats3 S1,
     Seats3 S2
WHERE S1.seat <= S2.seat /* 第一步：生成起点和终点的组合 */
  AND NOT EXISTS /* 第二步：描述序列内所有点需要满足的条件 */
    (SELECT *
     FROM Seats3 S3
     WHERE (S3.seat BETWEEN S1.seat AND S2.seat
         AND S3.status <> '未预订') /* 条件1的否定 */
        OR (S3.seat = S2.seat + 1 AND S3.status = '未预订') /* 条件2的否定 */
        OR (S3.seat = S1.seat - 1 AND S3.status = '未预订')); /* 条件3的否定 */

```

从这个视图中找出座位数（seat_cnt）最大的一行数据。

```mysql
SELECT start_seat, '~', end_seat, seat_cnt
FROM Sequences
WHERE seat_cnt = (SELECT MAX(seat_cnt) FROM Sequences);
```

## 单调递增和单调递减

假设存在下面这样一张反映了某公司股价动态的表。

```
+----------+-----+
|deal_date |price|
+----------+-----+
|2007-01-06|1000 |
|2007-01-08|1050 |
|2007-01-09|1050 |
|2007-01-12|900  |
|2007-01-13|880  |
|2007-01-14|870  |
|2007-01-16|920  |
|2007-01-17|1000 |
+----------+-----+

```

我们求一下股价单调递增的时间区间

```mysql
-- 先生成日期区间
select s1.deal_date as start_date, s2.deal_date as end_date
from mystock s1,
     mystock s2
where s1.deal_date < s2.deal_date;


select s1.deal_date as start_date, s2.deal_date as end_date
from mystock s1,
     mystock s2
where s1.deal_date < s2.deal_date
  and not exists(
        select *
        from mystock s3,
             mystock s4
        where s3.deal_date between s1.deal_date and s2.deal_date
          and s4.deal_date between s1.deal_date and s2.deal_date
          and s3.deal_date < s4.deal_date
          and s3.price >= s4.price
    );


```

## 小结

1．SQL处理数据的方法有两种。

2．第一种是把数据看成忽略了顺序的集合。

3．第二种是把数据看成有序的集合，此时的基本方法如下。

- a．首先用自连接生成起点和终点的组合
- b．其次在子查询中描述内部的各个元素之间必须满足的关系

4．要在SQL中表达全称量化时，需要将全称量化命题转换成存在量化命题的否定形式，并使用NOT EXISTS谓词。这是因为SQL只实现了谓词逻辑中的存在量词。

