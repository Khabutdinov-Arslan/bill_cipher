#! /usr/bin/python3
import json
import argparse
import sys

letter_stats = {0: 1472, 1: 348, 2: 403, 3: 1047, 4: 2483, 5: 351, 6: 506, 7: 1256, 8: 1174, 9: 24, 10: 224, 11: 988,
                12: 494, 13: 1249, 14: 1470, 15: 364, 16: 6, 17: 1171, 18: 1293, 19: 1688, 20: 635, 21: 216, 22: 490,
                23: 28, 24: 484, 25: 10}

parser = argparse.ArgumentParser(description='Simple encryptor and decryptor')


def create_arguments():
    global parser
    parser.add_argument('mode', help='encode, decode or hack')
    parser.add_argument('--input-file', help='file to process', default='')
    parser.add_argument('--output-file', help='result file', default='')
    parser.add_argument('--cipher', help='caesar or vigenere', default='caesar')
    parser.add_argument('--key', help='number from 0 to 25 for caesar, string for vigenere', default='0')
    parser.add_argument('--text-file', help='file to analyze')
    parser.add_argument('--model-file', help='output model file', default='')


def get_input(input_filename):
    if input_filename == '':
        content = sys.stdin.read()
    else:
        with open(input_filename, 'r') as input_file:
            content = input_file.read()
    return content


def return_output(output_text, output_filename):
    if output_filename == '':
        print(output_text, end='', sep='')
    else:
        with open(output_filename, 'w') as output_file:
            print(output_text, file=output_file, end='', sep='')


def shift_letter(letter, shift):
    return (letter + 26 + shift) % 26


def process_letter(letter, shift=0):
    letter_index = ord(letter)
    if (letter_index >= 65) and (letter_index <= 90):
        letter_index = shift_letter(letter_index - 65, shift) + 65
    else:
        if (letter_index >= 97) and (letter_index <= 122):
            letter_index = shift_letter(letter_index - 97, shift) + 97
    return chr(letter_index)


def get_letter_index(letter):
    letter_index = ord(letter)
    if (letter_index >= 65) and (letter_index <= 90):
        letter_index -= 65
    else:
        if (letter_index >= 97) and (letter_index <= 122):
            letter_index -= 97
        else:
            letter_index = -1
    return letter_index


def caesar(input_text, shift):
    output_text = ''
    for i in input_text:
        output_text += process_letter(i, shift)
    return output_text


def vigenere(input_text, shift_string, mode):
    output_text = ''
    shifts = []
    for i in shift_string:
        shifts.append(get_letter_index(i))
    j = 0
    for i in input_text:
        letter_index = get_letter_index(i)
        if letter_index == -1:
            output_text += i
        else:
            output_text += process_letter(i, shifts[j] * mode)
            j = (j + 1) % len(shifts)
    return output_text


def calculate_stats(input_text):
    letter_count = dict()
    for i in range(26):
        letter_count[i] = 0
    for i in input_text:
        letter_index = get_letter_index(i)
        if (letter_index != -1):
            letter_count[letter_index] += 1
    return json.dumps(letter_count)


def calculate_difference(input_text):
    letter_count = dict()
    difference_module = 0
    for i in range(26):
        letter_count[i] = 0
    for i in input_text:
        letter_index = get_letter_index(i)
        if letter_index != -1:
            letter_count[letter_index] += 1
    for i in letter_count.keys():
        difference_module += abs(letter_count[i] - letter_stats[i])
    return difference_module


def caesar_hack(input_text, stats_file=''):
    if stats_file != '':
        with open(stats_file, 'r') as input_file:
            dict_content = input_file.read()
        global letter_stats
        letter_stats = json.loads(dict_content)
        letter_stats = {int(k): int(v) for k, v in letter_stats.items()}
    best_shift = -1
    best_difference = -1
    for i in range(26):
        current_text = caesar(input_text, -i)
        current_difference = calculate_difference(current_text)
        if (best_shift == -1) or (current_difference < best_difference):
            best_difference = current_difference
            best_shift = i
    return caesar(input_text, -best_shift)


def encrypt_text(cipher, key, input_filename, output_filename):
    input_text = get_input(input_filename)
    if cipher == 'caesar':
        key = int(key)
        output_text = caesar(input_text, key)
    else:
        output_text = vigenere(input_text, key, 1)
    return_output(output_text, output_filename)


def decrypt_text(cipher, key, input_filename, output_filename):
    input_text = get_input(input_filename)
    if cipher == 'caesar':
        key = -int(key)
        output_text = caesar(input_text, key)
    else:
        output_text = vigenere(input_text, key, -1)
    return_output(output_text, output_filename)


def train_text(input_filename, output_filename):
    input_text = get_input(input_filename)
    output_text = calculate_stats(input_text)
    return_output(output_text, output_filename)


def hack_text(input_filename, output_filename, stats_filename):
    input_text = get_input(input_filename)
    output_text = caesar_hack(input_text, stats_filename)
    return_output(output_text, output_filename)


def process_arguments():
    global parser
    arguments = parser.parse_args()
    if arguments.mode == 'encode':
        encrypt_text(arguments.cipher, arguments.key, arguments.input_file, arguments.output_file)
    else:
        if arguments.mode == 'decode':
            decrypt_text(arguments.cipher, arguments.key, arguments.input_file, arguments.output_file)
        else:
            if arguments.mode == 'train':
                train_text(arguments.text_file, arguments.model_file)
            else:
                hack_text(arguments.input_file, arguments.output_file, arguments.model_file)


create_arguments()
process_arguments()
