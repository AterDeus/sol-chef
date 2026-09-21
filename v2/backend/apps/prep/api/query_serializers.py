from rest_framework import serializers

from apps.prep.constants import NO_LEFTOVER_FALSE, NO_LEFTOVER_TRUE, PrepMeal


class LooseBooleanField(serializers.BooleanField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            value = data.strip().lower()
            if value in NO_LEFTOVER_TRUE:
                return True
            if value in NO_LEFTOVER_FALSE:
                return False
            self.fail("invalid", input=data)
        return super().to_internal_value(data)


class RecipePrepQuerySerializer(serializers.Serializer):
    prep = serializers.SlugField(required=False)
    day = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=7,
        error_messages={
            "invalid": "Некорректное значение day.",
            "min_value": "day должен быть 1–7.",
            "max_value": "day должен быть 1–7.",
        },
    )
    meal = serializers.ChoiceField(
        required=False,
        choices=PrepMeal.values,
        error_messages={"invalid_choice": "meal: lunch или dinner."},
    )
    servings = serializers.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=6,
    )
    no_leftover = LooseBooleanField(
        required=False,
        default=False,
        error_messages={"invalid": "no_leftover: 1 или 0."},
    )

    def validate_servings(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("servings должен быть больше нуля.")
        return value

    def validate(self, attrs):
        has_day = "day" in attrs
        has_meal = "meal" in attrs
        if has_day != has_meal:
            raise serializers.ValidationError("Нужны оба day и meal, либо ни одного.")
        if (has_day or has_meal) and not attrs.get("prep"):
            raise serializers.ValidationError("Нужен query prep.")
        return attrs
