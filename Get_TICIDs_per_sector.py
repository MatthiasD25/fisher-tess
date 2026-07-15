# Python script for assigning Tmag <= 10 stars from the reduced sub-catalogs, created in "Get_reduced_TIC.ipynb", to TESS sectors 
# using tess-point: https://github.com/tessgi/tess-point

import os
import sys
import numpy as np
import pandas as pd
import multiprocessing as mp
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from tess_stars2px import tess_stars2px_function_entry


def process_star(args):
    """
    Worker function for multiprocessing.
    Determines the TESS sectors in which a given star is observed.
    """

    # Unpack input parameters
    ticid, ra, dec, tmag, sector_min, sector_max = args

    try:
        # Determine TESS sector coverage and detector information using tess-point
        (
            outID,
            outEclipLong,
            outEclipLat,
            sectors,
            cameras,
            ccds,
            colpix,
            rowpix,
            scinfo
        ) = tess_stars2px_function_entry(
            ticid,
            ra,
            dec
        )

    # Return failed TIC IDs and error messages
    except Exception as e:
        return {
            "error": (ticid, str(e))
        }

    # Ensure sectors are handled as an iterable integer array
    sectors = np.atleast_1d(
        sectors
    ).astype(int)

    results = []

    # Store all sectors within the requested range containing the star
    for sec in sectors:

        if sector_min <= sec <= sector_max:

            results.append(
                (
                    sec,
                    ticid,
                    ra,
                    dec,
                    tmag
                )
            )

    return {
        "results": results
    }


def main():

    # ======================================
    # SETTINGS
    # ======================================

    # Select hemisphere and declination range of the reduced TIC catalog
    hemisphere = "N"
    dec_num = 10

    # Define input catalog depending on hemisphere
    if hemisphere == "S":

        input_csv = (
            f"tic/TIC_reduced_"
            f"{hemisphere}{dec_num}_"
            f"{hemisphere}{dec_num-2}"
            f"_Tmag_10.csv"
        )

    elif hemisphere == "N":

        input_csv = (
            f"tic/TIC_reduced_"
            f"{hemisphere}{dec_num}_"
            f"{hemisphere}{dec_num+2}"
            f"_Tmag_10.csv"
        )

    # Output file prefix for sector-wise TIC lists
    output_prefix = "TICIDs_sector_"

    # Process all sectors of Cycles 1-7
    sector_min = 1
    sector_max = 96

    # Use all available CPU cores for parallel processing
    n_cores = os.cpu_count()

    print(
        f"[SYSTEM] Using "
        f"{n_cores} CPU cores"
    )

    # ======================================
    # LOAD EXISTING FILES
    # ======================================

    # Store already assigned TIC IDs for each sector to avoid duplicates
    existing_ids = defaultdict(set)

    print(
        "[SYSTEM] Loading "
        f"existing sector files / {hemisphere}{dec_num}..."
    )

    # Load existing sector catalogs if available
    for sec in range(
        sector_min,
        sector_max + 1
    ):

        file_path = (
            f"tic/"
            f"{output_prefix}"
            f"{sec}.csv"
        )

        if os.path.exists(
            file_path
        ):

            df_old = pd.read_csv(
                file_path
            )

            if not df_old.empty:

                existing_ids[
                    sec
                ] = set(
                    df_old[
                        "ID"
                    ].values
                )

            print(
                f"[SYSTEM] "
                f"Sector {sec}: "
                f"loaded "
                f"{len(existing_ids[sec])} "
                f"existing IDs"
            )

        else:

            print(
                f"[SYSTEM] "
                f"Sector {sec}: "
                f"no existing file"
            )

    # ======================================
    # LOAD INPUT
    # ======================================

    # Load reduced TIC catalog containing only relevant stellar parameters
    df = pd.read_csv(
        input_csv
    )

    # Extract required columns
    ids = df["ID"].values
    ras = df["ra"].values
    decs = df["dec"].values
    tmags = df["Tmag"].values

    n_total = len(df)

    print(
        f"[SYSTEM] Processing "
        f"{n_total} stars..."
    )

    # Create multiprocessing input arguments
    args_list = [

        (
            ids[i],
            ras[i],
            decs[i],
            tmags[i],
            sector_min,
            sector_max
        )

        for i in range(
            n_total
        )
    ]

    # ======================================
    # MULTIPROCESSING
    # ======================================

    # Store newly assigned TIC IDs for each sector
    new_sector_dict = defaultdict(list)

    # Assign stars to sectors in parallel
    with ProcessPoolExecutor(
        max_workers=n_cores
    ) as executor:

        for i, output in enumerate(

            executor.map(
                process_star,
                args_list,
                chunksize=100
            ),

            start=1
        ):

            sys.stdout.write(
                f"\r[SYSTEM] "
                f"{i}/{n_total}"
            )

            sys.stdout.flush()

            # Handle failed tess-point assignments
            if "error" in output:

                ticid, err = (
                    output[
                        "error"
                    ]
                )

                sys.stdout.write(
                    f"\n[ERROR] "
                    f"TIC {ticid}: "
                    f"{err}\n"
                )

                continue

            # Add new sector assignments while avoiding duplicates
            for (
                sec,
                ticid,
                ra,
                dec,
                tmag
            ) in output[
                "results"
            ]:

                if (
                    ticid
                    in existing_ids[
                        sec
                    ]
                ):
                    continue

                existing_ids[
                    sec
                ].add(
                    ticid
                )

                new_sector_dict[
                    sec
                ].append(

                    [
                        ticid,
                        ra,
                        dec,
                        tmag
                    ]
                )

    sys.stdout.write("\n")

    # ======================================
    # WRITE OUTPUT
    # ======================================

    print(
        "[SYSTEM] "
        "Writing updates..."
    )

    # Append newly identified stars to the corresponding sector files
    for sec in range(
        sector_min,
        sector_max + 1
    ):

        data = (
            new_sector_dict
            .get(sec, [])
        )

        if not data:
            continue

        out_file = (
            f"tic/"
            f"{output_prefix}"
            f"{sec}.csv"
        )

        df_new = pd.DataFrame(

            data,

            columns=[
                "ID",
                "ra",
                "dec",
                "Tmag"
            ]
        )

        # Add header only when creating a new file
        write_header = (
            not os.path.exists(
                out_file
            )
        )

        df_new.to_csv(

            out_file,

            mode="a",

            header=write_header,

            index=False
        )

        print(
            f"[SYSTEM] "
            f"Sector {sec}: "
            f"added "
            f"{len(df_new)} "
            f"new stars"
        )

    print("[SYSTEM] Done.")


if __name__ == "__main__":

    # Required for multiprocessing compatibility on some systems (e.g. Windows)
    mp.freeze_support()

    main()