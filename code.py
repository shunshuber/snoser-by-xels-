import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlparse
import time
import colorama
import os
import requests
import random
import re
import sys
import tempfile

colorama.init()

GREEN = colorama.Fore.GREEN
RED = colorama.Fore.RED
YELLOW = colorama.Fore.YELLOW
RESET = colorama.Fore.RESET

BANNER = f"""
{GREEN}
 ==================================================================
 | dev > 895DoxTool                      tg > @noshki8 | 18.10 |
 ==================================================================
 0 |  Выход (Exit)
 1 |  Снос Аккаунта (Account TakeDown)              
 2 |  Снос Канала (Channel TakeDown)             
 3 |  Снос Бота (Bot TakeDown)
 4 |  Снос Сессий (Session TakeDown)       
{RESET}                                                                                                                                                                   
"""

def load_from_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return [line.strip() for line in lines]  
    except FileNotFoundError:
        print(f"{RED}Ошибка: Файл '{filename}' не найден.{RESET}")
        return []
    except Exception as e:
        print(f"{RED}Ошибка при чтении файла '{filename}': {e}{RESET}")
        return []

def parse_senders(senders_list):
    try:
        senders_dict = {}
        for item in senders_list:
            match = re.search(r'"([\w\.-]+@[\w\.-]+):([^"]+)"', item)
            if match:
                email, password = match.groups()
                senders_dict[email] = password
        return senders_dict
    except Exception:
        pass

def load_proxies(filename):
    try:
        proxies = load_from_file(filename)
        valid_proxies = []
        for proxy in proxies:
            parts = proxy.split(':')
            if len(parts) == 2 or len(parts) == 4:
                valid_proxies.append(proxy)
            else:
                print(f"{YELLOW}Предупреждение: Неверный формат прокси '{proxy}'. Пропускается.{RESET}")
        return valid_proxies
    except Exception:
        pass

