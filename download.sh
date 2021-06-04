#!/bin/bash
for i in $(seq 1 200)
do
    echo 'start'
    echo $i
    pid=$(ps -ef | grep 'pipeline.py' | grep -v "grep" | awk '{print $2}')
    if [$pid == '']
    then
        echo 'no pipeline'
    else
        echo $pid
        kill -9 $pid
        sleep 5m
    fi
    cd /home/ganyunchong/Comments-Mining-System-for-Scholar-Citations
    python pipeline.py &
    sleep 2m
done
