aCnt=100

for i in $(seq 1 $aCnt); do
    #JSON_FMT='{"data": "hello %s"}'
    #Data=$(printf "$JSON_FMT" "$i")
    Data="data"
    echo $Data

    wget --quiet --post-data "$Data" --output-document=- "http://localhost:8080/api/test"
    sleep 1
done
