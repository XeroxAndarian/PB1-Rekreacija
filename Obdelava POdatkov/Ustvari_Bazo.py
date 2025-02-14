import subprocess

for file in ['Pridobi_Imena.py', 'Pridobi_Sezone.py', 'Pridobi_Tekma.py']:
    path = f'Obdelava POdatkov\{file}'
    print(f"Zaganjam {file}.")
    subprocess.run(["python", path])  

print('Baza ustvarjena!')