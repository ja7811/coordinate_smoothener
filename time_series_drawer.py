import json
import pandas as pd
import argparse
import os
from typing import TypedDict, List
import plotly.express as px

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def load_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = [json.loads(line) for line in file if line.strip()]
    return data


# Target data has these types
# { code: "OK", matchings: [], tracepoints: [{ location: [double, double] }] }
class Step(TypedDict):
    intersections: List[dict]

class Leg(TypedDict):
    steps: List[dict]

class Matching(TypedDict):
    confidence: float
    legs: List[dict]
    weight_name: str
    geometry: str
    weight: float
    duration: float
    distance: float

class Tracepoint(TypedDict):
    location: List[float]

class OriginalMapData(TypedDict):
    timestampe: str
    lat: float
    lng: float
    dist: float
    pace: float
    alt: int
    cadence: int
    bpm: int
    isRunning: bool

class OsrmMapData(TypedDict):
    code: str
    matchings: List[dict]
    tracepoints: List[Tracepoint]

def main(input_files, osrm_file = None, output_file=None):
    all_dataframes = []
    colors = ["red", "blue", "black", "green"]
    color_map = {}
    
    for i, file_path in enumerate(input_files):
        # Load data
        data = load_jsonl(file_path)
        
        # Create DataFrame
        df = pd.DataFrame({
            "lon": [item["lng"] for item in data],
            "lat": [item["lat"] for item in data],
        })
        
        # Assign type and color
        file_name = os.path.basename(file_path)
        df = df.assign(type=file_name)
        color_map[file_name] = colors[i % len(colors)]
        all_dataframes.append(df)
    
    # Combine all dataframes
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Load osrm data if provided
    if osrm_file:
        osrm_data: OsrmMapData = load_json(osrm_file)
        valid_tracepoints = [
            tp for tp in osrm_data['tracepoints']
            if tp is not None and 'location' in tp and isinstance(tp['location'], list) and len(tp['location']) == 2
        ]
        osrmDf = pd.DataFrame({
            "lon": [tp['location'][0] for tp in valid_tracepoints],
            "lat": [tp['location'][1] for tp in valid_tracepoints],
            "type": "OSRM Result"
        })
        color_map["OSRM Result"] = colors[len(all_dataframes) % len(colors)]
        combined_df = pd.concat([combined_df, osrmDf], ignore_index=True)

    # Multi Scatter View
    fig = px.scatter_map(
        combined_df,
        lat="lat",
        lon="lon",
        zoom=15,
        height=1200,
        map_style="open-street-map",
        title="Tracepoints Map (Multiple Files)",
        labels={"lat": "Latitude", "lon": "Longitude", "type": "Data Type"},
        hover_data=["lat", "lon", "type"],
        color="type",
        color_discrete_map=color_map,
        size_max=8
    )

    fig.update_layout(mapbox_style="open-street-map")
    
    # 지도 시각화 생성
    if output_file:
        fig.write_html(output_file)
        print(f"Map saved to {output_file}")
    else:
        fig.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='GPS 트레이스포인트 시각화')
    parser.add_argument('files', nargs='*', default=['dummy/data2.jsonl'], help='보여줄 JSONL 파일들 (기본값: dummy/data2.jsonl)')
    parser.add_argument('--osrm', help="OSRM API 응답 파일 경로 (선택적)")
    parser.add_argument('--output', '-o', help='HTML 출력 파일 경로 (지정하지 않으면 브라우저로 바로 표시)')
    args = parser.parse_args()
    
    main(args.files, args.osrm, args.output)