"""Reproducible extension of CISC7204 Exercise 8.02 by CHEN YU."""
from pathlib import Path
import csv
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import BoundaryNorm
import numpy as np

ROOT = Path(__file__).resolve().parent

def main():
    source = ROOT / 'us_states.json'
    features = json.loads(source.read_text())['features']
    assert len(features) == 52
    states = [f for f in features if f['properties']['NAME'] not in
              ('District of Columbia', 'Puerto Rico')]
    assert len(states) == 50
    rows = sorted([(f['properties']['NAME'], float(f['properties']['CENSUSAREA']))
                   for f in states], key=lambda x: x[1], reverse=True)
    assert all(np.isfinite(area) and area > 0 for _, area in rows)
    output = ROOT
    output.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig, ax = plt.subplots(figsize=(12, 7))
    patches, areas = [], []
    for feature in states:
        if feature['properties']['NAME'] in ('Alaska', 'Hawaii'):
            continue
        geometry = feature['geometry']
        polygons = ([geometry['coordinates']] if geometry['type'] == 'Polygon'
                    else geometry['coordinates'])
        for polygon in polygons:
            patches.append(Polygon(polygon[0], closed=True))
            areas.append(feature['properties']['CENSUSAREA'])
    cmap = plt.get_cmap('Reds', 10)
    norm = BoundaryNorm(np.linspace(0, 300000, 11), cmap.N)
    collection = PatchCollection(patches, cmap=cmap, norm=norm,
                                 edgecolor='#555555', linewidth=0.6)
    collection.set_array(np.asarray(areas))
    ax.add_collection(collection)
    ax.set(xlim=(-125, -66), ylim=(24, 50), xlabel='Longitude', ylabel='Latitude')
    ax.set_aspect(1 / np.cos(np.radians(38)))
    ax.set_title('Land area across the contiguous United States', loc='left',
                 fontsize=19, fontweight='bold', pad=16)
    fig.colorbar(collection, ax=ax, shrink=0.7, label='Land area (square miles)')
    fig.text(0.08, 0.04, '48 states shown; Alaska and Hawaii excluded from this view. '
             'Unprojected coordinates with a fixed aspect adjustment.\n'
             'Source: Packt Workshops GeoJSON, CENSUSAREA field. Historical teaching data.', fontsize=9)
    fig.subplots_adjust(bottom=0.18, top=0.88)
    fig.savefig(output / 'state_area_map.png', dpi=160, facecolor='white')
    plt.close(fig)

    top = rows[:10][::-1]
    fig, ax = plt.subplots(figsize=(11, 7))
    bars = ax.barh([name for name, _ in top], [area for _, area in top], color='#af302d')
    ax.bar_label(bars, labels=[f'{area:,.0f}' for _, area in top], padding=5, fontsize=10)
    ax.set_xlim(0, rows[0][1] * 1.22)
    ax.set_xlabel('Land area (square miles)')
    ax.set_title('Ten largest US states by land area', loc='left', fontsize=19,
                 fontweight='bold', pad=18)
    ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    ax.grid(axis='x', alpha=0.18)
    ax.set_axisbelow(True)
    fig.text(0.16, 0.035, 'Ranking includes all 50 states; DC and Puerto Rico excluded.\n'
             'Source: Packt Workshops GeoJSON, CENSUSAREA field. Historical teaching data.', fontsize=9)
    fig.subplots_adjust(left=0.16, bottom=0.17, right=0.97, top=0.88)
    fig.savefig(output / 'top_ten_states.png', dpi=160, facecolor='white')
    plt.close(fig)
    with (ROOT / 'state_area_summary.csv').open('w', newline='') as target:
        writer = csv.writer(target)
        writer.writerow(['state', 'land_area_square_miles'])
        writer.writerows(rows)
    facts = {'geojson_entries': len(features), 'states_ranked': len(rows),
             'largest_state': rows[0][0], 'largest_area_sq_miles': rows[0][1],
             'second_largest_state': rows[1][0], 'second_area_sq_miles': rows[1][1],
             'alaska_to_texas_ratio': rows[0][1] / rows[1][1],
             'smallest_state': rows[-1][0], 'smallest_area_sq_miles': rows[-1][1],
             'dataset_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
    (ROOT / 'findings.json').write_text(json.dumps(facts, indent=2) + '\n')
    print(json.dumps(facts, indent=2))

if __name__ == '__main__':
    main()
