/*
opyright:    Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.10
*/


function HttpRequest(aUrl, aFunc, aPostJson = null) {
    console.log(aUrl, aPostJson);

    let xhr = new XMLHttpRequest();
    if (aPostJson) {
        xhr.open('post', aUrl);
        xhr.setRequestHeader('Content-Type', 'application/json');
    } else {
        xhr.open('get', aUrl);
    }

    xhr.onload = function() {
        if (xhr.status == 200) {
            let Data = JSON.parse(xhr.responseText);
            aFunc(Data);
        } else {
            console.log('Server error ' + xhr.status);
        }
    }

    xhr.onerror = function() {
        console.log('Connection error');
    }

    if (aPostJson) {
        var aPostJson = JSON.stringify(aPostJson);
    }
    xhr.send(aPostJson);
}


class TWebSock {
    constructor() {
        this.Debug = false;
    };

    Log(aMsg) {
        if (this.Debug) {
            console.log(aMsg);
        }
    }

    Connect(aUrl) {
        let This = this;

        this.Log('Connect')
        this.ws = new WebSocket(aUrl);

        this.ws.onopen = function() {
            This.Log('OnOpen');
        };

        this.ws.onmessage = function(aEvent) {
            let Data = JSON.parse(aEvent.data);
            This.OnMessage(aEvent, Data);
        };

        this.ws.onclose = function() {
            This.Log('OnClose');
        };
    };

    Call(aPlugin, aParam) {
        let Data = JSON.stringify({'Plugin': aPlugin, 'Param': aParam});
        this.ws.send(Data);
    };

    OnOpen() {
        this.Log('OnOpen');
    };

    OnClose() {
        this.Log('OnClose');
    };

    OnMessage(aEvent) {
        this.Log('OnMessage');
    };
};