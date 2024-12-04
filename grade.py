import checker as ch
import os, sys
import shutil
import pandas as pd
import multiprocessing as mp
import pickle
import time
# import dill as pickle

submission_directory = "./submissions"

# (function to run, input file, model output file) - file names without _med.txt suffix
things_to_test = {
    "musk_sort": (ch.create_musk_obj, "lib", "musk_lib"),
    "musk_distinct": (ch.run_musk_distinct, "lib", "musk_lib"),
    "musk_search": (ch.run_musk_search, "lib", "musk_lib"),
    **{
        f"{coll_type}_insert": (ch.create_jgb_obj, "lib", f"{coll_type}_lib")
        for coll_type in ["jobs", "gates", "bezos"]
    },
    **{
        f"{coll_type}_distinct": (ch.run_jgb_distinct, "lib", f"{coll_type}_lib")
        for coll_type in ["jobs", "gates", "bezos"]
    },
    **{
        f"{coll_type}_search": (ch.run_jgb_search, "lib", f"{coll_type}_lib")
        for coll_type in ["jobs", "gates", "bezos"]
    },
    **{
        f"{coll_type}_rehash": (
            ch.run_rehashing,
            "rehash.txt",
            f"{coll_type}_rehash.txt",
        )
        for coll_type in ["chain", "linear", "double"]
    },
    "hash": (ch.run_hashing, "hash_large.txt", "model_hash_large.txt"),
}

all_files = ["hash_table.py", "library.py", "dynamic_hash_table.py"]


def get_params(file_name, test_type, lib_obj=None):
    z = 0
    sz = 0
    s = ""

    if test_type == "hash":
        with open(file_name, "r") as f:
            z, sz = map(int, f.readline().split())
            l = int(f.readline())

            s = f.readline()

        return (s, z, sz)

    if "rehash" in test_type:
        coll_type = test_type.split("_")[0].title()
        with open(file_name, "r") as f:
            z, sz, z2, c2 = map(int, f.readline().split())
            s = f.readline().split()
            student_filename = f"student_{file_name.split('/')[1]}"
            if "double_rehash" in test_type:
                return (s, coll_type, (z, z2, c2, sz), student_filename)
            else:
                return (s, coll_type, (z, sz), student_filename)

    # Is a lib tc
    book_titles = []
    books = []
    cnt_ops = []
    distinct_ops = []
    search_ops = []

    with open(file_name, "r") as f:
        z, sz, z2, c2 = map(int, f.readline().split())
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

    tc_sz = file_name.split("_")[-1]
    tc_sz = tc_sz.split(".")[0]
    if test_type == "musk_sort":
        return (books, book_titles)

    if test_type == "musk_distinct" or test_type == "musk_search":
        return (lib_obj, cnt_ops, distinct_ops, search_ops, f"student_musk_{tc_sz}.txt")

    coll_type = test_type.split("_")[0]
    if "insert" in test_type:
        if coll_type == "bezos":
            params = (z, z2, c2, sz)
        else:
            params = (z, sz)
        return (books, book_titles, coll_type.capitalize(), params)

    return (
        lib_obj,
        cnt_ops,
        distinct_ops,
        search_ops,
        f"student_{coll_type}_{tc_sz}.txt",
    )


def create_df(folders=None, reload=False):
    """
    Codes:
    1   - Correct Ans
    0   - Wrong Ans
    -1  - TLE
    -2  - MLE
    -3  - Not run yet
    """
    cols = (
        [
            f"{sz}_{test}"
            for sz in ["small", "med", "large"]
            for test in things_to_test.keys()
            if test != "hash" and "rehash" not in test
        ]
        + [f"{coll}_rehash" for coll in ["chain", "linear", "double"]]
        + ["hash"]
    )
    df = pd.DataFrame(columns=["Name"] + cols)
    cols = (
        [
            f"{sz}_{test}"
            for sz in ["small", "med", "large"]
            for test in things_to_test.keys()
            if test != "hash" and "rehash" not in test
        ]
        + [f"{coll}_rehash" for coll in ["chain", "linear", "double"]]
        + ["hash"]
    )
    df = pd.DataFrame(columns=["Name"] + cols + ["marks"])

    if folders:
        for sub in folders:
            row = {col: -3 for col in df.columns if col != "Name"}
            row["Name"] = sub

            df = df._append(row, ignore_index=True)

    df.set_index("Name", inplace=True, drop=False)
    df.to_csv("results.csv", index=True)
    columns_to_convert = df.columns.difference(["Name"])  # Exclude 'Name'
    df[columns_to_convert] = df[columns_to_convert].astype(float)
    return df


