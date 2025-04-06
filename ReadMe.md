# Wave Case

Max wave height finder.

## Install dependencies 

Install the required dependencies: 

```sh
python3 -m pip install -r requirements.txt
```

## Process the data

* Since, for this challenge, we only want the hmax for the given day we can slim down our dataset significantly.
  * `processing.py` takes the original dataset and extracts just the largest wave for that day, discarding the 23 hours worth of measurements that were less than or equal to the max.
  * This slims the dataset down from 45 to 2.3mb and makes lookups faster.
  * The results have been saved into `waves_2019-01-01-hmax-max.nc`