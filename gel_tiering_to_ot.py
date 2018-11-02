# Take a TSV file exported from LabKey and convert it to JSON following the OpenTargets "genetic association" schema
# https://github.com/opentargets/json_schema

import argparse
import csv
import json
import logging
import sys

SOURCE_ID = "eva" # TODO change when using own source

def main():
    parser = argparse.ArgumentParser(description='Generate Open Targets JSON from an input TSV file')

    parser.add_argument('--input', help="TSV input file", required=True, action='store')

    parser.add_argument('--schema', help='Location of file containing Open Targets genetic_association JSON schema',
                        required=True)

    parser.add_argument("--log-level", help="Set the log level", action='store', default='WARNING')

    args = parser.parse_args()

    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.getLevelName(args.log_level))

    logger.info("Reading TSV from " + args.input)

    required_columns = ["gene", "EFO", "variant"]

    count = 0

    with open(args.input) as tsv_file:

        reader = csv.DictReader(tsv_file, delimiter='\t')

        for column in required_columns:
            if column not in reader.fieldnames:
                logger.error("Required column %s does not exist in %s (columns in file are %s)"
                             % (column, args.input, reader.fieldnames))
                sys.exit(1)

        for row in reader:
            # TODO actually read score
            my_instance = build_evidence_strings_object(row['gene'], row['EFO'], row['variant'], 1)
            print(json.dumps(my_instance))
            count += 1

    logger.info("Processed %d objects" % count)


# TODO - other fields

def build_evidence_strings_object(gene, efo, variant, score):
    """
    Build a Python object containing the correct structure to match the Open Targets genetics.json schema
    :return:
    """

    logger = logging.getLogger(__name__)
    logger.debug("Building container object")

    obj = {
        "sourceID": SOURCE_ID,
        "access_level": "public",
        "validated_against_schema_version": "1.2.8",
        "unique_association_fields": {
            "gene": gene,
            "phenotype": efo,
            "variant": variant #TODO mode to make unique?
        },
        "target": {
            "id": "http://identifiers.org/ensembl/" + gene,
            "target_type": "http://identifiers.org/cttv.target/gene_variant",
            "activity": "http://identifiers.org/cttv.activity/loss_of_function"
        },
        "disease": {
            "id": efo
        },
        "type": "genetic_association",
        "variant": {
            "id": "http://identifiers.org/dbsnp/" + variant,
            "type": "snp single"
        },
        "evidence": {
            "gene2variant": {
                "is_associated": True,
                "date_asserted": "2018-10-22T23:00:00",
                "provenance_type": {
                    "database": {
                        "id": "abc",
                        "version": "1"
                    }
                },
                "evidence_codes": [
                    "http://identifiers.org/eco/cttv_mapping_pipeline"
                ],
                "functional_consequence": "http://purl.obolibrary.org/obo/SO_0001589"
            },
            "variant2disease": {
                "unique_experiment_reference": "STUDYID_1234",
                "is_associated": True,
                "date_asserted": "2018-10-22T23:00:00",
                "resource_score": {
                    "type": "probability",
                    "value": score
                },
                "provenance_type": {
                    "database": {
                        "id": "abc",
                        "version": "1"
                    }
                },
                "evidence_codes": [
                    "http://identifiers.org/eco/GWAS"
                ]
            }
        }
    }

    return obj


if __name__ == '__main__':
    sys.exit(main())
