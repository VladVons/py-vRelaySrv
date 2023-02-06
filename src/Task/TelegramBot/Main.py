# Created: 2022.04.14
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details

# UaWebScraper
# UaWebScraperBot


import asyncio
from aiogram.dispatcher.webhook import SendMessage
from aiogram import Bot, Dispatcher, executor, types
#
from Task.WebSrv import Api
from Inc.Db.DbList import TDbListSafe, TDbCond
from Inc.Util.Obj import DeepGet
from IncP.Log import Log


class TMain():
    def __init__(self, aConf: dict):
        self.Conf = aConf

    async def cmd_def(self, message: types.Message):
        await message.reply('unknown command')

    async def cmd_start(self, message: types.Message):
        DataA = await Api.DefHandler('get_sites')
        Data = DeepGet(DataA, 'Data.Data')
        if (Data):
            Dbl = TDbListSafe().Import(Data)
            Cond = TDbCond().AddFields([ ['eq', (Dbl, 'has_scheme'), True, True]])
            Dbl = Dbl.Clone(aFields=['url'], aCond=Cond)

            #return SendMessage(chat_id=message.chat.id, text='Hi from webhook!', reply_to_message_id=message.message_id)
            await message.reply('Hello from WebScraper bot!')
            await message.reply(str(Dbl))


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
