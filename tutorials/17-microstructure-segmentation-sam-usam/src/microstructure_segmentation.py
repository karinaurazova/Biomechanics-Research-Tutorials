"""Synthetic microstructure segmentation benchmark for Tutorial 17.

The module intentionally avoids heavyweight SAM/µSAM dependencies. Instead it
provides prompt-aware educational baselines and metrics that mirror the types
of checks needed before applying real foundation models to microscopy.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import math
import numpy as np
from scipy import ndimage as ndi
import matplotlib.pyplot as plt

Array = np.ndarray

@dataclass
class SyntheticMicrostructure:
    image: Array
    mask: Array
    pores: Array
    orientation: Array
    skeleton: Array
    instance: Array


def _draw_line(mask: Array, y0: float, x0: float, y1: float, x1: float, radius: int) -> None:
    n = int(max(abs(y1-y0), abs(x1-x0))) + 1
    yy = np.linspace(y0, y1, n)
    xx = np.linspace(x0, x1, n)
    H, W = mask.shape
    Y, X = np.ogrid[:H, :W]
    for y, x in zip(yy[::max(1, n//80)], xx[::max(1, n//80)]):
        mask[(Y-y)**2 + (X-x)**2 <= radius**2] = True


def generate_microstructure(size: int = 160, n_fibres: int = 34, radius_range=(1, 4),
                            pore_fraction: float = 0.07, noise: float = 0.10,
                            blur: float = 1.0, seed: int = 17) -> SyntheticMicrostructure:
    rng = np.random.default_rng(seed)
    H = W = size
    mask = np.zeros((H, W), dtype=bool)
    orientation = np.full((H, W), np.nan)
    instance = np.zeros((H, W), dtype=np.int32)
    Y, X = np.ogrid[:H, :W]
    for i in range(1, n_fibres + 1):
        angle = rng.vonmises(mu=np.deg2rad(25), kappa=2.2)
        length = rng.uniform(0.45*size, 1.15*size)
        cy, cx = rng.uniform(0.05*H, 0.95*H), rng.uniform(0.05*W, 0.95*W)
        dy, dx = 0.5*length*np.sin(angle), 0.5*length*np.cos(angle)
        radius = int(rng.integers(radius_range[0], radius_range[1]+1))
        before = mask.copy()
        _draw_line(mask, cy-dy, cx-dx, cy+dy, cx+dx, radius)
        new = mask & ~before
        orientation[new] = angle
        instance[new] = i
    pores = np.zeros_like(mask)
    for _ in range(max(4, int(pore_fraction*40))):
        py, px = rng.uniform(20, H-20), rng.uniform(20, W-20)
        rr = rng.uniform(3, 10)
        pore = (Y-py)**2 + (X-px)**2 <= rr**2
        pores |= pore
    mask &= ~pores
    instance[~mask] = 0
    orientation[~mask] = np.nan
    clean = mask.astype(float)
    shade = 0.18*np.sin(np.linspace(0, np.pi*2, W))[None, :] + 0.10*np.cos(np.linspace(0, np.pi*3, H))[:, None]
    image = 0.22 + 0.62*ndi.gaussian_filter(clean, blur) + shade
    image += noise*rng.normal(size=(H, W))
    image = np.clip(image, 0, 1)
    skeleton = skeletonize(mask)
    return SyntheticMicrostructure(image=image, mask=mask, pores=pores, orientation=orientation, skeleton=skeleton, instance=instance)


def threshold_global(image: Array, level: float = 0.52) -> Array:
    return image > level


def threshold_otsu(image: Array, bins: int = 256) -> Array:
    hist, edges = np.histogram(image.ravel(), bins=bins, range=(0, 1))
    centers = 0.5*(edges[:-1]+edges[1:])
    weight1 = np.cumsum(hist)
    weight2 = np.cumsum(hist[::-1])[::-1]
    mean1 = np.cumsum(hist*centers) / np.maximum(weight1, 1)
    mean2 = (np.cumsum((hist*centers)[::-1]) / np.maximum(weight2[::-1], 1))[::-1]
    variance12 = weight1[:-1]*weight2[1:]*(mean1[:-1]-mean2[1:])**2
    t = centers[:-1][np.argmax(variance12)]
    return image > t


def threshold_adaptive(image: Array, window: int = 25, offset: float = -0.02) -> Array:
    local = ndi.uniform_filter(image, size=window)
    return image > (local + offset)


def morphology_clean(mask: Array, radius: int = 2) -> Array:
    s = ndi.generate_binary_structure(2, 2)
    out = ndi.binary_opening(mask, structure=s, iterations=1)
    out = ndi.binary_closing(out, structure=s, iterations=radius)
    out = ndi.binary_fill_holes(out)
    return out.astype(bool)


def connected_components(mask: Array, min_size: int = 25):
    lab, n = ndi.label(mask)
    sizes = np.bincount(lab.ravel())
    keep = sizes >= min_size
    keep[0] = False
    return keep[lab], lab, int(n)


def distance_transform(mask: Array) -> Array:
    return ndi.distance_transform_edt(mask)


def skeletonize(mask: Array, max_iter: int = 256) -> Array:
    # Zhang-Suen thinning with numpy; sufficient for small teaching masks.
    img = mask.astype(np.uint8).copy()
    changed = True
    it = 0
    while changed and it < max_iter:
        changed = False
        for step in [0, 1]:
            P2 = np.roll(img, -1, axis=0); P3 = np.roll(np.roll(img, -1, axis=0), 1, axis=1)
            P4 = np.roll(img, 1, axis=1);  P5 = np.roll(np.roll(img, 1, axis=0), 1, axis=1)
            P6 = np.roll(img, 1, axis=0);  P7 = np.roll(np.roll(img, 1, axis=0), -1, axis=1)
            P8 = np.roll(img, -1, axis=1); P9 = np.roll(np.roll(img, -1, axis=0), -1, axis=1)
            neighbors = [P2,P3,P4,P5,P6,P7,P8,P9]
            B = sum(neighbors)
            A = sum((neighbors[i] == 0) & (neighbors[(i+1)%8] == 1) for i in range(8))
            if step == 0:
                m1 = P2*P4*P6 == 0; m2 = P4*P6*P8 == 0
            else:
                m1 = P2*P4*P8 == 0; m2 = P2*P6*P8 == 0
            remove = (img == 1) & (B >= 2) & (B <= 6) & (A == 1) & m1 & m2
            remove[[0,-1],:] = False; remove[:,[0,-1]] = False
            if remove.any():
                img[remove] = 0; changed = True
        it += 1
    return img.astype(bool)


def ridge_response(image: Array, sigma: float = 1.4) -> Array:
    smooth = ndi.gaussian_filter(image, sigma)
    gy, gx = np.gradient(smooth)
    return np.hypot(gx, gy)


def structure_tensor_orientation(image: Array, sigma: float = 2.0):
    gy, gx = np.gradient(ndi.gaussian_filter(image, 1.0))
    Jxx = ndi.gaussian_filter(gx*gx, sigma)
    Jyy = ndi.gaussian_filter(gy*gy, sigma)
    Jxy = ndi.gaussian_filter(gx*gy, sigma)
    theta = 0.5*np.arctan2(2*Jxy, Jxx-Jyy)
    coherence = np.sqrt((Jxx-Jyy)**2 + 4*Jxy**2) / np.maximum(Jxx+Jyy, 1e-9)
    return theta, coherence


def frangi_like(image: Array, sigmas=(1.0, 2.0, 3.0)) -> Array:
    responses = []
    for s in sigmas:
        I = ndi.gaussian_filter(image, s)
        Hxx = ndi.gaussian_filter(I, s, order=(0,2))
        Hyy = ndi.gaussian_filter(I, s, order=(2,0))
        Hxy = ndi.gaussian_filter(I, s, order=(1,1))
        tr = Hxx + Hyy
        det = Hxx*Hyy - Hxy*Hxy
        disc = np.maximum(tr*tr/4 - det, 0)
        l1 = tr/2 - np.sqrt(disc); l2 = tr/2 + np.sqrt(disc)
        vessel = np.exp(-(l1/(l2+1e-6))**2/0.5) * (1-np.exp(-(l1*l1+l2*l2)/0.02))
        vessel[l2 > 0] = 0
        responses.append(vessel)
    out = np.max(responses, axis=0)
    return (out - out.min()) / (np.ptp(out) + 1e-9)


def watershed_like(mask: Array) -> Array:
    dist = ndi.distance_transform_edt(mask)
    seeds, _ = ndi.label((dist > np.percentile(dist[mask], 75)) & mask) if mask.any() else (np.zeros_like(mask, int), 0)
    # A lightweight marker expansion: nearest labelled peak within the mask.
    if seeds.max() == 0:
        return seeds
    _, inds = ndi.distance_transform_edt(seeds == 0, return_indices=True)
    labels = seeds[tuple(inds)]
    labels[~mask] = 0
    return labels


def graph_from_skeleton(skel: Array):
    K = np.ones((3,3), int); K[1,1] = 0
    deg = ndi.convolve(skel.astype(int), K, mode='constant')
    nodes = skel & (deg != 2)
    branches = skel & (deg == 2)
    return {'nodes': int(nodes.sum()), 'branch_pixels': int(branches.sum()), 'endpoints': int((skel & (deg == 1)).sum()), 'junctions': int((skel & (deg >= 3)).sum())}


def random_forest_baseline(image: Array, seed: int = 0) -> Array:
    # Optional sklearn-free surrogate: average of multiscale intensity, ridge and local contrast.
    local = ndi.uniform_filter(image, 13)
    features = 0.55*image + 0.25*frangi_like(image) + 0.20*np.clip(image-local+0.5, 0, 1)
    return morphology_clean(features > threshold_value_otsu(features))


def patch_classifier_baseline(image: Array) -> Array:
    local_mean = ndi.uniform_filter(image, 17)
    local_var = ndi.uniform_filter(image*image, 17) - local_mean**2
    score = 0.7*(image-local_mean) + 0.3*np.sqrt(np.maximum(local_var, 0))
    return morphology_clean(score > np.percentile(score, 54))


def unet_like_baseline(image: Array) -> Array:
    # A tiny multiscale encoder-decoder analogue: fuse fine, medium and coarse responses.
    fine = image
    med = ndi.zoom(ndi.zoom(image, 0.5, order=1), 2.0, order=1)[:image.shape[0], :image.shape[1]]
    coarse = ndi.zoom(ndi.zoom(image, 0.25, order=1), 4.0, order=1)[:image.shape[0], :image.shape[1]]
    score = 0.50*fine + 0.30*med + 0.20*coarse + 0.15*frangi_like(image)
    return morphology_clean(score > threshold_value_otsu(score))


def domain_augment(image: Array, seed: int = 0) -> Array:
    rng = np.random.default_rng(seed)
    aug = np.clip(0.85*image + 0.15*rng.normal(size=image.shape) + 0.08*rng.uniform(-1,1), 0, 1)
    return aug


def threshold_value_otsu(image: Array, bins: int = 256) -> float:
    hist, edges = np.histogram(image.ravel(), bins=bins)
    centers = 0.5*(edges[:-1]+edges[1:])
    w1 = np.cumsum(hist); w2 = np.cumsum(hist[::-1])[::-1]
    m1 = np.cumsum(hist*centers)/np.maximum(w1,1)
    m2 = (np.cumsum((hist*centers)[::-1])/np.maximum(w2[::-1],1))[::-1]
    v = w1[:-1]*w2[1:]*(m1[:-1]-m2[1:])**2
    return float(centers[:-1][np.argmax(v)])


def sam_like_from_prompts(image: Array, positive_points=(), negative_points=(), box=None) -> Array:
    base = threshold_adaptive(image, 23, -0.015)
    yy, xx = np.indices(image.shape)
    confidence = np.zeros_like(image, float)
    for y, x in positive_points:
        confidence += np.exp(-((yy-y)**2+(xx-x)**2)/(2*22**2))
    for y, x in negative_points:
        confidence -= 1.4*np.exp(-((yy-y)**2+(xx-x)**2)/(2*18**2))
    if box is not None:
        y0, x0, y1, x1 = box
        boxmask = np.zeros_like(base, bool); boxmask[y0:y1, x0:x1] = True
        base &= ndi.binary_dilation(boxmask, iterations=2)
        confidence += 0.25*boxmask
    out = (0.55*base.astype(float) + 0.45*(confidence > 0.18)) > 0.45
    return morphology_clean(out)


def automatic_mask_generation(image: Array) -> Array:
    candidates = [threshold_global(image, t) for t in np.linspace(0.42, 0.62, 6)]
    candidates += [threshold_adaptive(image, w, off) for w in [17,25,35] for off in [-0.03, 0.0, 0.03]]
    # consensus mask mimics automatic proposal aggregation
    stack = np.mean([c.astype(float) for c in candidates], axis=0)
    return morphology_clean(stack > 0.45)


def usam_like_stack_propagation(stack: Array, first_mask: Array) -> Array:
    masks = [first_mask]
    prev = first_mask
    for k in range(1, stack.shape[0]):
        pred = ndi.binary_dilation(prev, iterations=1) & threshold_adaptive(stack[k], 25, -0.02)
        pred = morphology_clean(pred)
        masks.append(pred)
        prev = pred
    return np.array(masks)


def make_stack(base: SyntheticMicrostructure, n: int = 6, seed: int = 3) -> Array:
    rng = np.random.default_rng(seed)
    frames = []
    for k in range(n):
        shifted = ndi.shift(base.image, shift=(0.8*k, -0.4*k), order=1, mode='nearest')
        frames.append(np.clip(shifted + 0.04*rng.normal(size=base.image.shape), 0, 1))
    return np.array(frames)


def dice(a: Array, b: Array) -> float:
    a = a.astype(bool); b = b.astype(bool)
    return float(2*np.logical_and(a,b).sum() / max(a.sum()+b.sum(), 1))


def iou(a: Array, b: Array) -> float:
    a = a.astype(bool); b = b.astype(bool)
    return float(np.logical_and(a,b).sum() / max(np.logical_or(a,b).sum(), 1))


def precision_recall(pred: Array, truth: Array):
    pred = pred.astype(bool); truth = truth.astype(bool)
    tp = np.logical_and(pred, truth).sum(); fp = np.logical_and(pred, ~truth).sum(); fn = np.logical_and(~pred, truth).sum()
    return float(tp/max(tp+fp,1)), float(tp/max(tp+fn,1))


def boundary(mask: Array) -> Array:
    return mask.astype(bool) ^ ndi.binary_erosion(mask.astype(bool))


def boundary_fscore(pred: Array, truth: Array, tol: int = 2) -> float:
    bp, bt = boundary(pred), boundary(truth)
    near_t = ndi.binary_dilation(bt, iterations=tol)
    near_p = ndi.binary_dilation(bp, iterations=tol)
    p = np.logical_and(bp, near_t).sum()/max(bp.sum(),1)
    r = np.logical_and(bt, near_p).sum()/max(bt.sum(),1)
    return float(2*p*r/max(p+r, 1e-9))


def hausdorff_distance(pred: Array, truth: Array) -> float:
    bp, bt = boundary(pred), boundary(truth)
    if bp.sum() == 0 or bt.sum() == 0:
        return float('inf')
    dp = ndi.distance_transform_edt(~bp)
    dt = ndi.distance_transform_edt(~bt)
    return float(max(dt[bp].max(), dp[bt].max()))


def orientation_error(pred: Array, truth_orientation: Array, image: Array) -> float:
    theta, coh = structure_tensor_orientation(image)
    valid = pred.astype(bool) & np.isfinite(truth_orientation) & (coh > 0.08)
    if valid.sum() < 10: return float('nan')
    diff = np.abs(np.angle(np.exp(2j*(theta[valid] - truth_orientation[valid]))))/2
    return float(np.rad2deg(np.nanmedian(diff)))


def diameter_error(pred: Array, truth: Array) -> float:
    def avg_d(m):
        sk = skeletonize(m)
        d = 2*ndi.distance_transform_edt(m)
        return float(np.nanmean(d[sk])) if sk.any() else np.nan
    return float(abs(avg_d(pred)-avg_d(truth)))


def topology_errors(pred: Array, truth: Array) -> int:
    _, nt = ndi.label(truth); _, npred = ndi.label(pred)
    gt = graph_from_skeleton(skeletonize(truth)); gp = graph_from_skeleton(skeletonize(pred))
    return int(abs(npred-nt) + abs(gp['endpoints']-gt['endpoints']) + abs(gp['junctions']-gt['junctions']))


def pore_size_error(pred: Array, truth_pores: Array, truth_mask: Array) -> float:
    pred_pores = ndi.binary_fill_holes(pred) & ~pred
    truth_sizes = np.bincount(ndi.label(truth_pores)[0].ravel())[1:]
    pred_sizes = np.bincount(ndi.label(pred_pores & ~truth_mask)[0].ravel())[1:]
    if len(truth_sizes) == 0 or len(pred_sizes) == 0:
        return float('nan')
    return float(abs(np.median(pred_sizes)-np.median(truth_sizes)))


def skeleton_precision(pred: Array, truth: Array) -> float:
    sp = skeletonize(pred); st = skeletonize(truth)
    near = ndi.binary_dilation(st, iterations=2)
    return float(np.logical_and(sp, near).sum()/max(sp.sum(),1))


def fibre_continuity(pred: Array, truth: Array) -> float:
    _, nt = ndi.label(truth); _, npred = ndi.label(pred)
    return float(min(nt, npred)/max(nt, npred, 1))


def branch_preservation(pred: Array, truth: Array) -> float:
    gt = graph_from_skeleton(skeletonize(truth)); gp = graph_from_skeleton(skeletonize(pred))
    return float(min(gp['junctions'], gt['junctions'])/max(gp['junctions'], gt['junctions'], 1))


def evaluate(pred: Array, truth: Array, image: Array, truth_orientation: Array | None = None, pores: Array | None = None) -> dict:
    pr, re = precision_recall(pred, truth)
    out = {
        'Dice': dice(pred, truth), 'IoU': iou(pred, truth), 'Precision': pr, 'Recall': re,
        'Boundary_F': boundary_fscore(pred, truth), 'Hausdorff_px': hausdorff_distance(pred, truth),
        'Skeleton_precision': skeleton_precision(pred, truth), 'Topology_errors': topology_errors(pred, truth),
        'Fibre_continuity': fibre_continuity(pred, truth), 'Branch_preservation': branch_preservation(pred, truth),
        'Diameter_error_px': diameter_error(pred, truth),
    }
    if truth_orientation is not None:
        out['Orientation_error_deg'] = orientation_error(pred, truth_orientation, image)
    if pores is not None:
        out['Pore_size_error_px2'] = pore_size_error(pred, pores, truth)
    return out


def all_methods(sample: SyntheticMicrostructure) -> dict[str, Array]:
    image = sample.image
    methods = {
        'global_threshold': threshold_global(image),
        'otsu': threshold_otsu(image),
        'adaptive_threshold': threshold_adaptive(image),
    }
    methods['morphology'] = morphology_clean(methods['adaptive_threshold'])
    methods['connected_components'] = connected_components(methods['morphology'])[0]
    methods['watershed_mask'] = watershed_like(methods['connected_components']) > 0
    methods['frangi_like'] = morphology_clean(frangi_like(image) > 0.18)
    methods['random_forest_surrogate'] = random_forest_baseline(image)
    methods['patch_classifier'] = patch_classifier_baseline(image)
    methods['unet_like_baseline'] = unet_like_baseline(image)
    H, W = image.shape
    methods['sam_point'] = sam_like_from_prompts(image, positive_points=[(H//2, W//2)])
    methods['sam_pos_neg'] = sam_like_from_prompts(image, positive_points=[(45, 60), (95, 95), (115, 55)], negative_points=[(35, 120), (115, 125)])
    methods['sam_box'] = sam_like_from_prompts(image, positive_points=[(70,70)], box=(18, 18, H-18, W-18))
    methods['sam_auto_masks'] = automatic_mask_generation(image)
    return methods


def save_benchmark(sample: SyntheticMicrostructure, out_csv: Path) -> list[dict]:
    rows = []
    for name, pred in all_methods(sample).items():
        met = evaluate(pred, sample.mask, sample.image, sample.orientation, sample.pores)
        rows.append({'method': name, **met})
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    keys = list(rows[0].keys())
    with out_csv.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader(); writer.writerows(rows)
    return rows


def plot_overview(sample: SyntheticMicrostructure, out: Path, ru: bool = False):
    theta, coh = structure_tensor_orientation(sample.image)
    fig, ax = plt.subplots(2, 3, figsize=(12, 7.2), constrained_layout=True)
    items = [(sample.image, 'СЭМ-подобное изображение' if ru else 'SEM-like image'),
             (sample.mask, 'Истинная маска' if ru else 'Ground-truth mask'),
             (sample.pores, 'Поры' if ru else 'Pores'),
             (sample.skeleton, 'Скелет' if ru else 'Skeleton'),
             (coh, 'Когерентность структуры' if ru else 'Structure coherence'),
             (np.rad2deg(theta), 'Ориентация, градусы' if ru else 'Orientation, degrees')]
    for a, (im, title) in zip(ax.ravel(), items):
        a.imshow(im, cmap='gray' if im.dtype == bool else 'viridis')
        a.set_title(title, fontsize=10); a.set_xticks([]); a.set_yticks([])
    fig.suptitle('Tutorial 17: синтетическая микроструктура' if ru else 'Tutorial 17: synthetic microstructure', fontsize=14)
    out.parent.mkdir(parents=True, exist_ok=True); fig.savefig(out, dpi=180); plt.close(fig)


def plot_methods(sample: SyntheticMicrostructure, out: Path, ru: bool = False):
    methods = all_methods(sample)
    names = ['otsu','adaptive_threshold','morphology','frangi_like','sam_point','sam_pos_neg','sam_box','sam_auto_masks','unet_like_baseline']
    titles_ru = {'otsu':'Otsu','adaptive_threshold':'Adaptive threshold','morphology':'Морфология','frangi_like':'Frangi-like','sam_point':'SAM: точка','sam_pos_neg':'SAM: +/- точки','sam_box':'SAM: box','sam_auto_masks':'SAM: auto masks','unet_like_baseline':'U-Net-like'}
    fig, ax = plt.subplots(3, 3, figsize=(11, 10), constrained_layout=True)
    for a, name in zip(ax.ravel(), names):
        a.imshow(methods[name], cmap='gray')
        a.set_title(titles_ru[name] if ru else name.replace('_',' '), fontsize=10)
        a.set_xticks([]); a.set_yticks([])
    fig.suptitle('Сравнение методов сегментации' if ru else 'Segmentation method comparison', fontsize=14)
    fig.savefig(out, dpi=180); plt.close(fig)


def plot_metrics(rows: list[dict], out: Path, ru: bool = False):
    labels = [r['method'].replace('_','\n') for r in rows]
    dice_vals = [r['Dice'] for r in rows]
    topo = [r['Topology_errors'] for r in rows]
    x = np.arange(len(rows))
    fig, ax1 = plt.subplots(figsize=(13.5, 5.8), constrained_layout=True)
    ax1.bar(x-0.2, dice_vals, width=0.4, label='Dice')
    ax1.set_ylim(0, 1.05); ax1.set_ylabel('Dice')
    ax2 = ax1.twinx(); ax2.plot(x+0.2, topo, marker='o', label='Topology errors')
    ax2.set_ylabel('Ошибки топологии' if ru else 'Topology errors')
    ax1.set_xticks(x); ax1.set_xticklabels(labels, rotation=35, ha='right', fontsize=8)
    ax1.set_title('Dice не заменяет структурные метрики' if ru else 'Dice does not replace structural metrics')
    h1,l1 = ax1.get_legend_handles_labels(); h2,l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1+h2, l1+l2, loc='upper right')
    fig.savefig(out, dpi=180); plt.close(fig)


def plot_usam_stack(sample: SyntheticMicrostructure, out: Path, ru: bool = False):
    stack = make_stack(sample)
    first = sam_like_from_prompts(stack[0], positive_points=[(70,70)], box=(20,20,140,140))
    masks = usam_like_stack_propagation(stack, first)
    fig, ax = plt.subplots(2, 6, figsize=(14, 5.2), constrained_layout=True)
    for k in range(6):
        ax[0,k].imshow(stack[k], cmap='gray'); ax[0,k].set_title(('Срез ' if ru else 'Slice ')+str(k+1), fontsize=9)
        ax[1,k].imshow(masks[k], cmap='gray'); ax[1,k].set_title(('Маска ' if ru else 'Mask ')+str(k+1), fontsize=9)
        for a in [ax[0,k], ax[1,k]]: a.set_xticks([]); a.set_yticks([])
    fig.suptitle('μSAM-like propagation по синтетическому stack' if ru else 'µSAM-like propagation through a synthetic stack', fontsize=14)
    fig.savefig(out, dpi=180); plt.close(fig)


def write_dataset(sample: SyntheticMicrostructure, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    theta, coherence = structure_tensor_orientation(sample.image)
    np.savez_compressed(path, image=sample.image, mask=sample.mask, pores=sample.pores,
                        orientation=sample.orientation, skeleton=sample.skeleton,
                        instance=sample.instance, tensor_orientation=theta, coherence=coherence)


def reproduce(root: Path):
    fig = root/'figures'; data = root/'data'
    sample = generate_microstructure()
    write_dataset(sample, data/'example_microstructure.npz')
    rows = save_benchmark(sample, data/'segmentation_benchmark.csv')
    plot_overview(sample, fig/'microstructure_overview.png', ru=False)
    plot_overview(sample, fig/'microstructure_overview_ru.png', ru=True)
    plot_methods(sample, fig/'method_comparison.png', ru=False)
    plot_methods(sample, fig/'method_comparison_ru.png', ru=True)
    plot_metrics(rows, fig/'metrics_summary.png', ru=False)
    plot_metrics(rows, fig/'metrics_summary_ru.png', ru=True)
    plot_usam_stack(sample, fig/'usam_stack_propagation.png', ru=False)
    plot_usam_stack(sample, fig/'usam_stack_propagation_ru.png', ru=True)
    return rows
