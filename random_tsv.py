import random
import sys
import logging
from ontoma import OnToma
import argparse
import pandas as pd

# Generate a random sample from a TSV file, optionally mapping phenotypes to EFO

parser = argparse.ArgumentParser(description='Build random data from actual values in a TSV file')

parser.add_argument('-input', help="TSV input file", required=True, action='store')

parser.add_argument('-samples', type=int, help='Number of samples to output', required=True)

parser.add_argument('-columns', help="Columns to include, space separated. If not specifed, include all.", nargs='+')

parser.add_argument('-map_phenotypes',
                    help="Map phenotypes to EFO terms using OnToma. Value of this argument is the name of the phenotype column.",
                    action='store')

args = parser.parse_args()

table = pd.read_table(args.input, dtype='unicode')

if args.columns:
    columns = args.columns
else:
    columns = table.columns

# Cache columns as lists to avoid lots of expensive operations
columns_cache = {}

for column in columns:
    columns_cache[column] = table[column].unique().tolist()

if args.map_phenotypes:
    if not args.map_phenotypes in table.columns:
        print("Can't find %s column in %s" % (args.map_phenotypes, args.input))
        sys.exit(1)

    otmap = OnToma()
    ontoma_logger = logging.getLogger("ontoma.downloaders")
    ontoma_logger.setLevel(logging.WARNING)
    ontoma_logger2 = logging.getLogger("ontoma.interface")
    ontoma_logger2.setLevel(logging.WARNING)

for i in range(0, int(args.samples)):

    output_str = ""

    for column in columns:
        entries = columns_cache[column]
        choice = random.choice(entries)
        output_str += choice + "\t"
    if args.map_phenotypes and column == args.map_phenotypes:
        efo = otmap.find_term(choice)
        if efo:
            output_str += efo

    print(output_str)
