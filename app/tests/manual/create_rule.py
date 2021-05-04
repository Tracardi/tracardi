import json
from pprint import pprint

from app.uql.query.dispatcher import Host, Dispatcher
from app.uql.query.parser import Parser
from app.uql.query.grammar.grammars import read
from app.uql.query.transformers.create_rule_transformer import CreateRuleTransformer

p = Parser(read('uql_create_rule.lark'), start='create_rule')
t = p.parse(
    """
    
    # CREATE RULE 
    #     WITH TAGS ["długa","bśćółęńć-"] 
    #     "if identify the event properties to profile" 
    #     # DESCRIBE "Copies user data from events target properties to profile"
    #     IN SCOPE "kuptoo" 
    #     WHEN eventType="identify"
    #     THEN 
    #         profile.AddStringToList(a,"1"),profile.SetString(a,"1")
    
    # CREATE RULE 
    #     # WITH TAGS ["analytics"] 
    #     "Number of views" 
    #     DESCRIBE "Increment view property in profile with every view event"
    #     IN SCOPE "kuptoo" 
    #     WHEN event:type="click"
    #     THEN SetProfilePropertyFromEvent("nbOfViews","nbOfViews")
        
     # CREATE RULE 
     #    WITH TAGS ["analytics"] 
     #    "Number of views" 
     #    DESCRIBE "Increment view property in profile with every view event"
     #    IN SCOPE "kuptoo" 
     #    WHEN event:type="click"
     #    THEN EventToProfileProperty("nbOfViews","nbOfViews1")
        
     # CREATE RULE 
     #    # WITH TAGS ["analytics"] 
     #    "Number of views new" 
     #    DESCRIBE "NEW Increment view property in profile with every view event"
     #    IN SCOPE "kuptoo" 
     #    WHEN event:type="view"
     #    THEN IncrementProfileProperty("nbOfViews1")
        
    CREATE RULE 
        "name" 
        DESCRIBE "description"
        IN SCOPE "scope" 
        WHEN event:type="identify" AND event:scope = "my-site"  
        THEN profile.CopyAll()
    
    # CREATE RULE "Example: add to list" 
    # DESCRIBE "Uses AddToProfilePropertyList" 
    # IN SCOPE "site-1" WHEN event:type="add" 
    # THEN AddToProfileProperty("properties.listOfA","b")
    
    # CREATE RULE "Example: add to list" 
    # DESCRIBE "Uses AddToProfilePropertyList" 
    # IN SCOPE "site-1" WHEN event:type="add" 
    # THEN unomi:CopyProperty(event.x,prop.v)
    
    # CREATE RULE "Example: add to list" 
    # DESCRIBE "Uses AddToProfilePropertyList" 
    # IN SCOPE "site-1" WHEN event:type="add" and event:type=Date("now")
    # THEN unomi:SetProperty(event.x,Date("now")), unomi:SetProperty(event.x,Date("now"))

    """
)

query = CreateRuleTransformer().transform(t)
pprint(query)

# host = Host('localhost', port=8181, protocol='http').credentials('karaf','karaf')
# dispatcher = Dispatcher(host)
# response, _ = dispatcher.fetch(query)
# if response.status_code == 200:
#     pprint(json.loads(response.content))
# else:
#     print(response.content)
# print(response.status_code)
