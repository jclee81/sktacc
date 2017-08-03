#!/bin/bash
# TIM-AI means T-Infra Manager for AI Pre-requisite packages
# if you want to install latest stable version, copy mariadb.repo to /etc/yum.repo.d/
sudo cp mariaDB.repo /etc/yum.repos.d/

sudo yum install -y epel-release
sudo yum install -y python-devel python-pip mariadb mariadb-server
sudo easy_install-2.7 pip
sudo -E pip install PyMySQL
# pip upgrade
sudo -E pip install --upgrade pip
