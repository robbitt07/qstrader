from qstrader.asset.universe.universe import Universe
from qstrader.asset.asset import Asset

import pandas as pd
from typing import Dict, List, Optional, Union


class DynamicActiveDate(object):
    """
    An base Asset Date that defines a period in which an Asset is 
    within an DynamicUniverse.  Period can be defined as start to end 
    or just start with open ended invovlement in Universe.

    Parameters
    ----------
        start : date
            Start date inclusive of first active date within Universe
        end : Optional[date]
            End date inclusive of last active date within Universe
    
    """

    def __init__(self, start: pd.Timestamp, end: Optional[pd.Timestamp] = None) -> None:
        self.start: pd.Timestamp = start
        self.end: Optional[pd.Timestamp] = end

    def active_on_date(self, dt: pd.Timestamp) -> bool:
        if dt < self.start:
            return False
        if self.end is not None:
            return dt > self.end
        return True


class DynamicActiveDates(object):

    def __init__(self, dynamic_active_dates: List[DynamicActiveDate]) -> None:
        self.dynamic_active_dates: List[DynamicActiveDate] = dynamic_active_dates

    def active_on_date(self, dt: pd.Timestamp) -> bool:
        for dynamic_active_date in self.dynamic_active_dates:
            if dynamic_active_date.active_on_date(dt=dt):
                return True
        return False


AssetDateType = Optional[Union[pd.Timestamp, DynamicActiveDates]]


class DynamicUniverse(Universe):
    """
    An Asset Universe that allows a sequences of additions/removals
    of assets dynamically over time periods.  Either with simple 
    addition of assets as static dates or a sequence of Start/End 
    dates Asset is active within the Universe.

    Parameters
    ----------
    asset_dates : `dict{str: pd.Timestamp}`
        Map of assets and their entry date or Dynamic Active Dates.
    """

    def __init__(self, asset_dates: Dict[Asset: AssetDateType]):
        self.asset_dates: Dict[Asset: AssetDateType] = asset_dates

    def _assess_asset_date(self, dt: pd.Timestamp, asset_date: AssetDateType) -> bool:
        if asset_date is None:
            return False

        if isinstance(asset_date, pd.Timestamp):
            return dt >= asset_date

        return asset_date.active_on_date(dt=dt)

    def get_assets(self, dt: pd.Timestamp) -> List[Asset]:
        """
        Obtain the list of assets in the Universe at a particular
        point in time. This will always return a static list
        independent of the timestamp provided.

        If no date is provided do not include the asset. Only
        return those assets where the current datetime exceeds the
        provided datetime.

        Parameters
        ----------
        dt : `pd.Timestamp`
            The timestamp at which to retrieve the Asset list.

        Returns
        -------
        `list[str]`
            The list of Asset symbols in the static Universe.
        """
        return [
            asset for asset, asset_date in self.asset_dates.items()
            if self._assess_asset_date(dt=dt, asset_date=asset_date)
        ]
