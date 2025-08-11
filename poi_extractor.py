import argparse
import json

def load_jsonl(file_path: str) -> list[dict]:
    records = []
    json_decode_error_occurred = False

    # 파일을 읽고 dict로 변환하여 리스트에 추가
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    record = json.loads(line)
                    records.append(record)
                except json.JSONDecodeError as e:
                    json_decode_error_occurred = True
    
    # 파싱 에러 발생 시 경고 출력
    if json_decode_error_occurred:
        print(f"Warning: JSON decode error occurred in '{file_path}'; Some lines may be missing")

    return records

def extract_poi_by_distance(gps_data: list[dict], interval_m: float) -> list[dict]:
    # 예외 처리
    if not gps_data:
        return []
    if interval_m <= 0:
        raise ValueError("Interval must be greater than 0")
    if not all('lat' in coord and 'lng' in coord and 'dist' in coord for coord in gps_data):
        raise ValueError("Invalid jsonl data: Each coordinate must contain 'lat', 'lng', and 'dist' fields")
    
    # POI 추출
    poi_list = []

    # 첫 번째 점은 항상 POI로 추가
    poi_list.append(gps_data[0])
    for coord in gps_data[1:]:
        # 현재 점과 직전 POI 간의 거리 계산
        dist = coord['dist'] - poi_list[-1]['dist']
        # 만약 interval_m 이상이면 POI로 추가
        if dist >= interval_m:
            poi_list.append(coord)

    # 마지막 점도 항상 POI로 추가
    if poi_list[-1] != gps_data[-1]:
        poi_list.append(gps_data[-1])

    return poi_list


def extract_poi(input_file: str, interval_m: float, output_file: str = ""):
    gps_data = load_jsonl(input_file)
    poi_list = extract_poi_by_distance(gps_data, interval_m)

    # 출력
    if output_file:
        # 파일로 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            for poi in poi_list:
                f.write(json.dumps(poi, ensure_ascii=False) + '\n')
    else:
        # 콘솔에 출력
        for poi in poi_list:
            print(json.dumps(poi, ensure_ascii=False))




# poi만 extract하여 jsonl 방식으로 출력
if __name__ == "__main__":
    # 명령줄 인수 파싱
    parser = argparse.ArgumentParser(description='POI 추출기')
    parser.add_argument('input_file', help="POI를 추출할 시계열 파일 경로 (jsonl 형식)")
    parser.add_argument('--meter', '-m', type=float, default=100.0, help='POI 추출 간격 (미터 단위, 기본값: 100.0)')
    parser.add_argument('--output_file', '-o', help='POI 추출 결과를 저장할 JSONL 파일 경로 (지정하지 않으면 콘솔에 출력)')
    args = parser.parse_args()

    # POI 추출
    extract_poi(args.input_file, args.meter, args.output_file)