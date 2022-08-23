# Установка

1. Создать файл локальных настроек (обязательно)
```
carparts$ touch app/settings_local.py
```
2. Указать логин и пароль для сайта (опционально, пока поддерживается только emex). Если логин не указать, запрос будет сделан от анонимного пользователя.
```
# settings_local.py
EMEX_LOGIN = 'login'
EMEX_PASSWORD = 'password'
```
3. Создать virtual env
```
carparts$ python3 -m venv venv
```
4. Активировать virtual env
```
carparts$ source venv/bin/activate
```
5. Установить пакеты
```
(venv) carparts$ pip install -r requirements.txt
```
6. В папку `input` положить csv файлы с информацией о запчастях. Парсер прочитает каждый файл и сложит все связанные данные с сайта в соответствующий файл в выходной директории. Пример.

Ввод:
```
# input/toyota.csv
9091510001,toyota
1740874020,toyota

# input/kashiyama.csv
D2023,kashiyama
D2118,kashiyama
```

Вывод:
```
# output/toyota_output.csv
code,id,manufacturer,part_number,rating,description,amount,price,working_hours,delivery_duration
9091510001,W0UKE71QGF1MCRU4,Toyota,90915-10001,4.9,ФИЛЬТР МАСЛЯНЫЙ,8,1033,,2 дня
```
7. Запустить парсер
```
(venv) carparts$ cd app
(venv) carparts/app$ python main.py
```

# CLI

## Помощь

Чтобы посмотреть доступные аргументы нужно запустить скрипт с аргументом `-h`:

```
(venv) carparts/app$ python main.py -h
usage: main.py [-h] [--loglevel {info,warning,error}] [--output OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  --loglevel {info,warning,error}
                        Set log level
  --output OUTPUT       Comma-separated list of writers (csv and xlsx
                        supported)
```

## Логирование

По умолчанию лог складывается в `log/parser.log`. Поддерживается несколько уровней логирования:
1. info - логировать всё
2. warning - логировать только предупреждения
3. error - логировать только ошибки и исключения

## Формат вывода

Поддерживается два варианта вывода данных: csv и xslx. Оба вместе или по отдельности:
```
python main.py --output=csv
python main.py --output=xlsx
python main.py --output=csv,xlsx
```
Каждый форматтер создаёт свой собственный файл.

**Предупреждение**: не открывать файлы в выходной директории чтобы дать парсеру возможность записать файлы без ошибок.
