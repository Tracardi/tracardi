uri_mapper = {
    ('select', 'event'):    ('cxs/events/search', 'POST', 200),
    ('select', 'profile'):  ('cxs/profiles/search/', 'POST', 200),
    ('select', 'rule'):     ('cxs/rules/query/detailed', 'POST', 200),
    ('select', 'goal'):     ('cxs/goals/query/', 'POST', 200),
    ('select', 'segment'):  ('cxs/segments/query/', 'POST', 200),
    ('select', 'scoring'):  ('cxs/scoring/query/', 'POST', 200),
    ('select', 'campaign'): ('cxs/campaigns/query', 'POST', 200),
    ('select', 'session'):  ('cxs/profiles/search/sessions/', 'POST', 200),

    ('create', 'segment'):  ('cxs/segments/', 'POST', 204),
    ('create', 'rule'):     ('cxs/rules/', 'POST', 204),
    ('create', 'goal'):     ('cxs/goals/', 'POST', 204),

    ('delete', 'segment'):  ('cxs/segments/{item-id}', 'DELETE', 200),
    ('delete', 'rule'):     ('cxs/rules/{item-id}', 'DELETE', 204),
    ('delete', 'profile'):  ('cxs/profiles/{item-id}', 'DELETE', 204),
    ('delete', 'goal'):     ('cxs/goals/{item-id}', 'DELETE', 204),
    ('delete', 'scoring'):  ('cxs/scorings/{item-id}', 'DELETE', 204),
    ('delete', 'scope'):    ('cxs/cluster/{item-id}', 'DELETE', 204),
    ('delete', 'campaign'): ('cxs/campaigns/{item-id}', 'DELETE', 204),

    ('info', 'cluster'):    ('cxs/cluster', 'GET', 200)

}