# Commons

## SQL 字面量

单引号 双引号 以及 反引号的作用

String 类型的字面量

Int 

DATE DATETIME TIMESTAMP

```sql
DATE 'str'
TIME 'str'
TIMESTAMP 'str'

# ODBC
{ d 'str' }
{ t 'str' }
{ ts 'str' }
```

## character set and collation

```sql
SET NAMES 'utf8mb4';

SHOW CHARACTER SET LIKE 'utf%';

SHOW CHARACTER SET;

SELECT * FROM INFORMATION_SCHEMA.CHARACTER_SETS


# collate 排序集

SELECT COLLATION_NAME FROM INFORMATION_SCHEMA.COLLATIONS

SHOW COLLATION WHERE Charset = 'utf8mb4';

# 常见的建表语句

CREATE TABLE t1
(
    c1 CHAR(10) CHARACTER SET latin1 COLLATE latin1_german1_ci
) DEFAULT CHARACTER SET latin2 COLLATE latin2_bin;

# 查看系统变量
SHOW VARIABLES LIKE 'character_set%';
# 所有的系统变量
# https://dev.mysql.com/doc/refman/8.0/en/server-system-variables.html#sysvar_character_set_server


```

字符集（Character Set）决定了数据库中可以存储哪些字符和如何编码这些字符。它直接关联到文本数据的存储方式。

排序集（Collation）决定了对文本数据进行比较和排序时的规则。它不涉及字符的存储方式，而是关注字符之间的排序和比较方式。

在MySQL查询中，使用BINARY关键字可以改变比较操作的默认行为，使其执行二进制比较而不是默认的字符集比较。

具体地说，在使用 BINARY 字符集的列中，每个字符将直接映射为对应的二进制值，而不会使用字符集编码进行存储。
这意味着不论该字符在哪个字符集中有何种编码，它在数据库中存储的都将是其原始的二进制形式。

### Connection Character Sets and Collations

在处理客户端和服务器之间连接的流量时，还涉及到其他字符集和排序系统变量。每个客户端都有特定于会话的连接相关的字符集和排序系统变量。
这些会话系统变量值在连接时初始化，但可以在会话中更改。

对于系统变量和回话变量，需要区分 @ 在设置变量

```sql
SET NAMES {'charset_name'
    [COLLATE 'collation_name'] | DEFAULT}

```

This statement sets the three session system variables `character_set_client`, 
`character_set_connection`, and `character_set_results` to the given character set.

```

服务器字符集和排序规则。
character_set_server
collation_server

默认数据集的字符集和排序规则。
character_set_database
collation_database

语句离开客户端时使用什么字符集?
character_set_client

服务器在接收到语句后应该转换成什么字符集?
character_set_connection
collation_connection

    服务器将客户端发送的语句从character_set_client转换为character_set_connection
    collation_connection 对于字面值字符串的比较很重要。
    对于字符串与列值的比较，collation_connection无关紧要，因为列有自己的排序规则，排序规则优先级更高


在将查询结果发送回客户端之前，服务器应该将查询结果转换为什么字符集?
character_set_results 

    要告诉服务器不执行结果集或错误消息的转换，将character_set_results设置为NULL或binary:

------------------------------------------------------
相关变量的查看方式: 


SELECT * FROM performance_schema.session_variables
WHERE VARIABLE_NAME IN (
  'character_set_client', 'character_set_connection',
  'character_set_results', 'collation_connection'
) ORDER BY VARIABLE_NAME;

SHOW SESSION VARIABLES LIKE 'character\_set\_%';
SHOW SESSION VARIABLES LIKE 'collation\_%';

```
