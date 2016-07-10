# ETL
## Instructions

1) Extract
To extract data (retrieve all entities and dump to \n delimited json):
```python
# iPython shell in to the desired server you wish to extract from
import json

from etl import extract


for model in [Building, Space, Organization, User, Media]:
    model_name = model.__class__.__name__
    all_ents = []
    for ents in extract.get_entities(model):
        all_ents.extend(ents)
    with open("{}.json".format(model_name), "w") as f:
        f.write("\n".join(map(json.dumps, all_ents)))
```


2) Transform
```
pyton run.py
```
