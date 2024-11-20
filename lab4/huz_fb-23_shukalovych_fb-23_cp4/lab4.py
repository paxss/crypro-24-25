import random
import math
from math_operations import *

YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

rsa_keys = {}
messages = {}
ciphertext = None       # ШТ
decrypted_message = None
signed_message = None   # Підписане повідомлення
signature = None        # Підпис
hash_value = None       # Хеш повідомлення

# Функція для перевірки числа на простоту за допомогою тесту Міллера-Рабіна
def is_prime_miller_rabin(p, k=10):
    if p < 2 or p % 2 == 0:
        return p == 2

    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    for prime in small_primes:
        if p % prime == 0 and p != prime:
            return False

    s = 0
    d = p - 1
    while d % 2 == 0:
        d //= 2
        s += 1

    def check_composite(a):
        x = pow(a, d, p)
        if x == 1 or x == p - 1:
            return False
        for _ in range(s - 1):
            x = pow(x, 2, p)
            if x == p - 1:
                return False
        return True

    for _ in range(k):
        a = random.randint(2, p - 2)
        if math.gcd(a, p) != 1 or check_composite(a):
            return False

    return True

# Функція для генерації випадкового простого числа довжини щонайменше n біт
def generate_prime(bits, k=10):
    while True:
        candidate = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime_miller_rabin(candidate, k):
            return candidate

# Функція для генерації двох пар простих чисел
def generate_prime_pairs(bits=256):
    while True:
        # Генерація простих чисел для абонента A
        p = generate_prime(bits)
        q = generate_prime(bits)
        pq = p * q

        # Генерація простих чисел для абонента B
        p1 = generate_prime(bits)
        q1 = generate_prime(bits)
        p1q1 = p1 * q1

        if pq <= p1q1:
            return (p, q), (p1, q1)

# Функція для розширеного алгоритму Евкліда
def mod_inverse(e, phi):
    b = extended_euclidean(e, phi)
    if b is None:
        raise ValueError("Обернений елемент не існує.")
    return b

# Функція для генерації ключової пари RSA
def generate_rsa_key_pair(bits=256):
    # Генерація простих чисел p і q
    p = generate_prime(bits)
    q = generate_prime(bits)

    # Обчислення n та функції Ойлера phi(n)
    n = p * q
    phi = (p - 1) * (q - 1)

    # Вибір відкритого експонента e
    e = 2**16 + 1
    if math.gcd(e, phi) != 1:
        raise ValueError("Невдалий вибір e, знайдено спільний дільник з phi.")

    # Обчислення секретного експонента d
    d = mod_inverse(e, phi)

    # Повернення ключів
    public_key = (e, n)
    private_key = (d, p, q)

    return public_key, private_key

def GenerateKeyPair(bits=256):
    global rsa_keys
    public_key_a, private_key_a = generate_rsa_key_pair(bits)
    rsa_keys["A"] = {"public_key": public_key_a, "private_key": private_key_a}

    public_key_b, private_key_b = generate_rsa_key_pair(bits)
    rsa_keys["B"] = {"public_key": public_key_b, "private_key": private_key_b}


# Процедура шифрування повідомлення
def Encrypt(user):
    global rsa_keys, messages
    e, n = rsa_keys[user]["public_key"]

    message = random.randint(1000, 10000)  # Генерація випадкового повідомлення
    ciphertext = pow(message, e, n)

    # Зберігаємо повідомлення та криптограму в словнику
    messages[user] = {"message": message, "ciphertext": ciphertext}

    print(f"Повідомлення для {user}: {message}")
    print(f"Криптограма для {user}: {ciphertext}")


# Процедура розшифрування повідомлення
def Decrypt(user):
    global messages, decrypted_message, rsa_keys
    if "ciphertext" not in messages.get(user, {}):
        print(f"Помилка: Криптограма для {user} відсутня!")
        return
    d, p, q = rsa_keys[user]["private_key"]
    n = p * q

    ciphertext = messages[user]["ciphertext"]
    decrypted_message = pow(ciphertext, d, n)
    print(f"Розшифроване повідомлення для {user}: {decrypted_message}")

    if decrypted_message == messages[user]["message"]:
        print("Розшифрування успішне!")
    else:
        print("Помилка розшифрування!")


