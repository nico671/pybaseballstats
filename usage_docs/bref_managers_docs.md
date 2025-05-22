# Baseball Reference Managers Docs

## Source

The data is pulled from [this Baseball Reference Page](https://www.baseball-reference.com/leagues/majors/2025-managers.shtml). Note: there is one page per year, the given link is for the 2025 season.

## Available Functions

- `managers_basic_data`: Returns basic information about all MLB managers for a given year.
- `manager_tendencies_data`: Returns data on the tendencies of all MLB managers for a given year.

## Usage

### Managers Basic Data

#### Accessing the Function

```python
# option 1
from pybaseballstats.bref_managers import managers_basic_data
managers_basic_data(year)
# option 2
import pybaseballstats as pyb   
pyb.bref_managers.managers_basic_data(year)
```

#### Example

```python
# Get the basic data for all MLB managers in 2023
managers_data = managers_basic_data(2023)
print(managers_data)
```

This will return a DataFrame with the basic data for all MLB managers in 2023.

### Manager Tendencies Data

#### Accessing the Function

```python
# option 1
from pybaseballstats.bref_managers import manager_tendencies_data
manager_tendencies_data(year)
# option 2
import pybaseballstats as pyb
pyb.bref_managers.manager_tendencies_data(year)
```

#### Example

```python
# Get the tendencies data for all MLB managers in 2023
manager_tendencies = manager_tendencies_data(2023)
print(manager_tendencies)
```

This will return a DataFrame with the tendencies data for all MLB managers in 2023.
