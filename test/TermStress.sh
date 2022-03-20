#!/bin/bash


Cmd="./TaskB.sh"

for i in {1..3}; do
    echo "i: $i"
    xfce4-terminal --minimize --hold --geometry=10x10 --initial-title="$Cmd $i" --command="$Cmd FindFile $i" --tab --command="$Cmd EchoLoop 100"
done
