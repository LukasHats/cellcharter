from __future__ import annotations

import warnings
from itertools import combinations
from pathlib import Path
from typing import Union

import anndata as ad
import geopandas
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import spatialdata as sd
import spatialdata_plot  # noqa: F401
from anndata import AnnData
from scipy.stats import ttest_ind
from squidpy._docs import d

from ._utils import adjust_box_widths


def plot_boundaries(
    adata: AnnData,
    sample: str,
    library_key: str = "sample",
    component_key: str = "component",
    alpha_boundary: float = 0.5,
    show_cells: bool = True,
    save: str | Path | None = None,
) -> None:
    """
    Plot the boundaries of the clusters.

    Parameters
    ----------
    %(adata)s
    sample
        Sample to plot.
    library_key
        Key in :attr:`anndata.AnnData.obs` where the sample labels are stored.
    component_key
        Key in :attr:`anndata.AnnData.obs` where the component labels are stored.
    alpha_boundary
        Transparency of the boundaries.
    show_cells
        Whether to show the cells or not.

    Returns
    -------
    %(plotting_returns)s
    """
    # Print warning and call boundaries
    warnings.warn(
        "plot_boundaries is deprecated and will be removed in the next release. " "Please use `boundaries` instead.",
        FutureWarning,
        stacklevel=2,
    )
    boundaries(
        adata=adata,
        sample=sample,
        library_key=library_key,
        component_key=component_key,
        alpha_boundary=alpha_boundary,
        show_cells=show_cells,
        save=save,
    )


@d.dedent
def boundaries(
    adata: AnnData,
    sample: str,
    library_key: str = "sample",
    component_key: str = "component",
    alpha_boundary: float = 0.5,
    show_cells: bool = True,
    save: str | Path | None = None,
) -> None:
    """
    Plot the boundaries of the clusters.

    Parameters
    ----------
    %(adata)s
    sample
        Sample to plot.
    library_key
        Key in :attr:`anndata.AnnData.obs` where the sample labels are stored.
    component_key
        Key in :attr:`anndata.AnnData.obs` where the component labels are stored.
    alpha_boundary
        Transparency of the boundaries.
    show_cells
        Whether to show the cells or not.

    Returns
    -------
    %(plotting_returns)s
    """
    adata = adata[adata.obs[library_key] == sample].copy()
    del adata.raw
    clusters = adata.obs[component_key].unique()

    boundaries = {
        cluster: boundary
        for cluster, boundary in adata.uns[f"shape_{component_key}"]["boundary"].items()
        if cluster in clusters
    }
    gdf = geopandas.GeoDataFrame(geometry=list(boundaries.values()))
    adata.obs.loc[adata.obs[component_key] == -1, component_key] = np.nan
    adata.obs.index = "cell_" + adata.obs.index
    adata.obs["instance_id"] = adata.obs.index
    adata.obs["region"] = "cells"

    xy = adata.obsm["spatial"]
    cell_circles = sd.models.ShapesModel.parse(xy, geometry=0, radius=3000, index=adata.obs["instance_id"])

    obs = pd.DataFrame(list(boundaries.keys()), columns=[component_key], index=np.arange(len(boundaries)).astype(str))
    adata_obs = ad.AnnData(X=pd.DataFrame(index=obs.index, columns=adata.var_names), obs=obs)
    adata_obs.obs["region"] = "clusters"
    adata_obs.index = "cluster_" + adata_obs.obs.index
    adata_obs.obs["instance_id"] = np.arange(len(boundaries))
    adata_obs.obs[component_key] = pd.Categorical(adata_obs.obs[component_key])

    adata = ad.concat((adata, adata_obs), join="outer")

    adata.obs["region"] = adata.obs["region"].astype("category")

    table = sd.models.TableModel.parse(
        adata, region_key="region", region=["clusters", "cells"], instance_key="instance_id"
    )

    shapes = {
        "clusters": sd.models.ShapesModel.parse(gdf),
        "cells": sd.models.ShapesModel.parse(cell_circles),
    }

    sdata = sd.SpatialData(shapes=shapes, tables=table)

    ax = plt.gca()
    if show_cells:
        try:
            sdata.pl.render_shapes(elements="cells", color=component_key).pl.show(ax=ax, legend_loc=None)
        except TypeError:  # TODO: remove after spatialdata-plot issue  #256 is fixed
            warnings.warn(
                "Until the next spatialdata_plot release, the cells that do not belong to any component will be displayed with a random color instead of grey.",
                stacklevel=2,
            )
            sdata.tables["table"].obs[component_key] = sdata.tables["table"].obs[component_key].cat.add_categories([-1])
            sdata.tables["table"].obs[component_key] = sdata.tables["table"].obs[component_key].fillna(-1)
            sdata.pl.render_shapes(elements="cells", color=component_key).pl.show(ax=ax, legend_loc=None)

    sdata.pl.render_shapes(
        element="clusters",
        color=component_key,
        fill_alpha=alpha_boundary,
    ).pl.show(ax=ax)

    if save is not None:
        plt.savefig(save, bbox_inches="tight")


