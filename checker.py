import random

# from library import MuskLibrary, JGBLibrary
# from dynamic_hash_table import DynamicHashMap, DynamicHashSet
# from hash_table import HashSet
import library as lib
import dynamic_hash_table as dht
from prime_generator import set_primes
import hash_table as ht
import importlib
import sys

import resource


def limit_mem(limit_bytes):
    resource.setrlimit(resource.RLIMIT_AS, (limit_bytes, limit_bytes))


def get_rehash_primes_list(first_prime):
    max_size = int(1e7)
    is_prime = [True] * max_size

    for i in range(2, max_size):
        if is_prime[i]:
            for j in range(2 * i, max_size, i):
                is_prime[j] = False

    primes = []
    i = 2 * first_prime + 1
    while i < max_size:
        if is_prime[i]:
            primes.append(i)
            i = 2 * i + 1
        else:
            i += 1

    return primes[::-1]


def initialize(init_tb_sz):
    # Set primes etc.
    primes_list = get_rehash_primes_list(init_tb_sz)
    set_primes(primes_list.copy())


def reload_libs():
    try:
        importlib.reload(ht)
        importlib.reload(dht)
        importlib.reload(lib)
        return 0
    except Exception as e:
        print("Error in import:", e)
        return -1


def read_file(filename):
    params = None
    book_titles = []
    books = []
    cnt_ops = []
    distinct_ops = []
    search_ops = []

    with open(filename, "r") as f:
        params = map(int, f.readline().strip().split())
        n = int(f.readline().strip())
        for _ in range(n):
            book_titles.append(f.readline().strip())
            books.append(f.readline().strip().split())

        m = int(f.readline().strip())
        for _ in range(m):
            cnt_ops.append(f.readline().strip())

        m = int(f.readline().strip())
        for _ in range(m):
            distinct_ops.append(f.readline().strip())

        m = int(f.readline().strip())
        for _ in range(m):
            search_ops.append(f.readline().strip())

    return params, book_titles, books, cnt_ops, distinct_ops, search_ops


"""
Return Codes:
1   - Correct Ans
0   - Wrong Ans
-1  - TLE
-2  - MLE
"""
MEM_LIM = 1 * 1024 * 1024 * 1024  # 1GB


def create_musk_obj(books, book_titles):
    # limit_mem(MEM_LIM)
    try:
        musk_lib = lib.MuskLibrary(book_titles.copy(), books.copy())
        return musk_lib
    except Exception as e:
        print(f"Error: {e}")
        return None


def run_musk_distinct(musk_lib, cnt_ops, distinct_ops, search_ops, filename):
    # filename: file name of student output file
    # limit_mem(MEM_LIM)
    orig_stdout = sys.stdout
    f = open(filename, "w")
    sys.stdout = f
    try:
        for op in cnt_ops:
            print(musk_lib.count_distinct_words(op))
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 50)
    try:
        for op in distinct_ops:
            print(musk_lib.distinct_words(op))
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 50)
    sys.stdout = orig_stdout
    f.close()


def run_musk_search(musk_lib, cnt_ops, distinct_ops, search_ops, filename):
    # filename: file name of student output file
    # limit_mem(MEM_LIM)
    orig_stdout = sys.stdout
    f = open(filename, "a")
    sys.stdout = f
    try:
        for op in search_ops:
            print(musk_lib.search_keyword(op))
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 50)
    musk_lib.print_books()
    sys.stdout = orig_stdout
    f.close()


def create_jgb_obj(books, book_titles, type, params):
    # limit_mem(MEM_LIM)
    try:
        jgb_lib = lib.JGBLibrary(type, params)
        for title, book in zip(book_titles, books):
            jgb_lib.add_book(title, book)
        return jgb_lib
    except Exception as e:
        print(f"Error: {e}")
        return None


def run_jgb_distinct(jgb_lib, cnt_ops, distinct_ops, search_ops, filename):
    # filename: file name of student output file
    # limit_mem(MEM_LIM)
    orig_stdout = sys.stdout
    f = open(filename, "w")
    sys.stdout = f
    try:
        for op in cnt_ops:
            print(jgb_lib.count_distinct_words(op))
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 50)

    try:
        for op in distinct_ops:
            print(jgb_lib.distinct_words(op))
    except Exception as e:
        print(f"Error: {e}")

    print("-" * 50)
    sys.stdout = orig_stdout
    f.close()


