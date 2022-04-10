{% extends "Layout.tpl" %}

{% block content %}
<!--soup_test.tpl begin-->
    <form name="FormParse" method="post" action="/form/soup_test?action=go" enctype="multipart/form-data">
        <table width="100%">
            <tr>
                <td>url</td>
                <td><input type="text" name="Url" placeholder="url" style="width:100%" required value="{{ Form.Url }}"></td>
            </tr>
            <tr>
                <td>Script</td>
                <td><textarea name="Script" class="lined" rows="30" required>{{ Form.Script }}</textarea></td>
            </tr>
            <tr>
                <td>Output</td>
                <td><textarea readonly name="Output" rows="10">{{ Form.Output }}</textarea></td>
            <tr>
                <td colspan="2" style="text-align:center"><input type="submit" name="btn" value="OK" class="btn"></td>
            </tr>
        </table>
    </form>

    <link href="/www/jquery-linedtextarea.css" type="text/css" rel="stylesheet"/>
    <script src="https://code.jquery.com/jquery-1.12.4.min.js"></script>
    <script src="/www/jquery-linedtextarea.js"></script>
    <script>
        $(function() {
            $(".lined").linedtextarea(
                {selectedLine: 0}
            );
        });
    </script>
<!-soup_test.tpl end-->
{% endblock %}