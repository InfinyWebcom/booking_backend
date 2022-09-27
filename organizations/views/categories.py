from rest_framework.views import APIView
from rest_framework.response import Response as DjangoRestResponse
from rest_framework import authentication, permissions
from rest_framework import status
from rest_framework.exceptions import ParseError
from organizations.models.turf_category import TurfCategory
from organizations.serializers.turf_serializer import TurfCategorySerializer


class Categories(APIView):
    def get(self, request, *args, **kwargs):
        turf_obj = TurfCategory.objects.all()
        serializer = TurfCategorySerializer(turf_obj, many=True)
        return DjangoRestResponse(
            {
                "success": "Success",
                "totalcount": (turf_obj.count()),
                "categories": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