def run_jgb_search(jgb_lib, cnt_ops, distinct_ops, search_ops, filename):
    # filename: file name of student output file
    # limit_mem(MEM_LIM)
    orig_stdout = sys.stdout
    f = open(filename, "a")
    sys.stdout = f
    try:
        for op in search_ops:
            print(jgb_lib.search_keyword(op))
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 50)
    jgb_lib.print_books()
    sys.stdout = orig_stdout
    f.close()


def check_musk(student_filename, model_filename):
    student_file = open(student_filename, "r")
    student_lines = student_file.read()
    model_file = open(model_filename, "r")
    model_lines = model_file.read()

    student_output = student_lines.split("-" * 50)
    model_output = model_lines.split("-" * 50)
    correctness = [1, 1, 1, 1]

    # Check count distinct words
    cnt_distinct_words_student = student_output[0].strip().split("\n")
    cnt_distinct_words_model = model_output[0].strip().split("\n")
    if cnt_distinct_words_student != cnt_distinct_words_model:
        correctness[0] = 0

    # Check distinct words
    distinct_words_student = student_output[1].strip().split("\n")
    distinct_words_model = model_output[1].strip().split("\n")
    if distinct_words_student != distinct_words_model:
        correctness[1] = 0

    # Check search keyword
    search_keyword_student = student_output[2].strip().split("\n")
    search_keyword_model = model_output[2].strip().split("\n")
    if search_keyword_student != search_keyword_model:
        correctness[2] = 0

    # Check print books
    print_books_student = student_output[3].strip().split("\n")
    print_books_model = model_output[3].strip().split("\n")
    if len(print_books_student) != len(print_books_model):
        correctness[3] = 0
    else:
        for i in range(len(print_books_student)):
            book_title_student = print_books_student[i].split(":")[0].strip()
            book_title_model = print_books_model[i].split(":")[0].strip()
            if book_title_student != book_title_model:
                correctness[3] = 0
                break

            words_student = print_books_student[i].split(":")[1].strip().split("|")
            words_student = [word.strip() for word in words_student]
            words_model = print_books_model[i].split(":")[1].strip().split("|")
            words_model = [word.strip() for word in words_model]
            if words_student != words_model:
                correctness[3] = 0
                break

    return correctness


def check_jobs(student_filename, model_filename):
    student_file = open(student_filename, "r")
    student_lines = student_file.read()
    model_file = open(model_filename, "r")
    model_lines = model_file.read()

    student_output = student_lines.split("-" * 50)
    model_output = model_lines.split("-" * 50)

    correctness = [1, 1, 1, 1]

    # Check count distinct words
    cnt_distinct_words_student = student_output[0].strip().split("\n")
    cnt_distinct_words_model = model_output[0].strip().split("\n")
    if cnt_distinct_words_student != cnt_distinct_words_model:
        correctness[0] = 0

    # Check distinct words
    distinct_words_student = student_output[1].strip().split("\n")
    distinct_words_model = model_output[1].strip().split("\n")
    if distinct_words_student != distinct_words_model:
        correctness[1] = 0

    # Check search keyword
    search_keyword_student = student_output[2].strip().split("\n")
    search_keyword_model = model_output[2].strip().split("\n")
    # convert each item to list of words and ignore first and last character of '[' and ']'
    if len(search_keyword_student) != len(search_keyword_model):
        correctness[2] = 0
    else:
        for i in range(len(search_keyword_student)):
            search_student = search_keyword_student[i].strip()[1:-1].split(", ")
            search_student = [word.strip() for word in search_student]
            search_model = search_keyword_model[i].strip()[1:-1].split(", ")
            search_model = [word.strip() for word in search_model]
            search_student.sort()
            search_model.sort()
            if search_student != search_model:
                correctness[2] = 0

    # Check print books
    print_books_student = student_output[3].strip().split("\n")
    print_books_model = model_output[3].strip().split("\n")
    if len(print_books_student) != len(print_books_model):
        correctness[3] = 0
    else:
        books_student = []
        books_model = []

        for i in range(len(print_books_student)):
            book_title_student = print_books_student[i].split(":")[0].strip()
            book_title_model = print_books_model[i].split(":")[0].strip()

            words_student = print_books_student[i].split(":")[1].strip().split("|")
            words_student = [word.strip() for word in words_student]
            words_student = [word.split(";") for word in words_student]
            words_student = [[w.strip() for w in word] for word in words_student]

            words_model = print_books_model[i].split(":")[1].strip().split("|")
            words_model = [word.strip() for word in words_model]
            words_model = [word.split(";") for word in words_model]
            words_model = [[w.strip() for w in word] for word in words_model]

            books_student.append((book_title_student, words_student))
            books_model.append((book_title_model, words_model))

        # ordering of books in print_books does not matter
        books_student.sort()
        books_model.sort()
        if books_student != books_model:
            correctness[3] = 0

    return correctness


