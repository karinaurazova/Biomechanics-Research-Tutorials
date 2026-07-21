#!/usr/bin/env python3
"""Regenerate Tutorial 20 outputs."""
from __future__ import annotations
import csv, json, sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

def _find_repository_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "src").exists():
            return candidate
    raise RuntimeError("Could not find repository root.")

TUTORIAL_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = _find_repository_root(TUTORIAL_DIR)
SOURCE_DIRECTORY = REPOSITORY_ROOT / "src"
if str(SOURCE_DIRECTORY) not in sys.path: sys.path.insert(0, str(SOURCE_DIRECTORY))
from biomechanics_tutorials.multimodal_benchmark import PARAMETER_NAMES, PipelineResult, axial_difference, recover_structure, run_full_benchmark  # noqa: E402
DATA_DIR = TUTORIAL_DIR / "data"; FIG_DIR = TUTORIAL_DIR / "figures"
DATA_DIR.mkdir(exist_ok=True); FIG_DIR.mkdir(exist_ok=True)

def save_csv(path: Path, rows: list[dict[str, object]]) -> None:
    keys=[]
    for row in rows:
        for key in row:
            if key not in keys: keys.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer=csv.DictWriter(handle, fieldnames=keys); writer.writeheader(); writer.writerows(rows)

def save_fig(fig: plt.Figure, name: str, language: str) -> None:
    fig.savefig(FIG_DIR / f"{name}{'_ru' if language == 'ru' else ''}.png", dpi=160, bbox_inches="tight"); plt.close(fig)

def labels(language: str) -> dict[str,str]:
    en={"pipeline":"End-to-end verification-ready pipeline","ground":"Ground-truth microstructure","modalities":"Synthetic modalities","segmentation":"Segmentation masks","orientation":"Orientation recovery","mechanics":"Mechanics and DIC-like observations","inverse":"Inverse parameter identification","budget":"Stage-wise error budget"}
    ru={"pipeline":"Сквозной verification-ready pipeline","ground":"Истинная микроструктура","modalities":"Синтетические модальности","segmentation":"Маски сегментации","orientation":"Восстановление ориентаций","mechanics":"Механика и DIC-like наблюдения","inverse":"Обратная идентификация параметров","budget":"Поэтапный бюджет ошибок"}
    return ru if language == "ru" else en

def plot_pipeline(result: PipelineResult, language: str) -> None:
    t=labels(language); fig, ax = plt.subplots(figsize=(10,5.8)); ax.axis("off")
    names = ["Ground truth","Изображения","Сегментация","Структура","Механика","DIC-поля","Параметры"] if language == "ru" else ["Ground truth","Synthetic images","Segmentation","Structure","Mechanics","DIC fields","Parameters"]
    xs=np.linspace(0.07,0.93,len(names))
    for i,(x,n) in enumerate(zip(xs,names)):
        ax.text(x,0.55,n,ha="center",va="center",fontsize=9,bbox={"boxstyle":"round,pad=0.45","fc":"white","ec":"0.35"})
        if i < len(names)-1: ax.annotate("",xy=(xs[i+1]-0.06,0.55),xytext=(x+0.06,0.55),arrowprops={"arrowstyle":"->","lw":1.5})
    ax.text(0.5,0.85,t["pipeline"],ha="center",fontsize=15,weight="bold"); ax.text(0.5,0.22,"All hidden quantities are known" if language == "en" else "Все скрытые величины известны",ha="center",fontsize=10)
    save_fig(fig,"pipeline_overview",language)

def plot_ground(result: PipelineResult, language: str) -> None:
    t=labels(language); truth=result.truth
    fields=[truth.fiber_mask,truth.pore_mask,np.rad2deg(truth.theta),truth.kappa,truth.rho_f,truth.connectivity]
    names=["Маска волокон","Поры","Ориентация, град","Kappa","Доля волокон","Связность"] if language == "ru" else ["Fiber mask","Pores","Orientation, deg","Kappa","Fiber fraction","Connectivity"]
    fig,axes=plt.subplots(2,3,figsize=(10.6,7.2),constrained_layout=True)
    for ax,field,title in zip(axes.ravel(),fields,names):
        im=ax.imshow(field,origin="lower"); ax.set_title(title,fontsize=10); ax.set_xticks([]); ax.set_yticks([]); fig.colorbar(im,ax=ax,shrink=0.75)
    fig.suptitle(t["ground"],fontsize=15,weight="bold"); save_fig(fig,"ground_truth_fields",language)

