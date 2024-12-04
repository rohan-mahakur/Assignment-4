import random
import time


class LibraryGenerator:
    def __init__(self):
        random.seed(time.time())
        self.alphabet = (
            "abcdefghijklmnopqrstuvwxyz" + "abcdefghijklmnopqrstuvwxyz".upper()
        )

    def gen_random_word(self, min_len=1, max_len=10):
        word = ""
        for i in range(random.randint(min_len, max_len)):
            word += random.choice(self.alphabet)
        return word

    def gen_distinct_words(self, d, min_len=1, max_len=10):
        words = set()
        while len(words) < d:
            words.add(self.gen_random_word(min_len, max_len))
        return list(words)

    def gen_book_content(self, w, d, min_len=1, max_len=10):
        words = self.gen_distinct_words(d, min_len, max_len)
        book = []
        for _ in range(w):
            book.append(random.choice(words))
        return book
    
    def get_params(self, file_name):
        random.seed(time.time())
        dist_words = []
        num_books = 0
        with open(file_name, "r") as file:
            num_books = int(file.readline())
            
            for i in range(num_books):
                title = file.readline()
                words = file.readline().split()
                dist_words.append(len(set(words)))
        
        min_length = 2*max(num_books, max(dist_words))
        max_length = 5*min_length
        
        is_prime = [True] * (max_length+1)
        
        for i in range(2, max_length):
            if is_prime[i]:
                for j in range(2*i, max_length+1, i):
                    is_prime[j] = False
                    
        z = random.randint(10, 200)
        tb_sz = random.choice([x for x in range(min_length, max_length+1) if is_prime[x]])
        
        z2 = random.randint(10, z)
        c2 = random.choice([x for x in range(2, min_length) if is_prime[x]])
        
        return z, tb_sz, z2, c2
        
        
    def gen_testcase(
        self,
        num_books,
        num_words_min,
        num_words_max,
        num_distinct_min,
        num_distinct_max,
        min_len,
        max_len,
    ):
        book_titles = self.gen_distinct_words(num_books, min_len, max_len)
        books = []
        for _ in range(num_books):
            books.append(
                self.gen_book_content(
                    random.randint(num_words_min, num_words_max),
                    random.randint(num_distinct_min, num_distinct_max),
                    min_len,
                    max_len,
                )
            )
        return book_titles, books

    def print_testcase(
        self,
        filename,
        num_ops_cnt,
        num_ops_distinct,
        num_ops_search,
        book_titles,
        books,
    ):
        n = len(book_titles)
        books_content = set()
        for book in books:
            for word in book:
                books_content.add(word)
        books_content = list(books_content)

        cnt_ops = []
        for _ in range(num_ops_cnt):
            cnt_ops.append(random.choice(book_titles))
        distinct_ops = []
        for _ in range(num_ops_distinct):
            distinct_ops.append(random.choice(book_titles))

        search_ops = []
        for _ in range(num_ops_search):
            search_ops.append(random.choice(books_content))

        with open(filename, "w") as f:
            f.write(f"{n}\n")
            for title, book in zip(book_titles, books):
                f.write(title + "\n")
                f.write(" ".join(book) + "\n")

            f.write(f"{num_ops_cnt}\n")
            for op in cnt_ops:
                f.write(op + "\n")

            f.write(f"{num_ops_distinct}\n")
            for op in distinct_ops:
                f.write(op + "\n")

            f.write(f"{num_ops_search}\n")
            for op in search_ops:
                f.write(op + "\n")


if __name__ == "__main__":
    # add testcase configuration and print testcases
    gen = LibraryGenerator()
    
    with open("rehash_large.txt", "w") as f:
        s = gen.gen_book_content(500000, 400000, 3, 10)
        d = len(set(s))
        print(d)
        min_length = d//5
        max_length = d//2
        
        is_prime = [True] * (max_length+1)
        
        for i in range(2, max_length):
            if is_prime[i]:
                for j in range(2*i, max_length+1, i):
                    is_prime[j] = False
        
        tb_sz = random.choice([x for x in range(min_length, max_length+1) if is_prime[x]])         
        z = random.randint(10, tb_sz-1)
        
        c2 = random.choice([x for x in range(max(min_length//2, 10), min_length) if is_prime[x]])
        z2 = random.randint(1, c2-1)
        
        
        f.write(str(z) + " " + str(tb_sz) + " " + str(z2) + " " + str(c2) + "\n")
        f.write(" ".join(s)+"\n")
