import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Polygon, LineString
import contextily as ctx
import pyproj
import numpy as np
import geopandas as gpd


def plot_airspace(df_airspace, airspace_str="", fig=None, ax=None):
    """
    Plot an FIR polygon from a dataframe of ordered vertices.
    - df_FIR: dataframe containing columns ["Airspace ID","Sequence Number","Latitude","Longitude"]
              It can be the whole dataframe or already pre-filtered.
    - airspace_str: if provided, the function will filter df_FIR by this Airspace ID
    - fig, ax: optional matplotlib figure/axis to plot into (allows layering multiple FIRs)
    Returns: (fig, ax)
    """
    # Filter if an Airspace ID string was provided
    if airspace_str:
        subset = df_airspace[df_airspace["Airspace ID"] == airspace_str].copy()
    else:
        subset = df_airspace.copy()

    # Ensure we have the sequence order
    subset = subset.sort_values("Sequence Number")

    # Need at least 3 points to form a polygon
    if len(subset) < 3:
        raise ValueError(f"Not enough points to build a polygon for '{airspace_str}' (need >=3, got {len(subset)})")

    # Create polygon geometry (lon, lat)
    polygon = Polygon(zip(subset["Longitude"], subset["Latitude"]))
    gdf = gpd.GeoDataFrame({"Airspace ID": [airspace_str or subset["Airspace ID"].iloc[0]]},
                           geometry=[polygon], crs="EPSG:4326")

    # Project to Web Mercator for basemap compatibility
    gdf_web = gdf.to_crs(epsg=3857)

    # Create figure/axis if needed
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))

    # Plot the polygon
    gdf_web.plot(ax=ax, edgecolor="darkblue", facecolor="lightblue", alpha=0.3, linewidth=2, zorder=3)

    # Compute this polygon's bounds (in Web Mercator)
    xmin_f, ymin_f, xmax_f, ymax_f = gdf_web.total_bounds

    # If axis already has limits (we're overlaying), combine them so we don't shrink the view
    try:
        curr_xlim = ax.get_xlim()
        curr_ylim = ax.get_ylim()
        if curr_xlim != (0.0, 1.0) or curr_ylim != (0.0, 1.0):  # a heuristic: default axis limits are (0,1) before plotting
            xmin = min(curr_xlim[0], xmin_f)
            xmax = max(curr_xlim[1], xmax_f)
            ymin = min(curr_ylim[0], ymin_f)
            ymax = max(curr_ylim[1], ymax_f)
        else:
            xmin, ymin, xmax, ymax = xmin_f, ymin_f, xmax_f, ymax_f
    except Exception:
        xmin, ymin, xmax, ymax = xmin_f, ymin_f, xmax_f, ymax_f

    # Add padding (20%)
    x_pad = (xmax - xmin) * 0.2
    y_pad = (ymax - ymin) * 0.2
    ax.set_xlim(xmin - x_pad, xmax + x_pad)
    ax.set_ylim(ymin - y_pad, ymax + y_pad)

    # Add basemap AFTER setting the axis extent (contextily expects WebMercator extents)
    ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)

    # --- Label polygon (centroid in Web Mercator)
    centroid = gdf_web.geometry.iloc[0].centroid
    ax.text(
        centroid.x,
        centroid.y,
        airspace_str or subset["Airspace ID"].iloc[0],
        color="grey",
        fontsize=12,
        ha="center",
        va="center",
        fontweight="bold",
        zorder=4,
        alpha=0.8,
    )

    # Transformer from Web Mercator (EPSG:3857) to WGS84 (EPSG:4326)
    transformer = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
    
    # Get current plot limits in Web Mercator
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    
    # Convert corner points back to lon/lat
    lon_min, lat_min = transformer.transform(xlim[0], ylim[0])
    lon_max, lat_max = transformer.transform(xlim[1], ylim[1])
    
    # Set new ticks and labels
    ax.set_xticks(np.linspace(xlim[0], xlim[1], 6))
    ax.set_yticks(np.linspace(ylim[0], ylim[1], 6))
    ax.set_xticklabels([f"{lon:.1f}°" for lon in np.linspace(lon_min, lon_max, 6)])
    ax.set_yticklabels([f"{lat:.1f}°" for lat in np.linspace(lat_min, lat_max, 6)])
    
    # Optional axis labels
    ax.set_xlabel("Longitude (°)")
    ax.set_ylabel("Latitude (°)")

    # Labels and title
    #ax.set_xlabel("Longitude (Web Mercator)")
    #ax.set_ylabel("Latitude (Web Mercator)")

    return fig, ax


