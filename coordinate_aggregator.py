import argparse
import json

def aggregate_coordinates_and_print(input_file: str, n: int):
    aggregated_coords = []
    with open(input_file, 'r', encoding='utf-8') as f:
        coords = [json.loads(line.strip()) for line in f if line.strip()]
    
    for i in range(0, len(coords), n): # todo <<< this is trash
        chunk = coords[i:i+n]
        if len(chunk) < n:
            continue  # Skip incomplete chunks
        # 산술평균 진행
        avg_lat = sum(coord['lat'] for coord in chunk) / n 
        avg_lng = sum(coord['lng'] for coord in chunk) / n
        aggregated_coords.append({'lat': avg_lat, 'lng': avg_lng})
    
    # 결과 출력 - 파일 생성 대신 콘솔에 출력
    print(json.dumps(aggregated_coords, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregate N Gps coordinates into a single coordinate")
    parser.add_argument(
        'input',
        default = 'dummy/data2.jsonl',
        help='Input file to aggregate - which is GPS coordinates in JSONL format'
    )
    parser.add_argument(
        '--n',
        type=int,
        default=3,
        help='Number of coordinates to aggregate into a single coordinate'
    )
    args = parser.parse_args()
    aggregate_coordinates_and_print(args.input, args.n)
    
