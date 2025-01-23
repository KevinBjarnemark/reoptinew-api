from rest_framework import serializers


class ListOfPrimitiveDictField(serializers.Field):
    def to_internal_value(self, data):
        # Ensure the input is a list
        if not isinstance(data, list):
            raise serializers.ValidationError(
                "Expected a list of dictionaries."
            )
        # Ensure each item in the list is a dictionary
        for item in data:
            if not isinstance(item, dict):
                raise serializers.ValidationError(
                    "Each item must be a dictionary."
                )

            for key, value in item.items():
                # Ensure keys are strings
                if not isinstance(key, str):
                    raise serializers.ValidationError(
                        f"Key '{key}' must be a string."
                    )

                # Ensure values are bool, str, or number
                if not isinstance(value, (bool, str, int, float, type(None))):
                    raise serializers.ValidationError(
                        f"Value for '{key}' must be a boolean, string, "
                        + "or number."
                    )

                # Ensure strings and numbers are reasonable in length
                if (
                    isinstance(value, (str, int, float))
                    and len(str(value)) > 150
                ):
                    raise serializers.ValidationError(
                        f"Value for '{key}' exceeds the maximum allowed "
                        + "length of 150 characters."
                    )

        return data

    def to_representation(self, value):
        # Pass the data through as-is
        return value
