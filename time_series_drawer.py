import json
import pandas as pd
import argparse
import os
import plotly.express as px

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def load_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = [json.loads(line) for line in file if line.strip()]
    return data

def main(input_files, output_file=None):
    all_dataframes = []
    all_original_data = []  # 원본 데이터 저장
    colors = ["red", "blue", "black", "green"]
    color_map = {}
    
    for i, file_path in enumerate(input_files):
        # Load data
        data = load_jsonl(file_path)
        
        # Create DataFrame with additional hover data
        df = pd.DataFrame({
            "lon": [item["lng"] for item in data],
            "lat": [item["lat"] for item in data],
            "timestamp": [item.get("timeStamp", "N/A") for item in data],
            "altitude": [item.get("alt", "N/A") for item in data],
            "pace": [item.get("pace", "N/A") for item in data],
            "bpm": [item.get("bpm", "N/A") for item in data],
            "distance": [item.get("dist", "N/A") for item in data],
            "angle": [item.get("angle", "N/A") for item in data]
        })
        
        # Assign type and color
        file_name = os.path.basename(file_path)
        df = df.assign(type=file_name)
        color_map[file_name] = colors[i % len(colors)]
        all_dataframes.append(df)
    
    # Combine all dataframes
    combined_df = pd.concat(all_dataframes, ignore_index=True)

    # Multi Line + Scatter View
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    # Add line traces first (so they appear behind points)
    for file_type in combined_df['type'].unique():
        df_subset = combined_df[combined_df['type'] == file_type]
        fig.add_trace(go.Scattermap(
            lat=df_subset['lat'],
            lon=df_subset['lon'],
            mode='lines',
            line=dict(color=color_map[file_type], width=2),
            name=f"{file_type} (line)",
            showlegend=False
        ))
    
    # Add scatter points on top
    for file_type in combined_df['type'].unique():
        df_subset = combined_df[combined_df['type'] == file_type]
        fig.add_trace(go.Scattermap(
            lat=df_subset['lat'],
            lon=df_subset['lon'],
            mode='markers',
            marker=dict(color=color_map[file_type], size=6),
            name=file_type,
            hovertemplate='<b>%{text}</b><br>' +
                         'Lat: %{lat}<br>' +
                         'Lon: %{lon}<br>' +
                         'Timestamp: %{customdata[0]}<br>' +
                        #  'Altitude: %{customdata[1]}<br>' +
                        #  'Pace: %{customdata[2]}<br>' +
                        #  'BPM: %{customdata[3]}<br>' +
                        #  'Distance: %{customdata[4]}<br>' +
                         'Angle: %{customdata[5]}<extra></extra>',
            text=[file_type] * len(df_subset),
            customdata=df_subset[['timestamp', 'altitude', 'pace', 'bpm', 'distance', 'angle']].values
        ))
    
    fig.update_layout(
        map=dict(
            style="open-street-map",
            zoom=15,
            center=dict(
                lat=combined_df['lat'].mean(),
                lon=combined_df['lon'].mean()
            )
        ),
        height=1200,
        title="Tracepoints Map (Lines + Points)",
        showlegend=True
    )

    # 지도 시각화 생성
    if output_file:
        fig.write_html(output_file)
        print(f"Map saved to {output_file}")
    else:
        fig.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='GPS 트레이스포인트 시각화')
    parser.add_argument('files', nargs='*', default=['dummy/data2.jsonl'], help='보여줄 JSONL 파일들 (기본값: dummy/data2.jsonl)')
    parser.add_argument('--output', '-o', help='HTML 출력 파일 경로 (지정하지 않으면 브라우저로 바로 표시)')
    args = parser.parse_args()
    
    main(args.files, args.output)