def check_gates_bezos(student_filename, model_filename):
    student_file = open(student_filename, "r")
    student_lines = student_file.read()
    model_file = open(model_filename, "r")
    model_lines = model_file.read()

    student_output = student_lines.split("-" * 50)
    model_output = model_lines.split("-" * 50)

    correctness = [1, 1, 1, 1]

    # Check count distinct words
    cnt_distinct_words_student = student_output[0].strip().split("\n")
    cnt_distinct_words_model = model_output[0].strip().split("\n")
    if cnt_distinct_words_student != cnt_distinct_words_model:
        correctness[0] = 0

    # Check distinct words
    distinct_words_student = student_output[1].strip().split("\n")
    distinct_words_model = model_output[1].strip().split("\n")
    if distinct_words_student != distinct_words_model:
        correctness[1] = 0

    # Check search keyword
    search_keyword_student = student_output[2].strip().split("\n")
    search_keyword_model = model_output[2].strip().split("\n")
    if len(search_keyword_student) != len(search_keyword_model):
        correctness[2] = 0
    else:
        for i in range(len(search_keyword_student)):
            search_student = search_keyword_student[i].strip()[1:-1].split(", ")
            search_student = [word.strip() for word in search_student]
            search_model = search_keyword_model[i].strip()[1:-1].split(", ")
            search_model = [word.strip() for word in search_model]
            search_student.sort()
            search_model.sort()
            if search_student != search_model:
                correctness[2] = 0

    # Check print books
    print_books_student = student_output[3].strip().split("\n")
    print_books_model = model_output[3].strip().split("\n")
    if len(print_books_student) != len(print_books_model):
        correctness[3] = 0

    else:
        books_student = []
        books_model = []

        for i in range(len(print_books_student)):
            book_title_student = print_books_student[i].split(":")[0].strip()
            book_title_model = print_books_model[i].split(":")[0].strip()

            words_student = print_books_student[i].split(":")[1].strip().split("|")
            words_student = [word.strip() for word in words_student]

            words_model = print_books_model[i].split(":")[1].strip().split("|")
            words_model = [word.strip() for word in words_model]

            books_student.append((book_title_student, words_student))
            books_model.append((book_title_model, words_model))

        # ordering of books in print_books does not matter
        books_student.sort()
        books_model.sort()

        if books_student != books_model:
            correctness[3] = 0

    return correctness


def parse_hashset_string(hs, collision_type):
    slots = hs.strip().split("|")
    slots = [slot.strip() for slot in slots]
    if collision_type == "chain":
        new_slots = []
        for slot in slots:
            tmp = slot.split(";")
            tmp = [t.strip() for t in tmp]
            new_slots.append(tmp)
        return new_slots

    return slots


def check_rehash(student_filename, model_filename, collision_type):
    student_file = open(student_filename, "r")
    student_hs = student_file.read()
    model_file = open(model_filename, "r")
    model_hs = model_file.read()

    student_table = parse_hashset_string(student_hs, collision_type)
    model_table = parse_hashset_string(model_hs, collision_type)

    if student_table == model_table:
        return 1

    return 0


def check_hash(student_slot, model_slot):
    if student_slot == model_slot:
        return 1

    return 0


def run_rehashing(words, collision_type, params, filename):
    # filename: file name of student output file
    # limit_mem(MEM_LIM)
    initialize(params[-1])
    try:
        dhs = dht.DynamicHashSet(collision_type, params)
        for word in words:
            dhs.insert(word)
    except Exception as e:
        print(f"Error: {e}")

    with open(filename, "w") as f:
        f.write(dhs.__str__())


def run_hashing(hash_str, z, sz):
    # Call get_slot() of hashtable to ensure they are hashing in O(n)
    # limit_mem(MEM_LIM)
    try:
        hs = ht.HashSet("Chain", (z, sz))
        slot = hs.get_slot(hash_str)
        return slot
    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    current_limit, max_limit = resource.getrlimit(resource.RLIMIT_AS)

    # Print the current and maximum memory limits
    print(f"Current limit: {current_limit} bytes")
    print(f"Maximum limit: {max_limit} bytes")
    # add testcase filenames and run checker
    # checker = LibraryChecker()
    # checker.check("testcase.txt")
    create_jgb_obj(None, None, None, None, 1024 * 1024)
