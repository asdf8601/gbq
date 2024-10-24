# gbq

Simple Google Big Query CLI that relies on `pandas_gbq`.


## Installation


```bash
pip install git+https://github.com/mmngreco/gbq
```


## Usage

```bash
# String
gbq "select 1"

# send python code
gbq "select 1" -e "print(df)"

# silent mode
gbq "select 1" -e "print(df)" -q

# no cache
gbq "select 1" -e "print(df)" -f

# file
gbq ./query.sql
```


### Examples

You can try the following:

```bash
mkdir /tmp/gbq/
cd /tmp/gbq/
echo "select 1" > query.sql

# read query from a file
gbq ./query.sql
gbq ./query.sql -e "print(df.shape)"

# use python scrits
echo "print(df.shape)" >> script.py
echo "print(df.T)" >> script.py
gbq ./query.sql -e ./script.py
```

You can also use the `execute` function only

```python
from gbq import execute

execute("select 1")
```
