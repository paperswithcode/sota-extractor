from copy import deepcopy
from marshmallow import Schema, fields, pre_load, post_load, post_dump
from sota_extractor.taskdb.v01.models import Link, SotaRow, Sota, Dataset, Task


class LinkSchema(Schema):
    title = fields.String(missing="")
    url = fields.String(missing="")

    @post_load
    def post_load(self, data, **kwargs):
        return Link(**data)


class SotaRowSchema(Schema):
    model_name = fields.String(required=True)
    paper_title = fields.String(missing="")
    paper_url = fields.String(missing="")
    paper_date = fields.Date(format="%Y-%m-%d", allow_none=True, missing=None)
    code_links = fields.Nested(LinkSchema, many=True, missing=list)
    model_links = fields.Nested(LinkSchema, many=True, missing=list)
    metrics = fields.Dict(keys=fields.String(), values=fields.Inferred())
    uses_additional_data = fields.Boolean(
        default=False, missing=False, allow_none=False
    )

    @post_load
    def post_load(self, data, **kwargs):
        return SotaRow(**data)


class SotaSchema(Schema):
    metrics = fields.List(fields.String(), missing=list)
    rows = fields.Nested(SotaRowSchema, many=True, missing=list)

    @post_load
    def post_load(self, data, **kwargs):
        return Sota(**data)


class DatasetSchema(Schema):
    name = fields.String()
    is_subdataset = fields.Boolean()
    description = fields.String(missing="")
    sota = fields.Nested(SotaSchema, missing=lambda: Sota())
    subdatasets = fields.Nested("self", many=True, missing=list)
    links = fields.Nested(
        LinkSchema, data_key="dataset_links", many=True, missing=list
    )
    citations = fields.Nested(
        LinkSchema, data_key="dataset_citations", many=True, missing=list
    )

    @pre_load
    def pre_load(self, data, **kwargs):
        data = deepcopy(data)
        if "dataset" in data:
            data["name"] = data["dataset"]
            data["is_subdataset"] = False
            del data["dataset"]
        elif "subdataset" in data:
            data["name"] = data["subdataset"]
            data["is_subdataset"] = True
            del data["subdataset"]
        else:
            data["name"] = ""
            data["is_subdataset"] = False
        return data

    @post_load
    def post_load(self, data, **kwargs):
        dataset = Dataset(**data)
        for subdataset in dataset.subdatasets:
            subdataset.parent = dataset
        return dataset

    @post_dump
    def post_dump(self, data, **kwargs):
        if data["is_subdataset"]:
            data["subdataset"] = data["name"]
        else:
            data["dataset"] = data["name"]

        del data["name"]
        del data["is_subdataset"]
        return data


class TaskSchema(Schema):
    name = fields.String(required=True, data_key="task")
    description = fields.String(missing="")
    categories = fields.List(fields.String(), missing=list)
    datasets = fields.Nested(DatasetSchema, many=True, missing=list)
    subtasks = fields.Nested("self", many=True, missing=list)
    synonyms = fields.List(fields.String(), missing=list)
    source_link = fields.Nested(LinkSchema, allow_none=True, missing=None)

    @post_load
    def post_load(self, data, **kwargs):
        task = Task(**data)
        for subtask in task.subtasks:
            subtask.parent = task
        return task