def plot_modalities(result: PipelineResult, language: str) -> None:
    t=labels(language); mod=result.modalities
    fields=[mod.sem_like,mod.polarization_intensity,np.rad2deg(mod.polarization_angle),mod.fluorescence_like,mod.dic_reference]
    names=["СЭМ-подобное","Поляризационная интенсивность","Поляризационный угол","Флуоресценция","DIC-текстура"] if language == "ru" else ["SEM-like","Polarization intensity","Polarization angle","Fluorescence-like","DIC texture"]
    fig,axes=plt.subplots(2,3,figsize=(10.6,7.2),constrained_layout=True)
    for ax in axes.ravel(): ax.axis("off")
    for ax,field,title in zip(axes.ravel(),fields,names):
        im=ax.imshow(field,origin="lower"); ax.set_title(title,fontsize=10); fig.colorbar(im,ax=ax,shrink=0.75)
    fig.suptitle(t["modalities"],fontsize=15,weight="bold"); save_fig(fig,"synthetic_modalities",language)

def plot_segmentation(result: PipelineResult, language: str) -> None:
    t=labels(language); keys=["ground_truth","sem_otsu","sem_adaptive","fluorescence_otsu","polarization_otsu","multimodal_fusion"]
    names=["Истина","СЭМ Otsu","СЭМ adaptive","Флуоресценция","Поляризация","Fusion"] if language == "ru" else ["Truth","SEM Otsu","SEM adaptive","Fluorescence","Polarization","Fusion"]
    fig,axes=plt.subplots(2,3,figsize=(10.6,7.2),constrained_layout=True)
    for ax,key,title in zip(axes.ravel(),keys,names):
        ax.imshow(result.masks[key],origin="lower"); ax.set_title(title,fontsize=10); ax.set_xticks([]); ax.set_yticks([])
    fig.suptitle(t["segmentation"],fontsize=15,weight="bold"); save_fig(fig,"segmentation_results",language)

def plot_orientation(result: PipelineResult, language: str) -> None:
    t=labels(language); fields,_=recover_structure(result.truth,result.modalities,result.masks)
    error=np.rad2deg(np.abs(axial_difference(fields["fusion_theta"],result.truth.theta))) * result.truth.tissue_mask
    panels=[np.rad2deg(result.truth.theta),np.rad2deg(fields["fusion_theta"]),error]
    names=["Истинная ориентация","Fusion-ориентация","Абсолютная ошибка, град"] if language == "ru" else ["True orientation","Fusion orientation","Absolute error, deg"]
    fig,axes=plt.subplots(1,3,figsize=(11.4,4.5),constrained_layout=True)
    for ax,panel,title in zip(axes,panels,names):
        im=ax.imshow(panel,origin="lower"); ax.set_title(title,fontsize=10); ax.set_xticks([]); ax.set_yticks([]); fig.colorbar(im,ax=ax,shrink=0.78)
    fig.suptitle(t["orientation"],fontsize=15,weight="bold"); save_fig(fig,"orientation_recovery",language)

def plot_mechanics(result: PipelineResult, language: str) -> None:
    t=labels(language); case=result.load_cases[0]
    panels=[case.exx_true,case.exx_dic-case.exx_true,case.gxy_true]
    names=["Истинное exx","Ошибка DIC exx","Истинное gamma_xy","Измеренный вектор силы"] if language == "ru" else ["True exx","DIC exx error","True gamma_xy","Observed force vector"]
    fig,axes=plt.subplots(2,2,figsize=(10.2,7.0),constrained_layout=True)
    for ax,panel,title in zip(axes.ravel()[:3],panels,names[:3]):
        im=ax.imshow(panel,origin="lower"); ax.set_title(title,fontsize=10); ax.set_xticks([]); ax.set_yticks([]); fig.colorbar(im,ax=ax,shrink=0.75)
    ax=axes.ravel()[3]; ax.bar(["sxx","syy","sxy"],case.force_observed); ax.set_title(names[3],fontsize=10); ax.set_ylabel("stress-like force" if language == "en" else "сила / напряжение")
    fig.suptitle(t["mechanics"],fontsize=15,weight="bold"); save_fig(fig,"mechanics_and_dic",language)

