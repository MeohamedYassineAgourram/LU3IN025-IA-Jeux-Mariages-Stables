import exemple # Pour pouvoir utiliser les methodes de exemple.py
import heapq
import random
import time
import matplotlib.pyplot as plt

import gurobipy as gp
from gurobipy import GRB

#print("bonjour")
#maListe=exemple.lectureFichier("test.txt") # Execution de la methode lectureFichier du fichier exemple.
#print(maListe)
#print(len(maListe)) #Longueur de la liste.
#exemple.createFichierLP(maListe[0][0],int(maListe[1][0])) #Methode int(): transforme la chaine de caracteres en entier


# 1-Problème et affectation:
# QUESTION 1: ======================================================================================================================
def lire_preferences_etudiants(nom_fichier):
    with open(nom_fichier, "r") as f:
        lignes = f.readlines()
    
    CE = []
    for ligne in lignes[1:]:
        elements = ligne.split() # Ne pas oublier les parenthèses !
        
        # Les indices 0 et 1 sont l'ID et le nom
        preferences = [int(x) for x in elements[2:]]
        CE.append(preferences)
        
    return CE

def lire_preferences_parcours(nom_fichier):
    with open(nom_fichier, "r") as f:
        lignes = f.readlines()
        
    CP = []
    for ligne in lignes[2:]:
        elements = ligne.split()
        
        # Les indices 0 et 1 sont l'ID et le nom
        preferences = [int(x) for x in elements[2:]]
        CP.append(preferences)
        
    return CP

# === TEST ===
if __name__ == "__main__":
    CE = lire_preferences_etudiants("PrefEtu.txt")
    CP = lire_preferences_parcours("PrefSpe.txt")
    print("=======================================")
    print(" TEST Q1 ")
    print("=======================================")
    print("Première ligne de CE (Etu0) :", CE[0])
    print("Première ligne de CP (AI2D) :", CP[0])
    print("")
    print("")




# QUESTION 3: ======================================================================================================================
def gale_shapley_etudiants(CE, CP, capacites):
    n_etu = len(CE)
    n_parcours = len(CP)
    
    # 1. Précalcul de la matrice des rangs RP (inverse de CP)
    # RP[j][i] donnera le rang de l'étudiant i pour le parcours j
    RP = [[0] * n_etu for i in range(n_parcours)]
    for j in range(n_parcours):
        for rang, etu in enumerate(CP[j]):
            RP[j][etu] = rang
            
    # 2. Initialisation des structures de données (comme défini en Q2)
    libres = [] # Pile des étudiants libres [0, 1, ..., n-1]
    for i in range(n_etu):
        libres.append(i) 
    
    prochain_choix = [] # Indice du prochain master à tenter pour chaque étudiant
    for i in range(n_etu):
        prochain_choix.append(0)
    
    # Liste de Tas (Max-Heaps) pour stocker les affectations courantes de chaque master
    affectations = [[] for i in range(n_parcours)]
    
    # 3. Boucle principale
    while libres:
        etu = libres.pop() # On prend un étudiant libre en O(1)
        
        # Sécurité : si l'étudiant a épuisé tous ses choix (ne devrait pas arriver ici)
        if prochain_choix[etu] >= n_parcours:
            continue
            
        # Le master auquel l'étudiant fait sa proposition
        parcours = CE[etu][prochain_choix[etu]]
        prochain_choix[etu] += 1 # On prépare le prochain choix pour plus tard si besoin
        
        # Le rang de cet étudiant pour ce master précis
        rang_etu = RP[parcours][etu]
        
        # Le master a-t-il encore de la place ?
        if len(affectations[parcours]) < capacites[parcours]:
            # On accepte l'étudiant. On push (-rang, id_etu) pour simuler un Max-Heap
            heapq.heappush(affectations[parcours], (-rang_etu, etu))
        else:
            # Le master est plein. On regarde le pire étudiant actuellement accepté.
            # tas[0] donne l'élément à la racine, sans le retirer.
            pire_rang_neg, pire_etu = affectations[parcours][0]
            pire_rang = -pire_rang_neg
            
            # L'étudiant courant est-il meilleur (rang plus petit) que le pire ?
            if rang_etu < pire_rang:
                # Le master vire le pire étudiant et accepte le nouveau
                heapq.heappop(affectations[parcours]) # Enlève le pire en O(log C)
                heapq.heappush(affectations[parcours], (-rang_etu, etu)) # Ajoute le nouveau en O(log C)
                libres.append(pire_etu) # Le pire étudiant redevient libre !
            else:
                # L'étudiant courant est refusé, il reste libre pour le tour suivant
                libres.append(etu)
                
    # 4. Formatage du résultat : on extrait juste les ID des étudiants des tas
    resultat_final = []
    for tas in affectations:
        etudiants_acceptes = [etu for _, etu in tas]
        resultat_final.append(etudiants_acceptes)
        
    return resultat_final

