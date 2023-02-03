# Created: 2023.02.01
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


from .DbFields import TDbFields
from .DbList import TDbList


class TDbSql(TDbList):
    Table = ''

    def Export(self, aWithType: bool = True) -> dict:
        Res = super().Export(aWithType)
        Res['Table'] = self.Table
        return Res

    def Import(self, aData: dict, aWithType: bool = True) -> 'TDbSql':
        super().Import(aData, aWithType)
        self.Table = aData.get('Table')
        return self

    def GetSqlInsert(self, aTable: str, aReturning: list[str] = None) -> str:
        if (self.GetSize() > 0):
            Fields = [Val[0] for Key, Val in self.Fields.IdxOrd.items()]
            Fields = ', '.join(Fields)
            Values = [Rec.GetAsSql() for Rec in self]
            Values = '), ('.join(Values)
        else:
            Fields = ''
            Values = 'default values'

        Returning = 'returning ' + ', '.join(aReturning) if aReturning else ''
        return f'''
            insert into {aTable}
            {Fields}
            {Values}
            {Returning}
        '''

    def GetSqlUpdate(self, aTable: str, aRecNo: int = 0) -> str:
        self.RecNo = aRecNo
        return 'update %s set %s' % (aTable, self.Rec.GetAsSql())

    def GetSqlInsertUpdate(self, aTable: str, aUniqField: str) -> str:
        Insert = self.GetSqlInsert(aTable)
        Set = [
            '%s = excluded.%s' % (Key, Key)
            for Key in self.Fields
            if (Key != aUniqField)
        ]
        Set = ', '.join(Set)

        return f'''
            {Insert}
            on conflict ({aUniqField}) do update
            set {Set}
            returning id;
        '''
