import re

with open('d:/myPortfolioProject/BookStack_EnergyAttribution/.github/workflows/measure_energy_bookstack.yml', 'r') as f:
    win = f.read()
with open('d:/myPortfolioProject/BookStack_EnergyAttribution/.github/workflows/measure_energy_bookstack_mac.yml', 'r') as f:
    mac = f.read()

win_jobs = win[win.find('  profile-energy:'):]
win_jobs = win_jobs.replace('  profile-energy:', '  profile-windows:\n    name: Profile AMD Windows')
win_jobs = re.sub(r'DATA_DIR: .*', 'RUN_ID: "win_${{ github.run_id }}"\n      DATA_DIR: "D:\\\\myPortfolioProject\\\\BookStack_EnergyAttribution\\\\ResearchData\\\\cpudata\\\\${{ env.RUN_ID }}"', win_jobs, count=1)
win_jobs = win_jobs.replace('energy-traces-${{ github.run_id }}', 'energy-traces-${{ env.RUN_ID }}')
win_jobs = win_jobs.replace('${{ github.run_id }}', '${env:RUN_ID}')

mac_jobs = mac[mac.find('  profile-energy:'):]
mac_jobs = mac_jobs.replace('  profile-energy:', '  profile-mac:\n    name: Profile Apple Mac M2')

header = """name: BookStack Energy Profiling (Combined Windows & Mac)

on:
  workflow_dispatch:

jobs:
"""

combined = header + win_jobs + "\n" + mac_jobs

with open('d:/myPortfolioProject/BookStack_EnergyAttribution/.github/workflows/measure_energy_combined.yml', 'w', newline='\n') as f:
    f.write(combined)
print("Combined workflow created!")
