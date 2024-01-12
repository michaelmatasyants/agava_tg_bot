import asyncio

from django.core.management.base import BaseCommand

from users.bot import bot


class Command(BaseCommand):
    help = "Start Telegram bot"

    def handle(self, *args, **options):
        asyncio.run(bot.main())