def get_res(val):
    if val == 1:
        return 1
    return 0


def get_marks(row):
    m = 0

    # Musk Part
    m += (
        get_res(row["small_musk_distinct"]) * 0.5
        + get_res(row["med_musk_distinct"]) * 1
        + get_res(row["large_musk_distinct"]) * 1.5
    )
    m += (
        get_res(row["small_musk_search"]) * 0.5
        + get_res(row["med_musk_search"]) * 1
        + get_res(row["large_musk_search"]) * 1.5
    ) / 3
    # JGBLibs
    for coll_type in ["jobs", "gates", "bezos"]:
        for i, sz in enumerate(["small", "med", "large"]):
            for op in ["distinct", "search"]:
                m += get_res(row[f"{sz}_{coll_type}_{op}"]) * (i + 1) * 0.25

    # Rehashing
    for coll_type in ["chain", "linear", "double"]:
        m += get_res(row[f"{coll_type}_rehash"])
    # hash
    if get_res(row[f"hash"]) != 1:
        m = max(0, m - 1.6)
    return m


def get_submission_folders(directory=submission_directory):
    entries = os.listdir(directory)
    folders = [
        entry for entry in entries if os.path.isdir(os.path.join(directory, entry))
    ]
    return folders


class MemLimExceeded:
    def __init__():
        pass


def capture_return(func, params):
    try:
        ret = func(*params)
    except MemoryError as e:
        print("memory error in capture_return:",str(e))
        with open("retfile.pkl", "wb") as f:
            pass
        return
    except Exception as e:
        print("exception in capture_return:",e)
        with open("retfile.pkl", "wb") as f:
            pass
        return
    with open("retfile.pkl", "wb") as f:
        pickle.dump(ret, f)
    # print("Put")
    return


def check_function(func, params, timeout=5):
    st = ch.reload_libs()
    if st==-1:  # import error
        return -1
    proc = mp.Process(target=capture_return, args=(func, params))
    proc.start()
    proc.join(timeout=timeout)
    # print("Here")
    # print("Proc finished, output: ", return_queue.get())
    if proc.is_alive():
        proc.kill()
    # if return_queue.empty():
    #     print("Returning -1")
    #     return -1
    # print("Getting")
    # val = return_queue.get()
    try:
        with open("retfile.pkl", "rb") as f:
            val = pickle.load(f)
    except:
        return -1
    # print("Got")

    if isinstance(val, MemLimExceeded):
        # print("Returning -2")
        return -2
    # print("Returning", val)
    return val


