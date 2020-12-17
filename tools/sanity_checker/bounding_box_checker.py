class BoundingBoxChecker:
    def __init__(self):
        pass

    def run(self, label: dict):
        assert label["geometryType"] == "rectangle"

        is_ok = True
        return is_ok
