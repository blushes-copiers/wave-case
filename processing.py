import xarray as xr

"""
The dataset has the following format:
Dimensions:    (longitude: 720, latitude: 261, time: 24)
Coordinates:
  * longitude  (longitude) float32 3kB -180.0 -179.5 -179.0 ... 179.0 179.5
  * latitude   (latitude) float32 1kB 70.0 69.5 69.0 68.5 ... -59.0 -59.5 -60.0
  * time       (time) datetime64[ns] 192B 2019-01-01 ... 2019-01-01T23:00:00

Dataset variables: ['hmax', 'mwd', 'mwp', 'tmax', 'swh']
"""


def find_highest_hmax(ds):
    """
    Find the highest hmax value of the day for each longitude and latitude coordinate.

    Parameters:
    -----------
    ds : xarray.Dataset
        Input dataset containing the hmax variable and longitude, latitude and time dimensions

    Returns:
    --------
    xarray.Dataset
        Dataset containing only the lat/lng/time points with highest hmax values
    """
    hmax = ds["hmax"]
    # identify valid (not-all-NaN over time) grid points
    valid_mask = hmax.notnull().any(dim="time")

    # hard-filter the dataset to only valid points
    hmax_filtered = hmax.where(valid_mask)
    hmax_safe = hmax_filtered.fillna(float("-inf"))
    max_idx = hmax_safe.argmax(dim="time")

    # get max hmax and the time it occurred at
    max_time = ds["time"].isel(time=max_idx)
    max_hmax = hmax_filtered.max(dim="time")

    result = xr.Dataset({"hmax": max_hmax, "time": max_time})
    return result


if __name__ == "__main__":
    # load dataset
    ds = xr.open_dataset("waves_2019-01-01.nc")
    highest_hmax_ds = find_highest_hmax(ds)
    # save the result to a netCDF file
    highest_hmax_ds.to_netcdf("waves_2019-01-01-hmax-max.nc")

    # find highest wave at 0,0
    v = ds.sel(latitude=0.0, longitude=0.0, method="nearest")
    print(
        f"Max hmax at 0,0 (Null Island) 2019-01-01: {v["hmax"].max(dim="time").values}"
    )