def plot_shape_metrics(
    adata: AnnData,
    condition_key: str,
    condition_groups: list[str] | None = None,
    cluster_key: str | None = None,
    cluster_id: list[str] | None = None,
    component_key: str = "component",
    metrics: str | tuple[str] | list[str] = ("linearity", "curl"),
    figsize: tuple[float, float] = (8, 7),
    title: str | None = None,
) -> None:
    """
    Boxplots of the shape metrics between two conditions.

    Parameters
    ----------
    %(adata)s
    condition_key
        Key in :attr:`anndata.AnnData.obs` where the condition labels are stored.
    condition_groups
        List of two conditions to compare. If None, all pairwise comparisons are made.
    cluster_key
        Key in :attr:`anndata.AnnData.obs` where the cluster labels are stored. This is used to filter the clusters to plot.
    cluster_id
        List of clusters to plot. If None, all clusters are plotted.
    component_key
        Key in :attr:`anndata.AnnData.obs` where the component labels are stored.
    metrics
        List of metrics to plot. Available metrics are ``linearity``, ``curl``, ``elongation``, ``purity``.
    figsize
        Figure size.
    title
        Title of the plot.

    Returns
    -------
    %(plotting_returns)s
    """
    # Print warning and call shape_metrics
    warnings.warn(
        "plot_shape_metrics is deprecated and will be removed in the next release. "
        "Please use `shape_metrics` instead.",
        FutureWarning,
        stacklevel=2,
    )
    shape_metrics(
        adata=adata,
        condition_key=condition_key,
        condition_groups=condition_groups,
        cluster_key=cluster_key,
        cluster_id=cluster_id,
        component_key=component_key,
        metrics=metrics,
        figsize=figsize,
        title=title,
    )


