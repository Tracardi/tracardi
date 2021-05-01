import json

from app.uql.query.parser import Parser
from app.uql.query.grammar.grammars import read
from pprint import pprint
from app.uql.query.transformers.create_segment_transformer import CreateSegmentTransformer

p = Parser(read('uql_create_segment.lark'), start='create_segment')
t = p.parse(
    """
    # CREATE SEGMENT 
    # WITH TAGS ["długa","bśćółęńć-"] 
    # "At least 1 visit"
    # DESCRIBE "Copies user data from events target properties to profile"
    # IN SCOPE \"dupa\" 
    # WHEN profile:properties.nbOfVisits>=1
    
    # CREATE SEGMENT "Frequent customers" 
    # DESCRIBE "Frequent customers who made purchase at least 3 time a month." 
    # IN SCOPE "site-1" 
    # WHEN event.type="order"
    
    CREATE SEGMENT "my segment" 
    DESCRIBE "desc" 
    IN SCOPE "site-1" 
    WHEN properties.nbOfVisits>1


    """
)

print(t)
r = CreateSegmentTransformer().transform(t)
pprint(r)
print(json.dumps(r[3]))

