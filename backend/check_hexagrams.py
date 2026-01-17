
from app.core.constants import sixty_four_hexagrams_index

trigrams = ["乾", "坤", "震", "巽", "坎", "离", "艮", "兑"]
missing = []

for upper in trigrams:
    for lower in trigrams:
        if (upper, lower) not in sixty_four_hexagrams_index:
            missing.append(f'("{upper}", "{lower}")')

print("Missing combinations:")
for m in missing:
    print(m)
