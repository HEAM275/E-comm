from django.http import Http404
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from apps.products.serializer.category import (
    CategoryListSerializer,
    CategoryDetailSerializer,
    CategoryCreateSerializer,
    CategoryUpdateSerializer
)
from apps.products.models.category import Category

from apps.products.filters.category import CategoryProductFilter

from drf_yasg import openapi as oa
from drf_yasg.utils import swagger_auto_schema

from apps.common.views import BaseModelViewSet


class CategoryProductViewSet(BaseModelViewSet):
    """
    API endpoints for management of category products
    """

    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategoryListSerializer
    filter_class = CategoryProductFilter
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list']:
            return CategoryListSerializer
        elif self.action in ['retrieve']:
            return CategoryDetailSerializer
        elif self.action in ['create']:
            return CategoryCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CategoryUpdateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound("Categoria no encontrado")

    # --- LIST ---
    @swagger_auto_schema(
        operation_description="List all active category products",
        manual_parameters=[
            oa.Parameter(
                name='Authorization',
                in_=oa.IN_HEADER,
                description="Bearer <access_token>",
                type=oa.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: oa.Response(description='List of categories', schema=CategoryListSerializer(many=True)),
            403: oa.Response(description='Forbidden', schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
            404: oa.Response(description='Not found', schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # --- RETRIEVE ---
    @swagger_auto_schema(
        operation_description="Retrieve details of a specific category product",
        manual_parameters=[
            oa.Parameter(
                name='Authorization',
                in_=oa.IN_HEADER,
                description="Bearer <access_token>",
                type=oa.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: oa.Response(description='Category details', schema=CategoryDetailSerializer),
            403: oa.Response(description='Forbidden', schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
            404: oa.Response(description='Category not found', schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # --- CREATE ---
    @swagger_auto_schema(
        operation_description="Create a new category product",
        manual_parameters=[
            oa.Parameter(
                name='Authorization',
                in_=oa.IN_HEADER,
                description="Bearer <access_token>",
                type=oa.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            201: oa.Response(description='Category created successfully', schema=CategoryCreateSerializer),
            400: oa.Response(description='Validation error', schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
            403: oa.Response(description='Forbidden', schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'message': _('Category successfully created'),
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)

    # --- UPDATE / PARTIAL_UPDATE ---
    @swagger_auto_schema(
        operation_description="Update an existing category product",
        manual_parameters=[
            oa.Parameter(
                name='Authorization',
                in_=oa.IN_HEADER,
                description="Bearer <access_token>",
                type=oa.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: oa.Response(description='Category updated successfully', schema=CategoryUpdateSerializer),
            400: oa.Response(description='Validation error', schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
            403: oa.Response(description='Forbidden', schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
            404: oa.Response(description='Category not found', schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
        }
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        headers = self.get_success_headers(serializer.data)
        return Response({
            'message': _('Category successfully updated'),
            'data': serializer.data
        }, status=status.HTTP_200_OK, headers=headers)

    # --- DESTROY ---
    @swagger_auto_schema(
        operation_description="Soft delete a category product",
        manual_parameters=[
            oa.Parameter(
                name='Authorization',
                in_=oa.IN_HEADER,
                description="Bearer <access_token>",
                type=oa.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            204: oa.Response(description='Category successfully deleted'),
            403: oa.Response(description='Forbidden', schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
            404: oa.Response(description='Category not found', schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
        }
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'message': _('Category successfully deleted')
        }, status=status.HTTP_204_NO_CONTENT)
