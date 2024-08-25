from django.urls.converters import StringConverter


class BoolConverter(StringConverter):
    """
    A custom converter for handling boolean values in URLs.
    """

    def to_python(self, value):
        """
        Converts URL parameter to a Python boolean value.
        """
        if value.lower() in ('true', '1', 'yes'):
            return True
        elif value.lower() in ('false', '0', 'no'):
            return False
        else:
            raise ValueError("Invalid boolean value in URL.")

    def to_url(self, value):
        """
        Converts Python boolean value to a URL parameter.
        """
        if value is True:
            return 'true'
        elif value is False:
            return 'false'
        else:
            raise ValueError("Value is not a boolean.")