@d.dedent
def shape_metrics(
    adata: AnnData,
    condition_key: str,
    condition_groups: list[str] | None = None,
    cluster_key: str | None = None,
    cluster_id: list[str] | None = None,
    component_key: str = "component",
    metrics: str | tuple[str] | list[str] = ("linearity", "curl"),
    fontsize: str | int = "small",
    figsize: tuple[float, float] = (8, 7),
    title: str | None = None,
) -> None:
    """
    Boxplots of the shape metrics between two conditions.

    Parameters
    ----------
    %(adata)s
    condition_key
        Key in :attr:`anndata.AnnData.obs` where the condition labels are stored.
    condition_groups
        List of two conditions to compare. If None, all pairwise comparisons are made.
    cluster_key
        Key in :attr:`anndata.AnnData.obs` where the cluster labels are stored. This is used to filter the clusters to plot.
    cluster_id
        List of clusters to plot. If None, all clusters are plotted.
    component_key
        Key in :attr:`anndata.AnnData.obs` where the component labels are stored.
    metrics
        List of metrics to plot. Available metrics are ``linearity``, ``curl``, ``elongation``, ``purity``.
    figsize
        Figure size.
    title
        Title of the plot.

    Returns
    -------
    %(plotting_returns)s
    """
    if isinstance(metrics, str):
        metrics = [metrics]
    elif isinstance(metrics, tuple):
        metrics = list(metrics)

    metrics_df = {metric: adata.uns[f"shape_{component_key}"][metric] for metric in metrics}
    metrics_df[condition_key] = (
        adata[~adata.obs[condition_key].isna()]
        .obs[[component_key, condition_key]]
        .drop_duplicates()
        .set_index(component_key)
        .to_dict()[condition_key]
    )

    metrics_df[cluster_key] = (
        adata[~adata.obs[condition_key].isna()]
        .obs[[component_key, cluster_key]]
        .drop_duplicates()
        .set_index(component_key)
        .to_dict()[cluster_key]
    )

    metrics_df = pd.DataFrame(metrics_df)
    if cluster_id is not None:
        metrics_df = metrics_df[metrics_df[cluster_key].isin(cluster_id)]

    metrics_df = pd.melt(
        metrics_df[metrics + [condition_key]],
        id_vars=[condition_key],
        var_name="metric",
    )

    conditions = (
        enumerate(combinations(adata.obs[condition_key].cat.categories, 2))
        if condition_groups is None
        else [condition_groups]
    )

    for condition1, condition2 in conditions:
        fig = plt.figure(figsize=figsize)
        metrics_condition_pair = metrics_df[metrics_df[condition_key].isin([condition1, condition2])]
        ax = sns.boxplot(
            data=metrics_condition_pair,
            x="metric",
            hue=condition_key,
            y="value",
            showfliers=False,
            hue_order=[condition1, condition2],
        )

        ax.tick_params(labelsize=fontsize)
        ax.set_xlabel(ax.get_xlabel(), fontsize=fontsize)
        ax.tick_params(labelsize=fontsize)
        ax.set_ylabel(ax.get_ylabel(), fontsize=fontsize)

        adjust_box_widths(fig, 0.9)

        ax = sns.stripplot(
            data=metrics_condition_pair,
            x="metric",
            hue=condition_key,
            y="value",
            color="0.08",
            size=4,
            jitter=0.13,
            dodge=True,
            hue_order=condition_groups if condition_groups else None,
        )
        handles, labels = ax.get_legend_handles_labels()
        plt.legend(
            handles[0 : len(metrics_condition_pair[condition_key].unique())],
            labels[0 : len(metrics_condition_pair[condition_key].unique())],
            bbox_to_anchor=(1.24, 1.02),
            fontsize=fontsize,
        )

        for count, metric in enumerate(["linearity", "curl"]):
            pvalue = ttest_ind(
                metrics_condition_pair[
                    (metrics_condition_pair[condition_key] == condition1) & (metrics_condition_pair["metric"] == metric)
                ]["value"],
                metrics_condition_pair[
                    (metrics_condition_pair[condition_key] == condition2) & (metrics_condition_pair["metric"] == metric)
                ]["value"],
            )[1]
            x1, x2 = count, count
            y, h, col = (
                metrics_condition_pair[(metrics_condition_pair["metric"] == metric)]["value"].max()
                + 0.02
                + 0.05 * count,
                0.01,
                "k",
            )
            plt.plot([x1 - 0.2, x1 - 0.2, x2 + 0.2, x2 + 0.2], [y, y + h, y + h, y], lw=1.5, c=col)
            if pvalue < 0.05:
                plt.text(
                    (x1 + x2) * 0.5,
                    y + h * 2,
                    f"p = {pvalue:.2e}",
                    ha="center",
                    va="bottom",
                    color=col,
                    fontdict={"fontsize": fontsize},
                )
            else:
                plt.text(
                    (x1 + x2) * 0.5,
                    y + h * 2,
                    "ns",
                    ha="center",
                    va="bottom",
                    color=col,
                    fontdict={"fontsize": fontsize},
                )
        if title is not None:
            plt.title(title, fontdict={"fontsize": fontsize})
        plt.show()


