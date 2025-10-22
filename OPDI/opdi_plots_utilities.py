import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import pandas as pd
import numpy as np
from shapely.geometry import LineString
import pyproj

def plot_flight_trajectory_events(df_events, flight_id):
    """
    Plot a single flight's trajectory in 2D (map view) and its vertical profile (altitude over time).

    Parameters
    ----------
    df_flight : pd.DataFrame
        DataFrame containing at least:
        ['flight_id', 'event_time', 'latitude', 'longitude', 'altitude'].
    flight_id : str
        The flight identifier to plot.
    """

    # --- Filter and prepare data
    df = df_events[df_events["flight_id"] == flight_id].copy()
    if df.empty:
        print(f"No data found for flight_id {flight_id}")
        return

    df = df.sort_values("event_time")
    df["event_time"] = pd.to_datetime(df["event_time"])
    df["altitude_ft"] = df["altitude"] / 100.0  # convert to feet if values look like "x100"

    # --- Build GeoDataFrame and convert to Web Mercator for mapping
    gdf_points = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
        crs="EPSG:4326"
    )
    gdf_points_web = gdf_points.to_crs(epsg=3857)

    # --- Create line geometry
    line = LineString(zip(df["longitude"], df["latitude"]))
    gdf_line = gpd.GeoDataFrame({"flight_id": [flight_id]}, geometry=[line], crs="EPSG:4326").to_crs(epsg=3857)

    # --- Create figure with 2 subplots (map + vertical profile)
    fig, (ax_map, ax_vert) = plt.subplots(
        2, 1, figsize=(10, 12), gridspec_kw={'height_ratios': [2, 1]}
    )

    # =======================
    # MAP VIEW (Horizontal)
    # =======================
    gdf_line.plot(ax=ax_map, color="blue", linewidth=2, label="Trajectory")
    gdf_points_web.plot(ax=ax_map, column="altitude_ft", cmap="viridis", markersize=50, legend=True)

    # --- Basemap
    ctx.add_basemap(ax_map, source=ctx.providers.CartoDB.Positron, crs="EPSG:3857")

    # --- Padding and limits
    xmin, ymin, xmax, ymax = gdf_line.total_bounds
    x_pad, y_pad = (xmax - xmin) * 0.2, (ymax - ymin) * 0.2
    ax_map.set_xlim(xmin - x_pad, xmax + x_pad)
    ax_map.set_ylim(ymin - y_pad, ymax + y_pad)

    # --- Convert ticks to lat/lon labels
    transformer = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
    xlim, ylim = ax_map.get_xlim(), ax_map.get_ylim()
    lon_min, lat_min = transformer.transform(xlim[0], ylim[0])
    lon_max, lat_max = transformer.transform(xlim[1], ylim[1])
    ax_map.set_xticks(np.linspace(xlim[0], xlim[1], 6))
    ax_map.set_yticks(np.linspace(ylim[0], ylim[1], 6))
    ax_map.set_xticklabels([f"{lon:.1f}°" for lon in np.linspace(lon_min, lon_max, 6)])
    ax_map.set_yticklabels([f"{lat:.1f}°" for lat in np.linspace(lat_min, lat_max, 6)])

    # --- Map labels
    midpoint = gdf_line.geometry.iloc[0].interpolate(0.5, normalized=True)
    #ax_map.text(midpoint.x, midpoint.y, flight_id, color="lightgrey", fontsize=12,
    #            ha="center", va="center", weight="bold", alpha=0.8)
    ax_map.set_title(f"Horizontal Trajectory – Flight {flight_id}", fontsize=14)
    ax_map.set_xlabel("Longitude (°)")
    ax_map.set_ylabel("Latitude (°)")

    # =======================
    # VERTICAL PROFILE
    # =======================
    ax_vert.plot(df["event_time"], df["altitude_ft"], color="blue", linewidth=2)
    ax_vert.scatter(df["event_time"], df["altitude_ft"], c=df["altitude_ft"], cmap="viridis", s=30)
    ax_vert.set_title("Vertical Profile (Altitude vs Time)", fontsize=14)
    ax_vert.set_ylabel("Altitude (ft)")
    ax_vert.set_xlabel("Time (UTC)")
    ax_vert.grid(True)

    # --- Align x-axis time between panels
    ax_vert.set_xlim(df["event_time"].min(), df["event_time"].max())

    plt.tight_layout()
    plt.show()

    return fig, (ax_map, ax_vert)