# === TEST ===
capacites = [2, 1, 1, 1, 2, 1, 1, 1, 1, 2]
affectations_obtenues = gale_shapley_etudiants(CE, CP, capacites)
print("=======================================")
print(" TEST Q3 ")
print("=======================================")
print("Affectations GS Étudiants :", affectations_obtenues)
print("")
print("")




# QUESTION 4: ======================================================================================================================
def gale_shapley_parcours(CE, CP, capacites):
    n_etu = len(CE)
    n_parcours = len(CP)
    
    # 1. Précalcul de la matrice des rangs RE (inverse de CE)
    # RE[i][j] donne le rang du master j pour l'étudiant i. (O(1) à la consultation)
    RE = [[0] * n_parcours for i in range(n_etu)]
    for i in range(n_etu):
        for rang, master in enumerate(CE[i]):
            RE[i][master] = rang
            
    # 2. Initialisation des structures de données optimisées
    masters_actifs = [] # File des masters ayant encore des places
    for j in range(n_parcours):
        if capacites[j] > 0:
            masters_actifs.append(j)
            
    prochain_choix = [0] * n_parcours   # Indice du prochain étudiant à qui le master va proposer
    places_prises = [0] * n_parcours    # Compteur des places remplies pour chaque master
    affectation_etudiant = [-1] * n_etu # -1 signifie que l'étudiant n'a pas de master
    
    # 3. Boucle principale (Tant qu'il y a un master qui cherche à recruter)
    while masters_actifs:
        m = masters_actifs.pop() 
        
        # Sécurité : si le master a épuisé toute sa liste d'étudiants
        if prochain_choix[m] >= n_etu:
            continue
            
        # Le master fait sa proposition à l'étudiant suivant sur sa liste
        etu = CP[m][prochain_choix[m]]
        prochain_choix[m] += 1
        
        m_courant = affectation_etudiant[etu] # Master actuel de l'étudiant
        
        if m_courant == -1:
            # Cas 1 : L'étudiant est libre, il accepte l'offre
            affectation_etudiant[etu] = m
            places_prises[m] += 1
            
            # Si le master a encore des places, il retourne chercher d'autres étudiants
            if places_prises[m] < capacites[m]:
                masters_actifs.append(m)
                
        else:
            # Cas 2 : L'étudiant compare les deux offres via la matrice RE en O(1)
            if RE[etu][m] < RE[etu][m_courant]:
                # L'étudiant préfère le nouveau master (m), il abandonne l'ancien (m_courant)
                affectation_etudiant[etu] = m
                places_prises[m] += 1
                places_prises[m_courant] -= 1 # L'ancien master perd un étudiant !
                
                # Le nouveau master retourne en file s'il a encore de la place
                if places_prises[m] < capacites[m]:
                    masters_actifs.append(m)
                # L'ancien master a perdu une place, il redevient actif pour recruter !
                masters_actifs.append(m_courant) 
            else:
                # L'étudiant refuse, le master m a toujours une place vide, il re-tente au prochain tour
                masters_actifs.append(m)
                
    # 4. Formatage du résultat pour qu'il soit identique à la fonction de la Q3
    resultat_final = [[] for i in range(n_parcours)]
    for etu, m in enumerate(affectation_etudiant):
        if m != -1:
            resultat_final[m].append(etu)
            
    return resultat_final




