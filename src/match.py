def calculate_iou(seg1: tuple, seg2: tuple):
    """
    Calculate the Intersection over Union (IoU) for two segments.

    Args:
        seg1 (tuple): A tuple representing the start and end of the first segment.
        seg2 (tuple): A tuple representing the start and end of the second segment.

    Returns:
        float: The IoU value, which is the ratio of the intersection length to the union length 
               of the two segments. Returns 0.0 if there is no intersection.
    """

    s1, e1 = seg1
    s2, e2 = seg2
    inter_start = max(s1, s2)
    inter_end = min(e1, e2)
    if inter_start >= inter_end:
        return 0.0
    inter = inter_end - inter_start
    union = (e1 - s1) + (e2 - s2) - inter
    return inter / union if union != 0 else 0.0

def match_groups(G1: dict[str, tuple], G2: dict[str, tuple]):
    
    """
    Match groups G1 and G2 using a two-pass algorithm.

    First pass: assign each G2 to a G1 without any conflicts.
    Second pass: assign any remaining G2 to a G1 without any conflicts.

    Args:
        G1 (dict[str, tuple]): A dictionary representing the segments in the first group.
        G2 (dict[str, tuple]): A dictionary representing the segments in the second group.

    Returns:
        dict[str, list[str]]: A dictionary where the keys are G1 IDs and the values are lists
                              of G2 IDs that were assigned to the corresponding G1.
    """

    # Генерируем все возможные пары (G2, G1) с их IoU
    all_pairs = []
    for g2_id in G2:
        g2_seg = G2[g2_id]
        for g1_id in G1:
            g1_seg = G1[g1_id]
            iou = calculate_iou(g1_seg, g2_seg)
            all_pairs.append((g2_id, g1_id, iou))

    # Сортируем пары по убыванию IoU
    all_pairs_sorted = sorted(all_pairs, key=lambda x: -x[2])

    # Инициализация структур
    assignments = {g1_id: [] for g1_id in G1}
    assigned_g2 = set()
    g2_to_g1 = {}
    for g2_id in G2:

        # Собираем все возможные G1 для текущего G2 и сортируем их по IoU
        pairs_for_g2 = [(g1_id, iou) for (g2, g1_id, iou) in all_pairs_sorted if g2 == g2_id]
        g2_to_g1[g2_id] = pairs_for_g2

    iou_scores = []

    # Первый проход: жадное назначение без пересечений (только IoU > 0)
    for g2_id, g1_id, iou in all_pairs_sorted:
        if iou <= 0:
            continue  # Пропускаем пары с нулевым IoU
        if g2_id in assigned_g2:
            continue
        g2_seg = G2[g2_id]
        conflict = False
        for assigned_g2_id in assignments[g1_id]:
            assigned_seg = G2[assigned_g2_id]
            if (g2_seg[0] < assigned_seg[1] and g2_seg[1] > assigned_seg[0]):
                conflict = True
                break
        if not conflict:
            assignments[g1_id].append(g2_id)
            assigned_g2.add(g2_id)
            iou_scores.append(iou)

    # Второй проход: доназначение оставшихся G2 (только IoU > 0)
    unassigned_g2 = set(G2.keys()) - assigned_g2
    for g2_id in unassigned_g2:
        for g1_id, iou in g2_to_g1[g2_id]:
            if iou <= 0:
                continue  # Пропускаем пары с нулевым IoU
            g2_seg = G2[g2_id]
            conflict = False
            for assigned_g2_id in assignments[g1_id]:
                assigned_seg = G2[assigned_g2_id]
                if (g2_seg[0] < assigned_seg[1] and g2_seg[1] > assigned_seg[0]):
                    conflict = True
                    break
            if not conflict:
                assignments[g1_id].append(g2_id)
                assigned_g2.add(g2_id)
                iou_scores.append(iou)
                break

    result_dict = {
        g1_id: sorted(assignments[g1_id])  # Сортировка для детерминированности
        for g1_id in G1
    }

    result_score = round(sum(iou_scores) / len(iou_scores), 2)

    return result_score, result_dict


if __name__ == '__main__':
        
        G1 = {
            'A': (1, 4),
            'B': (6, 11),
            'C': (2, 11)
        }

        G2 = {
            'D': (2, 11),
            'F': (1, 4),
            'G': (6, 11)
        }

        score, _ = match_groups(G1, G2)
        print(score)
        
        G1 = {
            'A': (1, 4),
            'B': (6, 11),
            'C': (2, 11)
        }

        G2 = {
            'D': (2, 8),
            'E': (8, 11),
            'F': (1, 4),
            'G': (6, 11)
        }

        score, _ = match_groups(G1, G2)
        print(score)


        G1 = {
            'A': (1, 4),
            'B': (6, 11),
            'C': (2, 11)
        }

        G2 = {
            'D': (3, 7),
            'E': (8, 11),
            'F': (1, 2),
            'G': (6, 10)
        }

        score, _ = match_groups(G1, G2)
        print(score)

        G1 = {
            'A': (1, 4),
            'B': (6, 11)
        }

        G2 = {
            'C': (3, 7),
            'D': (8, 11),
            'E': (1, 2),
            'F': (6, 10)
        }

        score, _ = match_groups(G1, G2)
        print(score)

        G1 = {
            'A': (2, 11)
        }

        G2 = {
            'B': (3, 7),
            'C': (8, 11),
            'D': (1, 2),
            'E': (6, 10)
        }

        score, _ = match_groups(G1, G2)
        print(score)

        G1 = {
            'A': (2, 11)
        }

        G2 = {
            'B': (1, 2),
            'C': (2, 3),
            'D': (4, 6),
            'E': (7, 10)
        }

        score, _ = match_groups(G1, G2)
        print(score)