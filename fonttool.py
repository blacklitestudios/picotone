import sys
import io
from fontTools.ttLib import TTFont
from fontTools.merge import Merger
from fontTools.subset import Subsetter, Options
from fontTools.ttLib.scaleUpem import scale_upem  # <--- NEW IMPORT

def get_codepoints(font):
    """
    Returns a set of all unicode codepoints supported by the font.
    """
    codepoints = set()
    cmap = font.getBestCmap()
    if cmap:
        for code in cmap.keys():
            codepoints.add(code)
    return codepoints

def merge_fonts(base_path, source_path, output_path):
    # 1. Load Fonts
    print(f"Loading base font: {base_path}")
    base_font = TTFont(base_path)
    
    print(f"Loading source font: {source_path}")
    source_font = TTFont(source_path)

    # --- FIX FOR ASSERTION ERROR ---
    # Check if Units Per Em match. If not, scale the source font.
    base_upem = base_font['head'].unitsPerEm
    source_upem = source_font['head'].unitsPerEm

    if base_upem != source_upem:
        print(f"UPEM Mismatch detected! Base: {base_upem}, Source: {source_upem}")
        print(f"Scaling source font from {source_upem} to {base_upem}...")
        scale_upem(source_font, base_upem)
    # -------------------------------

    # 2. Identify missing codepoints
    base_codepoints = get_codepoints(base_font)
    source_codepoints = get_codepoints(source_font)
    
    missing_codepoints = source_codepoints - base_codepoints
    
    if not missing_codepoints:
        print("No new codepoints found in the source font. Nothing to merge.")
        return

    print(f"Found {len(missing_codepoints)} new codepoints to merge.")

    # 3. Subset the Source font
    print("Subsetting source font to isolate new glyphs...")
    options = Options()
    # Drop tables that cause merge conflicts or aren't needed for the patch
    options.drop_tables += ['GSUB', 'GPOS', 'FFTM', 'GDEF', 'BASE', 'JSTF', 'DSIG']
    options.layout_features = "*" 
    
    subsetter = Subsetter(options=options)
    subsetter.populate(unicodes=list(missing_codepoints))
    subsetter.subset(source_font)

    # 4. Save the subsetted font to a temporary memory buffer
    with io.BytesIO() as subset_stream:
        source_font.save(subset_stream)
        subset_stream.seek(0)

        # 5. Merge
        print("Merging fonts...")
        merger = Merger()
        
        # Merge the base path with the in-memory scaled subset
        merged_font = merger.merge([base_path, subset_stream])

        print(f"Saving result to {output_path}...")
        merged_font.save(output_path)
        print("Done.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python merge_fonttools.py <base.ttf> <source.ttf> <output.ttf>")
        sys.exit(1)

    base = sys.argv[1]
    source = sys.argv[2]
    output = sys.argv[3]

    merge_fonts(base, source, output)