from tracardi.domain.pro_service_form_data import ProService, ProServicePayload, ResourceMetadata, ProServiceFormData, \
    ProServiceFormMetaData, ProDestinationPackage
from tracardi.domain.resource import Resource


def test_default_name_and_description():
    pro_service = ProService(
        service=ProServicePayload(
            metadata=ResourceMetadata(
                type="test_type",
                name="name",
                description="desc",
                traffic="test_traffic",
                icon="test_icon",
                tags=["tag1", "tag2"]
            ),
            form=ProServiceFormData(
                metadata=ProServiceFormMetaData(
                    name="test_name"
                ),
                data={}
            )
        ),
        destination=ProDestinationPackage(
            form={},
            init={},
            package="package"
        )
    )

    resource = Resource.from_pro_service(pro_service)

    assert resource.name == "test_name"
    assert resource.description == "No description provided"