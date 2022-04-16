#!/bin/bash

# Copyright:   (c) 2017, Vladimir Vons, UA
# Author:      Vladimir Vons <VladVons@gmail.com>
# Created:     09.11.2017
# License:     GNU, see LICENSE for more details
# Description:


source ./const.conf
source ./common.sh


MakeDebControl()
{
echo "\
Package: $Name
Version: $Ver
Architecture: $Platform
Section: IoT
Priority: optional
Depends: python3-prctl, python3-pyodbc, odbc-mariadb
Recommends: monit, unixodbc, python3-mysqldb
Maintainer: Vladimir Vons <VladVons@gmail.com>
Homepage: http://oster.com.ua/software
Description: vRelay automation
" > $DirDebRoot/src/DEBIAN/control
}


Deb()
{
  Log "$0->$FUNCNAME($*)"

  find ./ \( -name "*.pyc" -o -name "*.log" -o -name "*.pyi" -o -name "*.db" \) -type f -delete

  Release="$DirSrc/$Name.bin"
  if [ ! -x $Release ]; then
    echo "Release not compiled $Release"
    exit
  fi

  DirApp="$DirDeb/usr/lib/$Name"
  mkdir -p $DirApp
  echo "Dst is $DirApp"

  MakeDebControl

  cp -R deb/src/CONTENTS/* $DirDeb
  cp -R deb/src/DEBIAN $DirDeb
  cp -R $DirSrc/$Name.{bin,sh,conf,key} $DirApp
  cp $DirSrc/Options.py $DirApp

  cp -R $DirSrc/Plugin $DirApp
  find $DirApp/Plugin/Devices   -type f | grep -v -f DebDevices.lst | xargs rm
  find $DirApp/Plugin/Providers -type f | grep -v -f DebProviders.lst | xargs rm

  rm -f $DirDeb.deb
  ExecM "dpkg-deb --build $DirDeb"
  rm -R $DirDeb
}


Release()
{
  Log "$0->$FUNCNAME($*)"

  #apt-get install python-dev 

  CurDir=$(pwd)
  find $DirSrc -name "*.pyc" -type f -delete

  sudo mkdir -p $DirSrcRelease
  sudo chown $USER $DirSrcRelease

  cp -R -L $DirSrc/* $DirSrcRelease
  cd $DirSrcRelease

  echo "Building in $(pwd) ..."
  #python3 -m nuitka  --remove-output $Name.py
  #python3 -m nuitka --follow-imports --remove-output --standalone $Name.py
  ExecM "python3 -m nuitka --follow-imports --include-plugin-directory=App --remove-output $Name.py"

  cd $CurDir
  cp $DirSrcRelease/$Name.bin $DirSrc
}


Install()
{
  Log "$0->$FUNCNAME($*)"

  pip3 install -r requires.txt

  # --- search unused variables, func, imports
  #ExecM "pip3 install vulture"
  #vulture ./src

  ExecM "pip3 install nuitka"
  ExecM "pip3 install --upgrade nuitka"
  ExecM "sudo apt install python3-dev --no-install-recommends"
}

DbDump()
{
  sudo -u postgres psql

  sudo -u postgres psql -l 
  sudo -u postgres psql -c "SELECT datname, dattablespace, datctype FROM pg_database WHERE datistemplate = false;"

  sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'new-password';"

  pg_dump  --host=localhost --username=postgres --password --dbname=test1 | gzip > test1.sql.gz

  sudo -u postgres psql -c "CREATE DATABASE test2;"
  createdb --host=localhost --username=postgres --password test2

  gunzip -c test1.sql.gz | psql --host=localhost --username=postgres --password test2
  gunzip -c test1.sql.gz | sudo -u postgres psql test2
}

App()
{
  Release
  Deb
}


clear
case $1 in
    Release)   "$1" "$2" "$3" ;;
    Deb)       "$1" "$2" "$3" ;;
    App)       "$1" "$2" "$3" ;;
    Install)   "$1" "$2" "$3" ;;
esac
