import asyncio
import os

import emoji
from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.markdown import hlink
from django.conf import settings

from users.models import TgUser

from .lexicon import LEXICON

os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'True'
storage = MemoryStorage()
router = Router()
bot = Bot(settings.BOT_TOKEN)


class FSMUserForm(StatesGroup):
    send_group_url = State()
    join_group = State()
    send_squad_url = State()
    join_squad = State()
    send_casino_url = State()
    join_casino = State()
    send_ref_link = State()


@router.message(CommandStart())
@router.message(CommandStart(), StateFilter(default_state))
async def start_process(message: Message, state: FSMContext):
    await state.clear()
    text_message = emoji.emojize(
        LEXICON['greeting'].format(message.chat.full_name)
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON['start_btn'],
                                 callback_data=LEXICON['start_btn'])
        ]
    ])
    try:
        user = TgUser.objects.get(tg_id=message.chat.id)
    except TgUser.DoesNotExist:
        await message.answer(text=text_message,
                             reply_markup=markup,
                             parse_mode='HTML')
        await state.set_state(FSMUserForm.send_group_url)
    else:
        if not user.joined_agava_crypto:
            await message.answer(text=text_message,
                                 reply_markup=markup,
                                 parse_mode='HTML')
            await state.set_state(FSMUserForm.send_group_url)
        elif not user.joined_squad:
            await state.set_state(FSMUserForm.send_squad_url)
        elif not user.got_free_dep:
            await state.set_state(FSMUserForm.send_casino_url)
        else:
            text_message = LEXICON['no_tasks'].format(message.chat.full_name)
            await message.answer(text=text_message)
            await state.set_state(FSMUserForm.send_ref_link)


@router.callback_query(F.data == LEXICON['start_btn'],
                       StateFilter(FSMUserForm.send_group_url))
async def process_join_group(callback: CallbackQuery, state: FSMContext):
    text_message = LEXICON['subscribe']
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON['subscribe_btn'],
                                 url=settings.GROUP_URL)
        ],
        [
            InlineKeyboardButton(text=LEXICON['next_btn'],
                                 callback_data=LEXICON['next_btn'])
        ]
    ])
    await callback.message.answer(text=text_message, reply_markup=reply_markup)
    await callback.answer()
    await state.set_state(FSMUserForm.join_group)


@router.callback_query(StateFilter(FSMUserForm.join_group))
@router.callback_query(F.data == LEXICON['next_btn'],
                       StateFilter(FSMUserForm.join_group))
async def check_join_group(callback: CallbackQuery, state: FSMContext):
    text_message = LEXICON['subscibe_2']
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON['subscribe_btn'],
                                 url=settings.GROUP_URL)
        ],
        [
            InlineKeyboardButton(text=LEXICON['next_btn'],
                                 callback_data=LEXICON['next_btn'])
        ]
    ])
    try:
        user_status = await bot.get_chat_member(chat_id=settings.GROUP_ID,
                                                user_id=callback.from_user.id)
    except TelegramBadRequest:
        await callback.message.answer(text=text_message,
                                      reply_markup=reply_markup)
        await state.set_state(FSMUserForm.join_group)
    else:
        if str(user_status.status) in ['ChatMemberStatus.MEMBER',
                                       'ChatMemberStatus.CREATOR']:
            user = TgUser.objects.create(nickname=callback.from_user.username,
                                         tg_id=callback.from_user.id,
                                         joined_agava_crypto=True)
            user.save()
            await state.set_state(FSMUserForm.send_squad_url)
        else:
            await callback.message.answer(text=text_message,
                                          reply_markup=reply_markup)
            await state.set_state(FSMUserForm.join_group)


@router.message(FSMUserForm.send_squad_url)
@router.callback_query(F.data == LEXICON['next_btn'],
                       StateFilter(FSMUserForm.send_squad_url))
async def process_join_squad(handled: Message | CallbackQuery,
                             state: FSMContext):
    if isinstance(handled, Message):
        message = handled
    else:
        message = handled.message
    await message.answer(text='process_join_squad')
    await state.set_state(FSMUserForm.join_squad)


# @router.callback_query(StateFilter(FSMUserForm.join_squad))
# async def send_game(message: Message, state: FSMContext):
#     print('send_game')
#     markup = InlineKeyboardMarkup(inline_keyboard=[
#             [InlineKeyboardButton(text=LEXICON['play_game_btn'],
#                                   url=settings.GAME_LINK)]]
#     )
#     await message.answer(text=LEXICON['second_link'],
#                          reply_markup=markup)
#     await message.answer(text=LEXICON['second_link'],
#                          reply_markup=markup)
#