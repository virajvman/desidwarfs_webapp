# Home page embedded figures

This folder is referenced by `index.html` to embed the catalog summary figures directly on the Home page. Each figure is shown as a web-friendly raster (`.jpg`/`.png`, ~150&ndash;320 dpi renders of the paper plots) that links to the full-resolution source PDF.

## Expected filenames

- `dwarf_galaxy_bowtie.{jpg,pdf}` — polar redshift slice of DESI DR1 dwarf galaxies in the cosmic web, with massive SDSS/NSA galaxies overplotted
- `zred_mstar_2d.{png,pdf}` — stellar mass vs. redshift for the four target samples (BGS Bright, BGS Faint, LOWZ, ELG)
- `dwarf_imgs_grid.{jpg,pdf}` — grid of example dwarf images binned by r-band magnitude and stellar mass
- `dwarf_egs.{png,pdf}` — example DESI spectra + Legacy Surveys cutouts of low-mass dwarfs
- `desi_logo.png` — DESI logo used in the Acknowledgements section

## Notes

- The Home page uses relative paths like `catalog_pdfs/dwarf_galaxy_bowtie.jpg`.
- Source PDFs live in `~/DESI2_LOWZ/quenched_fracs_nbs/paper_plots/` on NERSC; rasters were generated with Ghostscript (`gs -sDEVICE=png16m -dTextAlphaBits=4 -dGraphicsAlphaBits=4`) and image-heavy panels converted to JPEG.
