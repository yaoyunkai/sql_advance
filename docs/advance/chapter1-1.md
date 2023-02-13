# CASE 语句的用法

case表达式从SQL92标准引入。

## CASE表达式概述

CASE表达式有简单CASE表达式（simple case expression）和搜索CASE表达式（searched case expression）两种写法

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

