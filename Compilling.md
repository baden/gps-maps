# Сборка проекта #

## Необходимые компоненты: ##
  * Python >= 2.6 ([ссылка](http://www.python.org/download/))
  * Google App Engine ([ссылка](http://code.google.com/intl/ru/appengine/downloads.html))
Опционально
  * Aptana ([ссылка](http://www.aptana.org/studio/download))

## Исходные коды ##
Получить командой:
` svn checkout http://gps-maps.googlecode.com/svn/trunk/ gps-maps `
или через [веб-сервис](http://code.google.com/p/gps-maps/source/browse/)
или с помощью Aptana

Ничего компилировать не нужно, можно сразу запускать и пользоваться или опубликовать на хостинге Google.

Более подробное (в идеале пошаговое) описание будет чуть позже.


---

Итак пробуем описать...
## Ставим Aptana Studio. ##
Качаем инсталляцию с ([сайта](http://www.aptana.org/studio/download))
Ставим.
Доустанавливаем PyDev.

## Импортируем проект из SVN ##
**File** -> **Import** -> **SVN/Checkout Projects from SVN**

**Next**

**Create a new repository location**

Указываем **https://gps-maps.googlecode.com/svn/trunk/***

**Select the folder to be checked out from SNV** - Указываем верхний уровень. (https://gps-maps.googlecode.com/svn/trunk/) -> **Next**

Project name: gps-maps, Depth: full recursive (вобщем ничего не трогаем) -> **Next**

И наконец **Finish**.

Началось скачивание.

Проект должен появиться в списке проектов (**Projects**).

## Запускаем Google App Engine Launcher ##
Собственно запускаем (ярлык на рабочем столе).

Идем **File** -> **Add Existing Application...**

Указываем каталог проекта, например, **D:\Work\MAIN\GPS\GGT-200\SRC\SITE\svn\gps-maps**
И порт 8080 (в Google App Engine Launcher есть неприятный глюк, так что пока указываем 8080) -> Жмем **Add**.

Приложение появится в списке.
Можно сменить порт локального сервера на 80-тый, но необходимо быть уверенным что на 80-том порту нет других веб-серверов. Жмем двойной щелчек. И меняем порт на 80.

Все, можно запускать. Жмем **Run**. Ждем несколько секунд.
Жмем **Browse** и можем попробовать приложение в действии на локальном компьютере.

## Попробуем откоммитить изменения ##
Измененные файлы будут помечены звездочкой. Можно по правой клавише посмотреть какие были сделаны изменения (**Compare With** -> **Base revision**). И еще там много чего.

А как откоммитить я не догоняю :(

Вобщем доустановил Subversive и теперь есть пункт **Team**, а там и **Commit**. Единственное что я не уловил, а какже имя/пароль?
Извините, я немного запутался. После доустановки Subversive теперь появилось несколько разных SVN в системе и все несколько смешалось. Но в целом работать с SVN можно.