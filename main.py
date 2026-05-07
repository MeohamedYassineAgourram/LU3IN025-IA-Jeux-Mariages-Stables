import exemple # Pour pouvoir utiliser les methodes de exemple.py
import heapq
import random
import time
import matplotlib.pyplot as plt

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