def run_testcases(name, results_df, copy=False, write_to_df=True):
    result = {}
    if copy:
        destination_folder = os.getcwd()
        sourcedir_name = "submissions/" + name
        try:
            for file_name in all_files:
                source_file = os.path.join(sourcedir_name, file_name)
                shutil.copy(source_file, destination_folder)
        except:
            print("Couldn't copy files... skipping")
            return
        
    lib_objs = {}

    for test, (func, inp_file, out_file) in things_to_test.items():
        print(f"Running {test}...")

        if test == "hash":
            args = get_params("testcases/" + inp_file, test)
            # ans = check_function(func, args)
            start = time.time()
            ans = func(*args)
            print(f"Time taken: {time.time()-start:.4f}", )

            with open("model_output/" + out_file, "r") as f:
                model_ans = int(f.readline())

            if ans != -1 and ans != -2:
                try:
                    ans = 1 if ch.check_hash(ans, model_ans) else 0
                except:
                    ans = 0
            
            result[test] = ans
            if write_to_df:
                results_df.loc[name, test] = ans

        elif "rehash" in test:
            # if results_df.loc[name, test] != -3.0:
            #     print(f"{test} already ran. ans=", results_df[name][test])
            #     continue
            collision_type = test.split("_")[0]

            sz_inp_file = "testcases/" + inp_file
            sz_out_file = "model_output/" + out_file

            args = get_params(sz_inp_file, test)

            # Call the function and capture the result
            # ans = check_function(func, args)
            start = time.time()
            ans = func(*args)
            print(f"Time taken: {time.time()-start:.4f}")
            

            # Compare student output with model output
            if ans != -1 and ans != -2:
                try:
                    ans = ch.check_rehash(
                        f"student_{inp_file}", sz_out_file, collision_type
                    )
                except:
                    ans = 0
                    
            result[test] = ans
            if write_to_df:
                results_df.loc[name, test] = ans

        # Handling for library test cases (e.g., musk, jobs, gates, bezos)

        elif "musk" in test:
            if test == "musk_sort":
                for sz in ["small", "med", "large"]:
                    # if results_df.loc[name, sz + "_" + test] != -3:
                    #     print(f"{test} already ran. ans=", results_df[name][test])
                    #     continue
                    sz_inp_file = "testcases/" + inp_file + f"_{sz}.txt"
                    sz_out_file = "model_output/" + out_file + f"_{sz}.txt"

                    # Get the parameters for this specific test
                    args = get_params(sz_inp_file, test)

                    # Call the function and capture the result
                    start = time.time()
                    # ans = check_function(func, args)
                    ans = func(*args)
                    print(f"Time taken for {sz}: {time.time()-start:.4f}")

                    if ans == -1 or ans == -2:
                        lib_objs[sz_out_file] = None
                    else:
                        # save the lib_obj for later use
                        lib_objs[sz_out_file] = ans

            else:
                # musk_search
                for sz in ["small", "med", "large"]:
                    # if results_df.loc[name, sz + "_" + test] != -3:
                    #     print(f"{test} already ran. ans=", results_df[name][test])
                    #     continue
                    sz_inp_file = "testcases/" + inp_file + f"_{sz}.txt"
                    sz_out_file = "model_output/" + out_file + f"_{sz}.txt"

                    # Get the parameters for this specific test
                    if lib_objs[sz_out_file] is None:
                        ans = [0, 0, 0, 0]

                        if test == "musk_search":
                            # write to df
                            result["musk_"+sz] = ans
                            if write_to_df:
                                results_df.loc[name, f"{sz}_musk_sort"] = ans[3]
                                results_df.loc[name, f"{sz}_musk_distinct"] = (
                                    1 if (ans[0] == 1 and ans[1] == 1) else 0
                                )
                                results_df.loc[name, f"{sz}_musk_search"] = ans[2]


                    else:
                        args = get_params(sz_inp_file, test, lib_objs[sz_out_file])

                        # Call the function and capture the result
                        # ans = check_function(func, args)
                        start = time.time()
                        ans = func(*args)
                        print(f"Time taken: {time.time()-start:.4f}")

                        if test == "musk_search":
                            # Compare student output with model output
                            if ans != -1 and ans != -2:
                                try:
                                    ans = ch.check_musk(
                                        f"student_musk_{sz}.txt",
                                        sz_out_file,
                                    )
                                except:
                                    ans = [0,0,0,0]
                            else:
                                ans = [0,0,0,0]
                            # write to df
                            result["musk_"+sz] = ans
                            if write_to_df:
                                results_df.loc[name, f"{sz}_musk_sort"] = ans[3]
                                results_df.loc[name, f"{sz}_musk_distinct"] = (
                                    1 if (ans[0] == 1 and ans[1] == 1) else 0
                                )
                                results_df.loc[name, f"{sz}_musk_search"] = ans[2]
                    # Handle marks here...

        else:
            # jobs, gates, bezos
            if "insert" in test:
                for sz in ["small", "med", "large"]:
                    # if results_df.loc[name, sz + "_" + test] != -3:
                    #     print(f"{test} already ran. ans=", results_df[name][test])
                    #     continue
                    sz_inp_file = "testcases/" + inp_file + f"_{sz}.txt"
                    sz_out_file = "model_output/" + out_file + f"_{sz}.txt"

                    args = get_params(sz_inp_file, test)
                    # ans = check_function(func, args)
                    start = time.time()
                    ans = func(*args)
                    print(f"Time taken for {sz}: {time.time()-start:.4f}")

                    if ans == -1 or ans == -2:
                        ans = None
                    # save the lib_obj for later use
                    lib_objs[sz_out_file] = ans

            else:
                for sz in ["small", "med", "large"]:
                    # if results_df.loc[name, sz + "_" + test] != -3:
                    #     print(f"{test} already ran. ans=", results_df[name][test])
                    #     continue
                    sz_inp_file = "testcases/" + inp_file + f"_{sz}.txt"
                    sz_out_file = "model_output/" + out_file + f"_{sz}.txt"

                    if lib_objs[sz_out_file] is None:
                        ans = [0, 0, 0, 0]

                        if "search" in test:
                            # write to df
                            coll_type = test.split("_")[0]
                            result[coll_type+"_"+sz] = ans
                            if write_to_df:
                                
                                results_df.loc[name, f"{sz}_{coll_type}_insert"] = ans[3]
                                results_df.loc[name, f"{sz}_{coll_type}_distinct"] = (
                                    1 if (ans[0] == 1 and ans[1] == 1) else 0
                                )
                                results_df.loc[name, f"{sz}_{coll_type}_search"] = ans[2]

                    else:
                        args = get_params(sz_inp_file, test, lib_objs[sz_out_file])
                        # ans = check_function(func, args)
                        start = time.time()
                        ans = func(*args)
                        print(f"Time taken for {sz}: {time.time()-start:.4f}")

                        if "search" in test:
                            if ans != -1 and ans != -2:
                                checker_func = (
                                    ch.check_jobs
                                    if "jobs" in test
                                    else ch.check_gates_bezos
                                )
                                coll_type = test.split("_")[0]
                                try:
                                    ans = checker_func(
                                        f"student_{coll_type}_{sz}.txt",
                                        sz_out_file,
                                    )
                                except:
                                    ans = [0,0,0,0]
                            else:
                                ans = [0,0,0,0]
                                coll_type = test.split("_")[0]
                            
                            # print(f"\n\nans for {sz} {coll_type}: ", ans, "\n\n")
                            result[coll_type+"_"+sz] = ans

                            # write to df
                            if write_to_df:
                                results_df.loc[name, f"{sz}_{coll_type}_insert"] = ans[3]
                                results_df.loc[name, f"{sz}_{coll_type}_distinct"] = (
                                    1 if (ans[0] == 1 and ans[1] == 1) else 0
                                )
                                results_df.loc[name, f"{sz}_{coll_type}_search"] = ans[2]

                # Handle marks here...
        # print("Result: ", repr(ans))
        # results_df.loc[name, test] = ans
    print(result)


