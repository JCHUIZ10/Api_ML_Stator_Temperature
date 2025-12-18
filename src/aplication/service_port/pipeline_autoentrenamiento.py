from abc import ABC, abstractmethod

class PipelineAutoentrenamiento(ABC):
    
    @abstractmethod
    def star(self) -> bool: pass