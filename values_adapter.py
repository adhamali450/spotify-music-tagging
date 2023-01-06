class ValuesAdapter:
    __values = {
        'thresh_album': [],
        'thresh_track': [],
    }

    @staticmethod
    def get(key: str, default=None):
        try:
            return ValuesAdapter.__avg(ValuesAdapter.__values[key])
        except KeyError:
            return default

    @staticmethod
    def feed(key: str, value: float):
        ValuesAdapter.__values[key].append(value)

    @staticmethod
    def __avg(values: list):
        try:
            return sum(values) / len(values)
        except ZeroDivisionError:
            return 0
