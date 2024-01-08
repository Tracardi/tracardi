from tracardi.service.merging.merger import MergingStrategy, FieldMergingStrategy

rules = {
    "merge-with-cached-profile": [
        FieldMergingStrategy(
            field="segments",
            strategy=MergingStrategy(
                make_lists_uniq=True,
                no_single_value_list=False,
                default_list_strategy="override"
            )
        )
    ]
}
