from abc import ABCMeta, abstractmethod
from multiprocessing.pool import Pool
from typing import List, Optional

import numpy as np
import pandas as pd

from spdivik.kmeans._core import KMeans
from spdivik.types import Data


class Picker(metaclass=ABCMeta):
    @abstractmethod
    def score(self, data: Data, estimators: List[KMeans], pool: Pool = None) \
            -> np.ndarray:
        raise NotImplemented

    @abstractmethod
    def select(self, scores: np.ndarray) -> Optional[int]:
        raise NotImplemented

    @abstractmethod
    def report(self, estimators: List[KMeans], scores: np.ndarray) \
            -> pd.DataFrame:
        raise NotImplemented
