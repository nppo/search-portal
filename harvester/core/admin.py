from django.contrib import admin

from datagrowth.admin import DataStorageAdmin, DocumentAdmin, HttpResourceAdmin, ShellResourceAdmin

from core.models import (Dataset, DatasetVersion, Collection, Arrangement, Document, HarvestSource, ElasticIndex,
                         CommonCartridge, FileResource, TikaResource)


class HarvestSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "spec", "delete_policy", "created_at", "modified_at",)


class HarvestAdminInline(admin.TabularInline):
    model = HarvestSource.datasets.through
    fields = ("source", "harvested_at", "latest_update_at", "purge_after", "stage",)
    readonly_fields = ("harvested_at",)
    extra = 0


class DatasetAdmin(DataStorageAdmin):
    inlines = [HarvestAdminInline]


class DatasetVersionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_current', "created_at")


class ArrangementAdmin(DataStorageAdmin):
    search_fields = ["meta"]


class ExtendedDocumentAdmin(DocumentAdmin):
    list_display = ['__str__', 'dataset_version', 'collection', 'created_at', 'modified_at']
    list_filter = ('dataset_version', 'collection',)
    readonly_fields = ("created_at", "modified_at",)


class ElasticIndexAdmin(admin.ModelAdmin):
    list_display = ("name", "remote_name", "remote_exists", "error_count", "language", "created_at", "modified_at",
                    "pushed_at")


class CommonCartridgeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'upload_at', 'metadata_tag')


admin.site.register(HarvestSource, HarvestSourceAdmin)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(DatasetVersion, DatasetVersionAdmin)
admin.site.register(Collection, DataStorageAdmin)
admin.site.register(Arrangement, ArrangementAdmin)
admin.site.register(Document, ExtendedDocumentAdmin)
admin.site.register(ElasticIndex, ElasticIndexAdmin)
admin.site.register(CommonCartridge, CommonCartridgeAdmin)
admin.site.register(FileResource, HttpResourceAdmin)
admin.site.register(TikaResource, ShellResourceAdmin)
