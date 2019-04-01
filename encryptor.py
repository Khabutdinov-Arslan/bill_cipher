#! /usr/bin/python3
import json
import argparse
import sys
import string
import copy

ALPHABET_SIZE = len(string.ascii_lowercase)
SHIFT_STRING = string.ascii_lowercase + string.ascii_lowercase + string.ascii_uppercase + string.ascii_uppercase


def get_input(input_filename):
    if input_filename == '':
        return sys.stdin.read()
    else:
        with open(input_filename, 'r') as input_file:
            return input_file.read()


def return_output(output_text, output_filename):
    if output_filename == '':
        print(output_text, end='', sep='')
    else:
        with open(output_filename, 'w') as output_file:
            print(output_text, file=output_file, end='', sep='')


def get_letter_index(letter):
    letter_index = {}
    j = 0
    for i in string.ascii_lowercase + string.ascii_uppercase:
        letter_index[i] = j
        j = (j + 1) % ALPHABET_SIZE
    if letter in letter_index:
        return letter_index[letter]
    else:
        return None




def process_letter(letter, shift=0):
    if shift < 0:
        shift = 26 + shift
    if get_letter_index(letter) is None:
        return letter
    else:
        letter_index = {}
        j = 0
        for i in string.ascii_lowercase:
            letter_index[i] = j
            j += 1
        j = ALPHABET_SIZE * 2
        for i in string.ascii_uppercase:
            letter_index[i] = j
            j += 1
        return SHIFT_STRING[letter_index[letter] + shift]



def caesar(input_text, shift):
    return ''.join([process_letter(i, shift) for i in input_text])


def vigenere(input_text, shift_string, mode):
    shifts = []
    for i in shift_string:
        shifts.append(get_letter_index(i))
    j = 0
    output_array = []
    for i in input_text:
        letter_index = get_letter_index(i)
        if letter_index is None:
            output_array.append(i)
        else:
            output_array.append(process_letter(i, shifts[j] * mode))
            j = (j + 1) % len(shifts)
    return ''.join(output_array)


def calculate_stats(input_text):
    letter_count = dict()
    for i in range(ALPHABET_SIZE):
        letter_count[i] = 0
    for i in input_text:
        letter_index = get_letter_index(i)
        if letter_index is not None:
            letter_count[letter_index] += 1
    return letter_count


def calculate_difference(letter_stats_left, letter_stats_right):
    difference_module = 0
    for i in range(ALPHABET_SIZE):
        difference_module += abs(letter_stats_left[i] - letter_stats_right[i])
    return difference_module


def caesar_hack(input_text, stats_file=''):
    with open(stats_file, 'r') as input_file:
        dict_content = input_file.read()
        letter_stats = json.loads(dict_content)
        letter_stats = {int(k): int(v) for k, v in letter_stats.items()}
    best_shift = None
    best_difference = None
    current_stats = calculate_stats(input_text)
    for i in range(ALPHABET_SIZE):
        current_difference = calculate_difference(current_stats, letter_stats)
        if (best_shift is None) or (current_difference < best_difference):
            best_difference = current_difference
            best_shift = i
        new_stats = {}
        for k, v in current_stats.items():
            new_stats[(k + 1) % ALPHABET_SIZE] = v
        current_stats = copy.deepcopy(new_stats)
    return caesar(input_text, best_shift)


def encrypt_text(args):
    input_text = get_input(args.input_file)
    if args.cipher == 'caesar':
        key = int(args.key)
        if args.decrypt == True:
            key = -key
        output_text = caesar(input_text, key)
    else:
        if args.decrypt == True:
            output_text = vigenere(input_text, args.key, -1)
        else:
            output_text = vigenere(input_text, args.key, 1)
    return_output(output_text, args.output_file)


def train_text(args):
    input_text = get_input(args.text_file)
    output_text = json.dumps(calculate_stats(input_text))
    return_output(output_text, args.model_file)


def hack_text(args):
    input_text = get_input(args.input_file)
    output_text = caesar_hack(input_text, args.model_file)
    return_output(output_text, args.output_file)


def parser_init():
    parser = argparse.ArgumentParser(description='Simple encryption utility')
    subparsers = parser.add_subparsers()

    encode_parser = subparsers.add_parser('encode', help='Encode text')
    encode_parser.add_argument('--cipher', required=True, help='Caesar or Vigenere')
    encode_parser.add_argument('--key', required=True, help='Cipher key')
    encode_parser.add_argument('--input-file', default='')
    encode_parser.add_argument('--output-file', default='')
    encode_parser.add_argument('--decrypt', default=False)
    encode_parser.set_defaults(func=encrypt_text)

    decode_parser = subparsers.add_parser('decode', help='Decode text')
    decode_parser.add_argument('--cipher', required=True, help='Caesar or Vigenere')
    decode_parser.add_argument('--key', required=True, help='Cipher key')
    decode_parser.add_argument('--input-file', default='')
    decode_parser.add_argument('--output-file', default='')
    decode_parser.add_argument('--decrypt', default=True)
    decode_parser.set_defaults(func=encrypt_text)

    train_parser = subparsers.add_parser('train', help='Calculate language stats')
    train_parser.add_argument('--text-file', help='Input file', required=True)
    train_parser.add_argument('--model-file', help='Output file for stats', required=True)
    train_parser.set_defaults(func=train_text)

    hack_parser = subparsers.add_parser('hack', help='Decrypt text with unknown Caesar key')
    hack_parser.add_argument('--model-file', help='File with language stats', required=True)
    hack_parser.add_argument('--input-file', default='')
    hack_parser.add_argument('--output-file', default='')
    hack_parser.set_defaults(func=hack_text)

    try:
        arguments = parser.parse_args()
        arguments.func(arguments)
    except Exception:
        raise ValueError("Use correct argument format")


parser_init()
