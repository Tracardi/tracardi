from tracardi.service.storage.persistence_service import SqlSearchQueryParser


def test_parser():
    parser = SqlSearchQueryParser()
    # q = parser.parse("interests.pricing > 0 and interests.pricing< 100")
    q = parser.parse("interests.pricing between 0 and 100")
    print(q)