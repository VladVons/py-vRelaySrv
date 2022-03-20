#!/bin/bash


wget="wget --read-timeout=6 --tries=1 -qO-"


ExecM()
{
  aExec="$1";

  echo
  echo "$FUNCNAME, $aExec"
  eval "$aExec"
}


Loop()
{
  local aHosts=$1;

  TimeStart="$(date -u +%s)"
  Cnt=0
  while true; do
    echo
    Cnt=$((Cnt+1))
    TimeNow="$(date -u +%s)"
    echo "Cnt: $Cnt, Uptime: $((TimeNow-$TimeStart))"

    for Host in $aHosts; do
        echo $Host
        HostMpy $Host
        #HostHive $Host
    done

    sleep 2
  done
}

HostMpy()
{
    local aHost=$1;

    #$wget "$aHost/sys_info.py"
    $wget "$aHost"
}


Hosts="http://localhost:8080"
Loop $Hosts
