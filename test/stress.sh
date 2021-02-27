#!/bin/bash


Cmd="./wget.sh"

for i in {1..10}; do
    echo "i: $i"
    xfce4-terminal --minimize --hold --geometry=10x10 --initial-title="$Cmd $i" --command="$Cmd"
done

rm wget-log.*
