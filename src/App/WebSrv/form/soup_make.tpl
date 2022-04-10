{% extends "Layout.tpl" %}

{% block content %}
<!--soup_make.tpl begin-->
    <form name="FormParse" method="post" action="/form/soup_make?action=go" enctype="multipart/form-data">
        <table style="width:100%">
          <tr>
            <td>Url</td>
            <td colspan="6">
            <input type="text" name="Url" placeholder="url" style="width:100%" value="{{ Form.Url }}" required>
            </td>  
          </tr>
          <tr>
            <td>Path</td>
            <td colspan="6">
            <input type="text" name="Path" placeholder="path script" style="width:100%" value="{{ Form.Path }}">
            </td>  
          </tr>
          <tr>
            <td>Section</td>
            <td>Name</td>
            <td>Price</td>
            <td>PriceOld</td>
            <td>Stock</td>
            <td>Image</td>
            <td>SKU</td>
          </tr>
          <tr>
            <td>Script</td>
            <td><textarea name="Script_Name"     rows="6">{{ Form.Script_Name }}</textarea></td>
            <td><textarea name="Script_Price"    rows="6">{{ Form.Script_Price }}</textarea></td>
            <td><textarea name="Script_PriceOld" rows="6">{{ Form.Script_PriceOld }}</textarea></td>
            <td><textarea name="Script_Stock"    rows="6">{{ Form.Script_Stock }}</textarea></td>
            <td><textarea name="Script_Image"    rows="6">{{ Form.Script_Image }}</textarea></td>
            <td><textarea name="Script_SKU"      rows="6">{{ Form.Script_SKU }}</textarea></td>
          </tr>
          <tr>
            <td>Output</td>
            <td colspan="6"><textarea readonly name="Output" rows="30">{{ Form.Output }}</textarea></td>  
          </tr>
         <tr>
            <td colspan="7" style="text-align:center"><input type="submit" name="btn" value="OK" class="btn"></td>
         </tr>
        </table>
    </form>
<!-soup_make.tpl end-->
{% endblock %}
