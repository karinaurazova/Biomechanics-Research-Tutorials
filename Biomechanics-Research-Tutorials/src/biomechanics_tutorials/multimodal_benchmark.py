"""Multimodal verification-ready synthetic benchmark for Tutorial 20."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
import numpy as np
from numpy.typing import ArrayLike
from scipy import ndimage
from scipy.optimize import lsq_linear

@dataclass(frozen=True)
class GroundTruthMicrostructure:
    """Exact structural state of the synthetic tissue patch."""
    x: np.ndarray; y: np.ndarray; tissue_mask: np.ndarray; fiber_mask: np.ndarray; pore_mask: np.ndarray
    theta: np.ndarray; kappa: np.ndarray; rho_f: np.ndarray; connectivity: np.ndarray; parameters: np.ndarray
    @property
    def shape(self) -> tuple[int, int]: return self.fiber_mask.shape

@dataclass(frozen=True)
class SyntheticModalities:
    """Synthetic observations of the same hidden microstructure."""
    sem_like: np.ndarray; polarization_intensity: np.ndarray; polarization_angle: np.ndarray; fluorescence_like: np.ndarray; dic_reference: np.ndarray

@dataclass(frozen=True)
class LoadCase:
    """Synthetic load case with exact and DIC-like strains."""
    name: str; exx_true: np.ndarray; eyy_true: np.ndarray; gxy_true: np.ndarray
    exx_dic: np.ndarray; eyy_dic: np.ndarray; gxy_dic: np.ndarray; force_true: np.ndarray; force_observed: np.ndarray

@dataclass(frozen=True)
class PipelineResult:
    """Complete output of the multimodal benchmark."""
    truth: GroundTruthMicrostructure; modalities: SyntheticModalities; masks: dict[str, np.ndarray]
    segmentation_metrics: list[dict[str, float | str]]; orientation_metrics: list[dict[str, float | str]]
    load_cases: list[LoadCase]; parameter_results: list[dict[str, float | str]]; error_budget: list[dict[str, float | str]]

PARAMETER_NAMES = ("matrix_base", "density_gain", "fiber_scale", "connectivity_scale")

def normalize01(values: ArrayLike) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    return (values - np.nanmin(values)) / (np.nanmax(values) - np.nanmin(values) + 1e-12)

def axial_wrap(theta: ArrayLike) -> np.ndarray: return np.mod(np.asarray(theta, dtype=float), np.pi)

def axial_difference(a: ArrayLike, b: ArrayLike) -> np.ndarray:
    diff = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    return 0.5 * np.arctan2(np.sin(2 * diff), np.cos(2 * diff))

def generate_ground_truth_microstructure(shape: tuple[int, int] = (112, 128), seed: int = 20) -> GroundTruthMicrostructure:
    """Generate known fibers, pores, orientation fields and material parameters."""
    if shape[0] < 48 or shape[1] < 48: raise ValueError("Use at least a 48 by 48 grid.")
    rng = np.random.default_rng(seed); yy, xx = np.indices(shape, dtype=float)
    x = xx / (shape[1] - 1); y = yy / (shape[0] - 1)
    ellipse = ((x - 0.51) / 0.47) ** 2 + ((y - 0.51) / 0.41) ** 2 < 1.0
    pore_mask = np.zeros(shape, dtype=bool)
    for cx, cy, r in [(0.27,0.31,0.055),(0.68,0.34,0.043),(0.43,0.66,0.050),(0.77,0.70,0.037)]:
        pore_mask |= (x-cx)**2 + (y-cy)**2 < r**2
    tissue_mask = ellipse & ~pore_mask
    smooth = normalize01(ndimage.gaussian_filter(rng.normal(size=shape), sigma=5.0))
    theta = np.deg2rad(18) + 0.70*(y-0.5) + 0.23*np.sin(2*np.pi*x) + 0.10*np.sin(4*np.pi*y+0.7) + 0.05*(smooth-0.5)
    theta = axial_wrap(theta)
    normal_coord = x*np.sin(theta) - y*np.cos(theta)
    ridges = 0.5 + 0.5*np.cos(2*np.pi*(17*normal_coord + 0.12*smooth))
    band = 0.35 + 0.42*np.exp(-((y-0.52-0.08*np.sin(2*np.pi*x))**2)/(2*0.18**2)) + 0.20*np.exp(-((x-0.68)**2)/(2*0.20**2))
    score = normalize01(0.65*ridges + 0.55*band + 0.18*smooth)
    fiber_mask = (score > 0.49) & tissue_mask
    rho_f = np.clip(0.05 + 0.95*normalize01(ndimage.gaussian_filter(fiber_mask.astype(float), sigma=2.3)), 0, 1) * tissue_mask
    connectivity = np.clip(0.10 + 0.90*normalize01(ndimage.gaussian_filter(fiber_mask.astype(float), sigma=5.0)), 0, 1) * tissue_mask
    kappa = np.clip(0.7 + 7.5*rho_f + 3.0*connectivity + 0.25*rng.normal(size=shape), 0.2, 14.0)
    return GroundTruthMicrostructure(x, y, tissue_mask, fiber_mask, pore_mask, theta, kappa, rho_f, connectivity, np.array([18.0,24.0,150.0,68.0]))

def generate_dic_reference(shape: tuple[int, int], seed: int = 120) -> np.ndarray:
    rng = np.random.default_rng(seed); impulses = rng.random(shape) < 0.045
    speckles = ndimage.gaussian_filter(impulses.astype(float), sigma=1.1)
    texture = 0.55*normalize01(speckles) + 0.45*normalize01(ndimage.gaussian_filter(rng.normal(size=shape), 2.4))
    return normalize01(texture)

def render_modalities(truth: GroundTruthMicrostructure, seed: int = 21, sem_noise: float = 0.055, fluorescence_noise: float = 0.040, polarization_angle_noise_deg: float = 4.0) -> SyntheticModalities:
    rng = np.random.default_rng(seed)
    height = ndimage.gaussian_filter(truth.fiber_mask.astype(float), sigma=1.1); edge = np.hypot(*np.gradient(height))
    sem = normalize01(0.18 + 0.68*height + 0.22*normalize01(edge) + 0.10*truth.x + sem_noise*rng.normal(size=truth.shape)) * truth.tissue_mask
    retardance = normalize01(truth.rho_f * truth.kappa/(truth.kappa+2.0))
    pol_i = normalize01(0.20 + 0.75*retardance + 0.08*rng.normal(size=truth.shape)) * truth.tissue_mask
    pol_a = axial_wrap(truth.theta + np.deg2rad(polarization_angle_noise_deg)*rng.normal(size=truth.shape))
    illum = 0.65 + 0.35*np.exp(-((truth.x-0.45)**2 + (truth.y-0.45)**2)/0.30)
    fluo = normalize01(ndimage.gaussian_filter(truth.fiber_mask.astype(float), sigma=1.8)*illum + fluorescence_noise*rng.normal(size=truth.shape)) * truth.tissue_mask
    return SyntheticModalities(sem, pol_i, pol_a, fluo, generate_dic_reference(truth.shape, seed+100)*truth.tissue_mask)

def otsu_threshold(image: ArrayLike, bins: int = 256) -> float:
    values = np.asarray(image, dtype=float).ravel(); values = values[np.isfinite(values)]
    if values.size == 0: return 0.5
    hist, edges = np.histogram(values, bins=bins, range=(float(values.min()), float(values.max()))); centers = 0.5*(edges[:-1]+edges[1:])
    w1 = np.cumsum(hist); w2 = np.cumsum(hist[::-1])[::-1]
    m1 = np.cumsum(hist*centers)/np.maximum(w1, 1); m2 = (np.cumsum((hist*centers)[::-1])/np.maximum(w2[::-1], 1))[::-1]
    between = w1[:-1]*w2[1:]*(m1[:-1]-m2[1:])**2
    return float(centers[:-1][np.argmax(between)]) if between.size else float(np.mean(values))

def clean_mask(mask: np.ndarray) -> np.ndarray:
    st = np.ones((3,3), dtype=bool)
    return ndimage.binary_fill_holes(ndimage.binary_closing(ndimage.binary_opening(mask, structure=st), structure=st)).astype(bool)

def segment_modalities(truth: GroundTruthMicrostructure, modalities: SyntheticModalities) -> dict[str, np.ndarray]:
    sem_values = modalities.sem_like[truth.tissue_mask]
    sem_global = modalities.sem_like > (float(sem_values.mean()) + 0.15*float(sem_values.std()))
    sem_otsu = modalities.sem_like > otsu_threshold(sem_values)
    sem_adaptive = modalities.sem_like > (ndimage.gaussian_filter(modalities.sem_like, sigma=6.0) + 0.055)
    fluo_otsu = modalities.fluorescence_like > otsu_threshold(modalities.fluorescence_like[truth.tissue_mask])
    pol_otsu = modalities.polarization_intensity > otsu_threshold(modalities.polarization_intensity[truth.tissue_mask])
    fusion_score = normalize01(0.40*modalities.sem_like + 0.35*modalities.fluorescence_like + 0.25*modalities.polarization_intensity)
    fusion = fusion_score > otsu_threshold(fusion_score[truth.tissue_mask])
    raw = {"sem_global":sem_global,"sem_otsu":sem_otsu,"sem_adaptive":sem_adaptive,"fluorescence_otsu":fluo_otsu,"polarization_otsu":pol_otsu,"multimodal_fusion":fusion,"ground_truth":truth.fiber_mask}
    return {name: clean_mask(mask & truth.tissue_mask) for name, mask in raw.items()}

def binary_metrics(predicted: ArrayLike, truth: ArrayLike) -> dict[str, float]:
    p = np.asarray(predicted, dtype=bool); t = np.asarray(truth, dtype=bool)
    tp = float(np.logical_and(p,t).sum()); fp = float(np.logical_and(p,~t).sum()); fn = float(np.logical_and(~p,t).sum())
    return {"dice":2*tp/max(2*tp+fp+fn,1.0),"iou":tp/max(tp+fp+fn,1.0),"precision":tp/max(tp+fp,1.0),"recall":tp/max(tp+fn,1.0),"area_error":abs(float(p.mean())-float(t.mean()))/max(float(t.mean()),1e-12)}

def segmentation_benchmark(masks: dict[str, np.ndarray], truth: GroundTruthMicrostructure) -> list[dict[str, float | str]]:
    rows=[]
    for name, mask in masks.items():
        if name == "ground_truth": continue
        metrics = binary_metrics(mask, truth.fiber_mask); labels, count = ndimage.label(mask)
        largest = 0 if count == 0 else max(np.bincount(labels.ravel())[1:])
        rows.append({"method": name, **metrics, "continuity": float(largest/max(float(mask.sum()),1.0))})
    return rows

def structure_tensor_orientation(image: ArrayLike, sigma: float = 1.4) -> tuple[np.ndarray, np.ndarray]:
    image = np.asarray(image, dtype=float); gy, gx = np.gradient(ndimage.gaussian_filter(image, sigma=sigma))
    jxx = ndimage.gaussian_filter(gx*gx, sigma=2*sigma); jyy = ndimage.gaussian_filter(gy*gy, sigma=2*sigma); jxy = ndimage.gaussian_filter(gx*gy, sigma=2*sigma)
    normal = 0.5*np.arctan2(2*jxy, jxx-jyy); ridge = axial_wrap(normal + 0.5*np.pi)
    coherence = np.sqrt((jxx-jyy)**2 + 4*jxy**2)/(jxx+jyy+1e-12)
    return ridge, np.clip(coherence, 0, 1)

def orientation_mae_deg(predicted: ArrayLike, truth: ArrayLike, mask: ArrayLike) -> float:
    mask = np.asarray(mask, dtype=bool)
    if mask.sum() == 0: return float("nan")
    return float(np.rad2deg(np.mean(np.abs(axial_difference(predicted, truth)[mask]))))

def recover_structure(truth: GroundTruthMicrostructure, modalities: SyntheticModalities, masks: dict[str, np.ndarray]) -> tuple[dict[str, np.ndarray], list[dict[str, float | str]]]:
    sem_theta, sem_c = structure_tensor_orientation(modalities.sem_like); fluo_theta, fluo_c = structure_tensor_orientation(modalities.fluorescence_like)
    pol_theta = modalities.polarization_angle; pol_c = normalize01(modalities.polarization_intensity)
    fusion_theta = axial_wrap(0.5*np.arctan2(np.sin(2*sem_theta)*sem_c + np.sin(2*pol_theta)*pol_c, np.cos(2*sem_theta)*sem_c + np.cos(2*pol_theta)*pol_c))
    fusion_c = normalize01(0.5*sem_c + 0.5*pol_c)
    fields = {"sem_structure_tensor_theta":sem_theta,"fluorescence_structure_tensor_theta":fluo_theta,"polarization_theta":pol_theta,"fusion_theta":fusion_theta,"sem_coherence":sem_c,"fluorescence_coherence":fluo_c,"polarization_coherence":pol_c,"fusion_coherence":fusion_c}
    rows = [
        {"method":"sem_structure_tensor","orientation_mae_deg":orientation_mae_deg(sem_theta, truth.theta, masks["sem_otsu"]),"coherence_mean":float(np.mean(sem_c[truth.tissue_mask]))},
        {"method":"fluorescence_structure_tensor","orientation_mae_deg":orientation_mae_deg(fluo_theta, truth.theta, masks["fluorescence_otsu"]),"coherence_mean":float(np.mean(fluo_c[truth.tissue_mask]))},
        {"method":"polarization_harmonic_like","orientation_mae_deg":orientation_mae_deg(pol_theta, truth.theta, truth.fiber_mask),"coherence_mean":float(np.mean(pol_c[truth.tissue_mask]))},
        {"method":"sem_plus_polarization_fusion","orientation_mae_deg":orientation_mae_deg(fusion_theta, truth.theta, masks["multimodal_fusion"]),"coherence_mean":float(np.mean(fusion_c[truth.tissue_mask]))},]
    return fields, rows

def plane_stress_basis(exx: np.ndarray, eyy: np.ndarray, gxy: np.ndarray, nu: float = 0.45) -> np.ndarray:
    f=1/(1-nu**2); return np.stack([f*(exx+nu*eyy), f*(nu*exx+eyy), f*(0.5*(1-nu)*gxy)], axis=-1)

def fiber_basis(exx: np.ndarray, eyy: np.ndarray, gxy: np.ndarray, theta: np.ndarray) -> np.ndarray:
    nx, ny = np.cos(theta), np.sin(theta); e_f = nx**2*exx + ny**2*eyy + nx*ny*gxy
    return np.stack([e_f*nx**2, e_f*ny**2, e_f*nx*ny], axis=-1)

def stress_design_basis(exx: np.ndarray, eyy: np.ndarray, gxy: np.ndarray, theta: np.ndarray, rho_f: np.ndarray, connectivity: np.ndarray, mask: np.ndarray) -> np.ndarray:
    iso = plane_stress_basis(exx,eyy,gxy); fib = fiber_basis(exx,eyy,gxy,theta); out = np.zeros(exx.shape+(3,4), dtype=float)
    out[...,0]=iso; out[...,1]=rho_f[...,None]*iso; out[...,2]=rho_f[...,None]*fib; out[...,3]=(rho_f*connectivity)[...,None]*fib
    return out * mask[...,None,None]

def stress_from_parameters(exx: np.ndarray, eyy: np.ndarray, gxy: np.ndarray, theta: np.ndarray, rho_f: np.ndarray, connectivity: np.ndarray, mask: np.ndarray, parameters: ArrayLike) -> np.ndarray:
    return np.tensordot(stress_design_basis(exx,eyy,gxy,theta,rho_f,connectivity,mask), np.asarray(parameters, dtype=float), axes=([-1],[0]))

def build_load_cases(truth: GroundTruthMicrostructure, seed: int = 22, force_noise: float = 0.012, dic_noise: float = 0.00045) -> list[LoadCase]:
    rng=np.random.default_rng(seed); macros=[("uniaxial_x",0.026,-0.006,0.000),("uniaxial_y",-0.004,0.022,0.000),("simple_shear",0.002,-0.001,0.030),("biaxial",0.017,0.012,0.006)]
    het=0.20*(truth.rho_f-np.mean(truth.rho_f[truth.tissue_mask])); wave=np.sin(2*np.pi*truth.x)*np.sin(np.pi*truth.y); cases=[]
    for name, ex0, ey0, g0 in macros:
        exx=(ex0*(1+het)+0.0015*wave)*truth.tissue_mask; eyy=(ey0*(1-0.5*het)-0.0010*wave)*truth.tissue_mask; gxy=(g0*(1+0.4*het)+0.0012*np.cos(np.pi*truth.x))*truth.tissue_mask
        stress=stress_from_parameters(exx,eyy,gxy,truth.theta,truth.rho_f,truth.connectivity,truth.tissue_mask,truth.parameters); force=stress[truth.tissue_mask].mean(axis=0)
        observed=force + force_noise*(np.abs(force)+0.05)*rng.normal(size=3)
        cases.append(LoadCase(name, exx, eyy, gxy, exx+dic_noise*rng.normal(size=truth.shape)*truth.tissue_mask, eyy+dic_noise*rng.normal(size=truth.shape)*truth.tissue_mask, gxy+dic_noise*rng.normal(size=truth.shape)*truth.tissue_mask, force, observed))
    return cases

def assemble_inverse_system(load_cases: Iterable[LoadCase], theta: np.ndarray, rho_f: np.ndarray, connectivity: np.ndarray, mask: np.ndarray, use_dic: bool = True) -> tuple[np.ndarray, np.ndarray]:
    rows=[]; rhs=[]
    for case in load_cases:
        exx = case.exx_dic if use_dic else case.exx_true; eyy = case.eyy_dic if use_dic else case.eyy_true; gxy = case.gxy_dic if use_dic else case.gxy_true
        rows.append(stress_design_basis(exx,eyy,gxy,theta,rho_f,connectivity,mask)[mask].mean(axis=0)); rhs.append(case.force_observed)
    return np.vstack(rows), np.concatenate(rhs)

def estimate_parameters(A: np.ndarray, y: np.ndarray) -> np.ndarray: return np.asarray(lsq_linear(A, y, bounds=(0,np.inf), lsmr_tol="auto").x, dtype=float)

def recovered_structure_from_mask(truth: GroundTruthMicrostructure, theta: np.ndarray, mask: np.ndarray, coherence: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rho=normalize01(ndimage.gaussian_filter(mask.astype(float), sigma=2.2))*truth.tissue_mask; conn=normalize01(ndimage.gaussian_filter(mask.astype(float), sigma=5.0))*truth.tissue_mask
    if coherence is not None: conn = np.clip(0.55*conn + 0.45*normalize01(coherence), 0, 1) * truth.tissue_mask
    return theta, rho, conn, mask & truth.tissue_mask

def parameter_recovery_benchmark(truth: GroundTruthMicrostructure, masks: dict[str, np.ndarray], structure_fields: dict[str, np.ndarray], load_cases: list[LoadCase]) -> list[dict[str, float | str]]:
    scenarios={"oracle_ground_truth":(truth.theta,truth.rho_f,truth.connectivity,truth.tissue_mask),"sem_only":recovered_structure_from_mask(truth,structure_fields["sem_structure_tensor_theta"],masks["sem_otsu"],structure_fields["sem_coherence"]),"polarization_only":recovered_structure_from_mask(truth,structure_fields["polarization_theta"],masks["polarization_otsu"],structure_fields["polarization_coherence"]),"multimodal_fusion":recovered_structure_from_mask(truth,structure_fields["fusion_theta"],masks["multimodal_fusion"],structure_fields["fusion_coherence"])}
    rows=[]
    for name,(theta,rho,conn,mask) in scenarios.items():
        A,y=assemble_inverse_system(load_cases,theta,rho,conn,mask); est=estimate_parameters(A,y); pred=A@est
        row={"scenario":name,"relative_parameter_error":float(np.linalg.norm(est-truth.parameters)/np.linalg.norm(truth.parameters)),"relative_force_residual":float(np.linalg.norm(pred-y)/max(np.linalg.norm(y),1e-12)),"condition_number":float(np.linalg.cond(A))}
        for pname,true,value in zip(PARAMETER_NAMES, truth.parameters, est): row[f"{pname}_true"]=float(true); row[f"{pname}_estimated"]=float(value)
        rows.append(row)
    return rows

def error_budget_table(segmentation_metrics: list[dict[str, float | str]], orientation_metrics: list[dict[str, float | str]], parameter_results: list[dict[str, float | str]]) -> list[dict[str, float | str]]:
    return [{"stage":"segmentation","metric":"best_dice","value":max(float(r["dice"]) for r in segmentation_metrics),"interpretation":"mask agreement"},{"stage":"orientation","metric":"best_orientation_mae_deg","value":min(float(r["orientation_mae_deg"]) for r in orientation_metrics),"interpretation":"axial direction recovery"},{"stage":"inverse_mechanics","metric":"best_relative_parameter_error","value":min(float(r["relative_parameter_error"]) for r in parameter_results),"interpretation":"material parameter recovery"}]

def run_full_benchmark(seed: int = 20, shape: tuple[int, int] = (112,128), force_noise: float = 0.012, dic_noise: float = 0.00045) -> PipelineResult:
    truth=generate_ground_truth_microstructure(shape=shape, seed=seed); modalities=render_modalities(truth, seed=seed+1); masks=segment_modalities(truth, modalities)
    seg=segmentation_benchmark(masks, truth); fields,ori=recover_structure(truth, modalities, masks); cases=build_load_cases(truth, seed=seed+2, force_noise=force_noise, dic_noise=dic_noise); params=parameter_recovery_benchmark(truth, masks, fields, cases)
    return PipelineResult(truth, modalities, masks, seg, ori, cases, params, error_budget_table(seg, ori, params))
