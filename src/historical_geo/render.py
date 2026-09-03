"""One intentionally small static renderer for boundary hypotheses."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from PIL import Image
from shapely.geometry import shape

COLORS = ["#4C78A8", "#F58518", "#54A24B", "#E45756", "#72B7B2", "#B279A2", "#FF9DA6", "#9D755D"]


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render_surface(run_dir: Path, title: str | None = None) -> Path:
    run_dir = run_dir.resolve()
    surface_path = run_dir / "boundary-hypotheses.geojson"
    data = json.loads(surface_path.read_text(encoding="utf-8"))
    features = data.get("features", [])
    if not features:
        raise ValueError("cannot render an empty surface")
    if any(x.get("properties", {}).get("model_label") != "boundary_hypothesis" for x in features):
        raise ValueError("renderer accepts boundary_hypothesis features only")

    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    handles = []
    bounds = []
    for index, feature in enumerate(sorted(features, key=lambda x: x["properties"]["entity"])):
        geom = shape(feature["geometry"])
        color = COLORS[index % len(COLORS)]
        for polygon in ([geom] if geom.geom_type == "Polygon" else list(geom.geoms)):
            x, y = polygon.exterior.xy
            ax.fill(x, y, facecolor=color, edgecolor="#202020", linewidth=0.8, alpha=0.72)
        bounds.append(geom.bounds)
        handles.append(Patch(facecolor=color, edgecolor="#202020", label=feature["properties"]["entity"], alpha=0.72))
    minx=min(x[0] for x in bounds); miny=min(x[1] for x in bounds)
    maxx=max(x[2] for x in bounds); maxy=max(x[3] for x in bounds)
    padx=max((maxx-minx)*0.05,0.1); pady=max((maxy-miny)*0.05,0.1)
    ax.set_xlim(minx-padx,maxx+padx); ax.set_ylim(miny-pady,maxy+pady)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title(title or "Modeled territorial surfaces — not historical borders")
    ax.legend(handles=handles, loc="upper right", frameon=True)
    ax.set_xlabel("longitude / synthetic x")
    ax.set_ylabel("latitude / synthetic y")
    ax.grid(color="#dddddd", linewidth=0.4)
    fig.tight_layout()
    output = run_dir / "boundary-hypotheses.png"
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)

    with Image.open(output) as image:
        rgb = image.convert("RGB")
        colors = rgb.getcolors(maxcolors=rgb.width * rgb.height)
        unique_colors = len(colors) if colors is not None else 256
        nonblank = unique_colors > 8
    qa = {
        "nonblank": nonblank,
        "unique_colors": unique_colors,
        "feature_count": len(features),
        "model_labels": sorted({x["properties"]["model_label"] for x in features}),
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    }
    _write_json(run_dir / "render-qa.json", qa)
    if not nonblank:
        raise ValueError("render QA failed: image appears blank")
    return output
