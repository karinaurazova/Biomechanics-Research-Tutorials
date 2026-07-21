# Synthesis, secretion, and fibril assembly

Collagen production is a sequence of delayed biochemical processes. A stress or cytokine signal can alter transcription, but secreted procollagen must be processed and assembled before it contributes to the mature fibrillar network. The reduced model uses

$$\dot P=s-k_sP,$$
$$\dot C_i=k_sP-k_mC_i-k_{di}a_eC_i,$$
$$\dot C_m=k_mC_i-k_{dm}a_eC_m,$$

where $P$ is precursor, $C_i$ immature collagen, $C_m$ mature collagen, and $a_e$ effective enzyme activity.

The cascade creates a biologically meaningful delay: synthesis can rise immediately after overload, while mature collagen and stiffness change more slowly. This delay matters when loading is transient. A short signal may strongly alter precursor abundance but leave little mature matrix.

The equations are phenomenological. They represent process classes, not a complete reaction network. Their value is to prevent the common modeling error of equating production signal, deposited mass, and mechanical stiffness at the same instant.

## Key modeling checkpoint

State explicitly which quantities are conserved, which are constitutive assumptions, and which are experimentally observable.
