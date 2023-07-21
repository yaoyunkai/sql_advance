# 1-10 having子句

## 各队，全体点名

你需要做的是查出现在可以出勤的队伍。

```
+------+-------+------+
|member|team_id|status|
+------+-------+------+
|乔     |1      |待命    |
|凯斯    |2      |休息    |
|卡伦    |2      |出勤中   |
|卡根    |5      |待命    |
|哈特    |3      |待命    |
|简     |3      |待命    |
|米克    |1      |待命    |
|罗伯特   |5      |休息    |
|肯     |1      |出勤中   |
|贝斯    |4      |待命    |
|迪克    |3      |待命    |
|阿伦    |5      |出勤中   |
+------+-------+------+

```

你需要做的是查出现在可以出勤的队伍。可以出勤即队伍里所有队员都处于“待命”状态。

```mysql
select team_id, member
from teams t1
where not exists(
        select * from teams t2 where t1.team_id = t2.team_id and t2.status <> '待命'
    )

```

还可以使用having子句来进行查询：

```mysql
select team_id
from teams
group by team_id
having count(*) = sum(case when status = '待命' then 1 else 0 end);

select team_id
from teams
group by team_id
having count(*) = sum(IF(status = '待命', 1, 0));
```

HAVING子句中的条件还可以像下面这样写。

```mysql
SELECT team_id
FROM Teams
GROUP BY team_id
HAVING MAX(status) = '待命'
   AND MIN(status) = '待命';
```

如果元素最大值和最小值相等，那么这个集合中肯定只有一种值。因为如果包含多种值，最大值和最小值肯定不会相等。极值函数可以使用参数字段的索引，所以这种写法性能更好。

```mysql
SELECT team_id,
       IF(MAX(status) = '待命' AND MIN(status) = '待命', '全都在待命', '队长！人手不够') AS status
FROM Teams
GROUP BY team_id;
```

## 单重集合与多重集合

在1-7节中我们也说过，关系数据库中的集合是允许重复数据存在的多重集合。与之相反，通常意义的集合论中的集合不允许数据重复，被称为“单重集合”

```
+------+------------+--------+
|center|receive_date|material|
+------+------------+--------+
|东京    |2007-04-01  |锡       |
|东京    |2007-04-12  |锌       |
|东京    |2007-05-17  |铝       |
|东京    |2007-05-20  |锌       |
|名古屋   |2007-03-15  |钛       |
|名古屋   |2007-04-01  |钢       |
|名古屋   |2007-04-24  |钢       |
|名古屋   |2007-05-02  |镁       |
|名古屋   |2007-05-10  |钛       |
|大阪    |2007-04-20  |铜       |
|大阪    |2007-04-22  |镍       |
|大阪    |2007-04-29  |铅       |
|福冈    |2007-05-10  |锌       |
|福冈    |2007-05-28  |锡       |
+------+------------+--------+

```

调查出存在重复材料的生产地。

从表中我们可以看到，一个生产地对应着多条数据，因此“生产地”这一实体在表中是以集合的形式，而不是以元素的形式存在的。处理这种情况的基本方法就是使用GROUP BY子句将集合划分为若干个子集

```mysql
select center
from materials
group by center
having count(material) <> count(distinct material); -- 重复的和不重复的数量不一样
```

在数学中，通过GROUP BY生成的子集有一个对应的名字，叫作划分（partition）。

它是集合论和群论中的重要概念，指的是将某个集合按照某种规则进行分割后得到的子集。这些子集相互之间没有重复的元素，而且它们的并集就是原来的集合。这样的分割操作被称为划分操作。

顺便说一下，这个问题也可以通过将HAVING改写成EXISTS的方式来解决。

```mysql
select center, material
from materials s1
where exists(
              select *
              from materials s2
              where s1.center = s2.center
                and s1.receive_date <> s2.receive_date
                and s1.material = s2.material
          );
```

## 寻找缺失的编号

```mysql
-- 如果有查询结果，说明存在缺失的编号：只调查数列的连续性
SELECT '存在缺失的编号' AS gap
  FROM SeqTbl
HAVING COUNT(*) <> MAX(seq) - MIN(seq) + 1 ;
```

## 为集合设置详细的条件

这里以下面这张记录了学生考试成绩的表为例进行讲解。

```
+-------+-----+---+-----+
|student|class|sex|score|
+-------+-----+---+-----+
|001    |A    |男  |100  |
|002    |A    |女  |100  |
|003    |A    |女  |49   |
|004    |A    |男  |30   |
|005    |B    |女  |100  |
|006    |B    |男  |92   |
|007    |B    |男  |80   |
|008    |B    |男  |80   |
|009    |B    |女  |10   |
|010    |C    |男  |92   |
|011    |C    |男  |80   |
|012    |C    |女  |21   |
|013    |D    |女  |100  |
|014    |D    |女  |0    |
|015    |D    |女  |0    |
+-------+-----+---+-----+

```

第1题：请查询出75%以上的学生分数都在80分以上的班级。

```mysql
select class
from testresults
group by class
having count(*) * 0.75 <= sum(case when score >= 80 then 1 else 0 end);
```

第2题：请查询出分数在50分以上的男生的人数比分数在50分以上的女生的人数多的班级。

```mysql
select class
from testresults
group by class
having sum(case when sex = '男' and score > 50 then 1 else 0 end) >
       sum(case when sex = '女' and score > 50 then 1 else 0 end);
```

第3题：请查询出女生平均分比男生平均分高的班级。

```mysql
select class
from testresults
group by class
having avg(case when sex = '女' then score else 0 end) > avg(case when sex = '男' then score else 0 end);
```

从表中的数据我们可以发现，D班全是女生。在上面的解答中，用于判断男生的CASE表达式里分支ELSE 0生效了，于是男生的平均分就成了0分。对于女生的平均分约为33.3的D班，条件0 < 33.3也成立，所以D班也出现在查询结果里了。

这种处理方法看起来好像也没什么问题。但是，如果学号013的学生分数刚好也是0分，结果会怎么样呢？这种情况下，女生的平均分会变为0分，所以D班不会被查询出来。

```mysql
select class
from testresults
group by class
having avg(IF(sex = '女', score, NULL)) > avg(IF(sex = '男', score, NULL));
```

## 小结

