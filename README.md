## Что такое Pay4Win
Pay4Win - это сервис-рулетка, где любые пользователи могут участвовать в онлайн-розыгрышах Steam игр за монетки (фантики - ненастоящие платежные средства)

## Как пользоваться приложением
1. Посетитель авторизуется на сервисе через свой Steam аккаунт (oauth)
2. После авторизации пользователь пополняет свой счет фантиками
3. Пользователь выбирает понравившийся ему розыгрыш при помощи фильтров
4. Покупка билета за фантики делает пользователя участником розыгрыша
5. Когда все билеты будут раскуплены, система случайным образом выберет победителя
6. Победителю достается игра!

## Какой стек технологией используется в проекте
- Back-end написан целиком и полностью на **Python Django**
- Для обеспечения асинхронной работы розыгрышей в реальном времени используется **Redis**
- Front-end является адаптивным благодаря качественной верстке с использованием **HTML, CSS, JS** и **Bootstrap**
- Связь между клиентом и сервером в реальном времени обеспечивается при помощи **Ajax**, однако архитектура проекта
даст работать с сервисом и без возможности использования этой технологии (если у кого-то старый браузер)

## Структура проекта
Все приложение можно разделить на 2 части - основная часть, которая видна обычным пользователям и панель администратора.
Через панель администратора происходит создание розыгрышей и добавление информации во все разделы сайта. Она имеет следующий
вид:
![image](https://user-images.githubusercontent.com/67606335/178316707-813e5062-0c1c-455c-90ed-3f221c2ba9fd.png)
