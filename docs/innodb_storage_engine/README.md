# InnoDB 存储引擎

## 1. mysql体系结构和存储引擎

通过 `show engines` 或者 `information_schema.ENGINES` 来查看mysql支持的存储引擎：

```
 MySQL  localhost:33060+ ssl  SQL > show engines;
+--------------------+---------+----------------------------------------------------------------+--------------+------+------------+
| Engine             | Support | Comment                                                        | Transactions | XA   | Savepoints |
+--------------------+---------+----------------------------------------------------------------+--------------+------+------------+
| MEMORY             | YES     | Hash based, stored in memory, useful for temporary tables      | NO           | NO   | NO         |
| MRG_MYISAM         | YES     | Collection of identical MyISAM tables                          | NO           | NO   | NO         |
| CSV                | YES     | CSV storage engine                                             | NO           | NO   | NO         |
| FEDERATED          | NO      | Federated MySQL storage engine                                 | NULL         | NULL | NULL       |
| PERFORMANCE_SCHEMA | YES     | Performance Schema                                             | NO           | NO   | NO         |
| MyISAM             | YES     | MyISAM storage engine                                          | NO           | NO   | NO         |
| InnoDB             | DEFAULT | Supports transactions, row-level locking, and foreign keys     | YES          | YES  | YES        |
| BLACKHOLE          | YES     | /dev/null storage engine (anything you write to it disappears) | NO           | NO   | NO         |
| ARCHIVE            | YES     | Archive storage engine                                         | NO           | NO   | NO         |
+--------------------+---------+----------------------------------------------------------------+--------------+------+------------+
9 rows in set (0.0004 sec)
```

## 2. InnoDB存储引擎

show engine innodb status 解释：

```
I/O thread 0 state: IO thread 状态
Buffer pool size   512  : 缓冲池的大小 512 * 16k
Free buffers       241  : free列表中的页  241 * 16k
Database pages     264  : LRU列表中页的数量 264 * 16k

Pages made young 0, not young 0
0.00 youngs/s, 0.00 non-youngs/s    

Buffer pool hit rate   : 缓冲池的命中率

LRU len: 264, unzip_LRU len: 0  : unzip_LRU 压缩页

Modified db pages  0    : 脏页的数量


Log sequence number          377257329     : LSN 
Log buffer assigned up to    377257329
Log buffer completed up to   377257329
Log written up to            377257329
Log flushed up to            377257329
Added dirty pages up to      377257329
Pages flushed up to          377257329
Last checkpoint at           377257329


```

### 2.3 innodb体系架构

![MySQL5.6_innodb_storage_engine_architecture](./.assets/MySQL5.6_innodb_storage_engine_architecture-1692024408423-2.png)

#### 2.3.1 后台线程

刷新内存池中的数据，将已经修改的数据文件刷新到磁盘文件。

**Master Thread**

将缓冲池数据异步刷新到磁盘，保证数据的一致性，包括脏页的刷新，合并插入缓冲 insert buffer , undo页的回收

**IO Thread**

负责IO请求的回调处理。有四个IO thread，分别是 write，read, insert buffer 和 log 。

下面是相关的参数：

```
SQL > show variables like 'innodb_version';
+----------------+--------+
| Variable_name  | Value  |
+----------------+--------+
| innodb_version | 8.0.20 |
+----------------+--------+

SQL > show variables like 'innodb_%_io_threads';
+-------------------------+-------+
| Variable_name           | Value |
+-------------------------+-------+
| innodb_read_io_threads  | 4     |
| innodb_write_io_threads | 4     |
+-------------------------+-------+
```

可以通过 `show engine innodb status` 来观察IO thread.

```
--------
FILE I/O
--------
I/O thread 0 state: wait Windows aio (insert buffer thread)
I/O thread 1 state: wait Windows aio (log thread)
I/O thread 2 state: wait Windows aio (read thread)
I/O thread 3 state: wait Windows aio (read thread)
I/O thread 4 state: wait Windows aio (read thread)
I/O thread 5 state: wait Windows aio (read thread)
I/O thread 6 state: wait Windows aio (write thread)
I/O thread 7 state: wait Windows aio (write thread)
I/O thread 8 state: wait Windows aio (write thread)
I/O thread 9 state: wait Windows aio (write thread)
Pending normal aio reads: [0, 0, 0, 0] , aio writes: [0, 0, 0, 0] ,
 ibuf aio reads:, log i/o's:, sync i/o's:
Pending flushes (fsync) log: 0; buffer pool: 0
2525 OS file reads, 3473 OS file writes, 1743 OS fsyncs
0.00 reads/s, 0 avg bytes/read, 0.00 writes/s, 0.00 fsyncs/s
-------------------------------------
```

**Purge Thread**

回收已经使用并分配的undo页，相关配置：

```mysql
show variables like 'innodb_purge%';
```

**Page Cleaner Thread**

脏页的刷新操作都放入到单独的线程中来完成。

#### 2.3.2 内存

**缓冲池**

