from rest_framework import serializers
class DataTypeInfoSerializer(serializers.Serializer):
    inferred_type = serializers.CharField()
    display_type = serializers.CharField()
    possible_types = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )

class FileProcessResponseSerializer(serializers.Serializer):
    columns = serializers.DictField(
        child=DataTypeInfoSerializer()
    )
    preview_data = serializers.ListField(
        child=serializers.DictField(
            child=serializers.JSONField()
        )
    )