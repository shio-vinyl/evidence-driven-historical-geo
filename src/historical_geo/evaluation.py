"""External-reference and scenario-agreement evaluation for the public case."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pyproj import Transformer
from rasterio.features import rasterize, shapes
from shapely import union_all
from shapely.geometry import mapping, shape
from shapely.ops import transform as transform_geometry

from historical_geo import xtent
from historical_geo.pipeline import _geometry_to_grid_crs, _read_feature_collection, reconstruct, run_directory

EVIDENCE_SCENARIOS = ("verified-only", "reviewed-baseline", "inclusive")
MODEL_SCENARIOS = (
    "reviewed-baseline", "flat-natural", "projection-normal",
    "projection-expansive", "grid-5km", "grid-20km",
)
ALL_SCENARIOS = tuple(dict.fromkeys((*EVIDENCE_SCENARIOS, *MODEL_SCENARIOS)))
ZONE_LABELS = {1: "stable_core", 2: "model_sensitive_zone", 3: "evidence_sensitive_zone", 4: "unresolved_zone"}
ZONE_COLORS = {1: "#3B7A57", 2: "#E69F00", 3: "#7B61A8", 4: "#B94A48"}


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _surface(case: Path, slice_value: int, scenario: str) -> dict[str, Any]:
    return _read(run_directory(case, slice_value, scenario) / "boundary-hypotheses.geojson")


def _model_facts(case: Path, slice_value: int) -> dict[str, Any]:
    run = run_directory(case, slice_value, "reviewed-baseline")
    effective = _read(run / "effective-solver-input.json")
    city_control = {x["parameters"]["name"]: x["parameters"]["entity"] for x in effective["seeds"]}
    surface = _surface(case, slice_value, "reviewed-baseline")
    geoms = {x["properties"]["entity"]: shape(x["geometry"]) for x in surface["features"]}
    adjacencies = []
    names = sorted(geoms)
    for i, left in enumerate(names):
        for right in names[i + 1:]:
            shared = geoms[left].boundary.intersection(geoms[right].boundary)
            if not shared.is_empty and shared.length > 1e-8:
                adjacencies.append([left, right])
    return {"entities": sorted(geoms), "city_control": city_control, "adjacencies": adjacencies}


def build_reference_comparison(case_dir: Path) -> tuple[Path, dict[str, Any]]:
    case = case_dir.resolve(); out = case / "figures"
    register = _read(case / "reference-map-register.json")
    aliases = register["ontology_harmonization"]["entities"]
    report: dict[str, Any] = {
        "interpretation": "Categorical agreement with external cartography; no reference is ground truth and no value is a historical accuracy score.",
        "boundary_metrics_computed": False,
        "parameter_tuning_from_references": False,
        "slices": {},
    }
    rows_for_plot = []
    for slice_value in (1130, 1187):
        model = _model_facts(case, slice_value)
        model_adj = {tuple(sorted(x)) for x in model["adjacencies"]}
        slice_rows = []
        for ref in register["maps"]:
            target = ref["target_slice"]
            if not (target == slice_value or (slice_value == 1187 and target == "end_of_year_1187")):
                continue
            observations = ref.get("observations")
            if not observations:
                slice_rows.append({
                    "reference_id": ref["reference_id"], "comparison_status": "rights_or_access_blocked",
                    "date_alignment": ref["date_alignment"], "city_control": {"expressed": 0, "matched": 0, "reference_only": 0, "different": 0},
                    "entities": {"expressed": 0, "matched": 0, "reference_only": 0},
                    "adjacencies": {"expressed": 0, "matched": 0, "reference_only": 0},
                })
                continue
            city_rows=[]
            for city, raw_entity in observations.get("city_control", {}).items():
                ref_entity=aliases.get(raw_entity, raw_entity); model_entity=model["city_control"].get(city)
                status="matched" if model_entity==ref_entity else ("reference_only" if model_entity is None else "different")
                city_rows.append({"city":city,"reference_entity":ref_entity,"model_entity":model_entity,"status":status})
            ref_entities=[aliases.get(x,x) for x in observations.get("entities",[])]
            entity_rows=[{"entity":x,"status":"matched" if x in model["entities"] else "reference_only"} for x in ref_entities]
            adj_rows=[]
            for pair in observations.get("adjacencies",[]):
                normalized=tuple(sorted(aliases.get(x,x) for x in pair))
                adj_rows.append({"entities":list(normalized),"status":"matched" if normalized in model_adj else "reference_only"})
            row={
                "reference_id":ref["reference_id"],"comparison_status":"qualitative_compared","date_alignment":ref["date_alignment"],
                "city_control":{"expressed":len(city_rows),"matched":sum(x['status']=='matched' for x in city_rows),"reference_only":sum(x['status']=='reference_only' for x in city_rows),"different":sum(x['status']=='different' for x in city_rows),"items":city_rows},
                "entities":{"expressed":len(entity_rows),"matched":sum(x['status']=='matched' for x in entity_rows),"reference_only":sum(x['status']=='reference_only' for x in entity_rows),"items":entity_rows},
                "adjacencies":{"expressed":len(adj_rows),"matched":sum(x['status']=='matched' for x in adj_rows),"reference_only":sum(x['status']=='reference_only' for x in adj_rows),"items":adj_rows},
                "coastal_sequence":{"expressed":observations.get('coastal_sequence',[]),"method":"ordered named-place context only; no continuous coast polygon inferred"},
            }
            slice_rows.append(row); rows_for_plot.append((slice_value,row))
        report["slices"][str(slice_value)]={"reviewed_baseline":model,"references":slice_rows}
    report["interpretive_zones"]={
        "1130":{"stable_core":"Jerusalem, Damascus, Tripoli, Antioch, and Edessa are present in the reviewed baseline and the c.1140 comparator.","reference_only":"Shepherd depicts Fatimid Ascalon and Tortosa; both are reserved for the inclusive scenario.","periphery":"The atlas's continuous fills and desert edges are too generalized for line comparison."},
        "1187":{"stable_core":"The compared works retain an Ayyubid domain and Latin centers at Tyre, Tripoli, and Antioch.","reference_only":"Johnston assigns Jaffa to the 1187 conquest sequence; the reviewed baseline omits it because the textual page check remains unresolved.","periphery":"Neither c.1190 plate is treated as an end-of-year 1187 boundary."}
    }
    _write(out / "reference-comparison.json", report)

    fig, axes = plt.subplots(1, 2, figsize=(12, 6.4), dpi=160)
    for ax, slice_value in zip(axes, (1130,1187)):
        compared=[r for sl,r in rows_for_plot if sl==slice_value]
        y=np.arange(len(compared)); labels=[r['reference_id'].replace('_','\n',1) for r in compared]
        match=[]; gap=[]; total=[]
        for r in compared:
            m=r['city_control']['matched']+r['entities']['matched']+r['adjacencies']['matched']
            g=r['city_control']['reference_only']+r['city_control']['different']+r['entities']['reference_only']+r['adjacencies']['reference_only']
            match.append(m); gap.append(g); total.append(m+g)
        ax.barh(y,match,color='#3B7A57',label='categorical agreement')
        ax.barh(y,gap,left=match,color='#B94A48',label='reference-only / different')
        for yy,(m,g) in enumerate(zip(match,gap)): ax.text(m+g+.1,yy,f'{m}/{m+g}',va='center',fontsize=8)
        ax.set_yticks(y,labels,fontsize=7); ax.invert_yaxis(); ax.set_xlabel('expressed city, entity, and adjacency assertions'); ax.set_title(str(slice_value))
        ax.grid(axis='x',alpha=.25)
    handles,labels=axes[0].get_legend_handles_labels(); fig.legend(handles,labels,loc='lower center',ncol=2)
    fig.suptitle('External map comparison — categorical assertions, no boundary accuracy score')
    fig.tight_layout(rect=(0,.08,1,.94)); path=out/'reference-comparison.png'; fig.savefig(path,bbox_inches='tight'); plt.close(fig)
    return path, report


def _modal(stack: np.ndarray, max_code: int) -> tuple[np.ndarray, np.ndarray]:
    counts=np.stack([(stack==code).sum(axis=0) for code in range(max_code+1)])
    mode=counts.argmax(axis=0); agreement=counts.max(axis=0)/stack.shape[0]
    return mode, agreement


def _zone_geometries(zone: np.ndarray, grid: xtent.Grid) -> dict[int, Any]:
    result={}
    for value in ZONE_LABELS:
        geoms=[shape(g) for g,v in shapes(zone.astype('uint8'),mask=zone==value,transform=grid.transform) if int(v)==value]
        result[value]=union_all(geoms) if geoms else None
    return result


def build_uncertainty_analysis(case_dir: Path) -> tuple[Path, dict[str, Any]]:
    case=case_dir.resolve(); out=case/'figures'; cfg=_read(case/'case.json')['grid']
    analysis_grid=xtent.build_grid(tuple(cfg['bbox']),10000,str(cfg['crs']))
    land=union_all([_geometry_to_grid_crs(shape(x['geometry']),analysis_grid.crs) for x in _read_feature_collection(case/cfg['land_path'])])
    land_mask=xtent.rasterize_geom(analysis_grid,land).astype(bool)
    all_entities=sorted({f['properties']['entity'] for sl in (1130,1187) for sc in ALL_SCENARIOS for f in _surface(case,sl,sc)['features']})
    codes={name:i+1 for i,name in enumerate(all_entities)}
    inverse={v:k for k,v in codes.items()}
    report={
        'interpretation':'Agreement across the declared scenario set. It is not a probability, confidence interval, or historical truth surface.',
        'analysis_grid_resolution_m':10000,
        'evidence_scenarios':list(EVIDENCE_SCENARIOS),'model_scenarios':list(MODEL_SCENARIOS),
        'classification_rule':{
            'stable_core':'Evidence and model scenario groups are each unanimous on the same non-zero entity.',
            'model_sensitive_zone':'Evidence scenarios are unanimous; model scenarios are not.',
            'evidence_sensitive_zone':'Model scenarios are unanimous; evidence scenarios are not.',
            'unresolved_zone':'Both groups vary, they disagree despite internal unanimity, or assignment appears in only one group.'
        },'slices':{}
    }
    fig,axes=plt.subplots(1,2,figsize=(12,7),dpi=160)
    inverse_tf=Transformer.from_crs(analysis_grid.crs,'EPSG:4326',always_xy=True)
    for ax,sl in zip(axes,(1130,1187)):
        arrays={}
        for sc in ALL_SCENARIOS:
            items=[]
            for f in _surface(case,sl,sc)['features']:
                geom=_geometry_to_grid_crs(shape(f['geometry']),analysis_grid.crs)
                items.append((mapping(geom),codes[f['properties']['entity']]))
            arrays[sc]=rasterize(items,out_shape=analysis_grid.shape,transform=analysis_grid.transform,fill=0,dtype='int16')
        estack=np.stack([arrays[x] for x in EVIDENCE_SCENARIOS]); mstack=np.stack([arrays[x] for x in MODEL_SCENARIOS])
        emode,eagree=_modal(estack,len(codes)); mmode,magree=_modal(mstack,len(codes))
        any_assignment=((estack!=0).any(axis=0)|(mstack!=0).any(axis=0))&land_mask
        zone=np.zeros(analysis_grid.shape,dtype='uint8')
        stable=any_assignment&(eagree==1)&(magree==1)&(emode==mmode)&(emode!=0)
        evidence_sensitive=any_assignment&(eagree<1)&(magree==1)&~stable
        model_sensitive=any_assignment&(eagree==1)&(magree<1)&~stable
        unresolved=any_assignment&~stable&~evidence_sensitive&~model_sensitive
        zone[stable]=1;zone[model_sensitive]=2;zone[evidence_sensitive]=3;zone[unresolved]=4
        assessed=int(any_assignment.sum()); cell_area=100.0
        metrics={ZONE_LABELS[v]:{'cells':int((zone==v).sum()),'area_km2':round(int((zone==v).sum())*cell_area,1),'percent_of_assessed':round(100*int((zone==v).sum())/assessed,2) if assessed else 0} for v in ZONE_LABELS}
        metrics['outside_modeled']={'land_cells':int((land_mask&~any_assignment).sum()),'area_km2':round(int((land_mask&~any_assignment).sum())*cell_area,1)}
        metrics['mean_evidence_agreement']=round(float(eagree[any_assignment].mean()),4) if assessed else 0
        metrics['mean_model_agreement']=round(float(magree[any_assignment].mean()),4) if assessed else 0
        report['slices'][str(sl)]=metrics
        zone_geoms=_zone_geometries(zone,analysis_grid)
        land_wgs=transform_geometry(inverse_tf.transform,land)
        x,y=land_wgs.exterior.xy if land_wgs.geom_type=='Polygon' else ([],[])
        for value,g in zone_geoms.items():
            if g is None: continue
            wgs=transform_geometry(inverse_tf.transform,g)
            parts=[wgs] if wgs.geom_type=='Polygon' else list(wgs.geoms)
            for part in parts:
                xx,yy=part.exterior.xy;ax.fill(xx,yy,color=ZONE_COLORS[value],alpha=.82,lw=0)
        parts=[land_wgs] if land_wgs.geom_type=='Polygon' else list(land_wgs.geoms)
        for part in parts:
            xx,yy=part.exterior.xy;ax.plot(xx,yy,color='#555',lw=.45)
        ax.set_xlim(cfg['bbox'][0],cfg['bbox'][2]);ax.set_ylim(cfg['bbox'][1],cfg['bbox'][3]);ax.set_aspect('equal');ax.set_title(str(sl));ax.set_xlabel('longitude');ax.set_ylabel('latitude');ax.grid(alpha=.2,lw=.4)
    from matplotlib.patches import Patch
    handles=[Patch(facecolor=ZONE_COLORS[k],label=ZONE_LABELS[k].replace('_',' ')) for k in ZONE_LABELS]
    fig.legend(handles=handles,loc='lower center',ncol=2,fontsize=8)
    fig.suptitle('Scenario agreement zones — consistency within this scenario set, not probability')
    fig.tight_layout(rect=(0,.1,1,.94));path=out/'uncertainty-zones.png';fig.savefig(path,bbox_inches='tight');plt.close(fig)
    _write(out/'uncertainty-zones.json',report)
    return path,report


def build_research_evaluation(case_dir: Path) -> list[Path]:
    case=case_dir.resolve()
    for sl in (1130,1187):
        for scenario in ALL_SCENARIOS:
            reconstruct(case,sl,scenario=scenario)
    reference,_=build_reference_comparison(case)
    uncertainty,_=build_uncertainty_analysis(case)
    return [reference,uncertainty]
