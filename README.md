## Что такое Pay4Win?
Pay4Win - это сервис-рулетка, где любые пользователи могут участвовать в онлайн-розыгрышах Steam игр за монетки (фантики - ненастоящие платежные средства).

## Как пользоваться приложением?
1. Посетитель авторизуется на сервисе через свой Steam аккаунт (oauth).
2. После авторизации пользователь пополняет свой счет фантиками.
3. Пользователь выбирает понравившийся ему розыгрыш при помощи фильтров.
4. Покупка билета за фантики делает пользователя участником розыгрыша.
5. Когда все билеты будут раскуплены, система случайным образом выберет победителя.
6. Победителю достается игра!

## Какой стек технологией используется в проекте?
- Back-end написан целиком и полностью на **Python Django**.
- Для обеспечения асинхронной работы розыгрышей в реальном времени используется **Redis**.
- Front-end является адаптивным благодаря качественной верстке с использованием **HTML, CSS, JS** и **Bootstrap**.
- Связь между клиентом и сервером в реальном времени обеспечивается при помощи **Ajax**, однако архитектура проекта
даст работать с сервисом и без возможности использования этой технологии (если у кого-то старый браузер).

## Что такое розыгрыш?
**Розыгрыш** - это событие, к которому привязано несколько билетов. Пользователи могут покупать разное количество билетов для каждого розыгрыша. Стоимость билетов фиксирована для каждого розыгрыша. Таким образом, розыгрыш будет завершен, когда все его билеты будут куплены. Среди людей, купивших билеты данного розыгрыша, будет выбран один победитель - он и получит приз.

## Структура проекта
Все приложение можно разделить на 2 части.
### Панель администратора
Через панель администратора происходит создание розыгрышей и добавление информации во все разделы сайта. Сама панель администратора имеет следующий
вид:

![image](https://user-images.githubusercontent.com/67606335/178316707-813e5062-0c1c-455c-90ed-3f221c2ba9fd.png)

Администратор добавляет в систему информацию о новом розыгрыше. Как видно, имеется два раздела под названием "Розыгрыши" и "Розыгрыши фактические" - в первом разделе хранятся разновидности розыгрышей (именно их могут добавлять и править администраторы), а во втором разделе хранятся те розыгрыши, в которых могут принимать участие пользователи.
> Зачем нужна такая система?

Все очень просто!
Данное веб-приложение максимально автоматизирует все процессы. Таким образом, администратору достаточно создать шаблон розыгрыша, как по его прототипу система автоматически будет создавать розыгрыши для пользователей! Как только завершится один розыгрыш, система сразу же создаст такой же с теми же настройками. Это будет повторяться до тех пор, пока администратор не отключит данный вид розыгрышей.

Более того! При добавлении нового розыгрыша, администратору не нужно указывать всю информацию об игре - ему лишь нужно выбрать по какой игре из Steam будет проводиться данный розыгрыш:

![image](https://user-images.githubusercontent.com/67606335/178319562-5065b217-05ca-45fc-94cf-ab0b1578ddc3.png)

При добавлении игры также задействуется минимум информации - все для удобства и автоматизации ввода. Достаточно ввести желаемое описание, задать о ней базовую информацию и прикрепить ссылку на игру в Steam, после чего вся информация об игре спарсится со страницы Steam автоматически при загрузке в базу данных:

![image](https://user-images.githubusercontent.com/67606335/178320045-19bf2238-c3c5-4228-833c-cc8bb7b2b1cb.png)

Таким образом, благодрая продуманной архитектуре проекта, вести администрирование можно без остановки сервиса и отдельных розыгрышей!

### Пользовательская часть
На главной странице сервиса представлена основная информация о проекте, которая поможет пользователям сделать первые шаги:

![image](https://user-images.githubusercontent.com/67606335/178320673-76ad3dba-833b-4172-a62a-86e1798afb94.png)

В верхнем меню содержится весь необходимый функционал для использования приложения; главная страница представляет из себя компактную сборку основного контента со всего сайта. 

На странице "Как играть" размещена необходимая информация, которая поможет пользователям научиться принимать участие в розыгрышах и пользоваться сервисом:
![image](https://user-images.githubusercontent.com/67606335/178321465-ebbddb98-89c2-411c-a32b-06a808efe895.png)

Страница "FAQ" ответит на все вопросы, которые могут возникнуть у пользователей. В панели администратора есть отдельный раздел, который позволяет добавлять, удалять и редактировать вопросы на этой странице:

![image](https://user-images.githubusercontent.com/67606335/178321843-b116e595-576c-43b6-b971-56655238f0e9.png)

Страница "Розыгрыши" представляет из себя фильтр, с помощью которого пользователи могут искать нужный им тип розыгрышей (от типа розыгрыша зависит цена билета и ценовой диапазон призовой игры):

![image](https://user-images.githubusercontent.com/67606335/178322221-c0748ee3-efc5-4b92-98b3-ba6b9b4f1f88.png)

Страница "Контакты" содержит данные для связи с технической поддержкой:

![image](https://user-images.githubusercontent.com/67606335/178322498-50abbbc9-bc6e-47ba-832c-81459a727aaf.png)

Страница "Поиск" представляет собой фильтр, при помощи которого можно искать розыгрыши по заданным параметрам. Именно с нее удобнее всего проводить поиск розыгрышей пользователям:

![image](https://user-images.githubusercontent.com/67606335/178322794-6a1b0319-b4a9-474b-9a36-800aaf850b26.png)

Как видно, на ней отображаются карточки розыгрышей. По карточкам можно определить сколько билетов уже куплено, какая игра разыгрывается и т.п. Кроме того, можно перейти на страницу розыгрыша или купить билет за фантики.

При переходе на страницу розыгрыша, в ее верхней части можно увидеть всю информацию об игре - ее название, описание, ее трейлеры и картинки, связанные с ней. Вся эта информация берется прямо с ее страницы Steam:

![image](https://user-images.githubusercontent.com/67606335/178323505-9dbe75f2-457d-4e9b-bba7-67d21353410e.png)

Чуть ниже выведена информация о самом розыгрыше - о количестве купленных билетов, их цене, количестве оставшихся билетов, а также имеется кнопка покупки билета. Еще ниже приведен список событий розыгрыша (историй действий). В списке событий выводится информация о покупках билетов пользователями. Кроме того, на данной странице выводится информация о шансе выигрыша для данного пользователя (если пользователь принимает участие в розыгрыше):

![image](https://user-images.githubusercontent.com/67606335/178323900-5dcb1b7f-6e22-4519-976b-aadb8f97e648.png)

Покупка билетов, обновлении информации и любые другие взаимодействия с розыгрышами обновляются на странице в режиме реального времени благодаря Ajax на стороне клиента и Redis на стороне сервера.

После того, как все билеты куплены, происходит автоматический и полностью случайный выбор победителя. Выбор зависит от кол-ва купленных билетов. Чем больше куплено билетов, тем больше шанс у пользователя на победу. По результатм выбора объявляется победитель:

![image](https://user-images.githubusercontent.com/67606335/178324307-21128d17-6668-4773-943b-0c7e9654de06.png)

Статистика обновляется в личном кабинете у пользователя:

![image](https://user-images.githubusercontent.com/67606335/178324475-8da51513-45d5-49e9-a55c-fb00cccc5dd5.png)

Также, в кабинете пользователя можно посмотреть историю его игр:

![image](https://user-images.githubusercontent.com/67606335/178324579-ffb3ba67-0fbc-46c5-b5a9-6ac10a825fb5.png)

При желании, пользователь может сделать свой профиль приватным (скрыть его для всех, кроме себя).

Помимо всего, каждый розыгрыш имеет свой уникальный UUID, который используется для просмотра истории. При возникновении неполадок или обращении в техническую поддержку его можно использовать для более качественной обратной связи!

## Заключение
Данное веб-приложение не нарушает какие-либо права. Оно не связано с азартными играми и не сопряжено с возможностями материальных потерь. Участие в розыгрышах производится за "фантики" - не имеющие какой-либо материальной стоимости средства.
