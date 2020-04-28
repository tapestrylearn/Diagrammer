
class DiagrammerEngine:
    def __init__(self):
        self._bare_language_data = []

    def get_bare_language_data(self) -> dict:
        return self._bare_language_data
        
    def run_code(self, code: str, flags: [int]):
        pass