# QUESTION 5: ======================================================================================================================
if __name__ == "__main__":
    # 1. Lecture des fichiers (Q1)
    CE = lire_preferences_etudiants("PrefEtu.txt")
    CP = lire_preferences_parcours("PrefSpe.txt")
    
    # 2. Récupération des capacités (Ligne 'Cap' de PrefSpe.txt)
    capacites = [2, 1, 1, 1, 2, 1, 1, 1, 1, 2]
    
    print("=======================================")
    print(" RÉSULTATS : GALE-SHAPLEY CÔTÉ ÉTUDIANTS ")
    print("=======================================")
    affectations_etu = gale_shapley_etudiants(CE, CP, capacites)
    for i, etudiants in enumerate(affectations_etu):
        print(f"Parcours {i:2d} a recruté les étudiants : {etudiants}")
        
    print("=======================================")
    print(" RÉSULTATS : GALE-SHAPLEY CÔTÉ PARCOURS ")
    print("=======================================")
    affectations_parcours = gale_shapley_parcours(CE, CP, capacites)
    for i, etudiants in enumerate(affectations_parcours):
        print(f"Parcours {i:2d} a recruté les étudiants : {etudiants}")

    print("")
    print("")



# QUESTION 6: ======================================================================================================================
def paires_instables(affectation, CE, CP):
    """
    Prend en entrée une affectation (liste de listes) et les matrices de préférences.
    Retourne la liste des paires instables sous forme de tuples (etudiant, parcours).
    """
    n_etu = len(CE)
    n_parcours = len(CP)
    
    # 1. Précalcul des matrices de rangs pour des comparaisons ultra-rapides en O(1)
    RE = [[0] * n_parcours for _ in range(n_etu)]
    for i in range(n_etu):
        for rang, master in enumerate(CE[i]):
            RE[i][master] = rang
            
    RP = [[0] * n_etu for _ in range(n_parcours)]
    for j in range(n_parcours):
        for rang, etu in enumerate(CP[j]):
            RP[j][etu] = rang

    # 2. Retrouver le master actuel de chaque étudiant (Matrice inverse de l'affectation)
    affectation_etudiant = [-1] * n_etu
    for m, etudiants in enumerate(affectation):
        for etu in etudiants:
            affectation_etudiant[etu] = m
            
    instabilites = []
    
    # 3. On teste toutes les causes d'instabilité possibles
    for etu in range(n_etu):
        m_courant = affectation_etudiant[etu]
        
        # Sécurité : si l'étudiant n'a pas été affecté (ne devrait pas arriver ici)
        if m_courant == -1:
            continue
            
        rang_m_courant = RE[etu][m_courant]
        
        # L'étudiant ne va regarder QUE les masters qu'il préfère à son master actuel
        # CE[etu][:rang_m_courant] renvoie la sous-liste de ses choix préférés
        masters_preferes = CE[etu][:rang_m_courant]
        
        for p in masters_preferes:
            etudiants_du_parcours_p = affectation[p]
            
            # On cherche le pire étudiant actuellement dans ce master 'p'
            # (Celui qui a le plus grand rang selon RP)
            pire_etu_de_p = max(etudiants_du_parcours_p, key=lambda x: RP[p][x])
            
            # Le master 'p' préfère-t-il notre 'etu' à son 'pire_etu_de_p' ?
            if RP[p][etu] < RP[p][pire_etu_de_p]:
                instabilites.append((etu, p))
                
    return instabilites

# === TEST ===
if __name__ == "__main__":
    print("=======================================")
    print(" TEST Q6 ")
    print(" VÉRIFICATION DE LA STABILITÉ ")
    print("=======================================")
    
    instabilites_etu = paires_instables(affectations_etu, CE, CP)
    print(f"Paires instables (GS Étudiants) : {len(instabilites_etu)} -> {instabilites_etu}")
    
    instabilites_parcours = paires_instables(affectations_parcours, CE, CP)
    print(f"Paires instables (GS Parcours)  : {len(instabilites_parcours)} -> {instabilites_parcours}")

    print("")
    print("")





