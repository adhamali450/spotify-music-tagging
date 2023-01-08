class ValuesAdapter:
    __values = {
        'thresh_album': [],
        'thresh_track': [],
        'requests': 0,
    }

    @staticmethod
    def get(key: str, default=None):
        try:
            # if list -> min
            # if numeric -> val

            if isinstance(ValuesAdapter.__values[key], list):
                return min(ValuesAdapter.__values[key])
            else:
                return ValuesAdapter.__values[key]

        except KeyError:
            return default

    @staticmethod
    def feed(key: str, value: float):
        ValuesAdapter.__values[key].append(value)

    @staticmethod
    def increament(key: str, value: float):
        ValuesAdapter.__values[key] += value

    @staticmethod
    def __avg(values: list):
        try:
            return sum(values) / len(values)
        except ZeroDivisionError:
            return 0