def plot_route(df_route, fig=None, ax=None, route_id=""):
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))
        # initialize bounds if starting new figure
        ax._xmin, ax._xmax, ax._ymin, ax._ymax = None, None, None, None

    # --- Sort and create geometry
    df_route = df_route.sort_values("Sequence Number")
    line = LineString(zip(df_route["Longitude"], df_route["Latitude"]))
    gdf = gpd.GeoDataFrame({"Route ID": [route_id]}, geometry=[line], crs="EPSG:4326")
    gdf_web = gdf.to_crs(epsg=3857)

    # --- Plot route
    gdf_web.plot(ax=ax, linewidth=2, color="crimson", label=route_id)

    # --- Label roughly at midpoint
    midpoint = gdf_web.geometry.iloc[0].interpolate(0.5, normalized=True)
    ax.text(midpoint.x, midpoint.y, route_id, fontsize=12, color="grey",
            ha="center", va="center", weight="bold", alpha=0.8)

    # --- Update bounds
    xmin_f, ymin_f, xmax_f, ymax_f = gdf_web.total_bounds
    ax._xmin = xmin_f if ax._xmin is None else min(ax._xmin, xmin_f)
    ax._xmax = xmax_f if ax._xmax is None else max(ax._xmax, xmax_f)
    ax._ymin = ymin_f if ax._ymin is None else min(ax._ymin, ymin_f)
    ax._ymax = ymax_f if ax._ymax is None else max(ax._ymax, ymax_f)

    # --- Always update limits first
    x_pad = (ax._xmax - ax._xmin) * 0.2
    y_pad = (ax._ymax - ax._ymin) * 0.2
    ax.set_xlim(ax._xmin - x_pad, ax._xmax + x_pad)
    ax.set_ylim(ax._ymin - y_pad, ax._ymax + y_pad)
    
    # --- Re-add basemap each time so it fills the extended extent
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs="EPSG:3857")


    # --- Adjust limits with padding
    x_pad = (ax._xmax - ax._xmin) * 0.2
    y_pad = (ax._ymax - ax._ymin) * 0.2
    ax.set_xlim(ax._xmin - x_pad, ax._xmax + x_pad)
    ax.set_ylim(ax._ymin - y_pad, ax._ymax + y_pad)

    # --- Convert to lat/lon ticks
    transformer = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    lon_min, lat_min = transformer.transform(xlim[0], ylim[0])
    lon_max, lat_max = transformer.transform(xlim[1], ylim[1])
    ax.set_xticks(np.linspace(xlim[0], xlim[1], 6))
    ax.set_yticks(np.linspace(ylim[0], ylim[1], 6))
    ax.set_xticklabels([f"{lon:.1f}°" for lon in np.linspace(lon_min, lon_max, 6)])
    ax.set_yticklabels([f"{lat:.1f}°" for lat in np.linspace(lat_min, lat_max, 6)])
    ax.set_xlabel("Longitude (°)")
    ax.set_ylabel("Latitude (°)")
    ax.set_title("Routes", fontsize=14)

    return fig, ax


def plot_histogram_departures_arrivals_planned_actual(df_flights, airport):
    departures = df_flights[df_flights["ADEP"] == airport].copy()
    arrivals = df_flights[df_flights["ADES"] == airport].copy()
    
    # --- Extract hours for filed and actual times
    departures["FILED_HOUR"] = departures["FILED OFF BLOCK TIME"].dt.hour
    departures["ACTUAL_HOUR"] = departures["ACTUAL OFF BLOCK TIME"].dt.hour
    arrivals["FILED_HOUR"] = arrivals["FILED ARRIVAL TIME"].dt.hour
    arrivals["ACTUAL_HOUR"] = arrivals["ACTUAL ARRIVAL TIME"].dt.hour
    
    # --- Plot histograms
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    
    # Departures
    axes[0].hist(
        [departures["FILED_HOUR"], departures["ACTUAL_HOUR"]],
        bins=range(0, 25),
        label=["Filed", "Actual"],
        color=["skyblue", "steelblue"],
        alpha=0.8
    )
    axes[0].set_title(f"{airport} Departures by Hour")
    axes[0].set_xlabel("Hour of Day (UTC)")
    axes[0].set_ylabel("Number of Flights")
    axes[0].legend()
    
    # Arrivals
    axes[1].hist(
        [arrivals["FILED_HOUR"], arrivals["ACTUAL_HOUR"]],
        bins=range(0, 25),
        label=["Filed", "Actual"],
        color=["lightcoral", "indianred"],
        alpha=0.8
    )
    axes[1].set_title(f"{airport} Arrivals by Hour")
    axes[1].set_xlabel("Hour of Day (UTC)")
    axes[1].legend()
    
    plt.suptitle(f"Daily Flight Distribution at {airport}", fontsize=14)
    plt.tight_layout()
    plt.show()


