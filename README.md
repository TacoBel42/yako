Yako - билдер сценариев для телеграмм
```
/help - получение справочной информации

/edit_help
<HELP_TEXT> - изм. справки

/build - создание simple scenario + hot reload

/rebuild - hot reload 

/scenarios - получние всех сценариев и справки по ним

/operator - контакт оператора

/exit - выйти из сценария 
```

Сценарии так же можно обновлять командой build, он будет полностью перезаписан при совпадении имени(без префикса _auto)

Для запуска требуется указать в env:

+ ```TELEGRAM_BOT_TOKEN``` - Бот токен телеграмм
+ ```VEGA_SESSION``` - для корректной работы сценариев некоторых ВЕГИ