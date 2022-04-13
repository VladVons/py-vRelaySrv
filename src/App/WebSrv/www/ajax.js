pageCounter = 1;

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

function Func1() {
    //Url = 'https://learnwebcode.github.io/json-example/animals-' + pageCounter + '.json';
    Url = '/api/get_task';
    Post = {
        name: "hello",
        surname: "world"
    };

    HttpRequest(
        Url,
        function(aData) {
            console.log("aData", aData);

            htmlString = "";
            for (i = 0; i < aData.length; i++) {
                htmlString += "<p>" + aData[i].name;
            }

            animalContainer = document.getElementById("animal-info");
            animalContainer.insertAdjacentHTML('beforeend', htmlString);

            if (pageCounter++ > 3) {
                btn.classList.add("hide-me");
            }
        },
        Post
    );
}

btn = document.getElementById("btn");
btn.addEventListener("click", Func1);
