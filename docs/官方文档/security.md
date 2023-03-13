# 6 security

## 6.1 一般安全问题

### 6.1.1 安全准则

MySQL使用基于访问控制列表（ACL）的安全性 用户可以尝试的连接、查询和其他操作 来执行。

- Do not ever give anyone (except MySQL root accounts) access to the `user` table in the `mysql` system database! This is critical.

- 了解MySQL访问特权系统如何工作，使用`GRANT`和`REVOKE`语句来控制对MySQL的访问。不要授予不必要的特权。不要授予所有主机特权。

  - 使用SHOW GRANTS语句检查哪些帐户可以访问哪些帐户。然后使用REVOKE语句删除那些不需要的特权。

- 不要在数据库中存储明文密码。如果你的电脑被侵入，入侵者就可以获取完整的密码列表并使用它们。相反，使用`SHA2()`或其他单向哈希函数并存储哈希值。

  为防止使用彩虹表恢复密码，请不要对普通密码使用这些功能;相反，选择一些字符串作为salt，并使用`hash(hash(password)+salt)`值。

- 还是密码相关问题。。。

- 防火墙

- 访问MySQL的应用程序不应该信任用户输入的任何数据，应该使用适当的防御性编程技术来编写。

- 不要在互联网上传输普通(未加密)数据。每个有时间和能力拦截这些信息并将其用于自己目的的人都可以访问这些信息。相反，应该使用加密协议，如SSL或SSH。MySQL支持内部SSL连接。另一种技术是使用SSH端口转发为通信创建加密(和压缩)隧道。

- 学习使用tcpdump和strings实用程序。在大多数情况下，您可以通过发出如下命令来检查MySQL数据流是否未加密：

  ```shell
  $> tcpdump -l -i eth0 -w - src or dst port 3306 | strings
  ```

### 6.1.2 keep password secure

mysql cli输入密码的方式：最安全的方法是让客户端程序提示输入密码，或者在受适当保护的选项文件中指定密码。

```
$> mysql -u francis -p db_name
Enter password: ********
```

### 6.1.5 普通用户运行MySQL

- 修改数据库目录和文件，使user_name具有读写其中文件的权限

- 用该用户启动MySQL，或者使用 `mysqld --user==user_name`

- 或者修改配置文件：

  ```ini
  [mysqld]
  user=user_name
  ```

## 6.2 Access Control and Account Management

MySQL特权系统的主要功能是对从给定主机连接的用户进行身份验证，并将该用户与数据库上的特权(如SELECT、INSERT、UPDATE和DELETE)相关联。其他功能包括为管理操作授予特权的能力。

```
CREATE USER, grant, revoke
```

MySQL特权系统确保所有用户只能执行被允许的操作。作为用户，当您连接到MySQL服务器时，您的身份由**连接的主机和指定的用户名**决定。当您连接后发出请求时，系统根据您的身份和您想要做的事情授予权限。

MySQL同时考虑您的主机名和用户名来识别您，因为没有理由假定给定的用户名属于所有主机上的同一个人。

MySQL通过允许您区分恰好具有相同名称的不同主机上的用户来处理这个问题:您可以为来自office.example.com的joe的连接授予一组特权，并为来自home.example.com的joe的连接授予一组不同的特权。要查看给定帐户拥有哪些特权，请使用SHOW GRANTS语句。例如:

```mysql
SHOW GRANTS FOR 'joe'@'office.example.com';
SHOW GRANTS FOR 'joe'@'home.example.com';
```



