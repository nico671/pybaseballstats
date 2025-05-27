# Plotting Documentation

## Source

The plotting module provides visualization functions for baseball data analysis using matplotlib. Stadium data is sourced from included MLB stadium coordinate files.

## Available Functions

- `plot_stadium`: Create a stadium outline plot for a specific team
- `scatter_plot_over_stadium`: Overlay hit location data on a stadium plot
- `plot_strike_zone`: Create a strike zone visualization
- `plot_scatter_on_sz`: Overlay pitch location data on a strike zone plot

## Function Details

### plot_stadium()

**Parameters:**

- `team` (str): Team name/identifier for the stadium to plot
- `title` (str, optional): Custom title for the plot. Defaults to team name if not provided

**Returns:**

- `matplotlib.axes.Axes`: Matplotlib axis object with the stadium outline

**Description:**
Creates a scaled stadium outline plot based on team-specific coordinate data. The function reads stadium boundary data from an internal CSV file and renders the field dimensions.

### scatter_plot_over_stadium()

**Parameters:**

- `data` (pl.DataFrame): DataFrame containing hit coordinate data with `hc_x` and `hc_y` columns
- `team_stadium` (str): Team identifier for the stadium background

**Returns:**

- `matplotlib.axes.Axes`: Matplotlib axis object with stadium and scatter plot overlay

**Description:**
Combines a stadium plot with hit location scatter points. Requires coordinate data in Statcast format with `hc_x` and `hc_y` columns representing hit coordinates.

### plot_strike_zone()

**Parameters:**

- `sz_top` (float, optional): Top of strike zone in feet. Defaults to 3.389
- `sz_bot` (float, optional): Bottom of strike zone in feet. Defaults to 1.586

**Returns:**

- `matplotlib.axes.Axes`: Matplotlib axis object with strike zone outline

**Description:**
Creates a regulation strike zone visualization. The zone is 17 inches wide (8.5 inches on each side of home plate) with customizable top and bottom boundaries.

### plot_scatter_on_sz()

**Parameters:**

- `data` (pl.DataFrame | pd.DataFrame): DataFrame with pitch location data

**Required Columns:**

- `sz_top`: Strike zone top for each pitch
- `sz_bot`: Strike zone bottom for each pitch  
- `plate_z`: Vertical pitch location
- `plate_x`: Horizontal pitch location

**Returns:**

- `matplotlib.axes.Axes`: Matplotlib axis object with strike zone and pitch locations

**Raises:**

- `ValueError`: If required columns are missing
- `ValueError`: If DataFrame is empty

**Description:**
Overlays pitch location data on a strike zone plot. Uses the mean strike zone dimensions from the data and plots each pitch as a scatter point.

## Usage Examples

### Basic Stadium Plot

```python
# Option 1: Direct import
from pybaseballstats.plotting import plot_stadium

# Create a Yankees stadium plot
ax = plot_stadium("NYY")
plt.show()

# Create with custom title
ax = plot_stadium("LAD", title="Dodger Stadium - 2023 Season")
plt.show()

# Option 2: Module import
import pybaseballstats as pyb
ax = pyb.plotting.plot_stadium("BOS")
```

### Hit Location Analysis

```python
import polars as pl
from pybaseballstats.plotting import scatter_plot_over_stadium

# Assuming you have hit coordinate data
hit_data = pl.DataFrame({
    "hc_x": [126.3, 89.7, 156.8, 201.2],
    "hc_y": [204.1, 156.3, 178.9, 102.4],
    "events": ["single", "double", "home_run", "out"]
})

# Plot hits over Fenway Park
ax = scatter_plot_over_stadium(hit_data, "BOS")
plt.title("Hit Locations at Fenway Park")
plt.show()
```

### Strike Zone Visualization

```python
from pybaseballstats.plotting import plot_strike_zone

# Default strike zone
ax = plot_strike_zone()
plt.title("MLB Strike Zone")
plt.show()

# Custom strike zone dimensions
ax = plot_strike_zone(sz_top=3.5, sz_bot=1.4)
plt.title("Custom Strike Zone")
plt.show()
```

