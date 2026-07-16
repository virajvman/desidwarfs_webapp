"""Regenerate the webapp parquet from the full DR1 dwarf catalog.

Mirrors notebooks/catalog_paper/catalog_web_prep.ipynb, plus:
  - rows sorted by RA (better compression, future range-request queries)
  - writes both snappy and zstd variants for a size comparison
  - verifies content against the parquet currently in the webapp repo
"""
import os
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from astropy.table import Table, hstack

FITS = "/global/cfs/cdirs/desi/users/virajvm/desi_dwarf_cats/iron/desi_dr1_dwarf_catalog.fits"
CUR = "/global/homes/v/virajvm/desidwarfs_webapp/desi_dwarfs.parquet"
OUTDIR = os.path.dirname(os.path.abspath(__file__))

print("reading MAIN ...", flush=True)
data_cat = Table.read(FITS, hdu="MAIN")
print("reading FASTSPEC ...", flush=True)
fspec_cat = Table.read(FITS, hdu="FASTSPEC")

mask = data_cat["DWARF_MASKBIT"] == 0
data_cat = data_cat[mask]
fspec_cat = fspec_cat[mask]
print(f"rows after DWARF_MASKBIT==0: {len(data_cat):,}", flush=True)

main_cat = data_cat["TARGETID", "Z", "RA", "DEC", "LOG_MSTAR_M24", "MAG_R", "R50_R"]
main_cat["BA"] = data_cat["SHAPE_PARAMS"][:, 0]
main_cat["PA"] = data_cat["SHAPE_PARAMS"][:, 1]

# Ship the catalog's boolean membership flags directly (no consolidated
# SAMPLE priority column) — matches the FITS data model, and flags can
# legitimately overlap (e.g. ~48k galaxies are both BGS_BRIGHT and LOWZ).
flag_cols = ["IS_BGS_BRIGHT", "IS_BGS_FAINT", "IS_LOWZ", "IS_ELG", "IS_OTHER"]
for c in flag_cols:
    main_cat[c] = np.asarray(data_cat[c], dtype=bool)

n_noflag = int((~np.any([main_cat[c] for c in flag_cols], axis=0)).sum())
print(f"rows with no membership flag set: {n_noflag} (should be 0)")

tot_cat = hstack([main_cat, fspec_cat["HALPHA_FLUX"]])

df = tot_cat.to_pandas()
df["TARGETID"] = df["TARGETID"].astype("int64")
df = df.astype({
    "Z": "float32",
    "RA": "float64",
    "DEC": "float64",
    "LOG_MSTAR_M24": "float32",
    "MAG_R": "float32",
    "HALPHA_FLUX": "float32",
    "BA": "float32",
    "PA": "float32",
    "R50_R": "float32",
})

df = df.sort_values("RA", kind="stable").reset_index(drop=True)

for comp in ("snappy", "zstd"):
    path = os.path.join(OUTDIR, f"desi_dwarfs_{comp}.parquet")
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(table, path, compression=comp, row_group_size=100_000,
                   use_dictionary=True, version="2.6")
    print(f"wrote {path}  {os.path.getsize(path)/1e6:.1f} MB", flush=True)

# ---- verification against the parquet currently deployed ----
print("\nverifying against current webapp parquet ...", flush=True)
old = pq.read_table(CUR).to_pandas()
new = pd.read_parquet(os.path.join(OUTDIR, "desi_dwarfs_snappy.parquet"))

print(f"old rows: {len(old):,}  new rows: {len(new):,}")
print(f"old cols: {sorted(old.columns.tolist())}")
print(f"new cols: {sorted(new.columns.tolist())}")

old_ids = set(old["TARGETID"].astype("int64"))
new_ids = set(new["TARGETID"].astype("int64"))
print(f"TARGETID sets equal: {old_ids == new_ids}")
if old_ids != new_ids:
    print(f"  only in old: {len(old_ids - new_ids)}, only in new: {len(new_ids - old_ids)}"
          "  (expected: CFS catalog is a newer version than the pscratch v1.0 file)")

# compare matched rows only (float columns; SAMPLE no longer shipped)
o = old[old["TARGETID"].isin(new_ids)].sort_values("TARGETID").reset_index(drop=True)
n = new[new["TARGETID"].isin(old_ids)].sort_values("TARGETID").reset_index(drop=True)
print(f"comparing {len(o):,} matched rows:")
for c in [c for c in o.columns if c in n.columns and c not in ("TARGETID", "SAMPLE")]:
    ov, nv = o[c].values.astype("float64"), n[c].values.astype("float64")
    both_nan = np.isnan(ov) & np.isnan(nv)
    close = np.isclose(ov, nv, rtol=1e-6, equal_nan=True) | both_nan
    print(f"  {c}: mismatches = {int((~close).sum())}")

print("\nRA sorted:", bool((np.diff(new['RA'].values) >= 0).all()))
print("flag counts:")
for c in flag_cols:
    print(f"  {c}: {int(new[c].sum()):,}")

print(f"\nold file size: {os.path.getsize(CUR)/1e6:.1f} MB")
print("done", flush=True)
