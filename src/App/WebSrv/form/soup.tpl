{% extends "Layout.tpl" %}

{% block content %}
<!--soup.tpl begin-->


<form name="FormParse" method="post" action="/form/soup?action=go" onsubmit="return validateForm()" enctype="multipart/form-data">
    <table width="100%" class="table1">
        <tr>
            <td>url</td>
            <td>
                <input type="text" name="url" placeholder="url" style="width:100%" required value="{{ Form.Url }}">
            </td>
        </tr>
        <tr>
            <td>Script</td>
            <td>
                <textarea name="script" class="lined" rows="30" style="width:110%" wrap="off" required>{{ Form.Script }}</textarea>
            </td>
        </tr>
        <tr>
            <td>Result</td>
            <td>
                <textarea readonly name="output" rows="10" style="width:100%" wrap='off'>{{ Form.Output }}</textarea>
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

<!-soup.tpl end-->
{% endblock %}
