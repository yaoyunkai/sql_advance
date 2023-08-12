## encoding ctype & collate

1. **Encoding（编码）**：数据库的 `encoding` 定义了如何将字符映射到二进制数据，以便在存储和检索过程中使用。它决定了如何将字符编码为字节序列，以及如何将字节序列解码为字符。常见的编码包括 UTF-8、UTF-16、LATIN1 等。选择适当的编码对于支持各种语言和字符集非常重要。编码的选择会影响存储效率、字符集支持以及对特定语言的正确显示。
2. **Ctype（字符分类）**：`ctype`（字符分类）定义了字符如何被分类，以便在字符串比较和排序时进行正确的处理。它涉及到字符的一些特性，如大小写转换、空格处理等。`ctype` 设置对于确定字符串比较的规则很重要，因为它会影响到例如 `ORDER BY` 子句的排序结果。
3. **Collate（排序规则）**：`collate`（排序规则）定义了字符的比较和排序方式。它依赖于 `ctype`，确定字符在字符串比较中的相对顺序。不同的 `collate` 设置可以导致不同的排序结果，从而影响查询结果的顺序。

- `Encoding` 控制字符如何编码为字节序列和解码回字符，影响存储和检索。
- `Ctype` 确定字符的分类，如大小写转换、空格处理等，影响字符串比较。
- `Collate` 定义了字符的比较和排序规则，依赖于 `ctype`，影响字符串排序结果。

1. **C 排序规则**：C 排序规则是一种基于字节值的排序方式。在 C 排序规则下，字符串按照它们在内存中的字节值进行排序，不考虑字符的语言环境或地域差异。
2. **POSIX 排序规则**：POSIX 排序规则也是一种基于字节值的排序方式，但它考虑了一些本地化的特性。


## 数据类型

| 类型分类    | 数据类型                                                                           |
|---------|--------------------------------------------------------------------------------|
| 数值类型    | smallint, integer, bigint, serial, bigserial, real, double precision, numeric  |
| 字符串类型   | character, character varying, text                                             |
| 日期和时间类型 | date, time, time with time zone, timestamp, timestamp with time zone, interval |
| 布尔类型    | boolean                                                                        |
| 几何类型    | point, line, lseg, box, path, polygon, circle                                  |
| 二进制数据类型 | bytea                                                                          |
| 网络地址类型  | cidr, inet, macaddr                                                            |
| 枚举类型    | enum                                                                           |
| 比特串类型   | bit, bit varying                                                               |
| 文本搜索类型  | tsvector, tsquery                                                              |
| UUID类型  | uuid                                                                           |
| JSON类型  | json, jsonb                                                                    |
| 数组类型    | 数值数组, 字符数组 等                                                                   |
| 范围类型    | int4range, numrange, tsrange, daterange, int8range                             |
| 复合类型    | 多个字段组成的类型                                                                      |
| 域类型     | 用户定义的数据类型基于其他基本数据类型                                                            |

## MetaInfo

### 查看表结构

1. **使用 psql 命令行工具**：在终端中运行以下命令，将 `<table_name>` 替换为要查看的表名。

   ```
   bashCopy code
   psql -d your_database_name -c "\d+ <table_name>"
   ```

   这将显示表的详细结构，包括列名、数据类型、约束等信息。

1. **使用 SQL 查询**：在 psql 命令行工具或任何 PostgreSQL 客户端中，执行以下 SQL 查询，将 `<table_name>` 替换为要查看的表名。

   ```
   sqlCopy code
   \d+ <table_name>
   ```

   这将显示表的详细结构，与上述方法类似。

1. **查询系统表**：通过查询系统表，你也可以获取表的结构信息。运行以下查询，将 `<table_name>` 替换为要查看的表名。

   ```
   sqlCopy codeSELECT column_name, data_type, character_maximum_length
   FROM information_schema.columns
   WHERE table_name = '<table_name>';
   ```

   这将显示指定表的列名、数据类型和字符最大长度等信息。

### 查看索引

1. **使用 psql 命令行工具**：在终端中运行以下命令，将 `<table_name>` 替换为要查看索引的表名。

   ```
   bashCopy code
   psql -d your_database_name -c "\di <table_name>"
   ```

   这将显示与指定表相关的索引信息。

1. **使用 SQL 查询**：在 psql 命令行工具或任何 PostgreSQL 客户端中，执行以下 SQL 查询，将 `<table_name>` 替换为要查看索引的表名。

   ```
   sqlCopy code
   \di <table_name>
   ```

   这将显示与指定表相关的索引信息，类似于上述方法。

1. **查询系统表**：通过查询系统表，你可以获取与指定表相关的索引信息。运行以下查询，将 `<table_name>` 替换为要查看索引的表名。

   ```
   sqlCopy codeSELECT indexname, indexdef
   FROM pg_indexes
   WHERE tablename = '<table_name>';
   ```

   这将显示指定表的索引名称和索引定义。

