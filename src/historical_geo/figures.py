"""Case-study figures and diagnostics for the public Crusader fixture."""
from __future__ import annotations
import hashlib,itertools,json
from pathlib import Path
from typing import Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from PIL import Image
from shapely.geometry import LineString,box,shape
from shapely.ops import transform as transform_geometry
from pyproj import Transformer
from historical_geo.attractors import _lines,align_shared_boundary
from historical_geo.render import COLORS
from historical_geo.research_case import reconstruct_research_case

def _read(path:Path)->dict[str,Any]: return json.loads(path.read_text())
def _geoms(path:Path)->dict[str,Any]:
 d=_read(path); return {f["properties"]["entity"]:shape(f["geometry"]) for f in d["features"]}
def _parts(g): return [g] if g.geom_type=="Polygon" else [x for x in getattr(g,"geoms",[]) if x.geom_type=="Polygon"]
def _plot_geom(ax,g,**kw):
 for p in _parts(g):
  x,y=p.exterior.xy; ax.fill(x,y,**kw)
def _plot_outline(ax,g,**kw):
 for p in _parts(g):
  x,y=p.exterior.xy; ax.plot(x,y,**kw)
def _setup(ax,bbox):
 ax.set_xlim(bbox[0],bbox[2]); ax.set_ylim(bbox[1],bbox[3]); ax.set_aspect("equal"); ax.grid(color="#dddddd",lw=.35); ax.set_xlabel("longitude"); ax.set_ylabel("latitude")
def _qa(path:Path)->dict[str,Any]:
 with Image.open(path) as im:
  rgb=im.convert("RGB"); colors=rgb.getcolors(maxcolors=rgb.width*rgb.height); n=len(colors) if colors is not None else 256
 return {"path":path.name,"bytes":path.stat().st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"unique_colors":n,"nonblank":n>8}
def _entity_colors(names): return {n:COLORS[i%len(COLORS)] for i,n in enumerate(sorted(names))}
def _natural(case):
 d=_read(case/"natural-features.geojson"); return {f["properties"]["feature_id"]:shape(f["geometry"]) for f in d["features"]}
def _land(case): return shape(_read(case/"land.geojson")["features"][0]["geometry"])
def _admitted_anchor_decisions(case):
 bundle=_read(case/"research-bundle.json")
 return [d for d in bundle["model_decisions"] if d["role"]=="control_point" and d["review_status"]=="admitted"]

def _anchors(case,out,bbox):
 decisions=_admitted_anchor_decisions(case)
 colors=_entity_colors({d["parameters"]["entity"] for d in decisions}); land=_land(case); natural=_natural(case)
 fig,axs=plt.subplots(1,2,figsize=(12,7),dpi=160,sharex=True,sharey=True)
 for ax,sl in zip(axs,(1130,1187)):
  _plot_geom(ax,land,facecolor="#f3efe3",edgecolor="#777",lw=.4)
  for fid in ("natural-earth:lebanon-mountains","natural-earth:taurus-mountains"):_plot_geom(ax,natural[fid],facecolor="#8c8c8c",edgecolor="none",alpha=.18)
  j=natural["natural-earth:jordan-river"]
  for line in _lines(j): ax.plot(*line.xy,color="#3977a8",lw=1)
  for d in [x for x in decisions if x["parameters"]["slice"]==sl]:
   p=d["parameters"]; x,y=p["coordinates"]; ax.scatter(x,y,s=38,c=colors[p["entity"]],edgecolor="white",linewidth=.55,zorder=4)
   ax.annotate(p["name"],(x,y),xytext=(3,3),textcoords="offset points",fontsize=6.5)
  ax.set_title(f"{sl if sl==1130 else 'End of 1187'} evidence-backed point anchors")
  _setup(ax,bbox)
 fig.suptitle("Point evidence only — locality coordinates are approximate")
 handles=[Patch(facecolor=colors[n],label=n) for n in sorted(colors)]
 fig.legend(handles=handles,loc="lower center",ncol=3,fontsize=7,frameon=True); fig.tight_layout(rect=(0,.08,1,.95))
 p=out/"evidence-anchors.png"; fig.savefig(p,bbox_inches="tight"); plt.close(fig); return p

