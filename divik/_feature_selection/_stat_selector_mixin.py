from abc import ABCMeta

import numpy as np
from sklearn.feature_selection.base import SelectorMixin


class StatSelectorMixin(SelectorMixin, metaclass=ABCMeta):
    """
    Transformer mixin that performs feature selection given a support mask

    This mixin provides a feature selector implementation with `transform` and
    `inverse_transform` functionality given that `selected_` is specified
    during `fit`.

    Additionally, provides a `_to_characteristics` and `_to_raw` implementations
    given `stat`, optionally `use_log` and `preserve_high`.
    """
    def _to_characteristics(self, X):
        """Extract & normalize characteristics from data"""
        if self.stat == 'mean':
            vals = np.mean(X, axis=0)
        elif self.stat == 'var':
            vals = np.var(X, axis=0)
        else:
            raise ValueError('stat must be one of {"mean", "var"}')

        if hasattr(self, 'use_log') and self.use_log:
            if np.any(vals < 0):
                raise ValueError("Feature characteristic cannot be negative "
                                 "with log filtering")
            vals = np.log(vals)

        if hasattr(self, 'preserve_high') and not self.preserve_high:
            vals = -vals

        return vals

    def _to_raw(self, threshold):
        """Convert threshold to the feature characteristic space"""
        if hasattr(self, 'preserve_high') and not self.preserve_high:
            threshold = -threshold
        if hasattr(self, 'use_log') and self.use_log:
            threshold = np.exp(threshold)
        return threshold

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
