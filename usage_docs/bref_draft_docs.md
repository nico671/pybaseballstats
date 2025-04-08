# Baseball Reference Draft Docs

## Available Functions

- `draft_order_by_round`: Returns the draft order for a given round in a given year.
- `franchise_draft_order`: Returns the draft order for a given team in a given year.

## Usage

### Draft Order by Round

#### Accessing the Function

```python
# option 1
from pybaseballstats.bref_draft import draft_order_by_round 

# option 2
import pybaseballstats as pyb
pyb.bref_draft.draft_order_by_round
```

#### Example

```python
# Get the draft order for the 1st round of the 2023 MLB Draft
draft_order = draft_order_by_round(2023, 1)
print(draft_order)
```

This will return a DataFrame with the draft order for the 1st round of the 2023 MLB Draft.

### Franchise Draft Order

#### Accessing the Function

```python
# option 1
from pybaseballstats.bref_draft import franchise_draft_order
# option 2
import pybaseballstats as pyb
pyb.bref_draft.franchise_draft_order
```

#### Example

```python
# Get the draft order for the New York Yankees in the 2023 MLB Draft
draft_order = franchise_draft_order(2023, 'NYY') # currently the abbreviation needs to be passed in as a string but eventually it will be converted to an enum for ease of use
print(draft_order)
```

This will return a DataFrame with the draft order for the New York Yankees in the 2023 MLB Draft.
