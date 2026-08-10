# Isotaxis Artifact Evaluation

This repository contains the artifact for *Isotaxis: Optimal Asynchronous
Byzantine Consensus with Ordering Linearizability*. See
[README-AE.md](README-AE.md) for the complete build, evaluation, and expected
result instructions.

## Bundled HotStuff source

The artifact includes a modified snapshot of `hotstuff_rs` 0.4.0 under
[hotstuff_rs/](hotstuff_rs/). All builds automatically use this bundled version
through the local Cargo path dependency in
[hotstuff_runner/Cargo.toml](hotstuff_runner/Cargo.toml).

Clone the artifact with:

```bash
git clone https://github.com/xrxrxrxrxr/Isotaxis-ArtifactEvaluation.git
cd Isotaxis-ArtifactEvaluation
```

## Quick local run

```bash
./run_test.sh
```

For the local adversarial run, AWS experiments, configuration, and cleanup
commands, follow [README-AE.md](README-AE.md).
