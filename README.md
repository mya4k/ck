# ck
Бот для Цифровых кафедр

## Алгоритм работы бота
1. Бот встречает пользователя с кнопкой "Начать" (Команда /start), нажав на которую будет инициализирован бот в положение "Начальный экран".
2. После появится несколько функций: "Все слова категории" (/list), "Определить категорию" (/belongsto), "Все категории" (/categories) и "Помощь" (/help).
- Функция "Все слова категории" откроет строку ввода, в которую необходимо ввести название категории (вид спорта). Если введённый текст соответствует существующей категории, то  бот выведет список слов входящих в эту категорию с переводом.
- Функция "Определить категорию" откроет строку ввода и в которую необходимо ввести слово. Если слово существует в какой-либо категории, то бот выдаст информацию о том к какой категории оно принадлежит.
- Функция "Все категории" выводит список существующих категорий слов, которые являются допустимым вводом для функции "Все слова категории".
- Функция "Помощь" выведет инструкцию по использованию бота.
3. После использования любой из функций, бот возвращается в положение "Начальный экран")
