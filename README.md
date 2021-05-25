# Rogue-MySql-Web-Server
Add a Web Server base on Rogue Mysql Server to allow remote user get "mysql.log" content

# Usage:
modify "server.py" password and port, "rogue_mysql_server.py" PORT.After then run the command `./run.sh`

If a remote user want to get the Rogue Mysql Server read file result,"password" correct is necessary,or one will get connection failed

<img src="https://github.com/xiaopan233/Rogue-MySql-Web-Server/blob/main/img/2-2.png" width=800>


Web Server log file is "rms_server_log.txt"

<img src="https://github.com/xiaopan233/Rogue-MySql-Web-Server/blob/main/img/2-3.png" width=800>

# Change:
I have modified "rogue_mysql_server.py".Add two log output: 



Remote user or auto exp script can use regexp to match the content via the "Content Begin Flag"(dynamic, depend on SQL Query) and "Content End Flag"(fixed, value is "result off")


# Reference
https://github.com/allyshka/Rogue-MySql-Server
