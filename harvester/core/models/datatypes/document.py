import re
from copy import copy
from unidecode import unidecode
from django.db import models

from datagrowth.datatypes import DocumentBase


PRIVATE_PROPERTIES = ["pipeline", "from_youtube", "lowest_educational_level"]


class DocumentManager(models.Manager):

    def build_from_seed(self, seed, collection=None, metadata_pipeline_key=None):
        properties = copy(seed)  # TODO: use setters that update the pipeline?
        properties["id"] = seed["external_id"]
        properties["language"] = {
            "metadata": seed.get("language", None)
        }

        metadata_pipeline = properties.pop(metadata_pipeline_key, None)
        document = Document(properties=properties, collection=collection, pipeline={"metadata": metadata_pipeline})
        if collection:
            document.dataset_version = collection.dataset_version
        document.clean()
        return document


class Document(DocumentBase):

    objects = DocumentManager()

    dataset_version = models.ForeignKey("DatasetVersion", blank=True, null=True, on_delete=models.CASCADE)
    pipeline = models.JSONField(default=dict, blank=True)
    extension = models.ForeignKey("core.Extension", null=True, on_delete=models.SET_NULL)
    # NB: Collection foreign key is added by the base class

    def get_language(self):
        language = self.properties.get('language', None)
        if language is None:
            return
        return language.get("metadata", "unk")

    def get_search_document_extras(self, reference_id, title, text, video, material_types):
        suggest_completion = []
        if title:
            suggest_completion += title.split(" ")
        if text:
            suggest_completion += text.split(" ")[:1000]
        alpha_pattern = re.compile("[^a-zA-Z]+")
        suggest_completion = [  # removes reading signs and acutes for autocomplete suggestions
            alpha_pattern.sub("", unidecode(word))
            for word in suggest_completion
        ]
        extras = {
            '_id': reference_id,
            "language": self.get_language(),
            'suggest_completion': suggest_completion,
            'harvest_source': self.collection.name,
            'text': text,
            'suggest_phrase': text,
            'video': video,
            'material_types': material_types
        }
        return extras

    def get_extension_extras(self):
        extension_data = copy(self.extension.properties)
        if "keywords" in extension_data:
            extension_data["keywords"] = [entry["label"] for entry in extension_data["keywords"]]
        themes = extension_data.pop("themes", None)
        if themes:
            extension_data["research_themes"] = [entry["label"] for entry in themes]
        parents = extension_data.pop("parents", None)
        if parents:
            is_part_of = self.properties.get("is_part_of", [])
            is_part_of += parents
            is_part_of = list(set(is_part_of))
            extension_data["is_part_of"] = is_part_of
        children = extension_data.pop("children", None)
        if children:
            has_parts = self.properties.get("has_parts", [])
            has_parts += children
            has_parts = list(set(has_parts))
            extension_data["has_parts"] = has_parts
        return extension_data

    def to_search(self):
        if self.properties["state"] != "active":
            yield {
                "_id": self.properties["external_id"],
                "_op_type": "delete"
            }
            return
        elastic_base = copy(self.properties)
        elastic_base.pop("language")
        text = elastic_base.pop("text", None)
        if text and len(text) >= 1000000:
            text = " ".join(text.split(" ")[:10000])
        if self.extension:
            extension_details = self.get_extension_extras()
            elastic_base.update(extension_details)
        for private_property in PRIVATE_PROPERTIES:
            elastic_base.pop(private_property, False)
        video = elastic_base.pop("video", None)
        material_types = elastic_base.pop("material_types", None) or ["unknown"]
        elastic_details = self.get_search_document_extras(
            self.properties["external_id"],
            self.properties["title"],
            text,
            video,
            material_types=material_types
        )
        elastic_details.update(elastic_base)
        yield elastic_details