def test_proxy(proxy, timeout=5):
    try:
        if "@" in proxy:
            userpass, hostport = proxy.split("@")
            host, port = hostport.split(":")
            proxy_url = f"http://{userpass}@{host}:{port}"
        else:
            host, port = proxy.split(":")
            proxy_url = f"http://{host}:{port}"

        response = requests.get("http://www.google.com", proxies={"http": proxy_url, "https": proxy_url}, timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False
 
def get_working_proxies(proxies):
    working_proxies = []
    for proxy in proxies:
        if test_proxy(proxy):
            working_proxies.append(proxy)
            print(f"{GREEN}Прокси {proxy} работает.{RESET}")
        else:
            print(f"{YELLOW}Прокси {proxy} не работает.{RESET}")
    return working_proxies

def user_input(prompt):
    user_response = input(f"{GREEN}{prompt}{RESET} ")
    if user_response.lower() == 'cancel':
        main()
        return None
    return user_response

def send_email(sender_email, sender_password, receiver_email, subject, body, proxy=None, timeout=4):
    try:
        print(f"Попытка отправить письмо с {sender_email} на {receiver_email}: Начата")
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = None

        if proxy:
            if "@" in proxy:
                userpass, hostport = proxy.split("@")
                user, password = userpass.split(":")
                host, port = hostport.split(":")
                print(f"Ошибка: Аутентификация прокси не поддерживается.")
                return False
            else:
                host, port = proxy.split(":")
                try:
                    server = smtplib.SMTP(host, int(port), timeout=timeout)
                    server.starttls()
                except Exception as e:
                    print(f"Ошибка подключения к прокси: {e}")
                    return False
        else:
            server = smtplib.SMTP('smtp.mail.ru', 587, timeout=timeout)
            server.starttls()

        if server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            server.quit()
            print(f"Попытка отправить письмо с {sender_email} на {receiver_email}: Успешно")
            return True
        else:
            print(f"Ошибка: Не удалось инициализировать SMTP сервер.")
            return False

    except Exception as e:
        print(f"Ошибка при отправке письма от {sender_email} к {receiver_email}: {e}")
        return False

def process_task(task, senders_dict, working_proxies, sent_emails):
    choice, comp_choice, username, id, chat_link, violation_link, number, channel_link, channel_violation, bot_user = task
    receivers = load_from_file("receivers.txt")
    receivers = [line.strip().replace('"', '').replace("'",'').replace(',', '') for line in receivers]

    username_text = f"Его юзернейм - {username}," if username else ""
    id_text = f"его айди - {id}," if id else ""
    chat_link_text = f"ссылка на чат - {chat_link}," if chat_link else ""
    violation_link_text = f"ссылка на нарушения - {violation_link}." if violation_link else ""
    number_text = f"и номер телефона - {number}." if number else ""
    channel_link_text = f"Ссылка на канал - {channel_link}," if channel_link else ""
    channel_violation_text = f"Ссылка на нарушение - {channel_violation}." if channel_violation else ""
    bot_user_text = f"Ссылка на бота - {bot_user}." if bot_user else ""

    if choice == '1':
        comp_texts = {
            "1": {
                "ru": f"Здравствуйте, уважаемая поддержка. На вашей платформе я нашел пользователя, который отправляет множество ненужных сообщений - СПАМ. {username_text} {id_text} {chat_link_text} {violation_link_text} Пожалуйста, примите меры по отношению к данному пользователю.",
                "en": f"Hello, dear support. I found a user on your platform who sends a lot of unnecessary messages - SPAM. {username_text} {id_text} {chat_link_text} {violation_link_text} Please take action against this user."
            },
            "2": {
                "ru": f"Здравствуйте, уважаемая поддержка, на вашей платформе я нашел пользователя, который распространяет чужие данные без их согласия. {username_text} {id_text} {chat_link_text} {violation_link_text} Пожалуйста, примите меры по отношению к данному пользователю путем блокировки его аккаунта.",
                "en": f"Hello, dear support, I found a user on your platform who is distributing other people's data without their consent. {username_text} {id_text} {chat_link_text} {violation_link_text} Please take action against this user by blocking his account."
            },
            "3": {
                "ru": f"Здравствуйте, уважаемая поддержка Telegram. Хочу пожаловаться на пользователя. {username_text} {id_text} Данный пользователь оскорбляет третьих лиц матом (Статья 213 УК РФ). Вот ссылка на чат - {chat_link_text}, ссылка на нарушение - {violation_link_text}. Прошу заблокировать данного пользователя.",
                "en": f"Hello, dear Telegram support. I want to complain about a user. {username_text} {id_text} This user insults third parties with profanity (Article 213 of the Criminal Code of the Russian Federation). Here is the chat link - {chat_link_text}, violation link - {violation_link_text}. Please block this user."
            },
            "4": {
                "ru": f"Здравствуйте, уважаемая поддержка. Я случайно перешел по фишинговой ссылке и утерял доступ к своему аккаунту. {username_text} {id_text} {number_text} Пожалуйста, удалите аккаунт или обнулите сессии.",
                "en": f"Hello, dear support. I accidentally clicked on a phishing link and lost access to my account. {username_text} {id_text} {number_text} Please delete the account or reset the sessions."
            },
            "5": {
                "ru": f"Добрый день, поддержка Telegram! Аккаунт {username_text} {id_text} использует виртуальный номер, купленный на сайте по активации номеров. Отношения к номеру он не имеет. Прошу разобраться с этим.",
                "en": f"Good afternoon, Telegram support! Account {username_text} {id_text} uses a virtual number purchased on a number activation website. He has no relation to the number. Please investigate this."
            },
            "6": {
                "ru": f"Добрый день, поддержка Telegram! Аккаунт {username_text} {id_text} приобрел премиум в вашем мессенджере, чтобы рассылать спам-сообщения и обходить ограничения Telegram. Прошу проверить данную жалобу и принять меры!",
                "en": f"Good afternoon, Telegram support! Account {username_text} {id_text} purchased premium in your messenger to send spam messages and bypass Telegram restrictions. Please check this complaint and take action!"
            }
        }
        if comp_choice in comp_texts:
            subject_ru = 'Жалоба на аккаунт Telegram' if comp_choice in ["1", "2", "3", "5", "6"] else 'Я утерял свой аккаунт в Telegram'
            subject_en = 'Telegram account complaint' if comp_choice in ["1", "2", "3", "5", "6"] else 'I lost my Telegram account'
            subject = f"{subject_ru} / {subject_en}"
            comp_text_ru = comp_texts[comp_choice]["ru"].format(username_text=username_text, id_text=id_text, chat_link_text=chat_link_text, violation_link_text=violation_link_text, number_text=number_text)
            comp_text_en = comp_texts[comp_choice]["en"].format(username_text=username_text, id_text=id_text, chat_link_text=chat_link_text, violation_link_text=violation_link_text, number_text=number_text)
            comp_body = f"{comp_text_ru}\n\n{comp_text_en}"

            senders = list(senders_dict.items()) 
            for sender_email, sender_password in senders:
                for receiver in receivers:
                    proxy = random.choice(working_proxies) if working_proxies else None
                    if send_email(sender_email, sender_password, receiver, subject, comp_body, proxy):
                        print(f"{GREEN}Отправлено {receiver} от {sender_email} (прокси: {proxy}).{RESET}")
                        sent_emails[0] += 1
                    else:
                        print(f"{RED}Не удалось отправить {receiver} от {sender_email}.{RESET}")

    elif choice == '2':
        comp_texts = {
            "1": {
                "ru": f"Уважаемый агент Telegram, я обращаюсь к вам с жалобой на канал {channel_link_text}, который нарушает мои права на конфиденциальность. {channel_violation_text} Прошу удалить мои личные данные и принять меры.",
                "en": f"Dear Telegram agent, I am writing to complain about the channel {channel_link_text}, which violates my privacy rights. {channel_violation_text} Please remove my personal data and take action."
            },
            "2": {
                "ru": f"Здравствуйте, поддержка Telegram. На вашей платформе я нашел канал, который распространяет жестокое обращение с животными. {channel_link_text} {channel_violation_text} Пожалуйста, заблокируйте его.",
                "en": f"Hello, Telegram support. I found a channel promoting animal cruelty. {channel_link_text} {channel_violation_text} Please block it."
            },
            "3": {
                "ru": f"Здравствуйте, поддержка Telegram. На вашей платформе я нашел канал, который распространяет запрещенный контент. {channel_link_text} {channel_violation_text} Пожалуйста, заблокируйте его.",
                "en": f"Hello, Telegram support. I found a channel distributing illegal content. {channel_link_text} {channel_violation_text} Please block it."
            },
            "4": {
                "ru": f"Здравствуйте, поддержка Telegram. Жалуюсь на канал {channel_link_text}, который продает запрещенные услуги. {channel_violation_text} Прошу принять меры.",
                "en": f"Hello, Telegram support. I'm complaining about the channel {channel_link_text}, which sells illegal services. {channel_violation_text} Please take action."
            }
        }
        if comp_choice in comp_texts:
            subject_ru = 'Жалоба на канал Telegram'
            subject_en = 'Telegram channel complaint'
            subject = f"{subject_ru} / {subject_en}"
            comp_text_ru = comp_texts[comp_choice]["ru"].format(channel_link_text=channel_link_text, channel_violation_text=channel_violation_text)
            comp_text_en = comp_texts[comp_choice]["en"].format(channel_link_text=channel_link_text, channel_violation_text=channel_violation_text)
            comp_body = f"{comp_text_ru}\n\n{comp_text_en}"

            senders = list(senders_dict.items())
            for sender_email, sender_password in senders:
                for receiver in receivers:
                    proxy = random.choice(working_proxies) if working_proxies else None
                    if send_email(sender_email, sender_password, receiver, subject, comp_body, proxy):
                        print(f"{GREEN}Отправлено {receiver} от {sender_email} (прокси: {proxy}).{RESET}")
                        sent_emails[0] += 1
                    else:
                        print(f"{RED}Не удалось отправить {receiver} от {sender_email}.{RESET}")

    elif choice == '3':
        comp_texts = {
            "1": {
                "ru": f"Здравствуйте, поддержка Telegram. На вашей платформе я нашел бота, который нарушает правила. {bot_user_text} Пожалуйста, заблокируйте его.",
                "en": f"Hello, Telegram support. I found a bot that violates your rules. {bot_user_text} Please block it."
            }
        }
        if comp_choice == '1':
            subject_ru = 'Жалоба на бота Telegram'
            subject_en = 'Telegram bot complaint'
            subject = f"{subject_ru} / {subject_en}"
            comp_text_ru = comp_texts[comp_choice]["ru"].format(bot_user_text=bot_user_text)
            comp_text_en = comp_texts[comp_choice]["en"].format(bot_user_text=bot_user_text)
            comp_body = f"{comp_text_ru}\n\n{comp_text_en}"

            senders = list(senders_dict.items())
            for sender_email, sender_password in senders:
                for receiver in receivers:
                    proxy = random.choice(working_proxies) if working_proxies else None
                    if send_email(sender_email, sender_password, receiver, subject, comp_body, proxy):
                        print(f"{GREEN}Отправлено {receiver} от {sender_email} (прокси: {proxy}).{RESET}")
                        sent_emails[0] += 1
                    else:
                        print(f"{RED}Не удалось отправить {receiver} от {sender_email}.{RESET}")

    elif choice == '4':
        comp_texts = {
            "1": {
                "ru": f"Здравствуйте, поддержка Telegram. Мой аккаунт был заблокирован без причины. {number_text} {username_text} {id_text} Прошу разобраться и восстановить доступ.",
                "en": f"Hello, Telegram support. My account was blocked without reason. {number_text} {username_text} {id_text} Please investigate and restore access."
            }
        }
        if comp_choice == '1':
            subject_ru = 'Заблокирован аккаунт Telegram'
            subject_en = 'Telegram account blocked'
            subject = f"{subject_ru} / {subject_en}"
            comp_text_ru = comp_texts[comp_choice]["ru"].format(number_text=number_text, username_text=username_text, id_text=id_text)
            comp_text_en = comp_texts[comp_choice]["en"].format(number_text=number_text, username_text=username_text, id_text=id_text)
            comp_body = f"{comp_text_ru}\n\n{comp_text_en}"

            senders = list(senders_dict.items())
            for sender_email, sender_password in senders:
                for receiver in receivers:
                    proxy = random.choice(working_proxies) if working_proxies else None
                    if send_email(sender_email, sender_password, receiver, subject, comp_body, proxy):
                        print(f"{GREEN}Отправлено {receiver} от {sender_email} (прокси: {proxy}).{RESET}")
                        sent_emails[0] += 1
                    else:
                        print(f"{RED}Не удалось отправить {receiver} от {sender_email}.{RESET}")

def main():
    print(BANNER)

    senders_list = load_from_file("mails.txt")
    receivers = load_from_file("receivers.txt")
    proxies = load_proxies("proxies.txt")

    if not senders_list or not receivers:
        print(f"{RED}Ошибка: Проверьте файлы mails.txt и receivers.txt.{RESET}")
        return

    senders_dict = parse_senders(senders_list)
    working_proxies = get_working_proxies(proxies) if proxies else []

    sent_emails = [0]

    while True:
        choice = user_input("Выберите опцию (0-4):")
        if choice == '0':
            break
        elif choice in ['1', '2', '3', '4']:
            if choice == '1':
                print("1. Спам")
                print("2. Утечка данных")
                print("3. Оскорбления")
                print("4. Фишинг")
                print("5. Виртуальный номер")
                print("6. Злоупотребление премиумом")
                comp_choice = user_input("Выберите тип жалобы:")
                username = user_input("Юзернейм:")
                id = user_input("ID:")
                if comp_choice in ["1", "2", "3"]:
                    chat_link = user_input("Ссылка на чат:")
                    violation_link = user_input("Ссылка на нарушение:")
                else:
                    chat_link = None
                    violation_link = None
                if comp_choice == "4":
                    number = user_input("Номер телефона:")
                else:
                    number = None

                task = (choice, comp_choice, username, id, chat_link, violation_link, number, None, None, None)
                process_task(task, senders_dict, working_proxies, sent_emails)
                time.sleep(1)

            elif choice == '2':
                print("1. Личные данные")
                print("2. Жестокость")
                print("3. Запрещенный контент")
                print("4. Незаконные услуги")
                ch_choice = user_input("Выберите тип жалобы:")
                channel_link = user_input("Ссылка на канал:")
                channel_violation = user_input("Ссылка на нарушение:")

                task = (choice, ch_choice, None, None, None, None, None, channel_link, channel_violation, None)
                process_task(task, senders_dict, working_proxies, sent_emails)
                time.sleep(1)

            elif choice == '3':
                bot_user = user_input("Юзернейм бота:")
                task = (choice, "1", None, None, None, None, None, None, None, bot_user)
                process_task(task, senders_dict, working_proxies, sent_emails)
                time.sleep(1)

            elif choice == '4':
                username = user_input("Юзернейм:")
                id = user_input("ID:")
                number = user_input("Номер телефона:")
                task = (choice, "1", username, id, None, None, number, None, None, None)
                process_task(task, senders_dict, working_proxies, sent_emails)
                time.sleep(1)
            else:
                print(f"{RED}Неверный выбор.{RESET}")

        else:
            print(f"{RED}Неверный выбор.{RESET}")

    print(f"{GREEN}Всего отправлено писем: {sent_emails[0]}{RESET}")

if __name__ == "__main__":
    main()