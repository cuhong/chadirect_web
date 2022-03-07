from rest_framework import serializers

from carcompare.models import CompareDetail


class CompareDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompareDetail
        fields = [
            'start_date', 'car_no',
            'manufacturer', 'car_name', 'car_register_year',
            'detail_car_name', 'detail_option',
            'treaty_range',
            'youngest_driver_birthdate',
            'coverage_bil', 'coverage_pdl', 'coverage_mp_list', 'coverage_mp', 'coverage_umbi', 'coverage_cac',
            'treaty_ers', 'discount_bb'
        ]

    youngest_driver_birthdate = serializers.SerializerMethodField()

    def get_youngest_driver_birthdate(self, obj):
        return obj.youngest_driver_birthdate