@d.dedent
def plot_neighborhood_connectivity(
    adata,
    cluster_key: str,
    component_key: str,
    cluster_id: list = None,
    condition_key: str = None,
    condition_groups: list = None,
    library_key: str = "library_id",
    figsize: tuple = (12, 6),
    title: str = None,
    save: Union[str, Path] = None,
    dpi: int = 600,
    show: bool = True,
    **kwargs,
) -> Union[plt.Axes, pd.DataFrame]:
    """
    Calculates and plots the fraction of cells from neighborhoods that are associated to
    a connected component and thereby gives an idea about neighborhood connectivity

    Parameters
    --------------------------------------------------------------------------------------
    adata : AnnData
        AnnData object
    cluster_key: str
        Key in adata.obs that contains the cellcharter cluster information
    component_key: str
        Key in adata.obs that contains the connected component information after running
        cc.gr.connected_components
    condition_groups: list
        List of condition groups in condition_key to plot
    condition_key: str
        Key in adata.obs that contains the condition information if users want to compared
        conditions
    library_key: str
        Key in adata.obs that contains the sample or image ID information
    cluster_id: list
        List of cluster IDs in cluster_key to plot
    figsize: tuple
        Figure size
    title: str
        Title of the plot
    show: bool
        If True, the plot will be shown and axes are always returned,
        if False, the function will return the result dataframe

    Additional keyword arguments (**kwargs) will be passed to sns.violinplot()

    Returns
    --------------------------------------------------------------------------------------
    Union[None, pd.DataFrame]
        If show=True, returns ax and displays the plot
        If show=False, returns the computed DataFrame

    Examples
    --------------------------------------------------------------------------------------
    cc.pl_neighborhood_connectivity(adata,
                                    cluster_key='cellcharter_CN',
                                    component_key='component',
                                    condition_key='disease',
                                    library_key='library_id'
                                    )
    """
    # Checking mandatory parameters
    if not isinstance(adata, ad.AnnData):
        raise ValueError("adata must be an AnnData object")
    if not isinstance(cluster_key, str) or cluster_key not in adata.obs:
        raise ValueError(f"cluster_key '{cluster_key}' not found in adata.obs")
    if not isinstance(component_key, str) or component_key not in adata.obs:
        raise ValueError(f"component_key '{component_key}' not found in adata.obs")

    # Create a dataframe using the component, condition and cluster keys
    components = pd.crosstab(
        index=adata.obs[cluster_key], columns=adata.obs[library_key], values=adata.obs[component_key], aggfunc="count"
    )

    # Create a dataframe with the total number of cells in each cluster per image/library key
    totals = pd.crosstab(index=adata.obs[cluster_key], columns=adata.obs[library_key])

    # Calculate the fraction of cells in a connected component and map the conditions to the dataframe
    result = np.divide(components, totals)
    result = result.T.reset_index()
    result = result.melt(id_vars=library_key, var_name=cluster_key, value_name="fraction_in_component")
    if condition_key:
        condition_mapping = adata.obs.groupby(library_key)[condition_key].first().to_dict()
        result["condition"] = result[library_key].map(condition_mapping)

    # Filter for specific cluster groups if provided
    if cluster_id:
        result = result[result[cluster_key].isin(cluster_id)]

    # Filter for specific condition groups if provided
    if condition_key and condition_groups:
        result = result[result["condition"].isin(condition_groups)]

    del components, totals
    # Create the violinplot if show=True
    if show:
        fig, ax = plt.subplots(figsize=figsize)
        plot_kwargs = {"data": result, "x": cluster_key, "y": "fraction_in_component", "ax": ax}

        if condition_key:
            plot_kwargs["hue"] = "condition"
        sns.violinplot(**plot_kwargs, **kwargs)
        ax.set_ylabel("Neighborhood Connectivity")
        ax.set_xlabel("")
        ax.tick_params(axis="x", rotation=90)

        if title:
            ax.set_title(title)

        plt.tight_layout()

        if save:
            plt.savefig(save, dpi=dpi, bbox_inches="tight")

        plt.show()
        return ax

    # Return the result dataframe if show=False
    else:
        return result
