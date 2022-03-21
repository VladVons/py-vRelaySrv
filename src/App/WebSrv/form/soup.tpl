{% extends "Layout.tpl" %}

{% block content %}
<!--soup.tpl begin-->
<form name="FFS" method="post" action="/form/soup?action=go"" enctype="multipart/form-data">
    <table width="100%" border="1" cellspacing="0" cellpadding="0"
        <tr>
            <td align="left">url</td>
            <td align="left"><input type="text" id="uname" name="name" placeholder="check url" size="60"></td>
        </tr>
        <tr>
            <td>Script</td>
            <td align="left"><textarea name="Script" cols="60" rows="10"></textarea></td>
        </tr>
        <tr>
            <td>Result</td>
            <td align="left"><textarea readonly name="Output" cols="60" rows="10"></textarea></td>
        <tr>
            <td>&nbsp;</td>
            <td>&nbsp;</td>
        </tr>
        <tr>
            <td>&nbsp;</td>
            <td align="left"><input name="Url_Images" type="submit" value="OK"/></td>
        </tr>
    </table>
</form>
<!-soup.tpl end-->
{% endblock %}
