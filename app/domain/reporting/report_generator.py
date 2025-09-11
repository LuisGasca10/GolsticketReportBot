from abc import ABC, abstractmethod
from typing import List, Dict, Any

class IReportGenerator(ABC):
    @abstractmethod
    def generar(self, datos: List[Any], ruta_archivo: str, header_data: Dict) -> str:
        pass