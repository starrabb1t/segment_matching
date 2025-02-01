def calc_iou_on_groups(G1: list[tuple], G2: list[tuple]) -> float:

    """
    Calculate the Intersection over Union (IoU) for two groups of segments.

    The IoU is calculated as the ratio of the length of the intersection to the length of the union of the two groups.
    If the union has zero length, the IoU is defined to be 1.0 if both groups are empty, and 0.0 otherwise.

    Args:
        G1 (list[tuple]): The first group of segments, represented as a list of tuples (start, end).
        G2 (list[tuple]): The second group of segments, represented as a list of tuples (start, end).

    Returns:
        float: The IoU value, which is the ratio of the intersection length to the union length of the two groups.
    """

    # Вычисляем общую длину пересечения
    intersection = 0
    for a in G1:
        a_start, a_end = a
        for b in G2:
            b_start, b_end = b
            start = max(a_start, b_start)
            end = min(a_end, b_end)
            if start < end:
                intersection += end - start

    # Функция для объединения отрезков
    def merge_segments(segments):
        """
        Merge a list of segments (defined as tuples (start, end)) into a list of non-overlapping segments.

        The segments are first sorted by their start value. Then, the algorithm iterates through the sorted list.
        For each segment, it checks if it overlaps with the last segment in the merged list. If it does, the two segments
        are merged by updating the end of the last segment in the merged list to be the maximum of the two end values.
        If the segment does not overlap, it is appended to the merged list.

        Args:
            segments (list[tuple]): A list of segments to be merged.

        Returns:
            list[tuple]: A list of merged, non-overlapping segments.
        """
        if not segments:
            return []
        sorted_segs = sorted(segments, key=lambda x: x[0])
        merged = [sorted_segs[0]]
        for seg in sorted_segs[1:]:
            last_start, last_end = merged[-1]
            current_start, current_end = seg
            if current_start <= last_end:
                new_end = max(last_end, current_end)
                merged[-1] = (last_start, new_end)
            else:
                merged.append(seg)
        return merged

    # Вычисляем объединение и его длину
    merged_union = merge_segments(G1 + G2)
    union_length = sum(end - start for start, end in merged_union)

    # Обработка случая, когда объединение имеет нулевую длину
    if union_length == 0:
        return 1.0 if len(G1) == 0 and len(G2) == 0 else 0.0
    else:
        return intersection / union_length

def match(gt: dict[str, list[tuple]], pred: dict[str, list[tuple]]):

    _gt = gt.copy()
    _pred = pred.copy()
    
    result_iou = []
    result_map = {}

    while len(_gt) > 0 and len(_pred) > 0:

        max_iou = 0
        max_k1 = None
        max_k2 = None

        print('---')

        for k1, v1 in _pred.items():

            for k2, v2 in _gt.items():
                
                iou = calc_iou_on_groups(v1, v2)

                print(k2, k1, round(iou,2))

                if iou > max_iou:
                    max_iou = iou
                    max_k1 = k1
                    max_k2 = k2

        if max_iou == 0:
            break

        result_iou.append(max_iou)
        result_map[max_k2] = max_k1

        del _pred[max_k1]
        del _gt[max_k2]

    if len(result_iou) > 0:
        result_iou = sum(result_iou) / len(result_iou)
    
    else:
        result_iou = 0
        
    return result_iou, result_map


if __name__ == '__main__':

    ground_truth = {
        'AB': [
            (1,4),
            (6,11)
        ],
        'C': [
            (2,11),
        ]
    }

    prediction = {
        'DE': [
            (2,8),
            (8,11)
        ],
        'F': [
            (1,4)
        ],
        'G': [
            (6,11)
        ]
    }

    iou, _map = match(ground_truth, prediction)

    print(round(iou,2), _map)