import numpy as np
from sklearn.base import BaseEstimator
from sklearn.feature_selection.base import SelectorMixin
from ._gmm_selector import GMMSelector


class HighAbundanceAndVarianceSelector(BaseEstimator, SelectorMixin):
    """Feature selector that removes low-mean and low-variance features

    Exercises ``GMMSelector`` to filter out the low-abundance noise features
    and select high-variance informative features.

    This feature selection algorithm looks only at the features (X), not the
    desired outputs (y), and can thus be used for unsupervised learning.

    Parameters
    ----------
    use_log: bool, optional, default: False
        Whether to use the logarithm of feature characteristic instead of the
        characteristic itself. This may improve feature filtering performance,
        depending on the distribution of features, however all the
        characteristics (mean, variance) have to be positive for that -
        filtering will fail otherwise. This is useful for specific cases in
        biology where the distribution of data may actually require this option
        for any efficient filtering.

    min_features: int, optional, default: 1
        How many features must be preserved.

    min_features_rate: float, optional, default: 0.0
        Similar to ``min_features`` but relative to the input data features
        number.

    max_components: int, optional, default: 10
        The maximum number of components used in the GMM decomposition.

    Attributes
    ----------
    abundance_selector_: GMMSelector
        Selector used to filter out the noise component.

    variance_selector_: GMMSelector
        Selector used to filter out the non-informative features.

    selected_: array, shape (n_features,)
        Vector of binary selections of the informative features.

    Examples
    --------
    >>> import numpy as np
    >>> import divik.feature_selection as fs
    >>> np.random.seed(42)
    >>> # Data in this case must be carefully crafted
    >>> labels = np.concatenate([30 * [0] + 20 * [1] + 30 * [2] + 40 * [3]])
    >>> data = np.vstack(100 * [labels * 10.])
    >>> data += np.random.randn(*data.shape)
    >>> sub = data[:, :-40]
    >>> sub += 5 * np.random.randn(*sub.shape)
    >>> # Label 0 has low abundance but high variance
    >>> # Label 3 has low variance but high abundance
    >>> # Label 1 and 2 has not-lowest abundance and high variance
    >>> selector = fs.HighAbundanceAndVarianceSelector().fit(data)
    >>> selector.transform(labels.reshape(1,-1))
    array([[1 1 1 1 1 ...2 2 2]])

    """
    def __init__(self, use_log: bool = False, min_features: int = 1,
                 min_features_rate: float = 0., max_components: int = 10):
        self.use_log = use_log
        self.min_features = min_features
        self.min_features_rate = min_features_rate
        self.max_components = max_components

    def fit(self, X, y=None):
        """Learn data-driven feature thresholds from X.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape (n_samples, n_features)
            Sample vectors from which to compute feature characteristic.

        y : any
            Ignored. This parameter exists only for compatibility with
            sklearn.pipeline.Pipeline.

        Returns
        -------
        self
        """
        min_features = max(
            self.min_features, self.min_features_rate * X.shape[1])

        self.abundance_selector_ = GMMSelector(
            'mean', use_log=self.use_log, n_candidates=1,
            min_features=min_features, preserve_high=True,
            max_components=self.max_components
        ).fit(X)
        filtered = self.abundance_selector_.transform(X)
        self.selected_ = self.abundance_selector_.selected_.copy()

        self.variance_selector_ = GMMSelector(
            'var', use_log=self.use_log, n_candidates=None,
            min_features=min_features, preserve_high=True,
            max_components=self.max_components
        ).fit(filtered)
        self.selected_[self.selected_] = self.variance_selector_.selected_

        return self

    def _get_support_mask(self):
        """
        Get the boolean mask indicating which features are selected

        Returns
        -------
        support : boolean array of shape [# input features]
            An element is True iff its corresponding feature is selected for
            retention.
        """
        return self.selected_
