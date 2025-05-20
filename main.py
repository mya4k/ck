from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import pandas as pd
from rapidfuzz import fuzz



# Category 1: Футбол (Football) - 20 entries
football_terms = {
    "das Tor": "ворота",
    "der Torwart": "вратарь",
    "der Stürmer": "нападающий",
    "die Mannschaft": "команда",
    "der Schiedsrichter": "судья",
    "das Spielfeld": "поле",
    "der Elfmeter": "пенальти",
    "der Freistoß": "свободный удар",
    "der Eckball": "угловой",
    "der Anstoß": "начало игры",
    "die Abseitsregel": "правило офсайда",
    "der Angriff": "атака",
    "die Verteidigung": "защита",
    "der Pass": "пас",
    "der Konter": "контратака",
    "der Schuss": "удар",
    "das Torverhältnis": "разница мячей",
    "die Bundesliga": "Бундеслига",
    "die Weltmeisterschaft": "чемпионат мира",
    "der Pokal": "кубок"
}

# Category 2: Волейбол (Volleyball) - 20 entries
volleyball_terms = {
    "der Volleyball": "волейбольный мяч",
    "das Netz": "сетка",
    "der Aufschlag": "подача",
    "der Block": "блок",
    "die Annahme": "приём",
    "der Angriffsschlag": "нападающий удар",
    "die Rotation": "ротация",
    "die Mannschaftsaufstellung": "расстановка команды",
    "die Auszeit": "тайм-аут",
    "das Punktesystem": "система очков",
    "der Satz": "партия",
    "das Spielsystem": "система игры",
    "der Libero": "либеро",
    "der Zuspieler": "связующий",
    "die Spielposition": "игровая позиция",
    "die Schiedsrichterin": "судья (женщина)",
    "der Spielstand": "счёт игры",
    "die Aufstellung": "состав команды",
    "das Training": "тренировка",
    "die Nationalliga": "национальная лига"
}

# Category 3: Регби (Rugby) - 20 entries
rugby_terms = {
    "der Rugbyball": "регбийный мяч",
    "das Try": "попытка (очко)",
    "das Scrum": "схватка",
    "der Stoß": "толчок", # Impact/Push
    "der Kick": "удар",
    "die Verteidigungslinie": "линия защиты",
    "der Spielerwechsel": "замена игрока",
    "der Zweikampf": "борьба",
    "das Tackling": "захват",
    "die Abseitslinie": "офсайдная линия",
    "das Rugbyfeld": "поле для регби",
    "die Rugbyunion": "регбийный союз",
    "das Ligaspiel": "матч лиги",
    "das Gedränge": "схватка в движении", # Scrum in motion / ruck / maul
    "der Flügelspieler": "крайний нападающий",
    "die Positionen": "позиции игроков",
    "der Trainer": "тренер",
    "das Training": "тренировка", # Also appears in Volleyball & General Terms
    "die Taktik": "тактика",
    "die Meisterschaftsstrategie": "стратегия команды"
}

# Category 4: Теннис (Tennis) - 19 entries (all entries from 61-79)
tennis_terms = {
    "der Tennisball": "теннисный мяч",
    "der Tennisschläger": "теннисная ракетка",
    "das Netz": "сетка", # Also in Volleyball
    "der Aufschlag": "подача", # Also in Volleyball
    "der Satz": "сет", # In Tennis, refers to a set
    "das Spiel": "гейм",
    "die Grundlinie": "задняя линия",
    "die Aufschlaglinie": "линия подачи",
    "die Vorhand": "удар справа (форхенд)",
    "die Rückhand": "удар слева (бэкхенд)",
    "der Volley": "волей (удар с лёта)",
    "der Lob": "свеча (удар)",
    "der Stoppball": "укороченный удар",
    "das Match": "матч",
    "der Satzball": "сетбол",
    "die Platzierung": "размещение мяча",
    "der Tiebreak": "тай-брейк",
    "die Einzel": "одиночный матч",
    "die Doppel": "парный матч"
}

