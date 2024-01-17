import asyncio
import os

import emoji
from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from aiogram.utils.deep_linking import create_start_link
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
    send_casino_url = State()
    send_ref_link = State()


@router.message(Command('help'))
async def process_help(message: Message):
    await message.answer(text=LEXICON['help'])


@router.message(CommandStart())
@router.message(CommandStart(), StateFilter(default_state))
async def process_start(message: Message, state: FSMContext):
    if ' ' in message.text:
        if not TgUser.objects.filter(tg_id=message.chat.id):
            inviter_tg_id = int(message.text.split(' ')[-1])
            await state.update_data(inviter_tg_id=inviter_tg_id)
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
            text_message = LEXICON['completed'].format('1')
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text=LEXICON['yes_btn'],
                                         callback_data=LEXICON['yes_btn'])
                ]
            ])
            await message.answer(text=text_message,
                                 reply_markup=markup)
            await state.set_state(FSMUserForm.send_squad_url)
        elif not user.got_free_dep:
            text_message = LEXICON['completed'].format('2')
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text=LEXICON['yes_btn'],
                                         callback_data=LEXICON['yes_btn'])
                ]
            ])
            await message.answer(text=text_message,
                                 reply_markup=markup)
            await state.set_state(FSMUserForm.send_casino_url)
        else:
            text_message = LEXICON['no_tasks'].format(message.chat.full_name)
            markup = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text=LEXICON['invite_btn'],
                                     callback_data=LEXICON['invite_btn'])
            ]])
            await message.answer(text=text_message, reply_markup=markup)
            await state.set_state(FSMUserForm.send_ref_link)


@router.callback_query(F.data == LEXICON['start_btn'],
                       StateFilter(FSMUserForm.send_group_url))
async def process_join_group(callback: CallbackQuery, state: FSMContext):
    text_message = LEXICON['subscribe']
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON['join_group_btn'],
                                 url=settings.GROUP_URL)
        ],
        [
            InlineKeyboardButton(text=LEXICON['subscribe_btn'],
                                 callback_data=LEXICON['subscribe_btn'])
        ]
    ])
    await callback.message.answer(text=text_message, reply_markup=reply_markup)
    await callback.answer()
    await state.set_state(FSMUserForm.join_group)


@router.callback_query(StateFilter(FSMUserForm.join_group))
@router.callback_query(F.data == LEXICON['subscribe_btn'],
                       StateFilter(FSMUserForm.join_group))
async def check_join_group(callback: CallbackQuery, state: FSMContext):
    text_message = LEXICON['subscibe_2']
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON['join_group_btn'],
                                 url=settings.GROUP_URL)
        ],
        [
            InlineKeyboardButton(text=LEXICON['subscribe_btn'],
                                 callback_data=LEXICON['subscribe_btn'])
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
            answers = await state.get_data()
            if answers:
                inviter = TgUser.objects.get(tg_id=answers['inviter_tg_id'])
                inviter.friends = user
                inviter.save()
                text_message = LEXICON['invited'].format(user.nickname)
                await bot.send_message(chat_id=answers['inviter_tg_id'],
                                       text=text_message)
            text_message = LEXICON['completed'].format('1')
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text=LEXICON['yes_btn'],
                                         callback_data=LEXICON['yes_btn'])
                ]
            ])
            await callback.message.answer(text=text_message,
                                          reply_markup=markup)
            await state.set_state(FSMUserForm.send_squad_url)
        else:
            await callback.message.answer(text=text_message,
                                          reply_markup=reply_markup)


@router.callback_query(F.data == LEXICON['yes_btn'],
                       StateFilter(FSMUserForm.send_squad_url))
async def process_join_squad(callback: CallbackQuery, state: FSMContext):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON['join_btn'],
                                 url=settings.NOTCOIN_REFERAL_URL)
        ],
        [
            InlineKeyboardButton(text=LEXICON['next_btn'],
                                 callback_data=LEXICON['next_btn'])
        ]
    ])
    await callback.message.answer(text=LEXICON['squad'],
                                  reply_markup=markup)
    user = TgUser.objects.get(tg_id=callback.from_user.id)
    user.joined_squad = True
    user.save()
    await state.set_state(FSMUserForm.send_casino_url)


@router.callback_query(F.data == LEXICON['next_btn'],
                       StateFilter(FSMUserForm.send_casino_url))
@router.callback_query(F.data == LEXICON['yes_btn'],
                       StateFilter(FSMUserForm.send_casino_url))
async def send_casino_url(callback: CallbackQuery, state: FSMContext):
    markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=LEXICON['enter_btn'],
                                     url=settings.GAME_LINK)
            ],
            [
                InlineKeyboardButton(text=LEXICON['next_btn'],
                                     callback_data=LEXICON['next_btn'])
            ]
    ])
    user = TgUser.objects.get(tg_id=callback.from_user.id)
    user.got_free_dep = True
    user.save()
    await callback.message.answer(text=LEXICON['casino'],
                                  reply_markup=markup)
    await state.set_state(FSMUserForm.send_ref_link)


@router.callback_query(F.data == LEXICON['next_btn'],
                       StateFilter(FSMUserForm.send_ref_link))
@router.callback_query(F.data == LEXICON['yes_btn'],
                       StateFilter(FSMUserForm.send_ref_link))
async def invite_friends(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text=LEXICON['invite'])
    await asyncio.sleep(1)
    referal_url = await create_start_link(bot=bot,
                                          payload=callback.from_user.id)
    await callback.message.answer(text=LEXICON['invite_link'])
    await callback.message.answer(text=referal_url)
    await state.clear()
