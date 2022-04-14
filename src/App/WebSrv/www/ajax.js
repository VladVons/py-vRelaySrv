function HttpRequest(aUrl, aFunc, aPostJson = null) {
    console.log(aUrl, aPostJson);

    xhr = new XMLHttpRequest();
    if (aPostJson) {
        xhr.open('post', aUrl);
        xhr.setRequestHeader('Content-Type', 'application/json');
    } else {
        xhr.open('get', aUrl);
    }

    xhr.onload = function() {
        if (xhr.status == 200) {
            Data = JSON.parse(xhr.responseText);
            aFunc(Data);
        } else {
            console.log("Server error " + xhr.status);
        }
    };

    xhr.onerror = function() {
        console.log("Connection error");
    };

    if (aPostJson) {
        aPostJson = JSON.stringify(aPostJson);
    }
    xhr.send(aPostJson);
}
