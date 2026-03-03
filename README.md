# AI Hackaton

Проект был создан в рамках ИИ Хакатона университета УУНиТ. Обучена модель Yolo на сегментацию растений рукколы/пшеницы. Нейросеть сегментирует растение на лепестки, стебель, корень и автоматически подсчитывает длину и площадь всех сегментов, а также классифицирует растение. Датасет был предоставлен УФИЦ РАН.

## Характеристики модели

- **Box**:
    - **Precision**:

    - **Recall**:

    - **Mask50**:

    - **Mask50-95**:

- **Mask**:
    - **Precision**:

    - **Recall**:

    - **Mask50**:

    - **Mask50-95**:

## Установка

### 1. Проверка работы

Проверить работу сайта можно по [ссылке](http://94.41.18.199:3000/)

### 2. Установка через Docker

Для установки через docker вам понадобится docker и docker-compose:

```
docker compose up --build
```

в корне проекта

### 3. Пошаговая установка

3.1 Установить venv и зайти в нее

```
python -m venv .venv

.venv\Scripts\Activate
```

в папке **model**

3.2 Установить pytorch

```
pip install torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cu118
```

3.3 Установить ultralytics и thop

```
pip install ultralytics==8.4.18 ultralytics-thop==2.0.18
```

3.4 Установить базовые библиотеки

```
pip install -r requirements.txt
```

3.5 Загрузите датасет в папку model (папка dataset)

3.6 Выполните аугментацию (augmentation.py)

3.7 Для обучения модели запустите train.py

3.8 После обучения переместите папку модели в model/runs/segment
