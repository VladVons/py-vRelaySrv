<!doctype html>
<html>
  <head>
    {% block head %}
    <link rel="stylesheet" href="/www/style.css?q=3.2" type="text/css">
    <title>{{ Form.Title }}</title>
    {% endblock %}
  </head>

  <body>
    <div id="content">
        {% block content %}{% endblock %}
    </div>

    <div id="footer" class="app-footer">
        <a href="http://oster.com.ua">VladVons@gmail.com, 2022</a>
    </div>
  </body>

</html>