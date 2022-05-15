/*
opyright:    Vladimir Vons, UA
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.05.15
*/


function BtnGetSchemeEmpty_OnClick() {
    HttpRequest(
        '/api/get_scheme_empty',
        function(aData) {
            console.log('aData', aData);
            let DbL = new TDbList(aData['Data']['Data']);
            let Rec = DbL.Shuffle();
            document.getElementById('Url').value = Rec.GetField('url');
            document.getElementById('Script').value = '';
          },
        {'cnt': 10}
    );
};

function BtnGetSchemeDone_OnClick() {
    HttpRequest(
        '/api/get_scheme_not_empty',
        function(aData) {
            console.log('aData', aData);
            let DbL = new TDbList(aData['Data']['Data']);
            let Rec = DbL.Shuffle();
            document.getElementById('Url').value = Rec.GetField('url');
            document.getElementById('Script').value = Rec.GetField('scheme');
          },
        {'cnt': 10}
    );
};
