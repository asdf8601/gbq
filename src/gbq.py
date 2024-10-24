# ignore warnings from sqlalchemy and pandas
import warnings

warnings.filterwarnings("ignore")

import pandas as pd
import pandas_gbq
import os


def printer(*args, quiet=False, **kwargs):
    if not quiet:
        print(*args, **kwargs)


def find_fmt_keys(s: str) -> list[str] | None:
    import re
    pattern = r"{[^}]+}"
    matches = re.findall(pattern, s)
    return matches


def get_query(args):
    query_in = args.query
    try:
        with open(query_in, "r") as f:
            out = f.read()
    except FileNotFoundError:
        out = query_in

    # format {{{
    fmt_keys = find_fmt_keys(out)
    if fmt_keys:
        fmt_values = {}
        for key in fmt_keys:
            k = key[1:-1]
            fmt_values[k] = os.environ[k]
        out = out.format(**fmt_values)
    # }}}
    return out


def get_args():
    import argparse

    parser = argparse.ArgumentParser(description="Druid Query")
    parser.add_argument("query", help="Druid query or filename")
    parser.add_argument(
        "-e",
        "--eval-df",
        help="Evaluate 'df' using string or filename",
        default="",
    )
    parser.add_argument(
        "-n",
        "--no-cache",
        help="Do not use cache",
        action="store_true",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        help="Do not print the output except the code you use in eval-df",
        action="store_true",
    )
    parser.add_argument(
        "--pdb",
        help="Run pdb on start",
        action="store_true",
    )
    return parser.parse_args()


def get_eval_df(args):
    eval_df_in = args.eval_df
    try:
        with open(eval_df_in, "r") as f:
            out = f.read()
    except FileNotFoundError:
        out = eval_df_in
    return out


def get_temp_file(query):
    from hashlib import sha1
    from pathlib import Path

    qhash = sha1(query.encode()).hexdigest()
    temp_file = Path(f"/tmp/druidq/{qhash}.parquet")
    if not temp_file.parent.exists():
        temp_file.parent.mkdir(parents=True, exist_ok=True)

    return temp_file


def execute(query, no_cache=False, quiet=False):

    # cache {{
    temp_file = get_temp_file(query)
    if temp_file.exists():
        printer(f"Loading cache: {temp_file}", quiet=quiet)
        return pd.read_parquet(temp_file)
    # }}

    df = pandas_gbq.read_gbq(query)

    # cache {{
    printer(f"Saving cache: {temp_file}", quiet=quiet)
    try:
        df.to_parquet(temp_file)
    except Exception as e:
        printer(f"Error saving cache: {e}", quiet=quiet)
    # }}

    return df


def app():
    args = get_args()

    query = get_query(args)
    quiet = args.quiet

    if args.pdb:
        breakpoint()

    printer(f"In[query]:\n{query}", quiet=quiet)

    df = execute(query=query, no_cache=args.no_cache, quiet=quiet)
    printer(f"\nOut[df]:\n{df}", quiet=quiet)

    if args.eval_df:
        eval_df = get_eval_df(args)
        printer(f"\nIn[eval]:\n{eval_df}", quiet=quiet)

        printer("Out[eval]:", quiet=quiet)
        exec(eval_df, globals(), locals())


if __name__ == "__main__":
    app()