### Pitch Location Analysis

```python
import polars as pl
from pybaseballstats.plotting import plot_scatter_on_sz

# Sample pitch data (Statcast format)
pitch_data = pl.DataFrame({
    "plate_x": [-0.5, 0.2, 0.8, -0.3, 0.1],
    "plate_z": [2.1, 2.8, 1.9, 3.2, 2.4],
    "sz_top": [3.4, 3.4, 3.4, 3.4, 3.4],
    "sz_bot": [1.6, 1.6, 1.6, 1.6, 1.6],
    "pitch_type": ["FF", "SL", "CH", "CU", "FF"]
})

# Plot pitch locations
ax = plot_scatter_on_sz(pitch_data)
plt.title("Pitch Locations")
plt.xlabel("Horizontal Location (feet)")
plt.ylabel("Vertical Location (feet)")
plt.show()
```

### Advanced Usage with Real Data

```python
from pybaseballstats.plotting import plot_scatter_on_sz, scatter_plot_over_stadium
import matplotlib.pyplot as plt

# Assuming you have Statcast data from other pybaseballstats functions
# Filter for strikes vs balls
strikes = pitch_data.filter(pl.col("description").str.contains("strike"))
balls = pitch_data.filter(pl.col("description").str.contains("ball"))

# Create subplots for comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# Plot strikes
plt.sca(ax1)
plot_scatter_on_sz(strikes)
ax1.set_title("Strike Locations")

# Plot balls  
plt.sca(ax2)
plot_scatter_on_sz(balls)
ax2.set_title("Ball Locations")

plt.tight_layout()
plt.show()
```

### Combining with Data Analysis

```python
# Filter home runs and plot locations
home_runs = hit_data.filter(pl.col("events") == "home_run")

if home_runs.height > 0:
    ax = scatter_plot_over_stadium(home_runs, "NYY")
    plt.title("Home Run Locations - Yankees")
    plt.show()
else:
    print("No home run data available")
```

## Data Requirements

### Hit Coordinate Data

- **hc_x**: Horizontal hit coordinate (feet from home plate)
- **hc_y**: Vertical hit coordinate (feet from home plate)
- **Format**: Statcast coordinate system
- **Null handling**: Function filters out null coordinates automatically

### Pitch Location Data

- **plate_x**: Horizontal pitch location (feet from center of plate)
- **plate_z**: Vertical pitch location (feet above ground)
- **sz_top/sz_bot**: Strike zone boundaries (feet)
- **Format**: Statcast coordinate system

## Coordinate Systems

### Stadium Coordinates

- **Origin**: Home plate center
- **X-axis**: Negative = left field, Positive = right field
- **Y-axis**: Negative = towards outfield, Positive = towards backstop
- **Units**: Feet

### Strike Zone Coordinates  

- **Origin**: Center of home plate at ground level
- **X-axis**: Negative = inside to right-handed batter
- **Y-axis**: Height above ground
- **Units**: Feet

## Performance Notes

- Stadium plots are lightweight and render quickly
- Large scatter datasets (>10,000 points) may render slowly
- Consider sampling large datasets for better performance
- All functions return matplotlib axis objects for further customization

## Error Handling

Common issues and solutions:

- **Missing coordinate columns**: Ensure DataFrame has required columns
- **Empty DataFrames**: Functions will raise ValueError for empty data
- **Stadium data not found**: Verify team identifier matches available stadium data
- **Invalid coordinates**: Functions filter null values automatically

## Customization

All functions return matplotlib axis objects, allowing for additional customization:

```python
# Basic plot
ax = plot_stadium("LAA")

# Add custom elements
ax.set_title("Custom Title", fontsize=16)
ax.text(125, -125, "Custom annotation", ha='center')

# Modify scatter plot
ax = scatter_plot_over_stadium(data, "SF")
ax.collections[0].set_sizes([20])  # Larger points
ax.collections[0].set_color("blue")  # Different color

plt.show()
```
