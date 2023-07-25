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

