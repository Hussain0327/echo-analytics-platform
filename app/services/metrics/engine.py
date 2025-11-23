from typing import List, Dict, Type, Optional
import pandas as pd
from app.services.metrics.base import BaseMetric, MetricResult, MetricDefinition


class MetricsEngine:

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self._registry: Dict[str, Type[BaseMetric]] = {}

    def register(self, metric_class: Type[BaseMetric]):
        temp_df = pd.DataFrame()
        try:
            instance = metric_class.__new__(metric_class)
            instance.df = temp_df
            definition = instance.get_definition()
            self._registry[definition.name] = metric_class
        except Exception:
            pass

    def calculate(self, metric_name: str, **kwargs) -> MetricResult:
        if metric_name not in self._registry:
            raise ValueError(f"Unknown metric: {metric_name}")
        metric_class = self._registry[metric_name]
        metric = metric_class(self.df)
        return metric.calculate(**kwargs)

    def calculate_all(self, category: Optional[str] = None) -> List[MetricResult]:
        results = []
        for name, metric_class in self._registry.items():
            try:
                metric = metric_class(self.df)
                definition = metric.get_definition()
                if category and definition.category != category:
                    continue
                result = metric.calculate()
                results.append(result)
            except (ValueError, KeyError):
                continue
        return results

    def calculate_category(self, category: str) -> List[MetricResult]:
        return self.calculate_all(category=category)

    def list_metrics(self, category: Optional[str] = None) -> List[MetricDefinition]:
        definitions = []
        for metric_class in self._registry.values():
            try:
                instance = metric_class.__new__(metric_class)
                instance.df = pd.DataFrame()
                definition = instance.get_definition()
                if category and definition.category != category:
                    continue
                definitions.append(definition)
            except Exception:
                continue
        return definitions

    def available_metrics(self) -> List[str]:
        return list(self._registry.keys())