def run_all(load_existing=True):
    submissions = get_submission_folders()
    if not load_existing or not os.path.exists("./results.csv"):
        print("Can't find results.csv. Exiting...")
        return
        # results_df = create_df(submissions)
    else:
        results_df = pd.read_csv("./results.csv", index_col="Name")
        # results_df.reset_index(inplace=True, drop=False)
        # results_df["Name"] = results_df["Name"].str.strip()
        # print(results_df.head())
        # print(results_df.loc['Singh Yashwardhan 26203 ee3230385'])
        # print(type(submissions[0]))
        # return

    for i, nm in enumerate(submissions):
        print(f"{i}/{len(submissions)}. Running for", nm)
        # if results_df.loc[nm]['marks']!=-3:
        #     print(f"{nm} already ran. marks=", results_df.loc[nm]['marks'])
        #     continue
        run_testcases(nm, results_df, copy=True)
        new_marks = get_marks(results_df.loc[nm])
        old_marks = results_df.loc[nm, "marks"]
        if new_marks != old_marks:
            print(f"Old marks: {old_marks}, New marks: {new_marks}")
        results_df.loc[nm, "marks"] = get_marks(results_df.loc[nm])
        print(f"Total marks: ", results_df.loc[nm, "marks"])
        results_df.to_csv("results.csv", index=True)

    print(results_df)


def run_single_submission(name):
    # ensure files already copied
    # disable copy in run_testcases
    
    # create temp df
    folders = get_submission_folders()
    cols = (
        [
            f"{sz}_{test}"
            for sz in ["small", "med", "large"]
            for test in things_to_test.keys()
            if test != "hash" and "rehash" not in test
        ]
        + [f"{coll}_rehash" for coll in ["chain", "linear", "double"]]
        + ["hash"]
    )
    df = pd.DataFrame(columns=["Name"] + cols + ["marks"])

    if folders:
        for sub in folders:
            row = {col: -3 for col in df.columns if col != "Name"}
            row["Name"] = sub

            df = df._append(row, ignore_index=True)

    df.set_index("Name", inplace=True, drop=False)
    columns_to_convert = df.columns.difference(["Name"])  # Exclude 'Name'
    df[columns_to_convert] = df[columns_to_convert].astype(float)
    # print(df.head())
    run_testcases(name, df)
    print("Marks:" , get_marks(df.loc[name]))

if __name__ == "__main__":
    # run_all(load_existing=True)
    run_testcases(None, None, copy=False, write_to_df=False)

