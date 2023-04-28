# Телеграм бот поиска ближайших кафе, баров, ресторанов и т.д.  

_Telegram bot search for the nearest cafes, bars, restaurants, etc._  
_**Основной стэк**_:  
![Python](https://img.shields.io/badge/python-3.11-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-4.1-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Aiogram](https://img.shields.io/badge/Aiogram-2-ff1709?style=for-the-badge&logo=aiogram&logoColor=white&color=ff1709&labelColor=gray)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

**В ситуации, когда срочно необходимо найти уютное местечко с любимым
напитком ничего лучше вам не поможет.  
Это был хороший повод, чтобы
попрактиковаться в работе с библиотеками Django и Aiogram.**

### Возможности/Features:

* Этот телеграм бот умеет находить ближайшие заведения по выбранному пользователем типу (кафе, бар, ресторан и т.п.) и отсылать их локацию пользователю (пользователю, нужно только жмякнуть, чтобы открыть карту с нужным заведением).
* Возможен листинг заведений с дальнейшим удалением от местоположения пользователя.
* Фильтр мата с возможностью регулировки уровня строгости.
* Бот GoodOrBad собирает/показывает отзывы пользователей на посещенные заведения. 
* Заведения делятся на категории. 
* Добавлять заведения и категории  может только администратор.
* Для администратора разработана админка с возможностью создания/редактирования/удаления заведений и их категорий.

## Установка/Installation

Клонировать репозиторий и перейти в него в командной строке:
```bash
git clone https://github.com/Yohimbe227/goodorbad.git
```
```bash
cd goodorbad/
```
Cоздать и активировать виртуальное окружение:
```bash
python -m venv venv
```
```bash
source env/bin/activate
```
Обновить pip:
```bash
python -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```bash
pip install -r requirements.txt
```
Выполнить миграции:
```bash
python manage.py migrate
```
Запустить админку:
```bash
python manage.py runserver
```
Запустить бота:
```bash
python manage.py startbot
```

## Наполнение базы данных/Filling the database

Наполнение/обновление базы данных проводится через API от 2gis. Реализовано
посредством managment комманды Django.
```bash
python manage.py update_base
```
Duplicate table rows will be ignored.

## FAQ

**Вопрос 1/ Question 1**

Доступен ли сейчас этот бот для использования в телеграме?  

Is this bot available for use on Telegram?

**Ответ 1/ Answer 1**

Еще нет. Будет запущен, когда я разберусь с деплоем. Исправлю старые баги. Может попорошу кого-нибудь сделать ревью кода...  

Not yet. It will be launched when I figure out the deployment. I'll fix some old bugs. Maybe I'll get someone to do a code review...

**Вопрос 2/ Question 2**

В базе прям все все заведения?

Is this bot available for use on Telegram?

**Ответ 2/ Answer 2**

Увы нет. Собрать такую базу несложно, но нужны деньги. 

Alas, no. It's not hard to assemble such a base, but you need money.

**Вопрос 3/ Question 3**

Юрий, а для чего тогда тебе студенты, пусть ручками парсят!

Yuri, then what do you need students for, let them use their hands to parse!

**Ответ 3/ Answer 3**
Хм, жестокий ты... Почему бы и нет, но как бы увязать студентов, зачет по термеху и список баров в Тамбове?

Hmm, you're cruel... Why not, but how would you connect the students, the term paper, and the list of bars in Tambov?
## License

Не используйте этот программный продукт без согласования с автором. Он только для ознакомления!