def _recon(case,out,bbox):
 allg={sl:_geoms(case/"build"/f"run-{sl}"/"boundary-hypotheses.geojson") for sl in (1130,1187)}
 colors=_entity_colors(set().union(*[set(x) for x in allg.values()])); land=_land(case)
 fig,axs=plt.subplots(1,2,figsize=(12,7),dpi=160,sharex=True,sharey=True)
 for ax,sl in zip(axs,(1130,1187)):
  _plot_geom(ax,land,facecolor="#f2efe6",edgecolor="#888",lw=.35)
  for name,g in allg[sl].items(): _plot_geom(ax,g,facecolor=colors[name],edgecolor="#222",lw=.55,alpha=.72)
  ax.set_title(f"{sl if sl==1130 else 'End of 1187'} modeled surfaces"); _setup(ax,bbox)
 fig.suptitle("XTENT boundary hypotheses — not observed historical borders")
 handles=[Patch(facecolor=colors[n],edgecolor="#222",label=n,alpha=.72) for n in sorted(colors)]
 fig.legend(handles=handles,loc="lower center",ncol=3,fontsize=7); fig.tight_layout(rect=(0,.09,1,.95))
 p=out/"reconstruction-slices.png"; fig.savefig(p,bbox_inches="tight"); plt.close(fig); return p

