#!/bin/bash
# VladVons@gmail.com


FindFile()
{
  local aId=$1;

  #find ~/ | grep ".log" | tee ${0}_${aId}.log
  grep -Ril "hello" "/home/$USER" | tee ${0}_${aId}.log
}


EchoLoop()
{
  local aCnt=$1;

  for i in $(seq 1 $aCnt); do
    echo "EchoLoop $i"
    sleep 1
  done
}


echo "Info: $0, $1, $2"
case $1 in
    FindFile)    $1 $2 $3 ;;
    EchoLoop)    $1 $2 $3 ;;
esac
