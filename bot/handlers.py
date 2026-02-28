from aiogram import Router, types, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import sys
import os
import aiohttp
import asyncio

from config import API_URL
import keyboard as kb

router = Router()

class PhotoState(StatesGroup):
    waiting_for_photo = State()

@router.callback_query(F.data == "load_photo")
@router.message(F.text == "Отправить фото")
async def process_load_photo(message: types.Message | types.CallbackQuery, state: FSMContext):
    text = "Пожалуйста, отправьте фотографию растения для анализа."
    if isinstance(message, types.CallbackQuery):
        await message.message.answer(text, reply_markup=kb.main)
        await message.answer()
    else:
        await message.answer(text, reply_markup=kb.main)
    await state.set_state(PhotoState.waiting_for_photo)

@router.callback_query(F.data == "help")
@router.message(F.text == "О проекте")
async def process_help(message: types.Message | types.CallbackQuery):
    text = "Я могу помочь тебе с анализом растений! Просто отправь мне фотографию, и я сегментирую её на корень, стебель и листья, вычисляя их длину и площадь. Если у тебя есть вопросы, не стесняйся спрашивать!"
    if isinstance(message, types.CallbackQuery):
        await message.message.answer(text, reply_markup=kb.main)
        await message.answer()
    else:
        await message.answer(text, reply_markup=kb.main)




@router.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer("<b>🌿 ИИ-анализатор Пшеницы и Рукколы</b>\n\nПривет! Я сегментирую растение на <b>корень, стебель и листья</b>, вычисляя их длину и площадь.\n\nПроект создан для <b>ИИ-Хакатона</b> на базе технологий <i>YOLO</i> и данных <i>УФИЦ РАН</i>.\n\n📸 <b>Отправь фото для анализа!</b>", reply_markup=kb.main)
    await message.answer("Выберите действие:", reply_markup=kb.first)
