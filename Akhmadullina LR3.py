def split_into_blocks(data, block_size):
    """Разделяет данные на блоки заданного размера."""
    return [data[i:i + block_size] for i in range(0, len(data), block_size)]

def split_key(key, key_size):
    """Разделяет ключ на итерационные ключи."""
    return [key[i:i + key_size] for i in range(0, len(key), key_size)]

def feistel_round(L, R, key, F):
    """Один раунд сети Фейстеля."""
    T = [R[i] ^ key[i] for i in range(len(R))]
    V = F(T)
    new_L = R
    new_R = [L[i] ^ V[i] for i in range(len(L))]
    return new_L, new_R

def F(T, permutation):
    """Функция F: перестановка 16 бит."""
    # Преобразуем T в список из 16 битов (по 1 биту на каждый элемент)
    T_expanded = []
    for byte in T:
        for i in range(8):  # Разбиваем каждый байт на 8 битов
            T_expanded.append((byte >> (7 - i)) & 1)
    # Применяем перестановку
    V = [T_expanded[p] for p in permutation]
    # Сворачиваем результат обратно в 2 байта
    V_bytes = []
    for i in range(0, 16, 8):
        byte = 0
        for j in range(8):
            byte |= V[i + j] << (7 - j)
        V_bytes.append(byte)
    return V_bytes

def encrypt_block(block, keys, permutation):
    """Шифрует один блок с использованием сети Фейстеля."""
    L, R = block[:len(block)//2], block[len(block)//2:]
    for i, key in enumerate(keys):
        print(f"Раунд {i}")
        print(f"Начальное состояние регистров:\nL={to_hex(L)}\nR={to_hex(R)}")
        T = [R[j] ^ key[j] for j in range(len(R))]
        print(f"После сложения с итерационным ключом K{i}:\nT=R{i}+K{i}={to_hex(T)}")
        V = F(T, permutation)
        print(f"F(T{i})={to_hex(V)}")
        L, R = R, [L[j] ^ V[j] for j in range(len(L))]
        print(f"Состояние регистров после сложения с F(L{i}):\nL={to_hex(L)}\nR={to_hex(R)}\n")
    return L, R

def decrypt_block(block, keys, permutation):
    """Расшифровывает один блок с использованием сети Фейстеля."""
    L, R = block[:len(block)//2], block[len(block)//2:]
    for i, key in enumerate(reversed(keys)):
        print(f"Раунд {len(keys) - 1 - i}")
        print(f"Начальное состояние регистров:\nL={to_hex(L)}\nR={to_hex(R)}")
        T = [L[j] ^ key[j] for j in range(len(L))]
        print(f"После сложения с итерационным ключом K{len(keys) - 1 - i}:\nT=L{len(keys) - 1 - i}+K{len(keys) - 1 - i}={to_hex(T)}")
        V = F(T, permutation)
        print(f"F(T{len(keys) - 1 - i})={to_hex(V)}")
        L, R = [R[j] ^ V[j] for j in range(len(R))], L
        print(f"Состояние регистров после сложения с F(L{len(keys) - 1 - i}):\nL={to_hex(L)}\nR={to_hex(R)}\n")
    return L, R

def to_hex(data):
    """Преобразует список чисел в шестнадцатеричный формат."""
    return [f"{byte:02x}" for byte in data]

def main():
    # Параметры алгоритма
    block_size = 4  # Размер блока в байтах (32 бита)
    key_size = 2  # Размер итерационного ключа в байтах (16 бит)
    num_rounds = 8  # Количество раундов
    permutation = [15, 14, 12, 4, 0, 6, 3, 5, 1, 11, 8, 10, 7, 2, 9, 13]  # Перестановка для функции F

    # Исходные данные
    plaintext = [0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e, 0x3f,
                 0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x4b, 0x4c, 0x4d, 0x4e, 0x4f,
                 0x30, 0x31, 0x32, 0x33]
    key = [0x58, 0x9c, 0x9f, 0x34, 0x23, 0xd1, 0x9f, 0x1a, 0x22, 0xd1, 0xd8, 0xc3, 0x7c, 0xf0, 0x88, 0xd8]

    # Разделение текста и ключа на блоки
    blocks = split_into_blocks(plaintext, block_size)
    keys = split_key(key, key_size)

    print("Исходный текст:", to_hex(plaintext))
    print("Итерационные ключи:", [to_hex(key) for key in keys])

    print("\nШифрование:")
    encrypted_blocks = []
    for i, block in enumerate(blocks):
        print(f"Шаг {i}")
        print(f"Инициализация:\nL={to_hex(block[:block_size//2])}\nR={to_hex(block[block_size//2:])}\n")
        L, R = encrypt_block(block, keys, permutation)
        encrypted_blocks.extend(L + R)
        print(f"Зашифрованный блок R{i}):\n{to_hex(L)} {to_hex(R)}\n")

    print("Результат зашифрования:", to_hex(encrypted_blocks))

    print("\nРасшифрование:")
    decrypted_blocks = []
    for i, block in enumerate(split_into_blocks(encrypted_blocks, block_size)):
        print(f"Шаг {i}")
        print(f"Инициализация:\nL={to_hex(block[:block_size//2])}\nR={to_hex(block[block_size//2:])}\n")
        L, R = decrypt_block(block, keys, permutation)
        decrypted_blocks.extend(L + R)
        print(f"Расшифрованный блок R{i}):\n{to_hex(L)} {to_hex(R)}\n")

    print("Результат расшифрования:", to_hex(decrypted_blocks))

if __name__ == "__main__":
    main()