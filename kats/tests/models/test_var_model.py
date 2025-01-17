# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-unsafe

import unittest
from unittest import TestCase
from unittest.mock import patch

import matplotlib.pyplot as plt
import pandas as pd
from kats.consts import TimeSeriesData
from kats.data.utils import load_data
from kats.models.var import VARModel, VARParams


class testVARModel(TestCase):
    def setUp(self):
        DATA_multi = load_data("multivariate_anomaly_simulated_data.csv")
        self.TSData_multi = TimeSeriesData(DATA_multi)
        DATA_multi2 = load_data("multi_ts.csv")
        self.TSData_multi2 = TimeSeriesData(DATA_multi2)

    def test_fit_forecast(self) -> None:
        params = VARParams()
        m = VARModel(self.TSData_multi, params)
        m.fit()
        m.predict(steps=30, include_history=True)

    def test_model_wrong_param(self) -> None:
        params = VARParams()
        input_data = TimeSeriesData(pd.DataFrame())
        with self.assertRaises(ValueError):
            m = VARModel(input_data, params)
            m.fit()
            m.predict(steps=30, include_history=True)

    @patch("pandas.concat")
    def test_predict_exception(self, mock_obj) -> None:
        mock_obj.side_effect = Exception
        with self.assertRaisesRegex(
            Exception, "^Failed to generate in-sample forecasts for historical data"
        ):
            params = VARParams()
            m = VARModel(self.TSData_multi, params)
            m.fit()
            m.predict(steps=30, include_history=True)

    def test_predict_unfit(self) -> None:
        with self.assertRaises(ValueError):
            m = VARModel(self.TSData_multi, VARParams())
            m.predict(steps=30)

    def test_trivial_path(self) -> None:
        params = VARParams()
        params.validate_params()
        m = VARModel(self.TSData_multi, params)
        with self.assertRaises(NotImplementedError):
            VARModel.get_parameter_search_space()

    # @pytest.mark.image_compare
    def test_plot(self) -> plt.Figure:
        # Test the example from the 201 notebook.
        m = VARModel(self.TSData_multi2, VARParams())
        m.fit()
        m.predict(steps=90)
        m.plot()
        return plt.gcf()

    # @pytest.mark.image_compare
    def test_plot_include_history(self) -> plt.Figure:
        # This shouldn't error, but currently does.
        with self.assertRaises(ValueError):
            m = VARModel(self.TSData_multi2, VARParams())
            m.fit()
            m.predict(steps=90, include_history=True)
            m.plot()
            return plt.gcf()

    def test_plot_ax_not_supported(self) -> None:
        with self.assertRaises(ValueError):
            _, ax = plt.subplots()
            m = VARModel(self.TSData_multi, VARParams())
            m.fit()
            m.predict(steps=5)
            m.plot(ax=ax)

    def test_plot_unpredict(self) -> None:
        with self.assertRaises(ValueError):
            m = VARModel(self.TSData_multi, VARParams())
            m.plot()

    def test_str(self) -> None:
        result = str(VARModel(self.TSData_multi, VARParams()))
        self.assertEqual("VAR", result)


if __name__ == "__main__":
    unittest.main()