def plot_trajectory(df_points, ectrl_id="", label=None, fig=None, ax=None, cmap="viridis", color="blue"):
    """
    Plot one or more aircraft trajectories with background basemap and color-coded points by flight level.
    
    Parameters
    ----------
    df_points : pd.DataFrame
        DataFrame with columns ['Latitude', 'Longitude', 'Flight Level'].
    ectrl_id : str
        Trajectory ID (for title and legend).
    label : str
        Label for the trajectory (appears in legend). Defaults to ectrl_id.
    fig, ax : matplotlib Figure and Axes
        If provided, trajectory is added to the same map.
    cmap : str
        Matplotlib colormap for flight levels.
    """

    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(10, 10))
        # initialize extent tracking attributes
        ax._xmin, ax._xmax, ax._ymin, ax._ymax = None, None, None, None

    # --- Label fallback
    if label is None:
        label = str(ectrl_id)

    # --- Build trajectory line and points
    df_points = df_points.sort_values("Sequence Number")
    line = LineString(zip(df_points["Longitude"], df_points["Latitude"]))
    gdf_line = gpd.GeoDataFrame({"ECTRL ID": [ectrl_id]}, geometry=[line], crs="EPSG:4326").to_crs(epsg=3857)
    gdf_points = gpd.GeoDataFrame(
        df_points,
        geometry=gpd.points_from_xy(df_points["Longitude"], df_points["Latitude"]),
        crs="EPSG:4326"
    ).to_crs(epsg=3857)

    # --- Plot the trajectory line and colored points
    gdf_line.plot(ax=ax, linewidth=2, label=label, color=color)
    #gdf_points.plot(ax=ax, column="Flight Level", cmap=cmap, markersize=40, legend=True)

    # --- Update bounds dynamically
    xmin_f, ymin_f, xmax_f, ymax_f = gdf_line.total_bounds
    ax._xmin = xmin_f if ax._xmin is None else min(ax._xmin, xmin_f)
    ax._xmax = xmax_f if ax._xmax is None else max(ax._xmax, xmax_f)
    ax._ymin = ymin_f if ax._ymin is None else min(ax._ymin, ymin_f)
    ax._ymax = ymax_f if ax._ymax is None else max(ax._ymax, ymax_f)

    # --- Update limits and basemap every time
    x_pad = (ax._xmax - ax._xmin) * 0.3
    y_pad = (ax._ymax - ax._ymin) * 0.3
    ax.set_xlim(ax._xmin - x_pad, ax._xmax + x_pad)
    ax.set_ylim(ax._ymin - y_pad, ax._ymax + y_pad)
    ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, crs="EPSG:3857")

    # --- Add trajectory label near the midpoint
    midpoint = gdf_line.geometry.iloc[0].interpolate(0.5, normalized=True)
    ax.text(midpoint.x, midpoint.y, label, color="grey", fontsize=12,
            ha="center", va="center", weight="bold", alpha=0.8)

    # --- Convert axes ticks to lat/lon labels
    transformer = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    lon_min, lat_min = transformer.transform(xlim[0], ylim[0])
    lon_max, lat_max = transformer.transform(xlim[1], ylim[1])
    ax.set_xticks(np.linspace(xlim[0], xlim[1], 6))
    ax.set_yticks(np.linspace(ylim[0], ylim[1], 6))
    ax.set_xticklabels([f"{lon:.1f}°" for lon in np.linspace(lon_min, lon_max, 6)])
    ax.set_yticklabels([f"{lat:.1f}°" for lat in np.linspace(lat_min, lat_max, 6)])
    ax.set_xlabel("Longitude (°)")
    ax.set_ylabel("Latitude (°)")

    # --- Title and legend
    ax.set_title("Aircraft Trajectories", fontsize=14)
    ax.legend()

    return fig, ax

