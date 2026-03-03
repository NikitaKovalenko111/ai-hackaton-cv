from aiogram import Router, types, F, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import io
import aiohttp
import base64
import logging


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
    text = "<b>🌿 ИИ-Анализатор растений</b>\n\nЭтот бот разработан в рамках <b>ИИ-Хакатона</b> (27.02.2026 — 09.03.2026) при поддержке <b>Уфимского университета науки и технологий</b> и <b>УФИЦ РАН</b>.\n\n<b>👨‍💻 Команда разработчиков:</b> \nБайсалямов Р.Д. \nСтрельников Д.И. \nКоваленко Н.Н. \nМиргазямов С.И.\n\n<b>Что я умею:</b>\n• <b>Сегментация:</b> распознаю корень, стебель и листья пшеницы и рукколы.\n• <b>Измерения:</b> вычисляю длину и площадь корня/стебля, а также площадь листьев.\n• <b>Технологии:</b> использую Ultralytics YOLO и сервис RoboFlow.\n• <b>Данные:</b> предоставлены Институтом биохимии и генетики УФИЦ РАН.\n\n<b><i>«ТВОЙ КОД ИМЕЕТ ЗНАЧЕНИЕ!»</i></b>"
    if isinstance(message, types.CallbackQuery):
        await message.message.answer(text, reply_markup=kb.main)
        await message.answer()
    else:
        await message.answer(text, reply_markup=kb.main)


@router.message(PhotoState.waiting_for_photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext, bot: Bot):
    logging.info("Начало обработки фото")
    input_buffer = io.BytesIO()
    await bot.download(message.photo[-1], destination=input_buffer)
    input_buffer.seek(0)
    logging.info("Фото скачано в буфер")

    msg = await message.answer("🔄 Обработка и отправка...")

    try:
        logging.info(f"Отправка запроса на {API_URL}")
        timeout = aiohttp.ClientTimeout(total=400)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            data = aiohttp.FormData()
            data.add_field(
                'file',
                input_buffer,
                filename='image.jpg',
            content_type = 'image/jpeg'
            )

            logging.info("Начинаем запрос...")
            logging.info(data)
            async with session.post(API_URL, data=data) as resp:

                logging.info(f"Ответ сервера получен. Статус: {resp.status}")
                if resp.status == 200:
                    try:
                        result = await resp.json()
                        logging.info(f"JSON получен: {result}")
                    except Exception as json_err:
                        logging.error(f"Ошибка парсинга JSON: {json_err}")
                        text_resp = await resp.text()
                        logging.info(f"Текст ответа: {text_resp}")
                        await msg.edit_text(f"Ошибка API: Некорректный JSON.\n{text_resp[:100]}...")
                        return

                    resp_image_b64 = result.get("image_base64")
                    detections = result.get("detections", [])
                    lines = ["📊 <b>Результаты анализа:</b>\n"]

                    class_map = {
                        "root": "Корень",
                        "stem": "Стебель",
                        "leaf": "Лист"
                    }

                    if not detections:
                        lines.append("❌ Объекты не обнаружены.")
                    else:
                        detections = list(detections)
                        detections.sort(key=lambda x: x["class_name"])
                        for i, det in enumerate(detections):
                            raw_class = det.get("class_name", "unknown")
                            class_name = class_map.get(raw_class, raw_class.capitalize())
                            length_cm = det.get("length_cm", 0)
                            confidence = det.get("confidence", 0)

                            lines.append(f"{i + 1}) <b>{class_name}</b>: {length_cm} см (Точность: {int(confidence * 100)}%)")

                    resp_text = "\n".join(lines)

                    if resp_image_b64:
                        logging.info("Есть картинка в base64, декодируем...")
                        image_data = base64.b64decode(resp_image_b64)
                        await message.answer_photo(
                            photo=types.BufferedInputFile(image_data, filename="result.png"),
                            caption=resp_text
                        )
                        await msg.delete()
                    else:
                        logging.info(f"Картинки нет. Текст: {resp_text}")
                        await msg.edit_text(f"Результат: {resp_text}")
                else:
                    error_text = await resp.text()
                    logging.error(f"Ошибка сервера {resp.status}: {error_text}")
                    await msg.edit_text(f"Ошибка сервера: {resp.status}\n{error_text}")

    except Exception as e:
        logging.exception(f"ИСКЛЮЧЕНИЕ: {e}")
        await msg.edit_text(f"⚠️ Ошибка при обработке.")
    finally:
        input_buffer.close()
        await state.clear()


@router.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer("<b>🌿 ИИ-анализатор Пшеницы и Рукколы</b>\n\nПривет! Я сегментирую растение на <b>корень, стебель и листья</b>, вычисляя их длину и площадь.\n\nПроект создан для <b>ИИ-Хакатона</b> на базе технологий <i>YOLO</i> и данных <i>УФИЦ РАН</i>.\n\n📸 <b>Отправь фото для анализа!</b>", reply_markup=kb.main)
    await message.answer("Выберите действие:", reply_markup=kb.first)
