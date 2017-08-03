#!/bin/bash
stty -echo
read -p "current password:" current_pw;echo
read -p "new password:" new_pw;echo
read -p "confirm password:" confirm_pw;echo
stty echo

if [ $new_pw != $confirm_pw ]; then
	echo "password does not match!"
	exit
fi

mysql -uroot -p${current_pw} <<EOF
	use mysql;
	update user set password=password('${new_pw}') where user='root';
	flush privileges;
EOF
