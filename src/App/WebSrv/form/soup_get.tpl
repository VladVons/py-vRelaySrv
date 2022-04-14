{% extends "Layout.tpl" %}

{% block content %}
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js"></script>
    <script src="/www/ajax.js"></script>

    <form name="FormParse" method="post" action="/form/soup_get?action=go" enctype="multipart/form-data">
        <table style="width:100%">
            <tr>
                <th></th>
                <th style="width :90%"></th>
            <tr>
                <td>Url</td>
                <td>
                    <input type="text" name="Url" id="Url" placeholder="url" style="width:95%" required value="{{ Form.Url }}">
                    <button id="BtnGet" style="width:4%" onclick="BtnGet_OnClick()">get</button>
                </td>
            </tr>
            <tr>
                <td>Path</td>
                <td><input type="text" name="Path" placeholder="path script" style="width:100%" value="{{ Form.Path }}"></td>
            </tr>
            <tr>
                <td>Find regEx</td>
                <td><input type="text" name="Find" id="Find" placeholder="text" style="width:100%" required value="{{ Form.Find }}"></td>
            </tr>
            <tr>
                <td>Output</td>
                <td><textarea readonly name="Output" rows="30">{{ Form.Output }}</textarea> </td>
            <tr>
            <tr>
                <td colspan="2" style="text-align:center"><input type="submit" name="BtnOk" value="OK" class="btn"></td>
            </tr>
        </table>
    </form>

    <script>
        function BtnGet_OnClick() {
            HttpRequest(
                '/api/get_empty_scheme1',
                function(aData) {
                    console.log("aData", aData);
                    if (Object.keys(aData).length == 0) {
                        alert("request error")
                    }else{
                        document.getElementById("Url").value = aData["Data"]["site.url"];
                    }
                },
                {}
            );
        };
    </script>
<!-soup_get.tpl end-->
{% endblock %}