def _ablation(case,out,bbox):
 natural=_natural(case); all_names=set(); runs={}
 for sl in (1130,1187):
  runs[(sl,"baseline")]=_geoms(case/"build"/f"run-{sl}"/"boundary-hypotheses.geojson")
  runs[(sl,"flat")]=_geoms(case/"build"/f"run-{sl}-flat-natural"/"boundary-hypotheses.geojson")
  all_names |= set(runs[(sl,"baseline")])|set(runs[(sl,"flat")])
 colors=_entity_colors(all_names); fig,axs=plt.subplots(2,2,figsize=(11,10),dpi=160,sharex=True,sharey=True)
 for row,sl in enumerate((1130,1187)):
  for col,sc in enumerate(("flat","baseline")):
   ax=axs[row,col]
   for n,g in runs[(sl,sc)].items(): _plot_geom(ax,g,facecolor=colors[n],edgecolor="#222",lw=.4,alpha=.7)
   if sc=="baseline":
    for fid in ("natural-earth:lebanon-mountains","natural-earth:taurus-mountains"):_plot_outline(ax,natural[fid],color="#4d4036",lw=1)
   ax.set_title(f"{sl} — {'no natural barriers' if sc=='flat' else 'assumed bounded friction'}"); _setup(ax,bbox)
 fig.suptitle("Natural-feature ablation — geometry is data; friction strength is an assumption")
 fig.tight_layout(rect=(0,0,1,.96)); p=out/"natural-ablation.png"; fig.savefig(p,bbox_inches="tight"); plt.close(fig)
 tf=Transformer.from_crs("EPSG:4326","ESRI:102025",always_xy=True)
 report={"area_crs":"ESRI:102025","interpretation":"Symmetric-difference area measures model sensitivity, not historical accuracy.","slices":{}}
 for sl in (1130,1187):
  row={}
  for name in sorted(runs[(sl,"baseline")]):
   a=transform_geometry(tf.transform,runs[(sl,"baseline")][name]); b=transform_geometry(tf.transform,runs[(sl,"flat")][name])
   row[name]={"baseline_area_km2":round(a.area/1e6,1),"flat_area_km2":round(b.area/1e6,1),"symmetric_difference_km2":round(a.symmetric_difference(b).area/1e6,1)}
  report["slices"][str(sl)]=row
 (out/"natural-ablation.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); return p,report

def _attractors(case,out,bbox):
 before={"West":box(0,0,5,6),"East":box(5,0,10,6)}; synth_line=LineString([(5.2,-1),(5.2,7)]); synth=align_shared_boundary(before,synth_line,max_distance=.5,max_area_change=.1)
 geoms=_geoms(case/"build/run-1130/boundary-hypotheses.geojson"); jordan=max(_lines(_natural(case)["natural-earth:jordan-river"]),key=lambda x:x.length)
 candidates=[]
 for a,b in itertools.combinations(sorted(geoms),2):
  shared=geoms[a].boundary.intersection(geoms[b].boundary)
  if not shared.is_empty and shared.length>0: candidates.append((shared.distance(jordan),a,b))
 _,a,b=min(candidates); real=align_shared_boundary({a:geoms[a],b:geoms[b]},jordan,max_distance=.1,min_direction_similarity=.8,max_area_change=.05)
 fig,axs=plt.subplots(1,2,figsize=(12,5.8),dpi=160)
 for n,g in synth.geometries.items(): _plot_geom(axs[0],g,facecolor="#4C78A8" if n=="West" else "#F58518",edgecolor="#222",alpha=.65)
 axs[0].plot(*synth_line.xy,color="#2457a5",lw=2); axs[0].set_xlim(0,10); axs[0].set_ylim(0,6); axs[0].set_aspect("equal"); axs[0].set_title("Synthetic candidate: accepted\n(topology and area guards pass)")
 colors=_entity_colors([a,b]);
 for n in (a,b): _plot_geom(axs[1],geoms[n],facecolor=colors[n],edgecolor="#222",alpha=.65)
 axs[1].plot(*jordan.xy,color="#2457a5",lw=2,label="Jordan River candidate"); _setup(axs[1],bbox); axs[1].set_title(f"Real candidate: rejected ({real.reason})\nno geometry mutation")
 fig.suptitle("Guarded boundary-attractor diagnostics"); fig.tight_layout(rect=(0,0,1,.94)); p=out/"boundary-attractor-diagnostics.png"; fig.savefig(p,bbox_inches="tight"); plt.close(fig)
 report={"synthetic":{"accepted":synth.accepted,"reason":synth.reason,"distance":synth.distance,"direction_similarity":synth.direction_similarity,"max_area_change":synth.max_area_change},"real_jordan_candidate":{"entities":[a,b],"accepted":real.accepted,"reason":real.reason,"max_distance_degrees":.1,"minimum_direction_similarity":.8,"distance_degrees":real.distance,"direction_similarity":real.direction_similarity,"max_area_change":real.max_area_change,"geometry_mutated":real.accepted},"interpretation":"The real feature is context, not evidence of a historical boundary. Rejection preserves the baseline surfaces."}
 (out/"boundary-attractor-diagnostics.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); return p,report

def build_case_figures(case_dir:Path)->Path:
 case=case_dir.resolve(); out=case/"figures"; out.mkdir(parents=True,exist_ok=True); bbox=_read(case/"case.json")["grid"]["bbox"]
 from historical_geo.evaluation import build_research_evaluation
 frozen_evaluation_paths=build_research_evaluation(case)
 for sl in (1130,1187):
  reconstruct_research_case(case,sl,scenario="reviewed-baseline"); reconstruct_research_case(case,sl,scenario="flat-natural")
 paths=[_anchors(case,out,bbox),_recon(case,out,bbox)]; ab,abr=_ablation(case,out,bbox); at,atr=_attractors(case,out,bbox); paths += [ab,at]
 paths += frozen_evaluation_paths
 qa={"figures":[_qa(p) for p in paths],"all_nonblank":all(_qa(p)["nonblank"] for p in paths),"natural_ablation_report":"natural-ablation.json","attractor_report":"boundary-attractor-diagnostics.json","reference_comparison_report":"reference-comparison.json","uncertainty_report":"uncertainty-zones.json"}
 (out/"figure-qa.json").write_text(json.dumps(qa,indent=2,sort_keys=True)+"\n")
 return out
