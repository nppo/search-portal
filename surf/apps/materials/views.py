"""
This module contains implementation of REST API views for materials app.
"""

import json
from collections import OrderedDict

from django.conf import settings
from django.db.models import Q, Count
from django.http import Http404
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import (
    ModelViewSet
)

from surf.apps.filters.models import MpttFilterItem
from surf.apps.filters.utils import IGNORED_FIELDS, add_default_material_filters
from surf.apps.materials.filters import (
    CollectionFilter
)
from surf.apps.materials.models import (
    Collection,
    Material,
    CollectionMaterial,
    SharedResourceCounter,
    RESOURCE_TYPE_MATERIAL,
    RESOURCE_TYPE_COLLECTION
)
from surf.apps.materials.serializers import (
    SearchRequestSerializer,
    SearchRequestShortSerializer,
    KeywordsRequestSerializer,
    MaterialsRequestSerializer,
    CollectionSerializer,
    CollectionMaterialsRequestSerializer,
    MaterialShortSerializer,
    SharedResourceCounterSerializer
)
from surf.apps.materials.utils import (
    add_extra_parameters_to_materials,
    get_material_details_by_id,
    add_material_themes,
    add_material_disciplines,
    update_materials_data
)
from surf.vendor.edurep.xml_endpoint.v1_2.api import (
    XmlEndpointApiClient,
    AUTHOR_FIELD_ID
)


class MaterialSearchAPIView(APIView):
    """
    View class that provides search action for Material by filters, author
    lookup text.
    """

    permission_classes = []

    def post(self, request, *args, **kwargs):
        # validate request parameters
        serializer = SearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        filters = data.get("filters", [])
        # add additional filter by Author
        # if input data contains `author` parameter
        author = data.pop("author", None)
        if author:
            filters.append(dict(external_id=AUTHOR_FIELD_ID, items=[author]))

        # add default filters to search materials
        filters = add_default_material_filters(filters)

        data["filters"] = filters

        return_records = data.pop("return_records", None)
        return_filters = data.pop("return_filters", None)

        if not return_records:
            data["page_size"] = 0

        if return_filters:
            data["drilldown_names"] = _get_filter_categories()

        ac = XmlEndpointApiClient(
            api_endpoint=settings.EDUREP_XML_API_ENDPOINT)

        res = ac.search(**data)
        records = add_extra_parameters_to_materials(request.user, res["records"])

        rv = dict(records=records,
                  records_total=res["recordcount"],
                  filters=res["drilldowns"],
                  page=data["page"],
                  page_size=data["page_size"])
        return Response(rv)


def _get_filter_categories():
    """
    Make list of filter categories in format "edurep_field_id:item_count"
    :return: list of "edurep_field_id:item_count"
    """
    return ["{}:{}".format(f.external_id, 0)
            for f in MpttFilterItem.objects.all()
            if f.external_id not in IGNORED_FIELDS
            and f.level == 0]


class KeywordsAPIView(APIView):
    """
    View class that provides search of keywords by text.
    """

    permission_classes = []

    def get(self, request, *args, **kwargs):
        # validate request parameters
        serializer = KeywordsRequestSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        ac = XmlEndpointApiClient(
            api_endpoint=settings.EDUREP_XML_API_ENDPOINT)

        res = ac.autocomplete(**data)
        return Response(res)


_MATERIALS_COUNT_IN_OVERVIEW = 4


class MaterialAPIView(APIView):
    """
    View class that provides retrieving Material by its edurep id (external_id)
    or retrieving overview of materials.
    If external_id is exist in request data then `get()` method returns
    material by external_id, otherwise it returns overview of materials.
    """

    permission_classes = []

    def get(self, request, *args, **kwargs):
        # validate request parameters
        serializer = MaterialsRequestSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        # default is false in the serializer
        count_view = data["count_view"]
        if "external_id" in kwargs:
            return self.get_material(request,
                                     kwargs["external_id"],
                                     count_view=count_view,
                                     shared=data.get("shared"))

        if "external_id" in data:
            res = _get_material_by_external_id(request,
                                               data["external_id"],
                                               shared=data.get("shared"))

        else:
            # return overview of newest Materials
            ac = XmlEndpointApiClient(
                api_endpoint=settings.EDUREP_XML_API_ENDPOINT)

            # add default filters to search materials
            filters = add_default_material_filters()

            res = ac.search([],
                            # sort by newest items first
                            ordering="-lom.lifecycle.contribute.publisherdate",
                            filters=filters,
                            page_size=_MATERIALS_COUNT_IN_OVERVIEW)

            res = add_extra_parameters_to_materials(request.user,
                                                    res["records"])
        return Response(res)

    @staticmethod
    def get_material(request, external_id, count_view, shared=None):
        """
        Returns the list of materials by external id
        :param request: request instance
        :param external_id: external id of material
        :param shared: share type of material
        :param count_view: should the view be counted in the statistics?
        :return:
        """
        res = _get_material_by_external_id(request, external_id, shared=shared, count_view=count_view)

        if not res:
            raise Http404('No materials matches the given query.')

        return Response(res[0])


