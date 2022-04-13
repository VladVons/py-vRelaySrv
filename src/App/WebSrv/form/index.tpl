{% extends "Layout.tpl" %}

{% block content %}
<!--index.tpl begin-->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js"></script>
    <link href="/www/index.css" type="text/css"/>

    <table style="width:100%">
        <tr>
            <td><a href="form/soup_get">soup get</a></td>
        </tr>
        <tr>
            <td><a href="form/soup_make">soup make</a></td>
        </tr>
        <tr>
            <td><a href="form/soup_test">soup test</a></td>
        </tr>
        <tr>
            <button id="btn">AJAX test</button>
            <div id="animal-info"></div>
         </tr>
    </table>

    <script src="/www/ajax.js"></script>
<!--index.tpl end-->
{% endblock %}
