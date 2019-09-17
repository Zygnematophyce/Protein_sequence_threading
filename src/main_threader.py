import pandas as pd
import numpy as np
import math
import re


def begin_message():
    """ Méthode qui affiche différentes informations au démarrage du programme."""

    print("THREADER - Protein Sequence Threading Program")
    print("Built date : September 2019")
    print("usage : python3 main_threader.py\n")

def newline():
    """ Méthode qui ajoute une nouvelle ligne en output."""
    print("")

def euclidean_distance(dataframe, index, position = 1):
    """Méthode aui retourne la distance euclidienne entre 2 acides aminés."""
    xa = float(dataframe.iloc[index, 2])
    ya = float(dataframe.iloc[index, 3])
    za = float(dataframe.iloc[index, 4])

    # Coordonnée euclidienne du second AA.
    xb = float(dataframe.iloc[(position), 2])
    yb = float(dataframe.iloc[(position), 3])
    zb = float(dataframe.iloc[(position), 4])

    distance = math.sqrt(( (xb - xa)**2 + (yb - ya)**2 + (zb - za)**2 ))
    return distance

def read_pdb_file_to_dataframe(pdb_file):
    """ Méthode qui ouvre un fichier pdb et retourne sous forme de dataframe \
    les informations nécessaires.
    """
    dict_seq_c_alpha = {'AA':[],
                        'num_list':[],
                        'x':[],
                        'y':[],
                        'z':[]}

    with open(pdb_file, "r") as contents_pdb:
        numero_list = 0
        for line in contents_pdb:
            if line.startswith("ATOM") and line[12:16].strip() == "CA":
                numero_list += 1
                dict_seq_c_alpha['AA'].append(line[17: 20].strip())
                dict_seq_c_alpha['num_list'].append(line[22: 26].strip())
                dict_seq_c_alpha['x'].append(line[30: 38].strip())
                dict_seq_c_alpha['y'].append(line[38: 46].strip())
                dict_seq_c_alpha['z'].append(line[46: 54].strip())
            if numero_list == 10:
                break

    dataframe = pd.DataFrame(data = dict_seq_c_alpha,
                             index = np.arange(1, numero_list+1, 1))
    return dataframe

def create_distance_matrix(dataframe):
    """
    Méthode qui permet de créer un matrice de distance (= matrice de contact).
    """
    values_numpy = []
    index_and_columns_names = list(dataframe['AA'])

    for i in range(0, len(dataframe)):
        values_list = []
        for y in range(0, len(dataframe)):
            values_list.append(euclidean_distance(dataframe, i, y))
        values_numpy.append(values_list)

    dataframe_aa = pd.DataFrame(data = values_numpy,
                                index = index_and_columns_names,
                                columns = index_and_columns_names)
    return dataframe_aa

def pairwise_amino_acide(dataframe):
    """ Méthode qui revoie l'ensemble des couples AA possibles. """
     # Création de la colonne pour le dataframe.
    pairwise_amino_acide = []

    # Extraire l'ensemble des couples AA pour notre sequence.
    for i in  range(0,len(dataframe['AA'])):
        for y in  range(i,len(dataframe['AA'])):
            pairwise_amino_acide.append([dataframe.iloc[i,0],
                                         dataframe.iloc[y,0]])

    return pairwise_amino_acide

def create_regular_expression(pairwise_amino_acide):
    """
    Méthode qui retourne une liste contenant l'ensemble des
    expressions régulières a partir de tout les couples AA possibles.
    """
    expr_regular_pairwise = []

    for i in range(0, len(pairwise_amino_acide)):
        expr_regular = "^"+pairwise_amino_acide[i][0]+"\s[A-Z]{2}\s"+pairwise_amino_acide[i][1]+"\s[A-Z]{2}"
        expr_regular_pairwise.append([expr_regular])

    return expr_regular_pairwise

