# 01 Motivation

Fiber orientation is a state variable in many soft-tissue models, yet microscopy and synthetic images provide intensity rather than orientation directly. A reproducible image-to-orientation workflow must therefore expose its assumptions, scales, confidence measures, and failure modes.

The structure tensor is attractive because it converts local image gradients into a symmetric positive-semidefinite matrix. Its eigenvectors summarize dominant variation, while its eigenvalues quantify how strongly one direction dominates. For bright fiber-like ridges, the dominant gradient is normal to the ridge, so the reported fiber direction is obtained by a 90-degree rotation.

This tutorial starts with synthetic truth because it allows error to be measured pixel by pixel. The goal is verification of the computational method before any application to experimental images.
