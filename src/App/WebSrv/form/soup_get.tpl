{% extends "Layout.tpl" %}

{% block content %}
    </style>
    <form name="FormParse" method="post" action="/form/soup_get?action=go" enctype="multipart/form-data">
        <table style="width:100%">
            <tr>
                <th></th>
                <th style="width :90%"></th>
            <tr>
                <td>url</td>
                <td style="width:90%"><input type="text" name="Url" placeholder="url" style="width:100%" required value="{{ Form.Url }}"></td>
            </tr>
            <tr>
                <td>Find regEx</td>
                <td><input type="text" name="Find" placeholder="text" style="width:100%" required value="{{ Form.Find }}"></td>
            </tr>
            <tr>
                <td>Output</td>
                <td><textarea readonly name="Output" rows="30">{{ Form.Output }}</textarea> </td>
            <tr>
            <tr>
                <td colspan="2" style="text-align:center"><input type="submit" name="btn" value="OK" class="btn"></td>
            </tr>
        </table>
    </form>
<!-soup_get.tpl end-->
{% endblock %}