def create_potentiel_stat_from_dope(dope_file_par,
                                    pairwise_aa,
                                    expr_regular_pairwise):
    """
    Ouvre le fichier avec les potentiels statistiques pour extraire les
    informations nécessaire et les retroune dans un dictionnaire.
    """
    potentiel_statistique_dict = dict()
    x = [i for i in np.arange(0.0, (0.25*30), 0.25, float)]

    with open(dope_file_par, "r") as dope_file:
        for line in dope_file:
            if re.search("[A-Z]{3}\sCA\s[A-Z]{3}\sCA", line):
                for i in range(0, len(expr_regular_pairwise)):
                    if re.search(expr_regular_pairwise[i][0], line):
                        temporaire_list = list()
                        temporaire_list = line[13:].rsplit()
                        temporaire_name = pairwise_aa[i][0]+pairwise_aa[i][1]
                        potentiel_statistique_dict[temporaire_name] = pd.DataFrame([temporaire_list], columns = x, index = ["E"])

    return potentiel_statistique_dict

def create_empty_hight_matrix(lenght_x, lenght_y, columns_names):
    """ Méthode qui créé et retourne une matrice de haut niveau."""
    hight_matrix = np.full((lenght_x, lenght_y), None)
    hight_matrix_seq = pd.DataFrame(hight_matrix,
                                    columns = columns_names,
                                    index = np.arange(1,
                                                      len(columns_names)+1,
                                                      1))
    return hight_matrix_seq

if __name__ == '__main__':

    # Message du début de programme.
    begin_message()

    # Extraction des information du pdb.
    pdb_file_dataframe = read_pdb_file_to_dataframe("../data/2019-09-10/2xri.pdb")

    print("Informations du fichier .pdb :")
    print(pdb_file_dataframe)

    newline()

    # Création de la matrice de distance ou matrice de contact.
    distance_matrix = create_distance_matrix(pdb_file_dataframe)
    print(distance_matrix)

    # Création de tout les couples AA possibles.
    all_pairwises_aa_list = pairwise_amino_acide(pdb_file_dataframe)

    # Création de l'ensemblde des expressions régulières.
    expr_regular = create_regular_expression(all_pairwises_aa_list)

    # Création d'un dictionnaire stockant l'ensemble des potentiels statistiques.
    pot_stat_dict = create_potentiel_stat_from_dope("../data/2019-13-10/dope.par",
                                                    all_pairwises_aa_list,
                                                    expr_regular)

    # Création d'une matrice de haut niveau
    print("La matrice de haut niveau (hight matrix)")
    hight_matrix = create_empty_hight_matrix(len(distance_matrix.columns),
                                             len(distance_matrix.columns),
                                             distance_matrix.columns)
    print(hight_matrix)

    # Suite.

    aa_hight_matrix = hight_matrix.columns
    ca_hight_matrix = hight_matrix.index

    pos_x_hight_matrix = 0
    pos_y_hight_matrix = 0

    pos_x_low_matrix = 0
    pos_y_low_matrix = 0

    pos_y_low_matrix +=1
    print("{} CA{} {} CA{}".format(aa_hight_matrix[pos_y_hight_matrix],
                                   ca_hight_matrix[pos_x_hight_matrix],
                                   hight_matrix.columns[pos_y_low_matrix],
                                   hight_matrix.index[pos_x_low_matrix]))
    pos_x_low_matrix += 1
    print("{} CA{} {} CA{}".format(aa_hight_matrix[pos_y_hight_matrix],
                                   ca_hight_matrix[pos_x_hight_matrix],
                                   hight_matrix.columns[pos_y_low_matrix],
                                   hight_matrix.index[pos_x_low_matrix]))
    pos_y_low_matrix -= 1
    print("{} CA{} {} CA{}".format(aa_hight_matrix[pos_y_hight_matrix],
                                   ca_hight_matrix[pos_x_hight_matrix],
                                   hight_matrix.columns[pos_y_low_matrix],
                                   hight_matrix.index[pos_x_low_matrix]))

    print("Première low matrice")
