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
draft_order_by_round(year, draft_round)
# option 2
import pybaseballstats as pyb
pyb.bref_draft.draft_order_by_round(year, draft_round)
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
from pybaseballstats.bref_draft import BREFTeams
franchise_draft_order(year, BREFTeams.FOO)
# option 2
import pybaseballstats as pyb
pyb.bref_draft.franchise_draft_order(year, pyb.bref_draft.BREFTeams.FOO)
```

#### Example

```python
from pybaseballstats.bref_draft import franchise_draft_order
from pybaseballstats.bref_draft import BREFTeams
# Get the draft order for the New York Yankees in the 2023 MLB Draft
draft_order = franchise_draft_order(2023, BREFTeams.YANKEES) # currently the abbreviation needs to be passed in as a string but eventually it will be converted to an enum for ease of use
print(draft_order)
```

This will return a DataFrame with the draft order for the New York Yankees in the 2023 MLB Draft.

## Notes

To see all options for the BREFTeams enum, run the following code:

```python
from pybaseballstats.bref_draft import BREFTeams
print(BREFTeams.show_options())
```
