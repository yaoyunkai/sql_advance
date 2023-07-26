# innodb locking transaction model

## innodb lock

### Shared and Exclusive Locks

行级锁 row-level:

- S - shared lock: 允许持有锁的事务读取一行。
- X - exclusive locks: 允许持有锁的事务更新或删除行。

如果事务T1持有行r上的共享锁，那么来自不同事务T2的请求对行r上的锁的处理如下: T2对S锁的请求可以立即被授予。因此，T1和T2都对r持有S锁。T2对X锁的请求不能立即被授予。

如果事务T1持有行r上的独占锁(X)，则来自某个不同事务T2的对行r上任意类型锁的请求不能立即被授予。

### Intention locks

```mysql
-- IS
select ... for share

-- IX
select ... for update

lock tables ... 

```

InnoDB支持多粒度锁，允许行锁和表锁共存。例如，这样的语句:`LOCK TABLES … WRITE`在指定的表上使用排他锁(X锁)。为了实现多粒度级别的锁，InnoDB使用了意图锁。意图锁是表级别的锁，它指示事务以后对表中的某一行需要哪种类型的锁(共享的还是排他的)。

IS - 指示事务打算对表中的单个行设置共享锁。

IX - 指示事务打算对表中的单个行设置排他锁。

在事务获得表中某一行的共享锁之前，它必须首先获得表上的IS锁或更强的锁。

在事务获得表中某一行的排他锁之前，它必须首先获得该表上的IX锁。

|      | `X`      | `IX`       | `S`        | `IS`       |
| :--- | :------- | :--------- | :--------- | :--------- |
| `X`  | Conflict | Conflict   | Conflict   | Conflict   |
| `IX` | Conflict | Compatible | Conflict   | Compatible |
| `S`  | Conflict | Conflict   | Compatible | Compatible |
| `IS` | Conflict | Compatible | Compatible | Compatible |

意图锁的主要目的是显示某人正在锁定表中的一行，或者将要锁定表中的一行。

### Record locks

记录锁是索引记录上的锁。

记录锁总是锁定索引记录，即使表没有定义索引。对于这种情况，InnoDB创建一个隐藏的集群索引，并使用该索引进行记录锁定。

### Gap locks

间隙锁是在索引记录之间的间隙上的锁，或者在第一个索引记录之前或最后一个索引记录之后的间隙上的锁。

例如:`SELECT c1 FROM t WHERE c1 BETWEEN 10 and 20 For UPDATE`;防止其他事务将值15插入到列t.c1中，无论列中是否已经存在这样的值，因为范围中所有现有值之间的间隙被锁定。

间隙可以跨越单个索引值、多个索引值，甚至是空的。

对于使用唯一索引锁定行以搜索唯一行的语句，不需要间隙锁定。

InnoDB中的间隙锁是“纯抑制的”，这意味着它们的唯一目的是防止其他事务插入到间隙中。间隙锁可以共存。一个事务使用的间隙锁不会阻止另一个事务在相同的间隙上使用间隙锁。共享间隙锁和独占间隙锁之间没有区别。它们彼此不冲突，并且它们执行相同的功能。

间隙锁定可以显式禁用。如果将事务隔离级别更改为READ COMMITTED，就会发生这种情况。在这种情况下，对于搜索和索引扫描禁用间隙锁定，并且仅用于外键约束检查和重复键检查。

### Next-key locks

next-key锁是索引记录上的记录锁和索引记录之前的间隙上的间隙锁的组合。

InnoDB执行行级锁的方式是，当它搜索或扫描一个表索引时，它会在遇到的索引记录上设置共享锁或排他锁。因此，行级锁实际上是索引记录锁。索引记录上的next-key锁也会影响该索引记录之前的“间隙”。也就是说，next-key锁是索引记录锁加上索引记录前面的间隙锁。如果一个会话对索引中的记录R具有共享锁或排他锁，则另一个会话不能在索引顺序R之前的空白中插入新的索引记录。

### Insert Intention Locks

插入意图锁是insert操作在行插入之前设置的一种间隙锁。这个锁以这样一种方式表示插入的意图，即插入到相同索引间隙中的多个事务如果不在间隙内的相同位置插入，则不需要彼此等待。

