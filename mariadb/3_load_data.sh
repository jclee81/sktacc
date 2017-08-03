#!/bin/bash

if [ $# -ne 1 ];then
	echo "usage: $(basename $0) [data_dir]"
	exit 1
fi

echo -n "tim_admin password:"
read -s PW;echo

DIR=$1
TBLS="lab docker_image host user container"

for tbl in $TBLS; do
	mysql -utim_admin -p$PW << EOF
	LOAD DATA LOCAL INFILE "${DIR}/${tbl}.csv" INTO TABLE tim_db.$tbl FIELDS TERMINATED BY '|' LINES TERMINATED BY '\n';
EOF
done
