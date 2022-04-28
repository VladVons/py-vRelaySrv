    async def _GetSelectFields_0(self, aQuery: str) -> list:
        # ToDo
        if ('from' in aQuery.lower()):
            Pattern = 'select(.*)from'
        else:
            Pattern = 'select(.*)'

        Match = re.search(Pattern, aQuery, re.DOTALL | re.IGNORECASE)
        if (Match):
            Res = []
            for Item in  Match.group(1).split(','):
                Name = Item.strip().split()[-1]
                Arr = Name.split('.*')
                if (len(Arr) == 2):
                    Columns = await self._Db.GetTableColumns(Arr[0])
                    for Column in Columns:
                        Res.append(Column[0])
                # skip comma inside functions
                elif (not [x for x in '()' if (x in Name)]):
                    Res.append(Name)
            return Res