# ==================================================================================================================================
# PARTIE 2 : Évolution du temps de calcul
# QUESTION 7: ======================================================================================================================

def generer_CE(n, m=9):
    """
    Génère une matrice CE des préférences aléatoires de n étudiants sur m parcours.
    Retourne une liste de n listes, chacune contenant une permutation aléatoire de {0, ..., m-1}.
    """
    CE = []
    for i in range(n):
        # random.sample sur un range renvoie une liste mélangée sans doublons
        preferences_aleatoires = random.sample(range(m), m)
        CE.append(preferences_aleatoires)
    return CE

def generer_CP(n, m=9):
    """
    Génère une matrice CP des préférences aléatoires de m parcours sur n étudiants.
    Retourne une liste de m listes, chacune contenant une permutation aléatoire de {0, ..., n-1}.
    """
    CP = []
    for j in range(m):
        # Le parcours j classe les n étudiants de manière aléatoire
        preferences_aleatoires = random.sample(range(n), n)
        CP.append(preferences_aleatoires)
    return CP


# QUESTION 8: ==========================================================================================================
def generer_capacites(n, m=9):
    """
    Génère un tableau de capacités équilibrées pour m parcours dont la somme fait exactement n.
    """
    base_cap = n // m
    reste = n % m
    capacites = [base_cap] * m
    
    # On distribue le reste (les étudiants restants) sur les premiers parcours
    for i in range(reste):
        capacites[i] += 1
        
    return capacites

