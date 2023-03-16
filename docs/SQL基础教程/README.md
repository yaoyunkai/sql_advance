# SQL基础教程

```SQL
CREATE TABLE Product
(product_id      CHAR(4)      NOT NULL,
 product_name    VARCHAR(100) NOT NULL,
 product_type    VARCHAR(32)  NOT NULL,
 sale_price      INTEGER ,
 purchase_price  INTEGER ,
 regist_date     DATE ,
 PRIMARY KEY (product_id));

INSERT INTO Product VALUES ('0001', 'T恤' ,'衣服', 1000, 500, '2009-09-20');
INSERT INTO Product VALUES ('0002', '打孔器', '办公用品', 500, 320, '2009-09-11');
INSERT INTO Product VALUES ('0003', '运动T恤', '衣服', 4000, 2800, NULL);
INSERT INTO Product VALUES ('0004', '菜刀', '厨房用具', 3000, 2800, '2009-09-20');
INSERT INTO Product VALUES ('0005', '高压锅', '厨房用具', 6800, 5000, '2009-01-15');
INSERT INTO Product VALUES ('0006', '叉子', '厨房用具', 500, NULL, '2009-09-20');
INSERT INTO Product VALUES ('0007', '擦菜板', '厨房用具', 880, 790, '2008-04-28');
INSERT INTO Product VALUES ('0008', '圆珠笔', '办公用品', 100, NULL, '2009-11-11');
```

**查询一个表的相关信息**

```SQL
-- 1. 使用information_schema
SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
FROM information_schema.COLUMNS
WHERE TABLE_NAME = 'mytable';

SELECT COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_NAME = 'mytable' AND CONSTRAINT_NAME = 'PRIMARY';

SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_NAME = 'mytable' AND CONSTRAINT_NAME <> 'PRIMARY' AND REFERENCED_TABLE_NAME IS NOT NULL;

SELECT INDEX_NAME, COLUMN_NAME, NON_UNIQUE
FROM information_schema.STATISTICS
WHERE TABLE_NAME = 'mytable';

-- 2. 一些命令
SHOW TABLE STATUS LIKE 'table_name';

DESCRIBE table_name;

SHOW COLUMNS FROM table_name;

SHOW CREATE TABLE table_name;

SHOW INDEX FROM table_name;

```

## 3. 聚合与排序

```
group by 子句的使用问题:
1 . 在SELECT子句中书写了多余的列
2 . 在GROUP BY子句中写了列的别名
3 . GROUP BY子句结果的显示是无序的
4 . 在WHERE子句中使用聚合函数

having的用法是用来操作分组的。

WHERE 子句 = 指定行所对应的条件
HAVING 子句 = 指定组所对应的条件

聚合键所对应的条件不应该书写在HAVING子句当中，而应该书写在WHERE子句当中

SELECT 子句的执行顺序在 GROUP BY 子句之后，ORDER BY 子句之前。

drop table;
delete from table;
TRUNCATE table;
```

## 5. 复杂查询

### 5.1 视图

优点：

- 无需保存数据：表中存储的是实际数据，而视图中保存的是从表中取出数据所使用的SELECT语句。
- 第二个优点就是可以将频繁使用的 SELECT 语句保存成视图，这样 就不用每次都重新书写了。

```mysql
CREATE VIEW ProductSum (product_type, cnt_product)
AS
SELECT product_type, COUNT(*)
FROM Product
GROUP BY product_type;

select product_type, cnt_product from productsum;

-- 应该避免在视图的基础上创建视图。
CREATE VIEW ProductSumJim (product_type, cnt_product)
AS
SELECT product_type, cnt_product
FROM ProductSum
WHERE product_type = '办公用品';
```

定义视图不能使用 order by 子句。

删除视图：`drop view ProductSum`

### 5.2 子查询

子查询的特点概括起来就是一张一次性视图。

```SQL
select product_type, cnt_product
from (select product_type, count(*) as cnt_product
      from product
      group by product_type) as ProductSum
```

实际上，该 SELECT 语句包含嵌套的结构，首先会执行 FROM 子句 中的 SELECT 语句，然后才会执行外层的SELECT 语句。

```SQL
SELECT product_type, cnt_product
FROM (SELECT *
      FROM (SELECT product_type, COUNT(*) AS cnt_product
            FROM Product
            GROUP BY product_type) AS ProductSum
      WHERE cnt_product = 4) AS ProductSum2;
```

#### 标量子查询 scalar subquery

而标量子查询则有一个特殊的限制，那就是必须而且只能返回 1 行 1 列的结果，也就是返回表中某一行的某一列的值。

- 在where子句中使用标量子查询

查询出销售单价高于平均销售单价的商品。

```SQL
select product_id, product_name, sale_price
from product
where sale_price > (select avg(sale_price) from product)
```

- 在select子句中使用标量子查询

### 5.3 关联子查询

关联子查询会在细分的组内进行比较时使用。

关联子查询和GROUP BY子句一样，也可以对表中的数据进行切分。

关联子查询的结合条件如果未出现在子查询之中就会发生错误。

```SQL
select product_type, product_name, sale_price
from product as p1
where sale_price > (select avg(sale_price)
                    from product as p2
                    where p2.product_type = p1.product_type)
                    -- group by p2.product_type)
```

子查询中实际上可以不需要group by 子句。

在使用关联子查询时，需要在表所 对应的列名之前加上表的别名，以“< 表名 >.< 列名 >”的形式记述。

## 集合运算

### 关系除法

集合运算中的 除法通常称为关系除法。

```
+---+------+
|emp|skill |
+---+------+
|平井 |C++   |
|平井 |Oracle|
|平井 |Perl  |
|平井 |PHP   |
|平井 |UNIX  |
|渡来 |Oracle|
|相田 |C#    |
|相田 |Java  |
|相田 |Oracle|
|相田 |UNIX  |
|神崎 |Java  |
|神崎 |Oracle|
|神崎 |UNIX  |
|若田部|Perl  |
+---+------+

+------+
|skill |
+------+
|Java  |
|Oracle|
|UNIX  |
+------+

```

来思考一下如何从该表中选取出掌握了Skills表中所有3个领域的技术的员工吧，

```SQL
-- 差集为空表示与skills相同，那么not exists 表示全部都掌握了
SELECT DISTINCT emp 
FROM EmpSkills ES1 
WHERE NOT EXISTS (
  SELECT skill 
  FROM Skills 
  EXCEPT 
  SELECT skill 
  FROM EmpSkills ES2 
  WHERE ES1.emp = ES2.emp
);
```

## 窗口函数

