# Take a TSV file and convert it to JSON following the OpenTargets "genetic association" schema
# https://github.com/opentargets/json_schema

import python_jsonschema_objects as pjs
import pandas as pd

# TODO logging

# Read TSV


# Pull out data of interest


# Build JSON

builder = pjs.ObjectBuilder("genetics.json")  # TODO better way of referring to this

classes = builder.build_classes()  # Takes a few seconds

GBES_Class = classes['Genetics-basedEvidenceStrings']  # Need to refer to it this way due to - sign

# Create instance of main class, assign "easy" properties directly
my_instance = GBES_Class(access_level="public",
                         validated_against_schema_version="1.2.8",
                         sourceID='testing123',
                         type='genetic_association')

# More complex parts are Disease, Target, Variant, Evidence and UniqueAssociationFields
# Each of these as additional, non-required properties; only do required for now

# Disease
my_instance.disease = classes.Disease(id="http://www.ebi.ac.uk/efo/EFO_1234567")  # TODO replace with proper EFO term

# Target
my_instance.target = classes.Target(id='http://identifiers.org/ensembl/ENSG123456',
                                    activity='http://identifiers.org/cttv.activity/loss_of_function',
                                    target_type='http://identifiers.org/cttv.target/gene_variant')

# Variant - have to get the class a different way, see https://github.com/cwacek/python-jsonschema-objects/issues/32
Variant = getattr(classes, "Variant<anonymous>")
my_instance.variant = Variant(id='http://identifiers.org/dbsnp/rs1234', type='snp single')  # TODO replace with rsID

# The unique_association_fields object can have arbitrary keys and values, as long as they're strings
my_instance.unique_association_fields = classes.UniqueAssociationFields(field1="abc", field2="def")

# Evidence is made up of gene2variant and variant2disease
# Evidence
#   Gene2Variant
#       Provenance_type
#           Database
#       Simple fields
#
#   Variant2disease
#       xx
#       Simple fields

# Gene2variant first

db = classes.Database(id="abc", version="1")  # TODO set for correct database name
my_prov = classes.ProvenanceType(database=db)

Gene2variant = getattr(classes, "Gene2variant<anonymous>")
# TODO date, consequence, evidence codes
my_g2v = Gene2variant(date_asserted="2018-10-22T23:00:00",
                      functional_consequence="http://purl.obolibrary.org/obo/SO_0001589",
                      is_associated=True,
                      provenance_type=my_prov,
                      evidence_codes=["http://identifiers.org/eco/cttv_mapping_pipeline"])


# Variant2disease
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

Evidence = getattr(classes, "Evidence<anonymous>")
my_evidence = Evidence(gene2variant=my_g2v, variant2disease=my_v2d)

my_instance.evidence = my_evidence

# Then output JSON once all filled in
print(my_instance.serialize())
