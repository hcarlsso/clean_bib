import datetime
import sys
import os
from pathlib import Path
import re

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.customization import *


import yaml


input_b = "library.bib"
output_b = "library_clean.bib"

with open("ieee_abrv.yml", 'r') as stream:
    try:
        mapping_abbr = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

with open("conf_title_abbrv.yml", 'r') as stream:
    try:
        mapping_conf = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

with open("data.yml", 'r') as stream:
    try:
        refs_used = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

def check_periodical(record):

    required_types = [
        'author',
        'title',
        'journal',
        'volume',
        'number',
        'pages',
        'month',
        'year'
    ]

    if record['ENTRYTYPE'] == 'article':
        if all([t in record for t in required_types]):
            pass
        else:
            print('BROKEN PERIODICAL')
            print(record)
            print(set(required_types) - set(record.keys()))

def check_conf(record):

    required_types = [
        'author',
        'title',
        'booktitle',
        'pages',
        'year'
    ]

    if record['ENTRYTYPE'] == 'inproceedings':
        if all([t in record for t in required_types]):
            pass
        else:
            print('BROKEN CONF')
            print(record)
            print(set(required_types) - set(record.keys()))

def check_book(record):

    required_types = [
        'author',
        'title',
        'publisher',
        'address', # The city and country
        'year'
    ]

    if record['ENTRYTYPE'] == 'book':
        if all([t in record for t in required_types]):
            pass
        else:
            print('BROKEN BOOK')
            print(record)
            print(set(required_types) - set(record.keys()))


def abbrev_mapping(record, kw, mapping):

    if kw in record:

        print(record[kw])
        # record["journal"] = re.sub(
        #     pattern,
        #     lambda m: mapping_abbr.get(m.group(0)),
        #     record["journal"],
        #     # flags=re.IGNORECASE
        # )

        parts = record[kw].split()
        parts_conv = []
        for p in parts:
            if p in mapping:
                parts_conv.append(mapping[p])
            elif p[0:-1] in mapping: # Account for commma
                parts_conv.append(mapping[p[0:-1]])
            elif 'on' == p or 'and' == p:
                pass
            else:
                parts_conv.append(p)

        record[kw] = ' '.join(parts_conv)
        print(record[kw])
    return record


# Let's define a function to customize our entries.
# It takes a record and return this record.
def customizations(record):
    """Use some functions delivered by the library
    :param record: a record
    :returns: -- customized record
    """
    # record = type(record)
    # record = page_double_hyphen(record)
    # record = convert_to_unicode(record)
    ## delete the following keys.
    if record['ID'] not in refs_used:
        return {}

    unwanted = [
        "doi",
        "url",
        "abstract",
        "file",
        "gobbledegook",
        "isbn",
        "link",
        "keyword",
        "mendeley-tags",
        "annote",
        "pmid",
        "chapter",
        "institution",
        "issn",
        "eprint"
    ]
    for val in unwanted:
        record.pop(val, None)


    record = abbrev_mapping(record, "journal", mapping_abbr)
    if record['ENTRYTYPE'] == 'inproceedings':
        record = abbrev_mapping(record, "booktitle", mapping_conf)
    # record = ieee_abrv_mapping(record)



    check_periodical(record)
    check_conf(record)
    check_book(record)

    return record


def main(input_b, output_b):

    bib_database = None
    with open(input_b) as bibtex_file:
        parser = BibTexParser()
        parser.customization = customizations
        parser.ignore_nonstandard_types = False
        bib_database = bibtexparser.load(bibtex_file, parser=parser)

    # Filter out empty
    bib_database.entries = list(filter(None, bib_database.entries))
    # print(bib_database.entries)

    if bib_database :
        now = datetime.datetime.now()
        success = "{0} Loaded {1} found {2} entries".format(
            now, input_b, len(bib_database.entries)
        )
        print(success)
    else:
        now = datetime.datetime.now()
        errs = "{0} Failed to read {1}".format(now, input_b)
        print(errs)
        sys.exit(errs)

    bibtex_str = None
    if bib_database:
        writer = BibTexWriter()
        writer.order_entries_by = ('author', 'year', 'type')
        bibtex_str = bibtexparser.dumps(bib_database, writer)
        #print(str(bibtex_str))
        with open(output_b, "w") as text_file:
            print(bibtex_str, file=text_file)

    if bibtex_str:
        now = datetime.datetime.now()
        success = "{0} Wrote to {1} with len {2}".format(
            now, output_b, len(bibtex_str)
        )
        print(success)
    else:
        now = datetime.datetime.now()
        errs = "{0} Failed to write {1}".format(now, output_b)
        print(errs)
        sys.exit(errs)




if __name__ == '__main__':
    now = datetime.datetime.now()


    input_b = os.path.abspath(sys.argv[1])
    p = Path(input_b)
    filename_output = p.stem + '_clean' + p.suffix
    output_b = os.path.join(str(p.parents[0]), filename_output)



    print("{0} Cleaning duff bib records from {1} into {2}".format(
        now, input_b, output_b)
    )
    main(input_b,output_b)
