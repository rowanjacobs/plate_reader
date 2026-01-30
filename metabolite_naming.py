import csv


def find_metabolite(filename, well):
    if filename.endswith('.txt'):
        filename2 = filename
    else:
        filename2 = filename + '.txt'
    with open('filename-well-compounds.csv') as f:
        metabolites = csv.reader(f)

        for row in metabolites:
            if row[0] == filename2 and well in row[1]:
                return row[2]
