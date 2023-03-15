group by 子句的使用问题:
1 . 在SELECT子句中书写了多余的列
2 . 在GROUP BY子句中写了列的别名
3 . GROUP BY子句结果的显示是无序的
4 . 在WHERE子句中使用聚合函数

having:

WHERE 子句 = 指定行所对应的条件
HAVING 子句 = 指定组所对应的条件

聚合键所对应的条件不应该书写在HAVING子句当中，而应该书写在WHERE子句当中

SELECT 子句的执行顺序在 GROUP BY 子句之后，ORDER BY 子句之前。

drop table;
delete from table;
TRUNCATE table;