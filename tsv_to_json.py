# Take a TSV file and convert it to JSON following the OpenTargets "genetic association" schema
# https://github.com/opentargets/json_schema

import csv
import logging
import sys

import python_jsonschema_objects as pjs


# TODO logging
# TODO command-line args

SCHEMA = "genetics.json"
FILE = "test.tsv"
LOG_LEVEL = "INFO"

def main():

    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.getLevelName(LOG_LEVEL))

    logger.info("Reading JSON schema from " + SCHEMA)

    builder = pjs.ObjectBuilder(SCHEMA)  # TODO better way of referring to this

    logger.debug("Building classes from schema")

    classes = builder.build_classes()  # Takes a few seconds

    logger.info("Reading TSV from " + FILE)

    required_columns = ["gene", "EFO", "variant"]

    try:
        with open(FILE) as tsv_file:

            reader = csv.DictReader(tsv_file, delimiter='\t')

            for column in required_columns:
                if column not in reader.fieldnames:
                    logger.error("Required column %s does not exist in %s (columns in file are %s)" % (column, FILE, reader.fieldnames))
                    sys.exit(1)

            count = 0
            for row in reader:
                my_instance = build_evidence_strings_object(classes, row['gene'], row['EFO'], row['variant'])
                print(my_instance.serialize())
                count += 1

    except IOError as error:
        logger.error("Problem reading " + FILE, error)

    logger.info("Processed %d objects" % count)

def build_evidence_strings_object(classes, gene, efo, variant): # classes object, gene, EFO, rsID
    """
    Build a Python object containing the correct structure to match the Open Targets genetics.json schema
    :return:
    """

    logger = logging.getLogger(__name__)

    logger.debug("Building wrapper class")
    GBES_Class = classes['Genetics-basedEvidenceStrings']  # Need to refer to it this way due to - sign

    # Create instance of main class, assign "easy" properties directly
    # TODO what source ID to use?
    my_instance = GBES_Class(access_level="public",
                             validated_against_schema_version="1.2.8",
                             sourceID='testing123',
                             type='genetic_association')

    # More complex parts are Disease, Target, Variant, Evidence and UniqueAssociationFields
    # Each of these as additional, non-required properties; only do required for now

    # Disease
    logger.debug("Adding Disease")
    my_instance.disease = classes.Disease(id=efo)

    # Target
    logger.debug("Adding Target")
    ensembl_gene = "http://identifiers.org/ensembl/" + gene
    my_instance.target = classes.Target(id=ensembl_gene,
                                        activity='http://identifiers.org/cttv.activity/loss_of_function',
                                        target_type='http://identifiers.org/cttv.target/gene_variant')

    # Variant - have to get the class a different way, see https://github.com/cwacek/python-jsonschema-objects/issues/32
    logger.debug("Adding Variant")
    Variant = getattr(classes, "Variant<anonymous>")
    rs_id = "http://identifiers.org/dbsnp/" + variant
    my_instance.variant = Variant(id=rs_id,
                                  type='snp single')

    # The unique_association_fields object can have arbitrary keys and values, as long as they're strings
    logger.debug("Adding UniqueAssociationFields")
    my_instance.unique_association_fields = classes.UniqueAssociationFields(field1="abc", field2="def")

    # Evidence is made up of gene2variant and variant2disease
    # Evidence
    #   Gene2Variant
    #       Provenance_type
    #           Database
    #       Simple fields
    #
    #   Variant2disease
    #       Provenance_type
    #           Database
    #       Resource_score
    #       Simple fields

    # Gene2variant first

    db = classes.Database(id="abc", version="1")  # TODO set for correct database name
    my_prov = classes.ProvenanceType(database=db)

    logger.debug("Adding Gene2Variant")
    Gene2variant = getattr(classes, "Gene2variant<anonymous>")
    # TODO date, consequence, evidence codes
    # TODO is date important?
    my_g2v = Gene2variant(date_asserted="2018-10-22T23:00:00",
                          functional_consequence="http://purl.obolibrary.org/obo/SO_0001589",
                          is_associated=True,
                          provenance_type=my_prov,
                          evidence_codes=["http://identifiers.org/eco/cttv_mapping_pipeline"])


    # Variant2disease
    logger.debug("Adding Variant2Disease")
    Variant2disease = getattr(classes, "Variant2disease<anonymous>")
    # TODO date, separate provenance, evidence, reference
    my_v2d = Variant2disease(is_associated=True,
                             date_asserted="2018-10-22T23:00:00",
                             evidence_codes=["http://identifiers.org/eco/GWAS"],
                             provenance_type=my_prov,
                             unique_experiment_reference="STUDYID_1234")

    # TODO figure out how scoring works
    Rank = getattr(classes, "Rank<anonymous>")
    my_rank = Rank(sample_size=1, position=1, type="rank")
    my_resource_score = my_rank
    my_v2d.resource_score = my_resource_score

    # Finally create the Evidence object and add it to the main instance
    logger.debug("Adding Evidence")
    Evidence = getattr(classes, "Evidence<anonymous>")
    my_evidence = Evidence(gene2variant=my_g2v, variant2disease=my_v2d)

    my_instance.evidence = my_evidence

    return my_instance


if __name__ == '__main__':
    sys.exit(main())
