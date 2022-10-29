# Created: 2022.10.29
# Author: Vladimir Vons <VladVons@gmail.com>
# License: GNU, see LICENSE for more details


import os
import asyncio
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import aiosmtplib
#
from Inc.DataClass import DataClass


@DataClass
class TMailSmtp():
    username: str
    password: str
    hostname: str = 'smtp.gmail.com'
    port: int = 465
    use_tls: bool = True


@DataClass
class TMailSend():
    To: str
    Subject: str
    From: str
    Body: str = ''
    File: list[str] = []
    Data: dict = {}
    Lock: asyncio.Lock = None


class TMail():
    def __init__(self, aMailSmtp: TMailSmtp):
        self._MailSmtp = aMailSmtp

    async def Send(self, aData: TMailSend):
        EMsg = MIMEMultipart()
        EMsg['From'] = aData.From
        EMsg['To'] = ', '.join(aData.To)
        EMsg['Subject'] = aData.Subject
        if (aData.Body):
            EMsg.attach(MIMEText(aData.Body))

        for File in aData.File:
            with open(File, 'rb') as F:
                Part = MIMEApplication(F.read(), Name=os.path.basename(File))
                Part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(File)
                EMsg.attach(Part)

        for Key, Stream in aData.Data.items():
            Stream.seek(0)
            Part = MIMEApplication(Stream.read(), Name=Key)
            Part['Content-Disposition'] = f'attachment; filename="{Key}"'
            EMsg.attach(Part)
            Stream.close()

        Smtp = self._MailSmtp.__dict__
        await aiosmtplib.send(EMsg, **Smtp)
