import math

with open("./scorer/results/full.csv", "r", encoding="utf8") as file:
    xlsr_53 = []
    lv_60 = []

    for line in file:
        line = line.split(",")
        xlsr_53.append(float(line[4]))
        lv_60.append(float(line[5]))

avg_xlsr_53 = sum(xlsr_53) / len(xlsr_53)
sd_xlsr_53 = math.sqrt(sum([(v - avg_xlsr_53) for v in xlsr_53])/len(xlsr_53))

avg_lv_60 = sum(lv_60) / len(lv_60)
sd_lv_60 = math.sqrt(sum([(v - avg_lv_60)**2 for v in lv_60])/len(lv_60))

print(sd_xlsr_53, sd_lv_60)
        