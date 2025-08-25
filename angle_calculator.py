import math
import argparse
import json

############################################

def read_jsonl(input_file: str) -> list[dict]:
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

def write_jsonl(points: list[dict], output_file: str):
    if output_file:
        # 파일로 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            for pt in points:
                f.write(json.dumps(pt, ensure_ascii=False, separators=(',', ':')) + '\n')
    else:
        for pt in points:
            print(json.dumps(pt, ensure_ascii=False, separators=(',', ':')))

############################################

# 두 점 사이의 방위각 계산 (북쪽 = 0도, 시계방향 증가)
def bearing(from_point: dict, to_point: dict) -> float:
    lat1 = math.radians(from_point["lat"])
    lon1 = math.radians(from_point["lng"])
    lat2 = math.radians(to_point["lat"])
    lon2 = math.radians(to_point["lng"])

    dlon = lon2 - lon1

    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)

    theta = math.atan2(y, x)
    brng = (math.degrees(theta) + 360.0) % 360.0
    return brng

# 좌표 리스트에 angle 필드 계산하여 추가
def add_angles(coords: list[dict]) -> list[dict]:
    if not coords:
        return []

    result = []

    # 첫 점 angle = 0.0
    first = coords[0].copy()
    first["angle"] = 0.0
    result.append(first)

    # 중간 점들
    for i in range(1, len(coords) - 1):
        prev, curr, nxt = coords[i - 1], coords[i], coords[i + 1]

        bearing_prev = bearing(prev, curr)
        bearing_curr = bearing(curr, nxt)

        # angle = (bearing_curr - bearing_prev + 360.0) % 360.0
        angle = bearing_curr - bearing_prev

        new_point = curr.copy()
        new_point["angle"] = round(angle, 1)
        result.append(new_point)

    # 마지막 점 angle = None
    last = coords[-1].copy()
    last["angle"] = None
    result.append(last)

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", default="dummy/rdp_data1.jsonl")
    parser.add_argument("-o", "--output", help="Path to the output .jsonl file. If not provided, prints to stdout.")
    args = parser.parse_args()

    coords = read_jsonl(args.input)
    checkpoints = add_angles(coords)
    write_jsonl(checkpoints, args.output)


    # coords = [{"lat":0, "lng":0}, {"lat":0, "lng":1}, {"lat":1, "lng":1}, {"lat":1, "lng":2}, {"lat":2, "lng":2}, {"lat":2, "lng":3}, {"lat":2, "lng":4}, {"lat":2, "lng":5}, {"lat":2, "lng":6}]
    # checkpoints = add_angles(coords)
    # for pt in checkpoints:
    #     print(pt)