# Category 5: Общие спортивные термины (General Sports Terms) - 21 entries (all entries from 80-100)
general_sports_terms = {
    "das Spielfeld": "теннисное поле", # As written in the image for #80
    "der Wettkampf": "соревнование",
    "die Fitness": "физическая форма",
    "das Training": "тренировка", # Also appears in Volleyball & Rugby
    "die Medaille": "медаль",
    "der Sieg": "победа",
    "die Meisterschaft": "чемпионат",
    "die Zuschauer": "зрители",
    "die Veranstaltung": "мероприятие",
    "der Sportverein": "спортивный клуб",
    "der Rekord": "рекорд",
    "die Strategie": "стратегия",
    "das Teamwork": "командная работа",
    "die Motivation": "мотивация",
    "die Talentförderung": "поддержка талантов",
    "die Fairness": "честная игра",
    "das Ergebnis": "результат",
    "die Teilnahme": "участие",
    "die Begeisterung": "энтузиазм",
    "der Champion": "чемпион",
    "die Gesundheit": "здоровье"
}

# Combined dictionary for easier iteration
all_dictionaries_with_names = {
    "Футбол": football_terms,
    "Волейбол": volleyball_terms,
    "Регби": rugby_terms,
    "Теннис": tennis_terms,
    "Общие термины": general_sports_terms
}


