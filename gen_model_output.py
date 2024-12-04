from library import MuskLibrary, JGBLibrary
from hash_table import HashSet
from dynamic_hash_table import DynamicHashSet
from prime_generator import set_primes, get_next_size
import sys


def read_file(filename):
    params = None
    book_titles = []
    books = []
    cnt_ops = []
    distinct_ops = []
    search_ops = []

    with open(filename, "r") as f:
        params = list(map(int, f.readline().strip().split()))
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


def gen_musk(filename):
    _, book_titles, books, cnt_ops, distinct_ops, search_ops = read_file(filename)
    musk_lib = MuskLibrary(book_titles.copy(), books.copy())
    f = open(f"musk_{filename}", "w")

    orig_stdout = sys.stdout
    sys.stdout = f

    for op in cnt_ops:
        print(musk_lib.count_distinct_words(op))
    print("-" * 50)
    for op in distinct_ops:
        print(musk_lib.distinct_words(op))
    print("-" * 50)
    for op in search_ops:
        print(musk_lib.search_keyword(op))
    print("-" * 50)
    musk_lib.print_books()
    sys.stdout = orig_stdout
    f.close()


def gen_jobs(filename):
    params, book_titles, books, cnt_ops, distinct_ops, search_ops = read_file(filename)
    jgb_lib = JGBLibrary("Jobs", (params[0], params[1]))
    for title, book in zip(book_titles, books):
        jgb_lib.add_book(title, book)

    f = open(f"jobs_{filename}", "w")
    orig_stdout = sys.stdout
    sys.stdout = f
    for op in cnt_ops:
        print(jgb_lib.count_distinct_words(op))
    print("-" * 50)
    for op in distinct_ops:
        print(jgb_lib.distinct_words(op))
    print("-" * 50)
    for op in search_ops:
        print(jgb_lib.search_keyword(op))
    print("-" * 50)
    jgb_lib.print_books()
    sys.stdout = orig_stdout
    f.close()


def gen_gates(filename):
    params, book_titles, books, cnt_ops, distinct_ops, search_ops = read_file(filename)
    jgb_lib = JGBLibrary("Gates", (params[0], params[1]))
    for title, book in zip(book_titles, books):
        jgb_lib.add_book(title, book)

    f = open(f"gates_{filename}", "w")
    orig_stdout = sys.stdout
    sys.stdout = f
    for op in cnt_ops:
        print(jgb_lib.count_distinct_words(op))
    print("-" * 50)
    for op in distinct_ops:
        print(jgb_lib.distinct_words(op))
    print("-" * 50)
    for op in search_ops:
        print(jgb_lib.search_keyword(op))
    print("-" * 50)
    jgb_lib.print_books()
    sys.stdout = orig_stdout
    f.close()


def gen_bezos(filename):
    params, book_titles, books, cnt_ops, distinct_ops, search_ops = read_file(filename)
    jgb_lib = JGBLibrary("Bezos", (params[0], params[2], params[3], params[1]))
    for title, book in zip(book_titles, books):
        jgb_lib.add_book(title, book)

    f = open(f"bezos_{filename}", "w")
    orig_stdout = sys.stdout
    sys.stdout = f
    for op in cnt_ops:
        print(jgb_lib.count_distinct_words(op))
    print("-" * 50)
    for op in distinct_ops:
        print(jgb_lib.distinct_words(op))
    print("-" * 50)
    for op in search_ops:
        print(jgb_lib.search_keyword(op))
    print("-" * 50)
    jgb_lib.print_books()
    sys.stdout = orig_stdout
    f.close()


def gen_hash(filename):
    with open(filename, "r") as f:
        z, sz = map(int, f.readline().strip().split())
        n = int(f.readline().strip())
        hash_str = f.readline().strip()

    ht = HashSet("Chain", (z, sz))
    slot = ht.get_slot(hash_str)
    with open(f"model_{filename}", "w") as f:
        f.write(str(slot))


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


def gen_rehash(filename):
    with open(filename, "r") as f:
        z, sz, z2, c2 = map(int, f.readline().strip().split())
        words = f.readline().strip().split()

    primes_list = get_rehash_primes_list(sz)

    # Chain
    set_primes(primes_list.copy())
    dhs = DynamicHashSet("Chain", (z, sz))
    for word in words:
        dhs.insert(word)

    # print("Chain:", dhs.size, dhs.num_elements, dhs.get_load())
    with open(f"chain_{filename}", "w") as f:
        f.write(dhs.__str__())

    # Linear
    set_primes(primes_list.copy())
    dhs = DynamicHashSet("Linear", (z, sz))
    for word in words:
        dhs.insert(word)

    # print("Linear:", dhs.size, dhs.num_elements, dhs.get_load())
    with open(f"linear_{filename}", "w") as f:
        f.write(dhs.__str__())

    # Double
    set_primes(primes_list.copy())
    dhs = DynamicHashSet("Double", (z, z2, c2, sz))
    for word in words:
        dhs.insert(word)

    # print("Double:", dhs.size, dhs.num_elements, dhs.get_load())
    with open(f"double_{filename}", "w") as f:
        f.write(dhs.__str__())


if __name__ == "__main__":
    # tc = ["lib_small.txt", "lib_med.txt", "lib_large.txt"]
    # for t in tc:
    #     gen_musk(t)
    #     gen_jobs(t)
    #     gen_gates(t)
    #     gen_bezos(t)

    # tc = ["hash_large.txt"]
    # for t in tc:
    #     gen_hash(t)

    # tc = ["rehash_small.txt", "rehash_med.txt", "rehash_large.txt"]
    # for t in tc:
    #     gen_rehash(t)

    pass
