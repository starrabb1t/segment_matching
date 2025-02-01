# segment_matching

### 1. Dependencies

`sudo apt-get install python3-tk`
`pip install -r requirements.txt`

### 2. Tracker App

`./src/tracker.py`

`Open` - открыть видео \
`Play/Pause` - проиграть видео или поставить на паузу \
`Track` (checkbox) - если активно, то при проигрывании происходит трекинг \
`Stop Track` - остановить трекер для заданного object_id (будет вызвано диалоговое окно). Доступно только во время паузы \
`Export JSON` - экспорт размеченных таймлайнов из памяти в JSON (будет вызвано диалоговое окно) \
`List` - вывести в консоль список всех object_id в памяти \
`Del` - удалить все данные, ассоциированные с заданным object_id (будет вызвано диалоговое окно). Трекинг для object_id будет оставновлен 

### 3. Matcher

`./src/match.py`

Пример использования:

```
with open('data/json/1.json', 'r') as f:
    record_1 = json.loads(f.read())

with open('data/json/2.json', 'r') as f:
    record_2 = json.loads(f.read())

result_iou, result_map = match(record_1, record_2, True)

```