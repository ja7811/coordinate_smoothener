import argparse
import json


def write_jsonl(points: list[dict], output_file: str):
    if output_file:
        # 파일로 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            for pt in points:
                f.write(json.dumps(pt, ensure_ascii=False, separators=(',', ':')) + '\n')
    else:
        for pt in points:
            print(json.dumps(pt, ensure_ascii=False, separators=(',', ':')))


def aggregate_coordinates(input_file: str, n: int):
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
        # 기타 필드들은 첫 번째 좌표의 값을 사용
        aggregated = {k: v for k, v in chunk[0].items() if k not in ('lat', 'lng')}
        aggregated.update({'lat': avg_lat, 'lng': avg_lng})
        aggregated_coords.append(aggregated)
    # 결과 출력 - 파일 생성 대신 콘솔에 출력
    return aggregated_coords


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
    parser.add_argument("-o", "--output")
    args = parser.parse_args()
    coords = aggregate_coordinates(args.input, args.n)
    write_jsonl(coords, args.output)  # None이면 콘솔 출력
    