def plot_inverse(result: PipelineResult, language: str) -> None:
    t=labels(language); x=np.arange(len(PARAMETER_NAMES)); width=0.16; fig,ax=plt.subplots(figsize=(11.2,6.0))
    ax.bar(x-2*width,result.truth.parameters,width,label="truth" if language == "en" else "истина")
    for j,row in enumerate(result.parameter_results):
        vals=[float(row[f"{name}_estimated"]) for name in PARAMETER_NAMES]; ax.bar(x+(j-1)*width,vals,width,label=str(row["scenario"]).replace("_"," "))
    ax.set_xticks(x); ax.set_xticklabels(PARAMETER_NAMES,rotation=20,ha="right"); ax.set_ylabel("parameter value" if language == "en" else "значение параметра"); ax.set_title(t["inverse"],fontsize=15,weight="bold"); ax.legend(fontsize=8,ncols=2)
    save_fig(fig,"inverse_parameter_recovery",language)

def plot_budget(result: PipelineResult, language: str) -> None:
    t=labels(language); stages=[str(r["stage"]) for r in result.error_budget]; values=[float(r["value"]) for r in result.error_budget]
    fig,ax=plt.subplots(figsize=(9.2,5.8)); ax.bar(stages,values); ax.set_title(t["budget"],fontsize=15,weight="bold"); ax.set_ylabel("metric value" if language == "en" else "значение метрики"); ax.tick_params(axis="x",rotation=15)
    for i,val in enumerate(values): ax.text(i,val,f"{val:.3g}",ha="center",va="bottom")
    save_fig(fig,"end_to_end_error_budget",language)

def save_outputs(result: PipelineResult) -> None:
    save_csv(DATA_DIR/"segmentation_metrics.csv",result.segmentation_metrics); save_csv(DATA_DIR/"orientation_metrics.csv",result.orientation_metrics); save_csv(DATA_DIR/"parameter_recovery.csv",result.parameter_results); save_csv(DATA_DIR/"error_budget.csv",result.error_budget)
    save_csv(DATA_DIR/"load_cases.csv", [{"case":c.name,"force_true_xx":c.force_true[0],"force_true_yy":c.force_true[1],"force_true_xy":c.force_true[2],"force_observed_xx":c.force_observed[0],"force_observed_yy":c.force_observed[1],"force_observed_xy":c.force_observed[2]} for c in result.load_cases])
    np.savez_compressed(DATA_DIR/"multimodal_benchmark_dataset.npz", fiber_mask=result.truth.fiber_mask,pore_mask=result.truth.pore_mask,tissue_mask=result.truth.tissue_mask,theta=result.truth.theta,kappa=result.truth.kappa,rho_f=result.truth.rho_f,connectivity=result.truth.connectivity,true_parameters=result.truth.parameters,sem_like=result.modalities.sem_like,polarization_intensity=result.modalities.polarization_intensity,polarization_angle=result.modalities.polarization_angle,fluorescence_like=result.modalities.fluorescence_like,dic_reference=result.modalities.dic_reference)
    summary={"tutorial":20,"name":"Multimodal Verification-Ready Synthetic Benchmark","n_segmentation_methods":len(result.segmentation_metrics),"n_orientation_methods":len(result.orientation_metrics),"n_parameter_scenarios":len(result.parameter_results),"best_dice":max(float(r["dice"]) for r in result.segmentation_metrics),"best_parameter_error":min(float(r["relative_parameter_error"]) for r in result.parameter_results)}
    (DATA_DIR/"benchmark_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")

def main() -> None:
    result=run_full_benchmark(seed=20); save_outputs(result)
    for language in ["en","ru"]:
        plot_pipeline(result,language); plot_ground(result,language); plot_modalities(result,language); plot_segmentation(result,language); plot_orientation(result,language); plot_mechanics(result,language); plot_inverse(result,language); plot_budget(result,language)
    print(f"Tutorial 20 regenerated in {TUTORIAL_DIR}")
if __name__ == "__main__": main()
