from urlobject import URLObject

from django.conf import settings
from django.db import models

from datagrowth.configuration import create_config

from core.constants import Repositories
from core.models import HarvestHttpResource, ExtractionMapping
from sharekit.extraction import SharekitMetadataExtraction, SHAREKIT_EXTRACTION_OBJECTIVE


class SharekitMetadataHarvestManager(models.Manager):

    def _create_objective(self):
        extraction_mapping_queryset = ExtractionMapping.objects.filter(is_active=True, repository=Repositories.SHAREKIT)
        if extraction_mapping_queryset.exists():
            extraction_mapping = extraction_mapping_queryset.last()
            return extraction_mapping.to_objective()
        objective = {
            "@": "$.data",
            "external_id": "$.id",
            "state": SharekitMetadataExtraction.get_record_state
        }
        objective.update(SHAREKIT_EXTRACTION_OBJECTIVE)
        return objective

    def extract_seeds(self, set_specification, latest_update):
        latest_update = latest_update.replace(microsecond=0)
        queryset = self.get_queryset() \
            .filter(set_specification=set_specification, since__gte=latest_update, status=200)

        extract_config = create_config("extract_processor", {
            "objective": self._create_objective()
        })
        prc = SharekitMetadataExtraction(config=extract_config)

        results = []
        for harvest in queryset:
            seed_resource = {
                "resource": f"{harvest._meta.app_label}.{harvest._meta.model_name}",
                "id": harvest.id,
                "success": True
            }
            for seed in prc.extract_from_resource(harvest):
                seed["seed_resource"] = seed_resource
                results.append(seed)
        return results


class SharekitMetadataHarvest(HarvestHttpResource):

    objects = SharekitMetadataHarvestManager()

    URI_TEMPLATE = settings.SHAREKIT_BASE_URL + "/api/jsonapi/channel/v1/{}/repoItems?filter[modified][GE]={}"
    PARAMETERS = {
        "page[size]": 25
    }

    def auth_headers(self):
        return {
            "Authorization": f"Bearer {settings.SHAREKIT_API_KEY}"
        }

    def next_parameters(self):
        content_type, data = self.content
        next_link = data["links"].get("next", None)
        if not next_link:
            return {}
        next_url = URLObject(next_link)
        return {
            "page[number]": next_url.query_dict["page[number]"]
        }

    def handle_errors(self):
        content_type, data = self.content
        if data and not len(data.get("data", [])):
            self.status = 204

    class Meta:
        verbose_name = "Sharekit metadata harvest"
        verbose_name_plural = "Sharekit metadata harvest"