SIMILARITY_THRESHOLD = 70

	
async def ckstart(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text('Start')

async def ckhelp(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text('Help')

async def ckbelongsto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Takes a term and identifies which dictionary contains it.
    Searches both German terms (keys) and Russian translations (values).
    """
    if not context.args:
        await update.message.reply_text(
            "Пожалуйста, введите термин после команды, чтобы узнать, к какой категории он относится.\n"
            "Например: `/belongsto der Torwart` или `/belongsto вратарь`"
        )
        return

    search_term = " ".join(context.args).lower()
    found_in_categories = []

    for category_name, term_dict in all_dictionaries_with_names.items():
        for german_term, russian_translation in term_dict.items():
            if search_term == german_term.lower() or search_term == russian_translation.lower():
                found_in_categories.append(f"{category_name}: {german_term} - {russian_translation}")
                # If a direct match is found, we might want to stop or continue searching for other categories.
                # For now, we collect all categories it belongs to.

    if found_in_categories:
        response_message = f"Термин '{search_term}' найден в следующих категориях:\n"
        for entry in found_in_categories:
            response_message += f"- {entry}\n"
    else:
        response_message = f"Термин '{search_term}' не найден ни в одной категории."

    await update.message.reply_text(response_message)


async def ckcategories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Shows available dictionaries (categories).
    """
    category_names = sorted(all_dictionaries_with_names.keys())
    if category_names:
        response_message = "Доступные категории спортивных терминов:\n" + "\n".join(f"- {name}" for name in category_names)
    else:
        response_message = "Категории терминов не найдены."
    await update.message.reply_text(response_message)


async def cklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Lists all terms and their translations for a given dictionary (category).
    """
    if not context.args:
        await update.message.reply_text(
            "Пожалуйста, укажите название категории, которую вы хотите просмотреть.\n"
            "Например: `/list Футбол`\n"
            "Используйте `/categories` для просмотра доступных категорий."
        )
        return

    category_query = " ".join(context.args)
    # Find the category, allowing for case-insensitive matching
    matched_category_name = None
    for cat_name in all_dictionaries_with_names.keys():
        if cat_name.lower() == category_query.lower():
            matched_category_name = cat_name
            break

    if matched_category_name:
        term_dict = all_dictionaries_with_names[matched_category_name]
        if term_dict:
            response_message = f"Термины в категории '{matched_category_name}':\n\n"
            count = 0
            for german_term, russian_translation in term_dict.items():
                count += 1
                response_message += f"{count}. {german_term} - {russian_translation}\n"
                # Prevent messages from becoming too long for Telegram
                if len(response_message) > 3800 and count < len(term_dict) :
                    response_message += "[... остальные термины опущены из-за длины сообщения ...]"
                    break
        else:
            response_message = f"Категория '{matched_category_name}' существует, но в ней нет терминов."
    else:
        response_message = (
            f"Категория '{category_query}' не найдена.\n"
            "Пожалуйста, проверьте написание. Используйте `/categories` для просмотра доступных категорий."
        )
    
    await update.message.reply_text(response_message)

async def cksearch(update: Update, context: ContextTypes.DEFAULT_TYPE): # For PTB v20+
    """
    Handles the /search command.
    Takes a string and fuzzy searches for its occurrence in the dictionaries.
    Searches in both German terms (keys) and Russian translations (values).
    """
    try:
        if not context.args:
            await update.message.reply_text(
                "Пожалуйста, введите строку для поиска после команды.\n"
                "Например: /search ваш запрос"
            )
            return

        search_query = " ".join(context.args)
        
        found_entries = {} # To store unique entries with their best match

        for category_name, term_dict in all_dictionaries_with_names.items():
            for german_term, russian_translation in term_dict.items():
                current_best_ratio_for_entry = 0
                current_match_type_for_entry = None

                # Check similarity with German term
                ratio_german = fuzz.token_set_ratio(search_query.lower(), german_term.lower())
                if ratio_german >= SIMILARITY_THRESHOLD and ratio_german > current_best_ratio_for_entry:
                    current_best_ratio_for_entry = ratio_german
                    current_match_type_for_entry = "Термин (DE)"

                # Check similarity with Russian translation
                ratio_russian = fuzz.token_set_ratio(search_query.lower(), russian_translation.lower())
                if ratio_russian >= SIMILARITY_THRESHOLD and ratio_russian > current_best_ratio_for_entry:
                    current_best_ratio_for_entry = ratio_russian
                    current_match_type_for_entry = "Перевод (RU)"
                
                # If a match was found for this entry (either German or Russian)
                if current_match_type_for_entry:
                    # If this German term (entry) is already in found_entries,
                    # update it only if the new match has a higher similarity score.
                    if german_term in found_entries:
                        if current_best_ratio_for_entry > found_entries[german_term]["similarity"]:
                            found_entries[german_term] = {
                                "category": category_name,
                                "match_type": current_match_type_for_entry,
                                "german_term": german_term,
                                "russian_translation": russian_translation,
                                "similarity": current_best_ratio_for_entry
                            }
                    else: # New entry to add
                        found_entries[german_term] = {
                            "category": category_name,
                            "match_type": current_match_type_for_entry,
                            "german_term": german_term,
                            "russian_translation": russian_translation,
                            "similarity": current_best_ratio_for_entry
                        }
        
        results_list = list(found_entries.values())

        if not results_list:
            update.message.reply_text(f"Не найдено похожих терминов для '{search_query}'.")
            return

        # Sort results by similarity (highest first)
        results_list.sort(key=lambda x: x["similarity"], reverse=True)

        response_message = f"Результаты поиска для '{search_query}':\n\n"
        count = 0
        for res in results_list:
            count += 1
            response_message += (
                f"{count}. Категория: {res['category']}\n"
                f"   Найден по: {res['match_type']}\n"
                f"   Термин (DE): {res['german_term']}\n"
                f"   Перевод (RU): {res['russian_translation']}\n"
                f"   Сходство: {res['similarity']}%\n\n"
            )
            # Prevent messages from becoming too long for Telegram
            if len(response_message) > 3800 and count < len(results_list) : # Check before adding next item
                response_message += "[... остальные результаты опущены из-за длины сообщения ...]"
                break
        
        await update.message.reply_text(response_message)

    except Exception as e:
        print(f"Error in fuzzy_search_terms_command: {e}") # For server-side logging
        await update.message.reply_text("Извините, произошла ошибка при обработке вашего запроса.")


# Responses
async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
	await update.message.reply_text('Invalid command')


if __name__ == '__main__':
	app = Application.builder().token('8159215101:AAFfvgulxI6qwk7O1MY8FVwt2LEKkY5GMrY').build()
	app.add_handler(CommandHandler('start', ckstart))
	app.add_handler(CommandHandler('help', ckhelp))
	app.add_handler(CommandHandler('belongsto', ckbelongsto))
	app.add_handler(CommandHandler('list', cklist))
	app.add_handler(CommandHandler('categories', ckcategories))
	app.add_handler(CommandHandler('search', cksearch))
     
	
	""" app.add_handler(MessageHandler(filters.TEXT, handle_response)) """
	app.run_polling()
