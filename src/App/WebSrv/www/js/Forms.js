/*
opyright:    Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.05.15-2
*/


function BtnGetSchemeEmpty_OnClick() {
    HttpRequest(
        '/api/get_scheme_empty',
        function(aData) {
            console.log('aData', aData);
            let Dbl = new TDbList(aData['Data']['Data']);
            let Rec = Dbl.Shuffle();
            document.getElementById('Url0').value = Rec.GetField('url');
            document.getElementById('Script').value = '';
          },
        {'cnt': 10}
    );
};

function ClearObj(aTagName) {
    let Items = document.getElementsByTagName(aTagName);
    for (let i = 0; i < Items.length; i++) {
        if (Items[i].type.startsWith('text')) {
            Items[i].value = '';
        }
    }
}