def _get_material_by_external_id(request, external_id, shared=None, count_view=False):
    """
    Get Materials by edured id and register unique view of materials
    :param request:
    :param external_id: edured id of material
    :param shared: share type of material
    :return: list of materials
    """

    material, created = Material.objects.get_or_create(external_id=external_id)
    if created:
        material.sync_info()
    # increase unique view counter
    if count_view:
        material.view_count += 1
        material.save()

    if shared:
        # increase share counter
        counter_key = SharedResourceCounter.create_counter_key(
            RESOURCE_TYPE_MATERIAL,
            external_id,
            share_type=shared)

        SharedResourceCounter.increase_counter(counter_key, extra=shared)

    rv = get_material_details_by_id(external_id)
    rv = add_extra_parameters_to_materials(request.user, rv)
    rv = add_share_counters_to_materials(rv)
    return rv


class MaterialRatingAPIView(APIView):
    # I don't think we really need the get, but the frontend uses it so I'll leave it be
    def get(self, request, *args, **kwargs):
        external_id = request.GET['external_id']
        return Response(f"External id {external_id} is valid")

    def post(self, request, *args, **kwargs):
        params = request.data.get('params')
        external_id = params['external_id']
        star_rating = params['star_rating']
        material_object = Material.objects.get(external_id=external_id)
        if star_rating == 1:
            material_object.star_1 += 1
        if star_rating == 2:
            material_object.star_2 += 1
        if star_rating == 3:
            material_object.star_3 += 1
        if star_rating == 4:
            material_object.star_4 += 1
        if star_rating == 5:
            material_object.star_5 += 1
        material_object.save()
        return Response(material_object.get_avg_star_rating())


class MaterialApplaudAPIView(APIView):
    # I don't think we really need the get, but the frontend uses it so I'll leave it be
    def get(self, request, *args, **kwargs):
        external_id = request.GET['external_id']
        return Response(f"External id {external_id} is valid")

    def post(self, request, *args, **kwargs):
        params = request.data.get('params')
        external_id = params['external_id']
        material_object = Material.objects.get(external_id=external_id)
        material_object.applaud_count += 1
        material_object.save()
        return Response(material_object.applaud_count)


class CollectionViewSet(ModelViewSet):
    """
    View class that provides CRUD methods for Collection and `get`, `add`
    and `delete` methods for its materials.
    """

    queryset = Collection.objects.filter(deleted_at=None)
    serializer_class = CollectionSerializer
    filter_class = CollectionFilter
    permission_classes = []

    def get_queryset(self):
        return Collection.objects.annotate(community_cnt=Count('communities')).filter(community_cnt__gt=0)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        shared = request.GET.get("shared")
        if shared:
            # increase sharing counter
            counter_key = SharedResourceCounter.create_counter_key(
                RESOURCE_TYPE_COLLECTION,
                str(instance.id),
                share_type=shared)

            SharedResourceCounter.increase_counter(counter_key, extra=shared)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # only active and authorized users can create collection
        self._check_access(request.user)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # only active owners can update collection
        self._check_access(request.user, instance=self.get_object())
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # only active owners can delete collection
        self._check_access(request.user, instance=self.get_object())
        return super().destroy(request, *args, **kwargs)

    @action(methods=['post'], detail=True)
    def search(self, request, pk=None, **kwargs):
        """
        Search materials that are part of the collection
        """

        instance = self.get_object()
        return get_materials_search_response(instance.materials, request)

    @action(methods=['get', 'post', 'delete'], detail=True)
    def materials(self, request, pk=None, **kwargs):
        instance = self.get_object()

        if request.method == "GET":
            # validate request parameters
            serializer = CollectionMaterialsRequestSerializer(data=request.GET)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            ids = ['"{}"'.format(m.external_id)
                   for m in instance.materials.order_by("id").all()]

            rv = dict(records=[],
                      records_total=0,
                      filters=[],
                      page=data["page"],
                      page_size=data["page_size"])

            if ids:
                ac = XmlEndpointApiClient(
                    api_endpoint=settings.EDUREP_XML_API_ENDPOINT)

                res = ac.get_materials_by_id(ids, **data)
                records = res.get("records", [])
                records = add_extra_parameters_to_materials(request.user,
                                                            records)
                rv["records"] = records
                rv["records_total"] = res["recordcount"]

            return Response(rv)

        # only owners can add/delete materials to/from collection
        self._check_access(request.user, instance=instance)
        data = []
        for d in request.data:
            # validate request parameters
            serializer = MaterialShortSerializer(data=d)
            serializer.is_valid(raise_exception=True)
            data.append(serializer.validated_data)

        if request.method == "POST":
            self._add_materials(instance, data)

        elif request.method == "DELETE":
            self._delete_materials(instance, data)

        res = MaterialShortSerializer(many=True).to_representation(
            instance.materials.all())
        return Response(res)

    @staticmethod
    def _add_materials(instance, materials):
        """
        Add materials to collection
        :param instance: collection instance
        :param materials: added materials
        :return:
        """

        for material in materials:
            m_external_id = material["external_id"]

            details = get_material_details_by_id(m_external_id)
            if not details:
                continue

            keywords =details[0].get("keywords")
            if keywords:
                keywords = json.dumps(keywords)

            m, _ = Material.objects.update_or_create(
                external_id=m_external_id,
                defaults=dict(material_url=details[0].get("url"),
                              title=details[0].get("title"),
                              description=details[0].get("description"),
                              keywords=keywords))

            add_material_themes(m, details[0].get("themes", []))
            add_material_disciplines(m, details[0].get("disciplines", []))
            CollectionMaterial.objects.create(collection=instance, material=m)

    @staticmethod
    def _delete_materials(instance, materials):
        """
        Delete materials from collection
        :param instance: collection instance
        :param materials: materials that should be removed from collection
        :return:
        """

        materials = [m["external_id"] for m in materials]
        materials = Material.objects.filter(external_id__in=materials).all()
        instance.materials.remove(*materials)

    @staticmethod
    def _check_access(user, instance=None):
        """
        Check if user is active and owner of collection (if collection
        is not None)
        :param user: user
        :param instance: collection instance
        :return:
        """

        if not user or not user.is_active:
            raise AuthenticationFailed()


