{% extends "Layout.tpl" %}

{% block content %}
<!--soup_get.tpl begin-->
<form name="FormParse" method="post" action="/form/soup_get?action=go" onsubmit="return validateForm()" enctype="multipart/form-data">
    <table width="100%" class="table1">
        <tr>
            <td>url</td>
            <td>
                <input type="text" name="Url" placeholder="url" style="width:100%" required value="{{ Form.Url }}">
            </td>
        </tr>
        <tr>
            <td>Find</td>
            <td>
                <input type="text" name="Find" placeholder="text" style="width:100%" required value="{{ Form.Find }}">
            </td>
        </tr>
        <tr>
            <td>Result</td>
            <td>
                <textarea readonly name="Output" rows="30" style="width:100%" wrap='off'>{{ Form.Output }}</textarea>
            </td>
        <tr>
            <td>&nbsp;</td>
            <td>&nbsp;</td>
        </tr>
        <tr>
            <td>&nbsp;</td>
            <td align="center">
                <input type="submit" name="btn" value="OK" class="btn"> 
            </td>
        </tr>
    </table>
</form>
<!-soup_get.tpl end-->
{% endblock %}
