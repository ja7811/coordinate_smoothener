import json
import math
import argparse
from typing import List, Dict

# 상수로 사용할 오차 허용 범위 (단위: 미터)
EPSILON_METER = 10.0

# 선분과 점 사이 수직 거리 계산 (유클리드 거리 기반 - 엄밀히는 Haversine 사용해야 함)
def perpendicular_distance_meters(pt: Dict, start: Dict, end: Dict) -> float:
    # 선분의 길이의 제곱
    line_mag_sq = (end['lat'] - start['lat'])**2 + (end['lng'] - start['lng'])**2
    if line_mag_sq == 0.0:
        return math.sqrt((pt['lat'] - start['lat'])**2 + (pt['lng'] - start['lng'])**2)

    # 점 pt를 선분 위로 투영했을 때의 위치 계산
    u = ((pt['lat'] - start['lat']) * (end['lat'] - start['lat']) + (pt['lng'] - start['lng']) * (end['lng'] - start['lng'])) / line_mag_sq

    if u < 0.0:
        # 투영점이 선분의 start점 이전에 있을 경우, start점과의 거리 반환
        closest_point = start
    elif u > 1.0:
        # 투영점이 선분의 end점 이후에 있을 경우, end점과의 거리 반환
        closest_point = end
    else:
        # 투영점이 선분 내부에 있을 경우, 수선의 발 좌표 계산
        closest_point = {
            'lat': start['lat'] + u * (end['lat'] - start['lat']),
            'lng': start['lng'] + u * (end['lng'] - start['lng'])
        }

    # pt와 가장 가까운 점 사이의 유클리드 거리를 미터 단위로 가정하고 반환
    # (실제로는 위경도를 미터로 변환하는 과정이 필요함)
    dx = pt['lat'] - closest_point['lat']
    dy = pt['lng'] - closest_point['lng']
    # 위도 1도당 약 111km로 가정하여 미터로 환산
    return math.sqrt(dx**2 + dy**2) * 111000

# rdp 알고리즘 (재귀적 구현))
def _rdp(pts: List[Dict], start_idx: int, end_idx: int, out: List[Dict], epsilon: float = EPSILON_METER):
    dmax = -1.0
    index = -1

    start_pt = pts[start_idx]
    end_pt = pts[end_idx]

    for i in range(start_idx + 1, end_idx):
        d = perpendicular_distance_meters(pts[i], start_pt, end_pt)
        if d > dmax:
            index = i
            dmax = d

    if dmax > epsilon and index != -1:
        # 임계값보다 먼 점이 있으면, 그 점을 기준으로 구간을 나눠 재귀 호출
        _rdp(pts, start_idx, index, out, epsilon)
        _rdp(pts, index, end_idx, out, epsilon)
    else:
        # 임계값보다 먼 점이 없으면, 현재 구간의 종점만 결과에 추가
        out.append(pts[end_idx])


# RDP 알고리즘을 사용하여 좌표 리스트에서 핵심 꼭짓점을 추출
def extract_edge_points(points: List[Dict], epsilon: float) -> List[Dict]:
    if len(points) <= 2:
        return [{'lat': p['lat'], 'lng': p['lng']} for p in points]

    out = []
    # 시작점은 항상 포함
    out.append(points[0])
    
    _rdp(points, 0, len(points) - 1, out, epsilon)

    # 타임스탬프('timeStamp') 기준으로 정렬하여 경로의 순서를 보장
    out.sort(key=lambda p: p['timeStamp'])

    # 최종 결과는 'timeStamp'를 제외한 형태로 변환하여 반환
    return out


# .jsonl 파일을 읽어 Dict 리스트로 반환
def read_jsonl(input_file: str) -> List[Dict]:
    points = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip(): 
                    points.append(json.loads(line))
        return points
    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_file}'")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{input_file}'")
        exit(1)

# 결과 출력 (stdout 혹은 파일)
def write_jsonl(points: List[Dict], output_file: str):
    if output_file:
        # 파일로 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            for pt in points:
                f.write(json.dumps(pt, ensure_ascii=False) + '\n')
    else:
        for pt in points:
            print(json.dumps(pt, ensure_ascii=False))

# 메인
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simplify a polyline from a .jsonl file using the RDP algorithm.")
    parser.add_argument("input", default="dummy/data1.jsonl", help="Path to the input .jsonl file.")
    parser.add_argument("-o", "--output", help="Path to the output .jsonl file. If not provided, prints to stdout.")
    parser.add_argument("-e", "--epsilon", type=float, default=10.0, help="Epsilon value in meters for the RDP algorithm (default: 10.0).")
    args = parser.parse_args()

    original_points = read_jsonl(args.input)
    simplified_points = extract_edge_points(original_points, args.epsilon)

    write_jsonl(simplified_points, args.output)