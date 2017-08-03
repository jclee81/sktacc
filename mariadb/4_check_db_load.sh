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
	echo "- # of rows in $tbl: $(wc -l ${DIR}/${tbl}.csv)"
	mysql -utim_admin -p$PW << EOF
	select count(*) from tim_db.$tbl;
EOF
done
