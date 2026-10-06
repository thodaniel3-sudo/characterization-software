from pathlib import Path
import csv
import math


BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RAW_IMAGE_DIR = BASE_DIR / "data" / "raw" / "images"


# ============================================================
# GENERAL CSV FUNCTIONS
# ============================================================

def read_csv(filename):
    path = PROCESSED_DIR / filename

    if not path.exists():
        return []

    rows = []

    with open(path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            rows.append(dict(row))

    return rows


def to_float(value, default=None):
    try:
        if value is None:
            return default

        text = str(value).strip()

        if not text:
            return default

        return float(text)

    except (ValueError, TypeError):
        return default


def clean_number(value, decimals=4):
    if value is None:
        return "N/A"

    return round(float(value), decimals)


# ============================================================
# BET ANALYSIS
# ============================================================

def load_bet_summary():
    return read_csv("bet_summary.csv")


def get_bet_parameters():
    rows = load_bet_summary()

    parameters = []

    for row in rows:

        parameter = row.get("parameter", "").strip()
        method = row.get("method", "").strip()
        value = to_float(row.get("value"))
        unit = row.get("unit", "").strip()

        if parameter:
            parameters.append({
                "parameter": parameter,
                "method": method,
                "value": value,
                "unit": unit
            })

    return parameters


def get_bet_surface_area():
    rows = load_bet_summary()

    preferred = [
        "BET surface area",
        "BET Surface Area"
    ]

    for preferred_name in preferred:

        for row in rows:

            parameter = row.get("parameter", "").strip()

            if parameter == preferred_name:

                value = to_float(row.get("value"))

                if value is not None:
                    return value

    return None


def get_bet_isotherm():
    return read_csv("bet_isotherm.csv")


def get_bet_isotherm_summary():

    rows = get_bet_isotherm()

    adsorption = []
    desorption = []

    for row in rows:

        pressure = to_float(row.get("relative_pressure_p_p0"))
        volume = to_float(row.get("volume_adsorbed_cm3_g_STP"))
        branch = row.get("branch", "").strip().lower()

        if pressure is None or volume is None:
            continue

        point = {
            "pressure": pressure,
            "volume": volume
        }

        if branch == "adsorption":
            adsorption.append(point)

        elif branch == "desorption":
            desorption.append(point)

    return {
        "total_points": len(adsorption) + len(desorption),
        "adsorption_points": len(adsorption),
        "desorption_points": len(desorption)
    }


# ============================================================
# BJH ANALYSIS
# ============================================================

def load_bjh_adsorption():
    return read_csv("bjh_psd_adsorption.csv")


def load_bjh_desorption():
    return read_csv("bjh_psd_desorption.csv")


def _bjh_distribution_mode(rows):

    best_radius = None
    best_dv = None

    for row in rows:

        radius = to_float(row.get("pore_radius_nm"))
        dv = to_float(row.get("dV_logr_cm3_g"))

        if radius is None or dv is None:
            continue

        if dv < 0:
            continue

        if best_dv is None or dv > best_dv:

            best_dv = dv
            best_radius = radius

    return best_radius, best_dv


def get_bjh_mode_radius(branch="adsorption"):

    branch = branch.lower().strip()

    if branch == "desorption":
        rows = load_bjh_desorption()

    else:
        rows = load_bjh_adsorption()

    radius, _ = _bjh_distribution_mode(rows)

    return radius


def get_bjh_mode_diameter(branch="adsorption"):

    radius = get_bjh_mode_radius(branch)

    if radius is None:
        return None

    return radius * 2.0


def get_bjh_mode_differential_volume(branch="adsorption"):

    branch = branch.lower().strip()

    if branch == "desorption":
        rows = load_bjh_desorption()

    else:
        rows = load_bjh_adsorption()

    _, dv = _bjh_distribution_mode(rows)

    return dv


def get_bjh_total_pore_volume(branch="adsorption"):

    branch = branch.lower().strip()

    if branch == "desorption":
        rows = load_bjh_desorption()

    else:
        rows = load_bjh_adsorption()

    values = []

    for row in rows:

        value = to_float(
            row.get("cum_pore_volume_cm3_g")
        )

        if value is not None:
            values.append(value)

    if not values:
        return None

    return max(values)


def get_bjh_surface_area(branch="adsorption"):

    branch = branch.lower().strip()

    if branch == "desorption":
        rows = load_bjh_desorption()

    else:
        rows = load_bjh_adsorption()

    values = []

    for row in rows:

        value = to_float(
            row.get("cum_pore_surface_area_m2_g")
        )

        if value is not None:
            values.append(value)

    if not values:
        return None

    return max(values)


def get_bjh_summary():

    adsorption_radius = get_bjh_mode_radius("adsorption")
    desorption_radius = get_bjh_mode_radius("desorption")

    return {
        "adsorption_mode_radius_nm": adsorption_radius,
        "adsorption_mode_diameter_nm": (
            adsorption_radius * 2
            if adsorption_radius is not None
            else None
        ),
        "adsorption_mode_dv": get_bjh_mode_differential_volume(
            "adsorption"
        ),
        "adsorption_total_pore_volume_cm3_g":
            get_bjh_total_pore_volume("adsorption"),

        "desorption_mode_radius_nm": desorption_radius,
        "desorption_mode_diameter_nm": (
            desorption_radius * 2
            if desorption_radius is not None
            else None
        ),
        "desorption_mode_dv": get_bjh_mode_differential_volume(
            "desorption"
        ),
        "desorption_total_pore_volume_cm3_g":
            get_bjh_total_pore_volume("desorption")
    }


# ============================================================
# DFT ANALYSIS
# ============================================================

def load_dft_pore_size():
    return read_csv("dft_pore_size.csv")


def load_dft_fitting():
    return read_csv("dft_fitting.csv")


def get_dft_peak_pore_width():

    rows = load_dft_pore_size()

    best_width = None
    best_dv = None

    for row in rows:

        width = to_float(row.get("pore_width_nm"))
        dv = to_float(row.get("dVd_cm3_nm_g"))

        if width is None or dv is None:
            continue

        if dv <= 0:
            continue

        if best_dv is None or dv > best_dv:

            best_dv = dv
            best_width = width

    return best_width


def get_dft_peak_differential_volume():

    rows = load_dft_pore_size()

    best_dv = None

    for row in rows:

        dv = to_float(row.get("dVd_cm3_nm_g"))

        if dv is None or dv <= 0:
            continue

        if best_dv is None or dv > best_dv:
            best_dv = dv

    return best_dv


def get_dft_total_pore_volume():

    rows = load_dft_pore_size()

    values = []

    for row in rows:

        value = to_float(
            row.get("cum_pore_volume_cm3_g")
        )

        if value is not None:
            values.append(value)

    if not values:
        return None

    return max(values)


def get_dft_total_surface_area():

    rows = load_dft_pore_size()

    values = []

    for row in rows:

        value = to_float(
            row.get("cum_surface_area_m2_g")
        )

        if value is not None:
            values.append(value)

    if not values:
        return None

    return max(values)


def get_dft_summary():

    return {
        "peak_pore_width_nm": get_dft_peak_pore_width(),
        "peak_differential_volume_cm3_nm_g":
            get_dft_peak_differential_volume(),
        "total_pore_volume_cm3_g":
            get_dft_total_pore_volume(),
        "total_surface_area_m2_g":
            get_dft_total_surface_area()
    }


def calculate_dft_fit_statistics():

    rows = load_dft_fitting()

    measured = []
    fitted = []

    for row in rows:

        m = to_float(
            row.get("measured_volume_cm3_g")
        )

        f = to_float(
            row.get("fitted_volume_cm3_g")
        )

        if m is None or f is None:
            continue

        measured.append(m)
        fitted.append(f)

    if not measured:
        return {
            "points": 0,
            "rmse": None,
            "mae": None,
            "r2": None
        }

    n = len(measured)

    mse = sum(
        (a - b) ** 2
        for a, b in zip(measured, fitted)
    ) / n

    rmse = math.sqrt(mse)

    mae = sum(
        abs(a - b)
        for a, b in zip(measured, fitted)
    ) / n

    mean_measured = sum(measured) / n

    ss_total = sum(
        (a - mean_measured) ** 2
        for a in measured
    )

    ss_residual = sum(
        (a - b) ** 2
        for a, b in zip(measured, fitted)
    )

    if ss_total == 0:
        r2 = None
    else:
        r2 = 1 - (ss_residual / ss_total)

    return {
        "points": n,
        "rmse": rmse,
        "mae": mae,
        "r2": r2
    }


# ============================================================
# EDS
# ============================================================

def load_eds():
    return read_csv("eds_results.csv")


def get_eds_total():

    rows = load_eds()

    total = 0.0

    for row in rows:

        value = to_float(
            row.get("weight_percent")
        )

        if value is not None:
            total += value

    return total


def get_major_elements():

    rows = load_eds()

    elements = []

    for row in rows:

        element = row.get("element", "").strip()
        weight = to_float(row.get("weight_percent"))
        sigma = to_float(row.get("sigma"))

        if not element or weight is None:
            continue

        elements.append({
            "element": element,
            "weight_percent": weight,
            "sigma": sigma
        })

    elements.sort(
        key=lambda item: item["weight_percent"],
        reverse=True
    )

    return elements


def get_eds_summary():

    elements = get_major_elements()

    return {
        "total_weight_percent": get_eds_total(),
        "element_count": len(elements),
        "elements": elements
    }


# ============================================================
# XRD / SRD ANALYSIS
# ============================================================

def load_xrd():
    return read_csv("xrd_pattern.csv")


def get_xrd_peak():

    rows = load_xrd()

    points = []

    for row in rows:

        theta = to_float(
            row.get("two_theta_deg")
        )

        intensity = to_float(
            row.get("intensity_counts")
        )

        if theta is None or intensity is None:
            continue

        points.append({
            "two_theta": theta,
            "intensity": intensity
        })

    if not points:
        return None

    return max(
        points,
        key=lambda item: item["intensity"]
    )


def detect_xrd_peaks(min_prominence=25):

    rows = load_xrd()

    points = []

    for row in rows:

        theta = to_float(
            row.get("two_theta_deg")
        )

        intensity = to_float(
            row.get("intensity_counts")
        )

        if theta is None or intensity is None:
            continue

        points.append((theta, intensity))

    if len(points) < 3:
        return []

    peaks = []

    for i in range(1, len(points) - 1):

        left = points[i - 1][1]
        current = points[i][1]
        right = points[i + 1][1]

        if current <= left or current <= right:
            continue

        local_min = min(left, right)
        prominence = current - local_min

        if prominence >= min_prominence:

            peaks.append({
                "two_theta": points[i][0],
                "intensity": current,
                "prominence": prominence
            })

    peaks.sort(
        key=lambda item: item["intensity"],
        reverse=True
    )

    return peaks


def get_xrd_detected_peaks():

    return detect_xrd_peaks()


def get_xrd_peak_position():

    peak = get_xrd_peak()

    if peak is None:
        return None

    return peak["two_theta"]


def get_xrd_peak_intensity():

    peak = get_xrd_peak()

    if peak is None:
        return None

    return peak["intensity"]


def get_xrd_summary():

    strongest = get_xrd_peak()
    peaks = get_xrd_detected_peaks()

    return {
        "strongest_point": strongest,
        "detected_peak_count": len(peaks),
        "detected_peaks": peaks
    }


# ============================================================
# SEM / TEM
# ============================================================

def load_sem_metadata():
    return read_csv("sem_metadata.csv")


def get_sem_image_count():

    folder = RAW_IMAGE_DIR / "sem"

    if not folder.exists():
        return 0

    return len([
        file for file in folder.iterdir()
        if file.is_file()
        and file.suffix.lower() in {
            ".tif",
            ".tiff",
            ".png",
            ".jpg",
            ".jpeg"
        }
    ])


def get_tem_image_count():

    folder = RAW_IMAGE_DIR / "tem"

    if not folder.exists():
        return 0

    return len([
        file for file in folder.iterdir()
        if file.is_file()
        and file.suffix.lower() in {
            ".tif",
            ".tiff",
            ".png",
            ".jpg",
            ".jpeg"
        }
    ])


def get_image_paths():

    results = {
        "sem": [],
        "tem": []
    }

    for category in ["sem", "tem"]:

        folder = RAW_IMAGE_DIR / category

        if not folder.exists():
            continue

        for file in sorted(folder.iterdir()):

            if (
                file.is_file()
                and file.suffix.lower()
                in {".tif", ".tiff", ".png", ".jpg", ".jpeg"}
            ):

                results[category].append(file)

    return results


# ============================================================
# BASIC STATISTICS
# ============================================================

def calculate_mean(values):

    values = [
        float(value)
        for value in values
        if value is not None
    ]

    if not values:
        return None

    return sum(values) / len(values)


def calculate_standard_deviation(values):

    values = [
        float(value)
        for value in values
        if value is not None
    ]

    if len(values) < 2:
        return 0.0

    mean = calculate_mean(values)

    variance = sum(
        (value - mean) ** 2
        for value in values
    ) / (len(values) - 1)

    return math.sqrt(variance)


# ============================================================
# OVERALL SUMMARY
# ============================================================

def get_characterization_summary():

    return {
        "BET surface area (m²/g)": get_bet_surface_area(),

        "BJH adsorption mode radius (nm)":
            get_bjh_mode_radius("adsorption"),

        "BJH adsorption mode diameter (nm)":
            get_bjh_mode_diameter("adsorption"),

        "BJH adsorption pore volume (cm³/g)":
            get_bjh_total_pore_volume("adsorption"),

        "BJH desorption mode radius (nm)":
            get_bjh_mode_radius("desorption"),

        "BJH desorption mode diameter (nm)":
            get_bjh_mode_diameter("desorption"),

        "BJH desorption pore volume (cm³/g)":
            get_bjh_total_pore_volume("desorption"),

        "DFT peak pore width (nm)":
            get_dft_peak_pore_width(),

        "DFT pore volume (cm³/g)":
            get_dft_total_pore_volume(),

        "DFT surface area (m²/g)":
            get_dft_total_surface_area(),

        "XRD strongest intensity point (2θ)":
            get_xrd_peak_position(),

        "XRD strongest intensity":
            get_xrd_peak_intensity(),

        "XRD detected peaks":
            len(get_xrd_detected_peaks()),

        "EDS element count":
            len(get_major_elements()),

        "EDS total weight (%)":
            get_eds_total(),

        "SEM image count":
            get_sem_image_count(),

        "TEM image count":
            get_tem_image_count()
    }


def check_data_files():

    required = [
        "bet_isotherm.csv",
        "bet_summary.csv",
        "bjh_psd_adsorption.csv",
        "bjh_psd_desorption.csv",
        "dft_fitting.csv",
        "dft_pore_size.csv",
        "eds_results.csv",
        "sem_metadata.csv",
        "xrd_pattern.csv"
    ]

    results = {}

    for filename in required:

        results[filename] = (
            PROCESSED_DIR / filename
        ).exists()

    return results


def get_dataset_statistics():

    results = check_data_files()

    total = len(results)
    available = sum(
        1 for value in results.values()
        if value
    )

    percentage = (
        available / total * 100
        if total
        else 0
    )

    return {
        "available": available,
        "total": total,
        "percentage": percentage
    }


def evaluate_characterization():

    evaluation = []

    if get_bet_surface_area() is not None:
        evaluation.append(
            "BET analysis provides a measurable specific surface area."
        )

    if get_bjh_mode_radius("adsorption") is not None:
        evaluation.append(
            "BJH adsorption data provide a pore-size distribution."
        )

    if get_bjh_mode_radius("desorption") is not None:
        evaluation.append(
            "BJH desorption data provide a pore-size distribution."
        )

    if get_dft_peak_pore_width() is not None:
        evaluation.append(
            "DFT analysis provides a pore-width distribution."
        )

    if get_eds_total() is not None:
        evaluation.append(
            "EDS provides elemental composition data."
        )

    if len(get_xrd_detected_peaks()) > 0:
        evaluation.append(
            "XRD data contain detected local intensity maxima."
        )

    sem_count = get_sem_image_count()
    tem_count = get_tem_image_count()

    if sem_count:
        evaluation.append(
            f"{sem_count} SEM images are available for morphological examination."
        )

    if tem_count:
        evaluation.append(
            f"{tem_count} TEM images are available for morphological examination."
        )

    return evaluation


if __name__ == "__main__":

    print("=" * 70)
    print("MWCNT CHARACTERIZATION ANALYSIS TEST")
    print("=" * 70)

    print()
    print("BET SURFACE AREA")
    print(get_bet_surface_area())

    print()
    print("BJH SUMMARY")
    for key, value in get_bjh_summary().items():
        print(f"{key}: {value}")

    print()
    print("DFT SUMMARY")
    for key, value in get_dft_summary().items():
        print(f"{key}: {value}")

    print()
    print("DFT FIT STATISTICS")
    for key, value in calculate_dft_fit_statistics().items():
        print(f"{key}: {value}")

    print()
    print("EDS SUMMARY")
    print(get_eds_summary())

    print()
    print("XRD SUMMARY")
    print(get_xrd_summary())

    print()
    print("SEM IMAGES:", get_sem_image_count())
    print("TEM IMAGES:", get_tem_image_count())

    print()
    print("DATASET STATUS")
    print(get_dataset_statistics())

    print()
    print("EVALUATION")

    for item in evaluate_characterization():
        print("-", item)

    print()
    print("ANALYSIS TEST COMPLETE")