# Процедура для створення цифрового підпису
def Sign(user):
    global messages, signature, rsa_keys
    if "message" not in messages.get(user, {}):
        print(f"Помилка: Повідомлення для {user} відсутнє!")
        return
    d, p, q = rsa_keys[user]["private_key"]
    n = p * q

    message = messages[user]["message"]
    hash_value = hash(message)  # Використовуємо просту хеш-функцію
    signature = pow(hash_value, d, n)

    # Зберігаємо підпис в словнику
    messages[user]["signature"] = signature
    print(f"Цифровий підпис для {user}: {signature}")


# Процедура для перевірки цифрового підпису
def Verify(user):
    global messages, signature, rsa_keys
    if "signature" not in messages.get(user, {}):
        print(f"Помилка: Підпис для {user} відсутній!")
        return
    e, n = rsa_keys[user]["public_key"]

    signature = messages[user]["signature"]

    # Перевірка підпису
    verified_hash = pow(signature, e, n)
    print(f"Перевірений хеш для {user}: {verified_hash}")

    message = messages[user]["message"]
    if verified_hash == hash(message):
        print("Підпис правильний!")
    else:
        print("Підпис неправильний!")

def main():
    while True:
        print(YELLOW + "\n♥Меню♥" + RESET)
        print("1. Вибір випадкового простого числа")
        print("2. Генерація двох пар простих чисел")
        print("3. Генерація ключових пар RSA для абонентів A та B")
        print("4. Перехід до меню процедур")
        print("5. ...")
        print("6. Вийти")
        user_choice = input("Виберіть опцію: ").strip()
        if user_choice == '6':
            print(BLUE + " /}___/}❀\n( • . •)\n/ >    > Byeee" + RESET)
            break

        if user_choice == '1':
            random_prime = generate_prime(bits=10)
            if random_prime:
                print(f"Випадкове просте число: {random_prime}")
            else:
                print(f"Просте число не знайдено.")

        elif user_choice == '2':
            (p, q), (p1, q1) = generate_prime_pairs(bits=256)
            print(f"Пара простих чисел для абонента A: p = {p}, q = {q}")
            print(f"Пара простих чисел для абонента B: p1 = {p1}, q1 = {q1}")

        elif user_choice == '3':
            GenerateKeyPair(bits=256)
            print(f"Відкритий ключ абонента A: {rsa_keys['A']['public_key']}")
            print(f"Секретний ключ абонента A: {rsa_keys['A']['private_key']}")
            print(f"Відкритий ключ абонента B: {rsa_keys['B']['public_key']}")
            print(f"Секретний ключ абонента B: {rsa_keys['B']['private_key']}")

        elif user_choice == '4':
            while True:
                print(YELLOW + "\n-♥-Меню процедур-♥-" + RESET)
                print("0. Повернутись")
                print("1. Зашифрувати повідомлення для аб. А/В")
                print("2. Розшифрувати повідомлення для аб. А/В")
                print("3. Створити повідомлення з цифровим підписом для аб. А/В")
                print("4. Перевірка цифрового підпису для аб. А/В")

                text_choice = input("Виберіть опцію: ").strip()

                if text_choice == '1':
                    user = input("Виберіть користувача (A/B): ").strip().upper()
                    if user in rsa_keys:
                        Encrypt(user)
                    else:
                        print("Невірний вибір користувача або відсутня пара ключів.")

                elif text_choice == '2':
                    user = input("Виберіть користувача (A/B): ").strip().upper()
                    if user in rsa_keys:
                        Decrypt(user)
                    else:
                        print("Невірний вибір користувача або відсутня пара ключів.")

                elif text_choice == '3':
                    user = input("Виберіть користувача для підпису (A/B): ").strip().upper()
                    if user in rsa_keys:
                        Sign(user)
                    else:
                        print("Невірний вибір користувача або відсутня пара ключів.")

                elif text_choice == '4':
                    user = input("Виберіть користувача для перевірки підпису (A/B): ").strip().upper()
                    if user in rsa_keys:
                        Verify(user)
                    else:
                        print("Невірний вибір користувача або відсутня пара ключів.")

                elif text_choice == '0':
                    break
                else:
                    print("Неправильний вибір. Спробуйте знову.")

        elif user_choice == '5':
            print("краказябра")
        else:
            print("Неправильний вибір. Спробуйте знову.")

if __name__ == "__main__":
    main()
