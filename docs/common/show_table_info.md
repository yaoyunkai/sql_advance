```sql
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

-- 查询字符集相关

    show character set ;
    show collation like 'utf8mb4%cs';

```

