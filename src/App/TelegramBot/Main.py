'''
Author:      Vladimir Vons <VladVons@gmail.com>
Created:     2022.04.14
License:     GNU, see LICENSE for more details

UaWebScraper
UaWebScraperBot
'''


import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.webhook import SendMessage

#
from Inc.DB.DbList import TDbList, TDbCond
from IncP.Utils import GetNestedKey
from IncP.Log import Log
from App.WebSrv import Api


class TMain():
    def __init__(self, aConf: dict):
        self.Conf = aConf

    async def cmd_def(self, message: types.Message):
        await message.reply('unknown command')

    async def cmd_start(self, message: types.Message):
        DataA = await Api.WebClient.Send('web/get_sites')
        Data = GetNestedKey(DataA, 'Data.Data')
        if (Data):
            Dbl = TDbList().Import(Data)
            Cond = TDbCond().AddFields([ ['eq', (Dbl, 'has_scheme'), True, True]])
            Dbl = Dbl.Clone(aFields=['url'], aCond=Cond)
            DblRepr = Dbl._Repr(35)

            #return SendMessage(chat_id=message.chat.id, text='Hi from webhook!', reply_to_message_id=message.message_id)
            await message.reply('Hello from WebScraper bot!')
            await message.reply(DblRepr)


    async def Run(self):
        asyncio.sleep(1)
        Log.Print(1, 'i', 'TelegramBot')

        Token = self.Conf.get('Token')
        bot = Bot(token=Token)
        dp = Dispatcher(bot)
        dp.register_message_handler(self.cmd_start, commands=['start'])
        dp.register_message_handler(self.cmd_def)

        #executor.start_polling(dp, skip_updates=True)
        exe = executor.Executor(dp, skip_updates=True)
        try:
            #exe.on_startup(self.OnStartup)
            await exe.dispatcher.start_polling()
        finally:
            await exe.dispatcher.wait_closed()
            exe.dispatcher.stop_polling()