def mesurer_temps_execution():
    """
    Fonction principale pour la Q8 : fait varier n, chronomètre les algorithmes,
    et trace les courbes de temps moyen.
    """
    valeurs_n = list(range(200, 2001, 200)) # De 200 à 2000 avec un pas de 200
    temps_moyen_etu = []
    temps_moyen_parcours = []
    nb_tests = 10
    m = 9 # Nombre de parcours fixé
    
    print("Début des tests de performance (cela peut prendre quelques secondes...)")
    
    for n in valeurs_n:
        somme_temps_etu = 0
        somme_temps_parcours = 0
        capacites = generer_capacites(n, m)
        
        # On fait 10 tests pour moyenner les résultats et éviter les biais d'une instance spécifique
        for _ in range(nb_tests):
            # 1. Génération de nouvelles données aléatoires
            CE = generer_CE(n, m)
            CP = generer_CP(n, m)
            
            # 2. Chronométrage côté Étudiants
            t_debut = time.perf_counter()
            gale_shapley_etudiants(CE, CP, capacites)
            t_fin = time.perf_counter()
            somme_temps_etu += (t_fin - t_debut)
            
            # 3. Chronométrage côté Parcours
            t_debut = time.perf_counter()
            gale_shapley_parcours(CE, CP, capacites)
            t_fin = time.perf_counter()
            somme_temps_parcours += (t_fin - t_debut)
            
        # Calcul de la moyenne pour ce n
        temps_moyen_etu.append(somme_temps_etu / nb_tests)
        temps_moyen_parcours.append(somme_temps_parcours / nb_tests)
        print(f"n = {n:4d} traité avec succès.")
        
    # --- Tracé de la courbe avec Matplotlib ---
    plt.figure(figsize=(10, 6))
    plt.plot(valeurs_n, temps_moyen_etu, label="GS côté Étudiants", marker='o', linestyle='-', color='blue')
    plt.plot(valeurs_n, temps_moyen_parcours, label="GS côté Parcours", marker='s', linestyle='-', color='red')
    
    plt.title("Temps d'exécution moyen de Gale-Shapley en fonction du nombre d'étudiants (n)")
    plt.xlabel("Nombre d'étudiants n")
    plt.ylabel("Temps moyen d'exécution (en secondes)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Sauvegarde de l'image (pratique pour l'inclure dans ton rapport !)
    plt.savefig("graphe_Q8.png")
    print("\nLe graphique a été sauvegardé sous le nom 'graphe_Q8.png'.")
    
    # Affichage à l'écran
    plt.show()


# === TEST ===
if __name__ == "__main__":
    print("=======================================")
    print(" TEST Q8 ")
    print(" TRACAGE DES GRAPHES ")
    print("=======================================")
    mesurer_temps_execution()
    print("")


# QUESTION 10: =========================================================================================================
def gale_shapley_etudiants_iter(CE, CP, capacites):
    """Version de GS Étudiants qui retourne uniquement le nombre d'itérations."""
    n_etu = len(CE)
    n_parcours = len(CP)
    
    RP = [[0] * n_etu for _ in range(n_parcours)]
    for j in range(n_parcours):
        for rang, etu in enumerate(CP[j]):
            RP[j][etu] = rang
            
    libres = list(range(n_etu))
    prochain_choix = [0] * n_etu
    affectations = [[] for _ in range(n_parcours)]
    
    nb_iterations = 0
    
    while libres:
        nb_iterations += 1 # ON COMPTE CHAQUE TOUR DE BOUCLE
        etu = libres.pop()
        
        if prochain_choix[etu] >= n_parcours:
            continue
            
        parcours = CE[etu][prochain_choix[etu]]
        prochain_choix[etu] += 1
        rang_etu = RP[parcours][etu]
        
        if len(affectations[parcours]) < capacites[parcours]:
            heapq.heappush(affectations[parcours], (-rang_etu, etu))
        else:
            pire_rang_neg, pire_etu = affectations[parcours][0]
            pire_rang = -pire_rang_neg
            
            if rang_etu < pire_rang:
                heapq.heappop(affectations[parcours])
                heapq.heappush(affectations[parcours], (-rang_etu, etu))
                libres.append(pire_etu)
            else:
                libres.append(etu)
                
    return nb_iterations

def gale_shapley_parcours_iter(CE, CP, capacites):
    """Version de GS Parcours qui retourne uniquement le nombre d'itérations."""
    n_etu = len(CE)
    n_parcours = len(CP)
    
    RE = [[0] * n_parcours for _ in range(n_etu)]
    for i in range(n_etu):
        for rang, master in enumerate(CE[i]):
            RE[i][master] = rang
            
    masters_actifs = []
    for j in range(n_parcours):
        if capacites[j] > 0:
            masters_actifs.append(j)
            
    prochain_choix = [0] * n_parcours
    places_prises = [0] * n_parcours
    affectation_etudiant = [-1] * n_etu
    
    nb_iterations = 0
    
    while masters_actifs:
        nb_iterations += 1 # ON COMPTE CHAQUE TOUR DE BOUCLE
        m = masters_actifs.pop()
        
        if prochain_choix[m] >= n_etu:
            continue
            
        etu = CP[m][prochain_choix[m]]
        prochain_choix[m] += 1
        m_courant = affectation_etudiant[etu]
        
        if m_courant == -1:
            affectation_etudiant[etu] = m
            places_prises[m] += 1
            if places_prises[m] < capacites[m]:
                masters_actifs.append(m)
        else:
            if RE[etu][m] < RE[etu][m_courant]:
                affectation_etudiant[etu] = m
                places_prises[m] += 1
                places_prises[m_courant] -= 1
                if places_prises[m] < capacites[m]:
                    masters_actifs.append(m)
                masters_actifs.append(m_courant)
            else:
                masters_actifs.append(m)
                
    return nb_iterations

def mesurer_iterations():
    """
    Fonction principale pour la Q10 : trace la courbe du nombre moyen d'itérations.
    """
    valeurs_n = list(range(200, 2001, 200))
    iter_moyenne_etu = []
    iter_moyenne_parcours = []
    nb_tests = 10
    m = 9
    
    print("Début des tests d'itérations (cela peut prendre quelques secondes...)")
    
    for n in valeurs_n:
        somme_iter_etu = 0
        somme_iter_parcours = 0
        capacites = generer_capacites(n, m)
        
        for _ in range(nb_tests):
            CE = generer_CE(n, m)
            CP = generer_CP(n, m)
            
            # On additionne les itérations renvoyées par nos nouvelles fonctions
            somme_iter_etu += gale_shapley_etudiants_iter(CE, CP, capacites)
            somme_iter_parcours += gale_shapley_parcours_iter(CE, CP, capacites)
            
        iter_moyenne_etu.append(somme_iter_etu / nb_tests)
        iter_moyenne_parcours.append(somme_iter_parcours / nb_tests)
        print(f"n = {n:4d} traité avec succès (Itérations).")
        
    # --- Tracé de la courbe avec Matplotlib ---
    plt.figure(figsize=(10, 6))
    plt.plot(valeurs_n, iter_moyenne_etu, label="GS côté Étudiants (Itérations)", marker='o', linestyle='-', color='blue')
    plt.plot(valeurs_n, iter_moyenne_parcours, label="GS côté Parcours (Itérations)", marker='s', linestyle='-', color='red')
    
    plt.title("Nombre moyen d'itérations de Gale-Shapley en fonction de n")
    plt.xlabel("Nombre d'étudiants n")
    plt.ylabel("Nombre moyen d'itérations (Tours de boucle)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.savefig("graphe_Q10.png")
    print("\nLe graphique a été sauvegardé sous le nom 'graphe_Q10.png'.")
    plt.show()

# === TEST ===
if __name__ == "__main__":
    print("=======================================")
    print(" TEST Q10 ")
    print(" TRACAGE DES GRAPHES ")
    print("=======================================")
    mesurer_iterations()



# QUESTION 11: =====================================================================================================================
def Q11_gurobi(CE, CP, capacites):
    n_etu = len(CE)
    n_parcours = len(CP)
    
    # 1. Calcul des scores de Borda
    U_E = [[0] * n_parcours for _ in range(n_etu)]
    for i in range(n_etu):
        for rang, j in enumerate(CE[i]):
            U_E[i][j] = n_parcours - rang
            
    U_P = [[0] * n_etu for _ in range(n_parcours)]
    for j in range(n_parcours):
        for rang, i in enumerate(CP[j]):
            U_P[j][i] = n_etu - rang
            
    # 2. Création du modèle
    modele = gp.Model("Maximiser_Equite_Q11")
    modele.Params.LogToConsole = 0
    
    # 3. Variables de décision
    x = modele.addVars(n_etu, n_parcours, vtype=GRB.BINARY, name="x")
    z = modele.addVar(vtype=GRB.INTEGER, name="z") # z représente l'utilité minimale
    
    # 4. Fonction objectif : Maximiser z (l'utilité du pire étudiant)
    modele.setObjective(z, GRB.MAXIMIZE)
    
    # 5. Contraintes
    # Contraintes de base
    modele.addConstrs((gp.quicksum(x[i, j] for j in range(n_parcours)) == 1 for i in range(n_etu)), name="Affectation")
    modele.addConstrs((gp.quicksum(x[i, j] for i in range(n_etu)) <= capacites[j] for j in range(n_parcours)), name="Capacite")
    
    # Nouvelle contrainte Q11 : z doit être inférieur ou égal à l'utilité de CHAQUE étudiant
    modele.addConstrs((z <= gp.quicksum(U_E[i][j] * x[i, j] for j in range(n_parcours)) for i in range(n_etu)), name="Min_Utilite")
    
    # 6. Optimisation
    modele.optimize()
    
    # 7. Résultats
    if modele.status == GRB.OPTIMAL:
        print("\n=======================================")
        print(" RÉSULTATS Q11 : PLNE (Équité - Maximiser le minimum)")
        print("=======================================")
        
        affectation_Q11 = [[] for _ in range(n_parcours)]
        utilite_totale = 0
        utilites_etudiants = []
        
        for i in range(n_etu):
            for j in range(n_parcours):
                if x[i, j].x > 0.5:
                    affectation_Q11[j].append(i)
                    utilite_totale += U_E[i][j] + U_P[j][i]
                    utilites_etudiants.append(U_E[i][j])
                    
        utilite_moyenne = sum(utilites_etudiants) / n_etu
        instabilites = paires_instables(affectation_Q11, CE, CP)
        
        print(f"-> Utilité minimale garantie (z) : {z.x}")
        print(f"-> Utilité moyenne des étudiants : {utilite_moyenne:.2f}")
        print(f"-> Utilité totale (E + P) : {utilite_totale}")
        print(f"-> Nombre exact de paires instables (Q11) : {len(instabilites)}")
    else:
        print("Aucune solution trouvée pour Q11.")


# QUESTION 12: =====================================================================================================================
def Q12_gurobi(CE, CP, capacites):
    n_etu = len(CE)       # 13 étudiants
    n_parcours = len(CP)  # 10 parcours
    
    # 1. Calcul des scores de Borda (Utilités)
    # L'utilité maximale est le nombre d'options possibles.
    U_E = [[0] * n_parcours for _ in range(n_etu)]
    for i in range(n_etu):
        for rang, j in enumerate(CE[i]):
            U_E[i][j] = n_parcours - rang  # 10 - rang (10 pour le 1er choix, 1 pour le dernier)
            
    U_P = [[0] * n_etu for _ in range(n_parcours)]
    for j in range(n_parcours):
        for rang, i in enumerate(CP[j]):
            U_P[j][i] = n_etu - rang       # 13 - rang (13 pour le 1er choix, 1 pour le dernier)
            
    # 2. Création du modèle Gurobi
    modele = gp.Model("Maximiser_Efficacite_Q12")
    
    # Optionnel : Désactiver les longs logs de Gurobi dans la console pour plus de lisibilité
    modele.Params.LogToConsole = 0 
    
    # 3. Variables de décision (x_ij : binaire)
    x = modele.addVars(n_etu, n_parcours, vtype=GRB.BINARY, name="x")
    
    # 4. Fonction objectif : Maximiser la somme des utilités globales (étudiants + parcours)
    modele.setObjective(
        gp.quicksum((U_E[i][j] + U_P[j][i]) * x[i, j] for i in range(n_etu) for j in range(n_parcours)),
        GRB.MAXIMIZE
    )
    
    # 5. Contraintes
    # Contrainte A : Chaque étudiant est affecté à exactement 1 parcours
    modele.addConstrs((gp.quicksum(x[i, j] for j in range(n_parcours)) == 1 for i in range(n_etu)), name="Affectation_unique")
    
    # Contrainte B : Respect des capacités des parcours
    modele.addConstrs((gp.quicksum(x[i, j] for i in range(n_etu)) <= capacites[j] for j in range(n_parcours)), name="Capacite_parcours")
    
    # 6. Lancement de l'optimisation
    modele.optimize()
    
    # 7. Analyse et extraction des résultats
    if modele.status == GRB.OPTIMAL:
        print("\n=======================================")
        print(" RÉSULTATS Q12 : PLNE (Efficacité totale)")
        print("=======================================")
        
        utilites_etudiants = []
        
        for i in range(n_etu):
            for j in range(n_parcours):
                # x[i, j].x contient la valeur trouvée par Gurobi (0 ou 1)
                # On utilise > 0.5 pour éviter les erreurs d'arrondi des nombres flottants
                if x[i, j].x > 0.5: 
                    u_etu = U_E[i][j]
                    utilites_etudiants.append(u_etu)
                    print(f"Étudiant {i:2d} affecté au parcours {j} (Son score de Borda : {u_etu})")
                    
        utilite_moyenne = sum(utilites_etudiants) / n_etu
        utilite_minimale = min(utilites_etudiants)
        
        print("\n--- Réponses aux questions du rapport ---")
        print(f"Somme totale des utilités (étudiants + parcours) : {modele.objVal}")
        print(f"Utilité moyenne des étudiants : {utilite_moyenne:.2f}")
        print(f"Utilité minimale d'un étudiant : {utilite_minimale}")

        affectation_Q12 = [[] for _ in range(n_parcours)]
        for i in range(n_etu):
            for j in range(n_parcours):
                if x[i, j].x > 0.5: 
                    affectation_Q12[j].append(i)
                    
        instabilites_Q12 = paires_instables(affectation_Q12, CE, CP)
        print(f"-> Nombre exact de paires instables (Q12) : {len(instabilites_Q12)}")
        
    else:
        print("Aucune solution optimale trouvée.")


# QUESTION 14: =====================================================================================================================
def Q14_gurobi(CE, CP, capacites):
    n_etu = len(CE)
    n_parcours = len(CP)
    
    # 1. Calcul des scores de Borda
    U_E = [[0] * n_parcours for _ in range(n_etu)]
    for i in range(n_etu):
        for rang, j in enumerate(CE[i]):
            U_E[i][j] = n_parcours - rang
            
    U_P = [[0] * n_etu for _ in range(n_parcours)]
    for j in range(n_parcours):
        for rang, i in enumerate(CP[j]):
            U_P[j][i] = n_etu - rang
            
    # 2. Boucle pour tester les valeurs de k de 1 à 10
    for k in range(1, 11):
        modele = gp.Model(f"Q13_Q14_k_{k}")
        modele.Params.LogToConsole = 0 # Désactiver les logs
        
        x = modele.addVars(n_etu, n_parcours, vtype=GRB.BINARY, name="x")
        
        # Fonction objectif : Maximiser l'efficacité totale
        modele.setObjective(
            gp.quicksum((U_E[i][j] + U_P[j][i]) * x[i, j] for i in range(n_etu) for j in range(n_parcours)),
            GRB.MAXIMIZE
        )
        
        # Contraintes de base (Affectation unique et Capacités)
        modele.addConstrs((gp.quicksum(x[i, j] for j in range(n_parcours)) == 1 for i in range(n_etu)), name="Affectation")
        modele.addConstrs((gp.quicksum(x[i, j] for i in range(n_etu)) <= capacites[j] for j in range(n_parcours)), name="Capacite")
        
        # NOUVELLE CONTRAINTE Q13 : Garantie du Top k
        limite_utilite = n_parcours - k + 1
        modele.addConstrs((gp.quicksum(U_E[i][j] * x[i, j] for j in range(n_parcours)) >= limite_utilite for i in range(n_etu)), name="Top_k")
        
        # Exécution de l'optimisation
        modele.optimize()
        
        # 3. Si Gurobi trouve une solution, c'est que c'est le plus petit k possible !
        if modele.status == GRB.OPTIMAL:
            print("\n=======================================")
            print(f" RÉSULTATS Q14 : Solution trouvée pour le plus petit k = {k}")
            print("=======================================")
            
            for i in range(n_etu):
                for j in range(n_parcours):
                    if x[i, j].x > 0.5:
                        u_etu = U_E[i][j]
                        rang_obtenu = 10 - u_etu + 1
                        print(f"Étudiant {i:2d} affecté au parcours {j} (Son choix n°{rang_obtenu})")
                        
            print(f"\n-> Utilité totale : {modele.objVal}")

            affectation_Q14 = [[] for _ in range(n_parcours)]
            for i in range(n_etu):
                for j in range(n_parcours):
                    if x[i, j].x > 0.5:
                        affectation_Q14[j].append(i)
                        
            instabilites_Q14 = paires_instables(affectation_Q14, CE, CP)
            print(f"-> Nombre exact de paires instables (Q14 k={k}) : {len(instabilites_Q14)}")


            return # On a trouvé le plus petit k, on arrête la fonction !
            
    print("Aucune solution trouvée, même pour k=10.")



# ==============================================================================
# BLOC D'EXÉCUTION PRINCIPAL 
# ==============================================================================
if __name__ == "__main__":

    Q11_gurobi(CE, CP, capacites)
    Q12_gurobi(CE, CP, capacites)
    Q14_gurobi(CE, CP, capacites)


# --- CALCUL EXACT DES SCORES GALE-SHAPLEY ---
    def calculer_utilite_GS(affectation, CE, CP):
        n_etu = len(CE)
        n_parcours = len(CP)
        utilite_etudiants = 0
        utilite_totale = 0
        
        for j in range(n_parcours):
            for i in affectation[j]:
                u_E = n_parcours - CE[i].index(j)
                u_P = n_etu - CP[j].index(i)
                utilite_etudiants += u_E
                utilite_totale += (u_E + u_P)
                
        return utilite_totale, (utilite_etudiants / n_etu)

    tot_etu, moy_etu = calculer_utilite_GS(affectations_etu, CE, CP)
    print(f"\n-> GS Étudiants - Totale : {tot_etu}, Moyenne : {moy_etu:.2f}")