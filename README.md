This library harvests trait data from the [Encyclopedia of Live](https://eol.org). It can handle both the [EOL All traits CSV file](https://opendata.eol.org/dataset/all-trait-data-large) and the EOL API.  We recommend going with the API, since it seems more complete and is up-to-date.

The harvester returns Triple objects that hold triple statements (subject, prediate, object) and additionally references to source URLs or citations.

# Install

```shell
virtualenv venv
source venv/bin/activate
pip install .
```

# Usage
## Harvesting the EOL API for Trait data
Be aware that to harvest the EOL API, you need an access token. To receive this token, please follow the [instructions given by EOL](https://github.com/EOL/publishing/blob/master/doc/api.md).

A downside of this approach is that you have some delay (sometime multiple seconds with large response datasets) with each call to the API since the EOL server needs time to process, iterate and return the data.

```python
from eol import EncyclopediaOfLifeProcessing
from eol.handlers import EolTraitApiHandler
from eol.normalization import EolTraitApiNormalizer

# Setup
eol_api_token = "v3ryLongE0L4P1T0kenStr1ng"
eol_api_credentials = f"JWT {eol_api_token}"  # This format is required from the API

handler = EolTraitApiHandler(api_credentials=eol_api_credentials)
normalizer = EolTraitApiNormalizer()

eol = EncyclopediaOfLifeProcessing(handler, normalizer)

# Let's get the traits for the Cliff Chipmunk (https://eol.org/pages/311544)
# You can take the EOL page ID directly from the URL.
species_traits = eol.get_trait_data_for_eol_page_id("311544")
print(len(species_traits))
# 80

print(species_traits[0])
# Triple(
#   subject='311544',
#   predicate='http://eol.org/schema/terms/AETinRange',
#   object=407.56,
#   eol_record_id='R261-PK213792796',
#   unit='http://eol.org/schema/terms/millimeterspermonth',
#   source_url='http://esapubs.org/archive/ecol/E090/184/',
#   citation_text="Kate E. Jones, Jon Bielby, Marcel Cardillo, Susanne A. Fritz, Justin O'Dell, C. David L. Orme, Kamran Safi, Wes Sechrest, Elizabeth H. Boakes, Chris Carbone, Christina Connolly, Michael J. Cutts, Janine K. Foster, Richard Grenyer, Michael Habib, Christopher A. Plaster, Samantha A. Price, Elizabeth A. Rigby, Janna Rist, Amber Teacher, Olaf R. P. Bininda-Emonds, John L. Gittleman, Georgina M. Mace, and Andy Purvis. 2009. PanTHERIA: a species-level database of life history, ecology, and geography of extant and recently extinct mammals. Ecology 90:2648."
#)
```
You see that numerical values in the `object` of the created `Triple` are formatted automatically into `float` numbers. Strings (e.g. URIs) will be returned as strings (`str`).

## Harvesting the EOL All trait CSV file
A major advantage that comes with downloading the [All EOL Traits CSV file](https://opendata.eol.org/dataset/all-trait-data-large) and process it with the `eol-trait-harvester` is that, although the file is  huge (6+ GB), the data retrieval is fast. The `eol-trait-harverster` is optimized to not digest the whole file at once, but iteratively and hence should not kill a modern laptop.

The downside of using the CSV file is that not all traits are in there, at least within the project group, we had this impression. Also you have a long booting phase when the CSV file is digested by the harvester. But this is done only once at the beginning.

```python
from eol import EncyclopediaOfLifeProcessing
from eol.handlers import EolTraitCsvHandler
from eol.normalization import EolTraitCsvNormalizer

# Setup
eol_trait_csv_file_path = "/path/to/eol/all-traits.csv"
handler = EolTraitCsvHandler(eol_trait_csv_file_path)
normalizer = EolTraitCsvNormalizer()

eol = EncyclopediaOfLifeProcessing(handler, normalizer)

# The handling is just the same as in the example above.
species_traits = eol.get_trait_data_for_eol_page_id("311544")
print(len(species_traits))
# 80

print(species_traits[0])
# Triple(
#   subject='311544',
#   predicate='http://eol.org/schema/terms/AETinRange',
#   object=407.56,
#   eol_record_id='R261-PK213792796',
#   unit='http://eol.org/schema/terms/millimeterspermonth',
#   source_url='http://esapubs.org/archive/ecol/E090/184/',
#   citation_text="Kate E. Jones, Jon Bielby, Marcel Cardillo, Susanne A. Fritz, Justin O'Dell, C. David L. Orme, Kamran Safi, Wes Sechrest, Elizabeth H. Boakes, Chris Carbone, Christina Connolly, Michael J. Cutts, Janine K. Foster, Richard Grenyer, Michael Habib, Christopher A. Plaster, Samantha A. Price, Elizabeth A. Rigby, Janna Rist, Amber Teacher, Olaf R. P. Bininda-Emonds, John L. Gittleman, Georgina M. Mace, and Andy Purvis. 2009. PanTHERIA: a species-level database of life history, ecology, and geography of extant and recently extinct mammals. Ecology 90:2648."
#)
```

You see in the code, that we imported a different `Normalizer` than we did with the API example. You have to provide the correct `Normalizer` for the respective `Handler`. But you should see it from the name which `Normalizer` belongs to which `Handler`.

## Mapping other biodiversity provider IDs to EOL page IDs
EOL provides a [CSV file mapping EOL page IDs to other provider taxon IDs](https://opendata.eol.org/dataset/identifier-map). You can download this file and provide it to the `eol-trait-harvester`. This allows the harvester to convert provider IDs to EOL page IDs and _vice versa_.

```python
from eol import EncyclopediaOfLifeProcessing
from eol.handlers import EolTraitCsvHandler
from eol.normalization import EolTraitCsvNormalizer
from eol import DataProvider

# Setup
eol_trait_csv_file_path = "/path/to/eol/all-traits.csv"
eol_provider_mapping_csv_file_path = "/path/to/eol/provider-mapping.csv"

handler = EolTraitCsvHandler(eol_trait_csv_file_path)
normalizer = EolTraitCsvNormalizer()

eol = EncyclopediaOfLifeProcessing(
    handler, normalizer, eol_provider_mapping_csv_file_path
)

# If necessary, you can restrict or extend the data providers considered
# in the identifier conversion. Per default only GBIF is set!
# Implemented data providers are (in alphabetical order):
#   * Frost's 2018 Amphibian Species of the World
#   * GBIF
#   * Integrated Taxonomic Information System (ITIS)
#   * IUCN
#   * National Center for Biotechnology Information (NCBI)
#   * World Register of Marine Species (WoRMS)
#
# Restricting the data providers before the first call to the identifier converter,
# makes the first call faster, since less data has to be processed. However,
# if a data provider is not given as relevant data provider, no ID for this
# data provider will be returned!
#
# To add only WoRMS (in addition to GBIF), you can write:
eol.identifier_converter.relevant_data_providers.append(DataProvider.WoRMS)

# Convert to GBIF Taxon ID
gbif_taxon_id = eol.identifier_converter.from_eol_page_id(
            "21828356", DataProvider.Gbif)
print(gbif_taxon_id)
# 1057764

# Convert from GBIF to EOL page ID
eol_page_id = eol.identifier_converter.to_eol_page_id(
    "1057764", DataProvider.Gbif)
print(eol_page_id)
# 21828356

# You can also provide a list of data provider IDs. This speeds up the conversion of many IDs massively.
eol_page_id = eol.identifier_converter.to_eol_page_id(
    ["1057764"], DataProvider.Gbif)
print(eol_page_id)
# [21828356]

# When converting from EOL page ID and no data provider is given,
# a list of corresponding IDs is returned.
corresponding_ids = eol.identifier_converter.from_eol_page_id("46552319")
print(corresponding_ids)
# ['2269258', '117870']
```

# Tests
For running tests, you need to install the test dependencies while in the virtual environment:

```shell
pip install -e .[dev]
```

For running test, you need to have a `.env` file in the `tests` folder. The content should be like this:

```shell
EOL_API_TOKEN=abcdefghijklmnopqrstuvwxyz1234567890
```

where you substitute the part after the equal sign by your EOL API Token.

Subsequently, you can run:

```shell
pytest
```
