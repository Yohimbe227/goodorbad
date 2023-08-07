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

* Этот телеграм бот умеет находить ближайшие заведения по выбранному пользователем типу (кафе, бар, ресторан и т.п.) и отсылать их локацию пользователю (пользователю, нужно только жмякнуть, чтобы открыть карту с нужным заведением) или ввести свой примерный адресс в произвольном формате.
* Возможен листинг заведений с дальнейшим удалением от местоположения пользователя.
* Фильтр мата с возможностью регулировки уровня строгости.
* Бот NextPlace собирает/показывает отзывы пользователей на посещенные заведения. 
* Заведения делятся на категории. 
* Добавлять заведения и категории  может только администратор.
* Для администратора разработана админка с основной статистикой и возможностью создания/редактирования/удаления заведений и их категорий. 
Пощупать можно тут: http://212.237.35.59/admin/ login: the_best, pass: hr_tut (только просмотр, сами понимаете:))




## Наполнение базы данных/Filling the database

Наполнение/обновление базы данных проводится через различные API. Реализовано
посредством managment комманды Django.
```bash
python manage.py update_base
или
python manage.py update
```
В тексте файла update.py можно выбрать нужный город и категорию заведения.

## FAQ

**Вопрос 1/ Question 1**

Доступен ли сейчас этот бот для использования в телеграме?  

Is this bot available for use on Telegram?

**Ответ 1/ Answer 1**

Да доступен и полностью функционален. Ищите в телеграмм бот NextPlace! 

Yes available and fully functional. Look for the NextPlace bot in Telegram!

**Вопрос 2/ Question 2**

В базе прям все все заведения?

Does the database contain all of the places?

**Ответ 2/ Answer 2**

Нет. Такая цель не ставилась. Проект не предполагает коммерческого использования. Собранная база является временной и регулярно обновляется. Если Вы HR и хотите платить мне 1000000000 $ в миниту, то напишите мне и я добавлю нужный Вам город. 

No. That was not the goal. The project is not intended for commercial use. The database collected is temporary and regularly updated. If you HR and want to pay me $ 1000000000 per minitu, then write to me and I will add your desired city.

**Вопрос 3/ Question 3**

Юрий, а для чего тогда тебе студенты, пусть ручками парсят!

Yuri, then what do you need students for, let them use their hands to parse!

**Ответ 3/ Answer 3**
Хм, жестокий ты... Почему бы и нет, но как бы увязать студентов, зачет по термеху и список баров в Тамбове?

Hmm, you're cruel... Why not, but how would you connect the students, the term paper, and the list of bars in Tambov?

## Установка/Installation

Клонировать репозиторий и перейти в него в командной строке:
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
Чтобы проверить успешность установки, запустите следующую команду:
```bash
docker-compose --version
```
Вывод будет выглядеть следующим образом:
```bash
Output
docker-compose version 1.26.0, build 8a1c60f6
```
Скопируйте из папки infra файлы в папку /home/your_user/:
* заполненный Вашими данными файл .env.example, переименуйте его в .env и копируйте.
* папку nginx с ее содержимым.
* файл docker-compose.yaml.
А теперь просто запустите:
```bash
docker-compose up
```
Если нужна админка, то дополнительно выполните комманду:
```bash
sudo docker-compose exec -T telega gunicorn gob.wsgi:application --bind 0:8000
```
и она будет доступна по адресу http:yourdomain_or_ip/admin
## Author
 Юрий Каманин 
 [@Yohimbe227](https://www.github.com/Yohimbe227)

## License

Студентам Яндекс Практикума копировать запрещено совсем и категорически! А учиться кто будет? ;)
Не используйте этот программный продукт без согласования с автором. Он только для ознакомления! Вот такая жесткая лицензия).
