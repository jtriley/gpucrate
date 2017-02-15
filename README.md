# gpucrate

gpucrate creates hard-linked GPU driver (currently just NVIDIA) volumes for use
with docker, singularity, etc. This allows the exact system drivers to be
linked into a container without needing to maintain a separate container per
driver version.