缓冲池的配置参数： `innodb_buffer_pool_size` 单位为kb。

缓冲池的实例个数配置： `innodb_buffer_pool_instances`

查看缓冲池状态: `information_schema.INNODB_BUFFER_POOL_STATS`

```
 MySQL  localhost:33060+ ssl  SQL > select * from information_schema.INNODB_BUFFER_POOL_STATS\G
*************************** 1. row ***************************
                         POOL_ID: 0
                       POOL_SIZE: 512
                    FREE_BUFFERS: 241
                  DATABASE_PAGES: 264
              OLD_DATABASE_PAGES: 0
         MODIFIED_DATABASE_PAGES: 0
              PENDING_DECOMPRESS: 0
                   PENDING_READS: 0
               PENDING_FLUSH_LRU: 0
              PENDING_FLUSH_LIST: 0
                PAGES_MADE_YOUNG: 0
            PAGES_NOT_MADE_YOUNG: 0
           PAGES_MADE_YOUNG_RATE: 0
       PAGES_MADE_NOT_YOUNG_RATE: 0
               NUMBER_PAGES_READ: 9848
            NUMBER_PAGES_CREATED: 10790
            NUMBER_PAGES_WRITTEN: 17239
                 PAGES_READ_RATE: 0
               PAGES_CREATE_RATE: 0
              PAGES_WRITTEN_RATE: 0
                NUMBER_PAGES_GET: 14089198
                        HIT_RATE: 0
    YOUNG_MAKE_PER_THOUSAND_GETS: 0
NOT_YOUNG_MAKE_PER_THOUSAND_GETS: 0
         NUMBER_PAGES_READ_AHEAD: 1199
       NUMBER_READ_AHEAD_EVICTED: 23
                 READ_AHEAD_RATE: 0
         READ_AHEAD_EVICTED_RATE: 0
                    LRU_IO_TOTAL: 8
                  LRU_IO_CURRENT: 0
                UNCOMPRESS_TOTAL: 0
              UNCOMPRESS_CURRENT: 0
1 row in set (0.0005 sec)
```

**LRU list Free list & Flush List**

LRU列表有midpoint机制，新读取到的页，并不是直接放入到LRU的首部，而是放入到LRU列表的midpoint位置，配置参数为 `innodb_old_blocks_pct`

```
Variable_name: innodb_old_blocks_pct
        Value: 37
```

另一个机制：`innodb_old_blocks_itme` 当读取到mid位置后需要等待多久才会被加入到LRU列表的热端。

free list就相当于是数据库服务刚刚启动没有数据页时，维护buffer pool的空闲缓存页的数据结构。

当数据库刚启动时，页都存放在free列表中。当需要从缓冲池中分页时，首先从Free列表中查找是否有可用的空闲页，若有则将该页从Free列表中删除，放入到LRU列表中。否则，根据LRU算法，淘汰LRU列表末尾的页，将该内存空间分配给新的页。

当页从LRU列表的old部分加入到new部分时，称此时发生的操作为page made young，

而因为innodb_old_blocks_time的设置而导致页没有从old部分移动到new部分的操作称为page not made young。

查看LRU列表中的每个页的具体信息：`INNODB_BUFFER_PAGE_LRU`

----

在LRU中的页被修改后，该页称为脏页 dirty page, 数据库会通过 checkpoint机制将脏页刷新回磁盘。

OLDEST_MODIFICATION 标志表示脏页。

**重做日志缓冲 redo log buffer**

重做日志放入到缓冲区，然后按一定频率刷新到重做日志文件(每秒刷新一次会磁盘)

配置：`innodb_log_buffer_size`

### 2.4 checkpoint技术

write ahead log: 当事务提交时，先写重做日志，在修改页。当宕机时，通过重做日志来完成数据恢复。ACID的D。

checkpoint的目的是解决这些问题：

- 缩短数据库的恢复时间
- 缓冲池不够用时，刷新脏页到磁盘
- 重做日志不可用时，刷新脏页

当缓冲池不够用时，根据LRU算法会溢出最近最少使用的页，若此页为脏页，那么需要强制执行checkpoint, 将脏页刷回磁盘。

对于innodb，通过LSN `log sequence number` 来标记版本。每个页，重做日志和checkpoint中都有 LSN。

checkpoint的种类有：

- sharp checkpoint: 关闭数据库时，参数为 `innodb_fast_shutdown=1`
- fuzzy checkpoint

fuzzy checkpoint 会在如下几种情况下发生：

- master thread checkpoint: 每秒或者每十秒从脏页列表中刷新一定比例的页
- Flush LRU LIST checkpoint: 为了保证LRU列表中有空闲页可用，参数为 `innodb_lru_scan_depth`
- async/sync flush checkpoint: 重做日志文件不可用的情况，强制将页刷新回磁盘。保证重做日志的循环使用的可用性。
- dirty page too much checkpoint：脏页数量太多，导致强制进行 checkpoint. 参数为 `innodb_max_dirty_pages_pct`

### 2.5 Master Thread 工作方式