def get_materials_search_response(qs, request):
    """
    Searches materials according to search parameters and returns
    a paginated Response object
    :param qs: queryset of materials
    :param request: Request object
    :return: Response object
    """

    # validate request parameters
    serializer = SearchRequestShortSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    qs = _filter_materials_by_search_query(qs, data)
    qs = _ordering_materials_queryset(qs, data)
    materials = _paginate_materials_queryset(qs, request, data)
    return _get_paginated_materials_response(qs, materials, data)


_MATERIAL_SEARCH_FIELDS = ('material_url', 'title', 'description',
                           'keywords',)


def _filter_materials_by_search_query(qs, request_data):
    """
    Adds filters to materials queryset according to search parameters
    :param qs: queryset of materials
    :param request_data: dictionary of request parameters
    :return: updated queryset
    """

    search_text = request_data.get("search_text")
    if not search_text:
        return qs

    queries = []
    for st in search_text:
        text_qs_list = [Q(**{"{}__icontains".format(f): st})
                        for f in _MATERIAL_SEARCH_FIELDS]

        text_qs = text_qs_list.pop()

        while text_qs_list:
            text_qs |= text_qs_list.pop()

        queries.append(text_qs)

    all_qs = queries.pop()

    while queries:
        all_qs &= queries.pop()

    if all_qs:
        qs = qs.filter(all_qs)

    return qs


def _ordering_materials_queryset(qs, request_data):
    """
    Adds ordering to materials queryset according request parameters
    :param qs: queryset of materials
    :param request_data: dictionary of request parameters
    :return: updated queryset
    """

    qs = qs.order_by("id")
    return qs


def _paginate_materials_queryset(qs, request, request_data):
    """
    Prepares the requested page of materials with detailed data
    according to `page` and `page_size` parameters in request
    :param qs: queryset of materials
    :param request: Request object
    :param request_data: dictionary of request parameters
    :return: list of materials of requested page
    """

    page = request_data["page"]
    page_size = request_data["page_size"]
    material_cnt = qs.count()

    start_idx = (page - 1) * page_size
    if start_idx >= material_cnt:
        return []

    end_idx = start_idx + page_size
    if end_idx > material_cnt:
        end_idx = material_cnt

    materials = qs.all()[start_idx:end_idx:]
    material_ids = ['"{}"'.format(m.external_id) for m in materials]

    ac = XmlEndpointApiClient(
        api_endpoint=settings.EDUREP_XML_API_ENDPOINT)

    materials = ac.get_materials_by_id(material_ids, page_size=10)
    materials = materials.get("records", [])
    materials = add_extra_parameters_to_materials(request.user, materials)
    return materials


def _get_paginated_materials_response(qs, materials, request_data):
    return Response(OrderedDict([
        ('page', request_data["page"]),
        ('page_size', request_data["page_size"]),
        ('records_total', qs.count()),
        ('records', materials),
        ('filters', [])
    ]))


def add_share_counters_to_materials(materials):
    """
    Add share counter values for materials.
    :param materials: array of materials
    :return: updated array of materials
    """

    for m in materials:
        key = SharedResourceCounter.create_counter_key(RESOURCE_TYPE_MATERIAL,
                                                       m["external_id"])

        qs = SharedResourceCounter.objects.filter(counter_key__contains=key)

        m["sharing_counters"] = SharedResourceCounterSerializer(
            many=True
        ).to_representation(qs.all())

    return materials
