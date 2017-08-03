#!/bin/bash

MARIA_DB_HOST=$(hostname)
PASSWORD='niclab1234'

function create(){
	echo -n "MySql Root password:"
	read -s PW;echo
	mysql -uroot -p$PW << EOF
		CREATE DATABASE IF NOT EXISTS tim_db;
		CREATE USER IF NOT EXISTS 'tim_admin'@'%' IDENTIFIED BY '${PASSWORD}';
		CREATE USER IF NOT EXISTS 'tim_admin'@'localhost' IDENTIFIED BY '${PASSWORD}';
		CREATE USER IF NOT EXISTS 'tim_admin'@'${MARIA_DB_HOST}' IDENTIFIED BY '${PASSWORD}';
		FLUSH PRIVILEGES;
		GRANT ALL PRIVILEGES ON tim_db.* TO 'tim_admin'@'%';
		GRANT ALL PRIVILEGES ON tim_db.* TO 'tim_admin'@'localhost';
		GRANT ALL PRIVILEGES ON tim_db.* TO 'tim_admin'@'${MARIA_DB_HOST}';
		USE tim_db;
		SOURCE create_table.sql
EOF
}

function clean(){
	echo -n "MySql Root password:"
	read -s PW;echo
	mysql -uroot -p$PW << EOF
		DROP DATABASE IF EXISTS tim_db;
		DROP USER IF EXISTS 'tim_admin'@'%';
		DROP USER IF EXISTS 'tim_admin'@'localhost';
		DROP USER IF EXISTS 'tim_admin'@'${MARIA_DB_HOST}';
EOF
}

if [ $# -ne 1 ]; then
	echo "usage: $(basename $0) [clean|create]"
	exit 1
fi

if [ $1 == "clean" ];then
	clean
elif [ $1 == "create" ];then
	shift
	create
else 
	echo "usage: $(basename $0) [clean|create]"
fi
