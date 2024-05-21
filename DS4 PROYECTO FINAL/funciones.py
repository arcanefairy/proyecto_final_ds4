import csv
import requests
from bs4 import BeautifulSoup

def carga_csv(nombre_archivo: str) -> list:
    lista = []
    with open(nombre_archivo, 'r', encoding="utf-8", errors='ignore') as archivo:
        lista = list(csv.DictReader(archivo))
    return lista

def crea_diccionario_revistas(lista_revista: list) -> dict:
    d = {}
    for revista in lista_revista:
        if isinstance(revista, dict) and "TITULO" in revista:
            key = revista["TITULO"]
            if isinstance(key, str):
                d[key] = revista
    return d

def crea_diccionario_alfabetico(lista_revistas: list) -> dict:
    d = {}
    for revista in lista_revistas:
        titulo = revista['TITULO']
        primera_letra = titulo[0].upper()
        if primera_letra in d:
            d[primera_letra].append(revista)
        else:
            d[primera_letra] = [revista]
    d = {k: v for k, v in sorted(d.items(), key=lambda item: item[0])}
    return d

def realizar_busqueda(query, diccionarios_revistas: list) -> list:
    resultados = []
    for diccionario in diccionarios_revistas:
        for revista in diccionario.values():
            if query.lower() in revista.get('TITULO', '').lower():
                resultados.append(revista)
    return resultados

def scimagojr_journal_ranks_csv():
    '''
    Informacion de Journal Ranks en CSV 
    '''
    url = 'https://www.scimagojr.com/journalrank.php'
    filename = 'scimagojr_journal_ranks.csv'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('div', class_='table_wrap').find('table')

        table_data = []
        for row in table.find_all('tr'):
            cols = row.find_all('td')
            row_data = [col.text.strip() for col in cols]
            table_data.append(row_data)

        with open(filename, 'w', newline='') as archivo:
            writer = csv.writer(archivo)
            writer.writerow(['Rank', 'Title', 'Type', 'SJR', 'H index', 'Total Docs. (2023)', 'Total Docs. (3 years)', 'Total Refs. (2023)', 'Total Cites (3 years)', 'Citable Docs. (3years)', 'Cites / Doc. (2years)', 'Ref. / Doc. (2023)'])
            writer.writerows(table_data)    

        print(f'Journal Ranks guardados en {filename}')
    else:
        print('Extracción fallida de journal ranks')

def extract_external_links(url, file_links):
    '''
    Extraer los links externos para obtener mas informacion de cada revista y guardarlos en un txt
    '''
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('div', class_='table_wrap').find('table')

    external_links = []
    for row in table.find_all('tr'):
        a_tag = row.find('a')
        if a_tag and a_tag['href'].startswith('journalsearch.php?q='):
            external_links.append(a_tag['href'])
    with open(file_links, 'w') as f:
        for link in external_links:
            f.write(f"{link}\n")

def scrapper_journal_links():
    '''
    Con los links extraidos hacer un web scrapper para sacar la informacion necesaria y guardarla en un csv
    '''
    data_list = []
    with open('external_links.txt', 'r') as file:
        for line in file:
            link = line.strip()
            response = requests.get("https://www.scimagojr.com/" + link)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                background_div = soup.find('div', class_='background')
                data = {}
                if background_div:
                    publisher = background_div.find('h2', string='Publisher')
                    country = background_div.find('h2', string='Country')
                    subject_area = background_div.find('h2', string='Subject Area and Category')
                    issn = background_div.find('h2', string='ISSN')
                    coverage = background_div.find('h2', string='Coverage')
                    if publisher:
                        data['publisher'] = publisher.find_next_sibling("p").text.strip()
                    if country:
                        data['country'] = country.find_next_sibling("p").text.strip()
                    if subject_area:
                        data['subject_area'] = subject_area.find_next_sibling("p").text.strip()
                    if issn:
                        data['issn'] = issn.find_next_sibling("p").text.strip()
                    if coverage:
                        data['coverage'] = coverage.find_next_sibling("p").text.strip()          
                else:
                    print('No se encontró la sección de background.')
                data_list.append(data)
            else:
                print(f'Error al visitar el enlace {link}. Código de estado: {response.status_code}.')
    
    with open('moreinfoSmJr.csv', 'w', newline='') as csvfile:
        fieldnames = ['publisher', 'country', 'subject_area', 'issn', 'coverage']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in data_list:
            writer.writerow(data)

    return data_list

if __name__ == "__main__":
    lista = carga_csv("datos/revistas/REVISTAS_INFO.csv")

    d = crea_diccionario_revistas(lista)
    for titulo, revista in d.items():
        print(f"Revista: {titulo}")
   
    d = crea_diccionario_alfabetico(lista)
    for titulo, revista in d.items():
        print(f"Revista: {titulo}")