### AUTO-INC Locks

AUTO-INC锁是一种特殊的表级锁，用于在具有AUTO_INCREMENT列的表中插入事务。在最简单的情况下，如果一个事务正在向表中插入值，那么任何其他事务都必须等待对该表进行自己的插入，以便第一个事务插入的行接收连续的主键值。

`innodb_autoinc_lock_mode` 

[MySQL :: MySQL 8.0 Reference Manual :: 15.6.1.6 AUTO_INCREMENT Handling in InnoDB](https://dev.mysql.com/doc/refman/8.0/en/innodb-auto-increment-handling.html#innodb-auto-increment-lock-modes)

## 事务模型

### 事务隔离级别

下面的列表描述了MySQL如何支持不同的事务级别。该列表从最常用的级别到最不常用的级别。

**REPEATABLE READ**

对于locking reads(SELECT with For UPDATE或For SHARE)、UPDATE和DELETE语句，锁定取决于语句是使用具有唯一搜索条件的唯一索引，还是使用具有唯一搜索条件的范围类型搜索条件。

对于具有唯一查询条件的唯一索引，InnoDB只锁定找到的索引记录，而不锁定之前的空白记录。

对于其他搜索条件，InnoDB锁定扫描的索引范围，使用间隙锁或下一键锁来阻止其他会话插入到范围所覆盖的间隙中。

**READ COMMITTED**

对于locking reads(SELECT with For UPDATE或For SHARE)、UPDATE语句和DELETE语句，InnoDB只锁索引记录，而不锁它们之前的gap，因此允许在被锁的记录旁边自由插入新记录。间隙锁定仅用于外键约束检查和重复键检查。

对于UPDATE或DELETE语句，InnoDB只对更新或删除的行持有锁。不匹配行的记录锁在MySQL计算完WHERE条件后释放。这大大降低了死锁的概率，但死锁仍然可能发生。

对于UPDATE语句，如果一行已经被锁定，InnoDB执行“半一致”读取，将最新提交的版本返回给MySQL，以便MySQL可以确定该行是否符合UPDATE的WHERE条件。如果行匹配(必须更新)，MySQL再次读取该行，这一次InnoDB要么锁定它，要么等待锁定它。

**READ UNCOMMITTED**

**SERIALIZABLE**

### autocommit, Commit, and Rollback

在InnoDB中，所有的用户活动都发生在事务中。如果启用了自动提交模式，则每个SQL语句单独形成一个事务。默认情况下，MySQL为每个新连接启动会话时都启用了自动提交，因此MySQL在每个SQL语句没有返回错误时都会在该语句之后进行提交。

```mysql
mysql> CREATE TABLE customer (a INT, b CHAR (20), INDEX (a));
Query OK, 0 rows affected (0.00 sec)
mysql> -- Do a transaction with autocommit turned on.
mysql> START TRANSACTION;
Query OK, 0 rows affected (0.00 sec)
mysql> INSERT INTO customer VALUES (10, 'Heikki');
Query OK, 1 row affected (0.00 sec)
mysql> COMMIT;
Query OK, 0 rows affected (0.00 sec)
mysql> -- Do another transaction with autocommit turned off.
mysql> SET autocommit=0;
Query OK, 0 rows affected (0.00 sec)
mysql> INSERT INTO customer VALUES (15, 'John');
Query OK, 1 row affected (0.00 sec)
mysql> INSERT INTO customer VALUES (20, 'Paul');
Query OK, 1 row affected (0.00 sec)
mysql> DELETE FROM customer WHERE b = 'Heikki';
Query OK, 1 row affected (0.00 sec)
mysql> -- Now we undo those last 2 inserts and the delete.
mysql> ROLLBACK;
Query OK, 0 rows affected (0.00 sec)
mysql> SELECT * FROM customer;
+------+--------+
| a    | b      |
+------+--------+
|   10 | Heikki |
+------+--------+
1 row in set (0.00 sec)
mysql>

```

### Consistent Nonlocking Reads

一致性读意味着InnoDB使用多版本控制向查询提供数据库在某个时间点的快照。查询查看在该时间点之前提交的事务所做的更改，而稍后或未提交的事务所做的更改则不查看。该规则的例外情况是，查询会看到同一事务中较早的语句所做的更改。这个异常会导致以下异常:如果更新表中的某些行，SELECT会看到更新行的最新版本，但也可能看到任何行的旧版本。如果其他会话同时更新同一表，则该异常意味着您可能会看到该表处于数据库中从未存在过的状态。

一致性读是InnoDB在`READ COMMITTED`和`REPEATABLE READ`隔离级别下处理SELECT语句的默认模式。一致性读不会在它访问的表上设置任何锁，因此其他会话可以在对表执行一致性读的同时自由地修改这些表。

假设您以默认的REPEATABLE READ隔离级别运行。当你发出一个一致性读(也就是一个普通的SELECT语句)时，InnoDB会给你的事务一个查询看到数据库的时间点。如果另一个事务在您指定的时间点之后删除了一行并提交，则不会看到该行已被删除。

### Locking Reads

如果在同一事务中查询数据，然后插入或更新相关数据，则常规 SELECT 语句无法提供足够的保护。其他事务可以更新或删除你刚刚查询过的相同行。InnoDB 支持两种类型的锁定读取，可提供额外的安全性：

`select ... for share`

对读取的任何记录设置共享模式锁。其他会话可以读取这些记录，但在你的事务提交前不能修改它们。如果这些记录中的任何一条被另一个尚未提交的事务修改，查询会等待该事务结束，然后使用最新的值。

`select ... for update`

对于搜索遇到的索引记录，会锁定记录和任何相关的索引项，就像为这些记录发布 UPDATE 语句一样。其他事务将被阻止更新这些记录、执行 SELECT ... FOR SHARE 或在某些事务隔离级别中读取数据。一致读取会忽略在读取视图中存在的记录上设置的任何锁。

这些子句主要用于处理树形结构或图形结构数据，可以是单个表中的数据，也可以是分割在多个表中的数据。您可以从一个地方到另一个地方遍历边缘或树枝，同时保留返回并更改这些 "指针 "值的权利。

**Locking Read Concurrency with NOWAIT and SKIP LOCKED**

## InnoDB 中不同 SQL 语句设置的锁

在 MySQL 的可重复读（Repeatable Read）隔离级别下，范围查询会对记录加锁，但并不是简单的行级别锁。

在可重复读隔离级别下，MySQL 使用多版本并发控制（MVCC）来实现事务隔离。MVCC 可以通过在每个数据行上保存不同版本的数据来实现并发读写而不会相互干扰。对于范围查询（Range Query），MySQL 会使用间隙锁（Gap Locks）来保证事务的隔离性。

间隙锁是一种特殊类型的锁，用于锁定一个范围而不是具体的数据行。当一个事务执行范围查询时，MySQL 会在范围内的间隙上设置锁，防止其他事务在同一范围内插入新的数据。这样做是为了防止幻读（Phantom Read）的问题，即在一个范围查询中，其他事务插入了新数据，导致查询结果出现不一致的情况。

请注意，间隙锁并不会阻止其他事务对已存在的数据行进行读取或修改，只会阻止其他事务在锁定的范围内插入新数据。因此，间隙锁不会对已存在的数据行进行加锁，只会对范围查询的间隙加锁。

---

锁定读取、更新或删除通常会对 SQL 语句处理过程中扫描的每条索引记录设置记录锁。至于语句中是否有排除记录的WHERE条件，这并不重要。InnoDB 不会记住确切的 WHERE 条件，而只知道扫描了哪些索引范围。锁通常是Next-key锁，也会阻止插入记录前的 "间隙"。不过，可以显式禁用间隙锁，这样就不会使用Next-key锁。

如果在搜索中使用了二级索引，并且要设置的索引记录锁是排他的，InnoDB 也会检索相应的聚类索引记录并对其设置锁。

如果没有适合语句的索引，而 MySQL 又必须扫描整个表才能处理语句，那么表中的每一行都会被锁定，这反过来又会阻止其他用户对表的所有插入操作。创建良好的索引非常重要，这样您的查询就不会扫描超过必要数量的行。

**select from**

是一致读取，读取数据库快照，不设置锁，除非事务隔离级别设置为 SERIALIZABLE。

## Phantom Rows 幻行

当同一查询在不同时间产生不同的记录集时，事务中就会出现所谓的幽灵问题。例如，如果 SELECT 执行了两次，但第二次返回了一条记录，而第一次没有返回，那么这条记录就是 "幽灵 "记录。

为了防止幻影，InnoDB使用了一种名为 "下一键锁定"（next-key locking）的算法，它将索引行锁定与间隙锁定结合在一起。InnoDB执行行级锁的方式是，当它搜索或扫描表索引时，它会在遇到的索引记录上设置共享或独占锁。因此，行级锁实际上就是索引记录锁。此外，索引记录上的下一键锁还会影响索引记录之前的 "间隙"。也就是说，下一键锁是索引记录锁加上索引记录前的间隙锁。如果一个会话对索引中的记录 R 有共享或独占锁，另一个会话就不能在索引顺序中紧靠 R 之前的间隙中插入新的索引记录。

## 死锁

和死锁相关的三个变量：

```
innodb_deadlock_detect
innodb_lock_wait_timeout
innodb_print_all_deadlocks

```

查看正在使用的锁和死锁：

```mysql
mysql> SELECT REQUESTING_ENGINE_LOCK_ID as Req_Lock_Id,
              REQUESTING_ENGINE_TRANSACTION_ID as Req_Trx_Id,
              BLOCKING_ENGINE_LOCK_ID as Blk_Lock_Id, 
              BLOCKING_ENGINE_TRANSACTION_ID as Blk_Trx_Id
        FROM performance_schema.data_lock_waits;
+----------------------------------------+------------+----------------------------------------+-----------------+
| Req_Lock_Id                            | Req_Trx_Id | Blk_Lock_Id                            | Blk_Trx_Id      |
+----------------------------------------+------------+----------------------------------------+-----------------+
| 139816129437696:27:4:2:139816016601240 |      43260 | 139816129436888:27:4:2:139816016594720 | 421291106147544 |
+----------------------------------------+------------+----------------------------------------+-----------------+
1 row in set (0.00 sec)

mysql> SELECT ENGINE_LOCK_ID as Lock_Id, 
              ENGINE_TRANSACTION_ID as Trx_id, 
              OBJECT_NAME as `Table`, 
              INDEX_NAME as `Index`, 
              LOCK_DATA as Data, 
              LOCK_MODE as Mode, 
              LOCK_STATUS as Status, 
              LOCK_TYPE as Type 
        FROM performance_schema.data_locks;
+----------------------------------------+-----------------+---------+---------+------------+---------------+---------+--------+
| Lock_Id                                | Trx_Id          | Table   | Index   | Data       | Mode          | Status  | Type   |
+----------------------------------------+-----------------+---------+---------+------------+---------------+---------+--------+
| 139816129437696:1187:139816016603896   |           43260 | Animals | NULL    | NULL       | IX            | GRANTED | TABLE  |
| 139816129437696:1188:139816016603808   |           43260 | Birds   | NULL    | NULL       | IS            | GRANTED | TABLE  |
| 139816129437696:28:4:2:139816016600896 |           43260 | Birds   | PRIMARY | 'Buzzard'  | S,REC_NOT_GAP | GRANTED | RECORD |
| 139816129437696:27:4:2:139816016601240 |           43260 | Animals | PRIMARY | 'Aardvark' | X,REC_NOT_GAP | WAITING | RECORD |
| 139816129436888:1187:139816016597712   | 421291106147544 | Animals | NULL    | NULL       | IS            | GRANTED | TABLE  |
| 139816129436888:27:4:2:139816016594720 | 421291106147544 | Animals | PRIMARY | 'Aardvark' | S,REC_NOT_GAP | GRANTED | RECORD |
+----------------------------------------+-----------------+---------+---------+------------+---------------+---------+--------+
6 rows in set (0.00 sec)
```

