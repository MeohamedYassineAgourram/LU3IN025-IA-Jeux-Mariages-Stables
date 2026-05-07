# TME - semaines 1 à 3

## 1 Problème et aﬀectation:

### Q1. Lecture des fichiers et extraction des matrices $C_E$ et $C_P$
Pour cette première étape, nous avons implémenté deux fonctions distinctes permettant de parser les fichiers textes fournis et de construire les matrices de préférences $C_E$ (étudiants) et $C_P$ (parcours).
* **Structure de données** : Nous avons fait le choix de représenter les matrices $C_E$ et $C_P$ sous la forme de listes de listes en Python. Ainsi, accéder aux préférences de l'étudiant $i$ se fait en temps constant $O(1)$ via l'instruction *``CE[i]``*, qui retourne la liste ordonnée de ses vœux.
* **Traitement du parsing** : Pour le fichier *``PrefEtu.txt``*, nous ignorons la première ligne d'en-tête contenant le nombre total d'étudiants. Pour le fichier *``PrefSpe.txt``*, nous ignorons les deux premières lignes qui contiennent respectivement le nombre d'étudiants et les capacités d'accueil des parcours.
* **Nettoyage des données** : Lors de la lecture ligne par ligne, nous utilisons la méthode *``split()``* pour isoler chaque élément. Nous ignorons systématiquement les deux premières colonnes (l'indice numérique et le label sous forme de chaîne de caractères, par exemple "Etu0" ou "AI2D") pour ne conserver que les identifiants numériques des choix, que nous castons explicitement en entiers (int) afin de pouvoir les manipuler lors de l'algorithme de Gale-Shapley.

### Q2. Choix et justification des structures de données pour l'algorithme de Gale-Shapley
Pour garantir une complexité optimale de l'algorithme de Gale-Shapley (idéalement $O(n \times m)$ dans notre cas asymétrique, avec $n$ étudiants et $m$ parcours), il est impératif de réduire la complexité temporelle de chaque opération interne à $O(1)$ ou s'en approchant. Voici les structures de données que nous avons choisies :
1. **Trouver un étudiant libre à chaque itération** :        
        --> *``Structure``* : Une liste utilisée comme une Pile (LIFO) ou une File (FIFO), contenant initialement les identifiants de tous les étudiants.        
        --> *``Complexité``* : L'ajout (si un étudiant est rejeté) et le retrait (pour traiter un étudiant libre) s'effectuent en temps constant $O(1)$. La complexité spatiale est de $O(n)$.

2. **Trouver le prochain parcours à qui faire une proposition** :           
        --> *``Structure``* : Un tableau d'entiers prochain_choix de taille $n$, initialisé à 0. L'index représente l'étudiant, et la valeur correspond à l'index de son prochain choix dans sa liste de préférences $C_E$.          
        --> *``Complexité``* : La consultation et l'incrémentation de cette valeur se font en $O(1)$. Cela évite de modifier la matrice $C_E$. Complexité spatiale : $O(n)$.

3. **Trouver la position de l'étudiant $i$ dans le classement du parcours $j$** :                 
        --> *``Structure``* : Une matrice des rangs $R_P$ (inverse de $C_P$). Cette matrice de dimensions $m \times n$ est précalculée avant de lancer l'algorithme. La case $R_P[j][i]$ contient le rang (entier) de l'étudiant $i$ selon le parcours $j$       
        --> *``Complexité``* : Le précalcul coûte $O(m \times n)$ en temps, mais une fois créé, l'accès au rang en cours d'algorithme se fait en temps constant $O(1)$. Sans cela, la recherche aurait coûté $O(n)$ à chaque proposition. La complexité spatiale est de $O(m \times n)$.

4. et 5. **Trouver l'étudiant le moins préféré et le remplacer** :                
        --> *``Structure``* : Pour chaque parcours, nous maintenons les étudiants actuellement affectés dans un Tas (Heap), et plus spécifiquement une file de priorité implémentée sous forme de Max-Heap.La priorité de chaque étudiant dans le tas est définie par son rang selon le parcours (obtenu en $O(1)$ via la matrice précalculée $R_P$). L'étudiant le moins préféré (celui ayant le rang numérique le plus élevé) est ainsi toujours maintenu à la racine du tas.               
        --> *``Complexités``* :                
                * **Trouver le moins préféré (Opération 4)** : L'accès à la racine du tas se fait en temps constant $O(1)$.          
                * **Remplacer un étudiant (Opération 5)** : Remplacer consiste à extraire l'élément à la racine (l'étudiant rejeté) et à insérer le nouvel étudiant. Ces deux opérations de maintien de la structure de tas s'effectuent en $O(\log C)$, où $C$ est la capacité du parcours.

### Q3. Implémentation et analyse de la complexité de Gale-Shapley "côté étudiants"
L'algorithme a été implémenté en se basant sur les structures de données qu'on a justifiées à la question précédente.

**Logique d'implémentation :**     
1. Nous calculons au début une matrice des rangs $R_P$ à partir de $C_P$.
2. Une pile (*``libres``*) gère les étudiants sans affectation qu'on a décrit comme libre.
3. Pour chaque proposition d'un étudiant $i$ à un parcours $j$, le parcours compare le rang de $i$ (récupéré en $O(1)$ via $R_P$) avec le rang de son "pire" étudiant actuellement affecté. Ce dernier est toujours situé à la racine du Max-Heap gérant les affectations du parcours $j$.
4. Si l'étudiant proposant est meilleur, il remplace le pire étudiant du tas, et ce dernier est réinséré dans la pile libres pour qu'il soit traité dans le prochain tour de boucle.

**Analyse de la complexité :**    
Soit $n$ le nombre d'étudiants, $m$ le nombre de parcours, et $C$ la capacité maximale d'un parcours.

* **Complexité temporelle : $\mathcal{O}(n \cdot m \cdot \log C)$**
        --> Le précalcul de la matrice $R_P$ nécessite de parcourir toutes les préférences des masters, soit $\mathcal{O}(m \cdot n)$.      
        --> Dans le pire des cas, chaque étudiant peut faire une proposition à chaque master. Le nombre maximal de propositions est donc de $n \times m$.         
        --> À chaque itération (proposition), extraire un étudiant libre, trouver son prochain choix et consulter son rang se font en $\mathcal{O}(1)$.         
        --> Si le parcours accepte l'étudiant, l'insertion (et l'éventuelle suppression du pire étudiant) dans le Max-Heap prend $\mathcal{O}(\log C)$.         
        --> La boucle principale s'exécute donc en $\mathcal{O}(n \cdot m \cdot \log C)$. La complexité totale est par conséquent dominée par $\mathcal{O}(n \cdot m \cdot \log C)$. (Mais comme dans notre cas $C \le 2$, $\log C$ est une constante négligeable, la complexité devient $\mathcal{O}(n \cdot m)$).   
        
* **Complexité spatiale : $\mathcal{O}(n \cdot m)$**
        --> Les matrices $C_E$, $C_P$ et $R_P$ occupent chacune un espace $\mathcal{O}(n \cdot m)$.               
        --> Les structures utilitaires (*``libres``*, *``prochain_choix``*) prennent $\mathcal{O}(n)$.              
        --> Les listes de tas stockant les affectations prennent un espace total proportionnel à la somme des capacités, soit $\mathcal{O}(n)$.              
        --> L'espace mémoire globale de notre algorithme est donc bornée par $\mathcal{O}(n \cdot m)$.

### Q4. Adaptation de Gale-Shapley "côté parcours"
1. **Logique de l'adaptation :**
Comme indiqué dans le cours, cette version inversée de l'algorithme "Proposer et Rejeter" permet de trouver l'affectation "hôpital-optimale" (ici parcours-optimale) au lieu de l'affectation "interne-optimale". Dans cette configuration, un master (qui possède une capacité $C$) continue de formuler des propositions tant qu'il a des places vacantes. Un étudiant (qui n'a qu'une seule place) accepte la première offre, puis ne la quitte que s'il reçoit une proposition d'un master qu'il préfère strictement.

2. **Structures de données optimisées :**
* **Matrice des rangs des étudiants ($R_E$) :** Inverse de la matrice $C_E$, calculée au démarrage en $O(n \times m)$. Elle permet à un étudiant, lors d'une nouvelle proposition, de comparer le rang du nouveau parcours avec celui de son parcours actuel en temps constant $O(1)$.
* **File *``masters_actifs``* :** Contient les parcours ayant des places disponibles. L'ajout et l'extraction se font en $O(1)$.
* **Tableaux d'états :** *``prochain_choix``* gère l'avancement dans les listes de préférences des parcours, *``places_prises``* gère le remplissage des capacités, et *``affectation_etudiant``* mémorise le parcours actuel de chaque étudiant. Tous offrent un accès et une modification en $O(1)$. Il n'y a plus besoin de structure de Tas (Heap) asymétrique car l'étudiant ne stocke qu'une seule affectation.

3. **Complexité :**
* **Temporelle : $O(n \times m)$**
Le précalcul de $R_E$ prend $O(n \times m)$. Dans la boucle principale, chaque parcours propose au maximum une fois à chaque étudiant, limitant le nombre total d'itérations à $n \times m$. Toutes les opérations internes (comparaison $R_E$, mises à jour des tableaux, gestion de la file) coûtant $O(1)$, la complexité totale est de $O(n \times m)$.
* **Spatiale : $O(n \times m)$**
Dominée par le stockage de la matrice $R_E$ et des listes de préférences. Les tableaux d'état n'occupent qu'un espace $O(n + m)$.

### Q5. Application des algorithmes sur les instances de test
Nous avons exécuté nos deux implémentations de l'algorithme de Gale-Shapley sur les instances fournies (*``PrefEtu.txt``* et *``PrefSpe.txt``*), en paramétrant le vecteur de capacités des $m=10$ parcours : $C = [2, 1, 1, 1, 2, 1, 1, 1, 1, 2]$. (La somme des capacités est de 13, ce qui correspond exactement au nombre d'étudiants).

Résultats obtenus :
* **Affectation GS côté Étudiants :**                 
Parcours  0 a recruté les étudiants : [12, 5]               
Parcours  1 a recruté les étudiants : [4]             
Parcours  2 a recruté les étudiants : [9]          
Parcours  3 a recruté les étudiants : [8]         
Parcours  4 a recruté les étudiants : [11, 10]           
Parcours  5 a recruté les étudiants : [0]         
Parcours  6 a recruté les étudiants : [1]        
Parcours  7 a recruté les étudiants : [7]         
Parcours  8 a recruté les étudiants : [6]           
Parcours  9 a recruté les étudiants : [2, 3]          

* **Affectation GS côté Parcours :**             
Parcours  0 a recruté les étudiants : [5, 12]           
Parcours  1 a recruté les étudiants : [4]         
Parcours  2 a recruté les étudiants : [9]            
Parcours  3 a recruté les étudiants : [8]            
Parcours  4 a recruté les étudiants : [10, 11]            
Parcours  5 a recruté les étudiants : [0]          
Parcours  6 a recruté les étudiants : [1]         
Parcours  7 a recruté les étudiants : [7]         
Parcours  8 a recruté les étudiants : [6]         
Parcours  9 a recruté les étudiants : [2, 3]         

### Q6. Vérification de la stabilité des affectations
Pour vérifier la validité de nos algorithmes, nous avons implémenté un vérificateur qui s'appuie strictement sur la définition d'une paire instable vue en cours : une affectation n'est pas stable s'il existe une paire (Étudiant $i$, Parcours $j$) telle que l'étudiant $i$ préfère le parcours $j$ à son affectation courante, et que le parcours $j$ préfère l'étudiant $i$ à au moins l'un de ses étudiants actuellement affectés.

**Implémentation du vérificateur :**
Notre méthode *``paires_instables(affectation, CE, CP)``* suit la logique suivante :
1. Elle calcule les matrices de rangs $R_E$ et $R_P$ pour évaluer les préférences en temps constant $O(1)$.          
2. Pour chaque étudiant, elle isole l'ensemble des parcours qu'il préfère strictement à son affectation courante.          
3. Pour chacun de ces parcours cibles, elle identifie l'étudiant "le moins préféré" actuellement affecté (celui ayant le pire rang selon $R_P$).            
4. Elle compare le rang de l'étudiant évalué avec celui de ce "pire" étudiant. Si le parcours préfère le nouvel étudiant, la paire est déclarée instable.        

**Résultats et validation :**
En passant les résultats obtenus à la Question 5 dans ce vérificateur, nous obtenons les retours suivants de la console :
* *``Paires instables (GS Étudiants) : 0 -> []``*
* *``Paires instables (GS Parcours)  : 0 -> []``*               

Ces listes vides prouvent de manière empirique que les deux variantes de l'algorithme de Gale-Shapley implémentées aux questions 3 et 4 fonctionnent correctement sur cette instance et retournent bien des mariages parfaitement stables.


## 2 Évolution du temps de calcul

### Q7. Génération de matrices de préférences aléatoires
Pour évaluer la montée en charge de nos algorithmes, nous avons implémenté deux générateurs d'instances aléatoires. Afin de rendre le code modulable, nous avons ajouté le nombre de parcours $m$ en paramètre avec 9 comme valeur par défaut.

* **Matrice $C_E$ (Étudiants) :** La fonction `generer_CE(n, m)` crée une liste de $n$ listes. Pour chaque étudiant, nous utilisons la fonction `random.sample(range(m), m)` de la bibliothèque standard de Python. Cela génère une permutation aléatoire uniforme des entiers de $0$ à $m-1$, représentant les préférences de l'étudiant, en temps $O(m)$. La complexité totale de la génération est donc en $\mathcal{O}(n \times m)$.
* **Matrice $C_P$ (Parcours) :** De manière symétrique, la fonction `generer_CP(n, m)` crée une liste de $m$ listes. Pour chaque parcours, nous générons une permutation aléatoire des entiers de $0$ à $n-1$ via `random.sample(range(n), n)`, ce qui s'effectue en temps $O(n)$. La complexité totale est également en $\mathcal{O}(n \times m)$.

Ces deux fonctions renvoient des structures de données strictement identiques (des listes de listes) à celles produites par nos fonctions de parsing de la Question 1. Ainsi, elles sont directement compatibles avec nos implémentations de l'algorithme de Gale-Shapley (Q3 et Q4).

### Q8. Mesures expérimentales du temps de calcul
Pour analyser le comportement pratique de nos algorithmes face au passage à l'échelle, nous avons mis en place une campagne d'expérimentation avec le protocole suivant :

* **Variation de la taille de l'instance** : Nous avons fait varier le nombre d'étudiants $n$ de **200 à 2000** par pas de 200, tout en gardant le nombre de parcours $m$ fixé à 9.
* **Génération des capacités** : Pour chaque valeur de $n$, nous avons réparti les capacités de manière équilibrée et déterministe. Chaque parcours reçoit une capacité de base de $n \div 9$ (division entière), et le reste (modulo) est distribué unité par unité sur les premiers parcours afin que la somme totale des capacités vaille exactement $n$.
* **Robustesse de la mesure** : Nous avons généré 10 instances aléatoires distinctes pour chaque valeur de $n$. Le temps retenu et affiché sur la courbe est la **moyenne des 10 exécutions**, mesurée grâce à la fonction haute précision `time.perf_counter()` de Python qui contrairement à `time.time()`, cette fonction est conçue spécifiquement pour mesurer des performances d'exécution (en nanosecondes). C'est beaucoup plus précis sur des algorithmes rapides.

**Résultats obtenus :**
*(Le graphique ci-dessous a été généré via la bibliothèque `matplotlib`)*

![Graphe Q8 - Temps d'exécution moyen](graphe_Q8.png)

### Q9. Analyse de la complexité observée
**1. Observation empirique (Lecture du graphique) :**                
Sur le graphique généré à la question précédente, nous observons que le temps de calcul moyen pour les deux variantes de l'algorithme croît de manière strictement proportionnelle au nombre d'étudiants $n$. Concrètement, lorsque la taille de l'instance double (par exemple en passant de $n=500$ à $n=1000$), le temps d'exécution double également. Sur un graphique, cette croissance proportionnelle se traduit par des lignes droites. Cela caractérise visuellement et empiriquement une **complexité linéaire**, notée $\mathcal{O}(n)$.

**2. Cohérence avec l'analyse théorique :**            
Ce comportement pratique valide parfaitement notre analyse mathématique théorique. En effet, nous avons établi aux questions 3 et 4 que la complexité temporelle théorique de nos algorithmes était de $\mathcal{O}(n \times m)$ dans le pire des cas, en considérant le coût des opérations internes (comme l'insertion dans un tas de petite taille) comme asymptotiquement négligeable.

L'apparente contradiction entre la théorie $\mathcal{O}(n \times m)$ et la pratique $\mathcal{O}(n)$ s'explique par notre protocole expérimental :
* Dans nos tests, nous faisons varier $n$ (de 200 à 2000), mais le nombre de parcours $m$ reste une **constante fixée à 9**.
* La complexité théorique pour cette expérience devient donc $\mathcal{O}(n \times 9)$.
* En notation asymptotique (Grand O), les constantes multiplicatives sont ignorées car elles ne modifient pas l'allure générale de la courbe de croissance. Mathématiquement, $\mathcal{O}(9n)$ équivaut strictement à $\mathcal{O}(n)$.

La théorie prédisait donc une ligne droite pour un nombre de parcours fixe, ce qui est exactement ce que l'expérience nous démontre.

**3. Analyse de la différence de pente (La constante cachée) :**               
Bien que les deux courbes soient des droites de complexité linéaire, nous remarquons que la courbe rouge (algorithme "côté parcours") possède une pente plus raide que la courbe bleue (algorithme "côté étudiants"). Elle prend un peu plus de temps pour traiter le même nombre d'étudiants.

Cela s'explique par la **constante cachée** de la notation $\mathcal{O}(n)$. En réalité, le temps d'exécution est $T(n) = c \times n$. Ici, la constante $c$ (le temps de traitement de base pour un étudiant) est plus élevée dans la version "parcours" à cause de la logique de l'algorithme:

* **Dans la version "côté étudiants"** : Un étudiant ne recherche qu'une seule affectation. Une fois accepté, il ne retourne dans la boucle d'affectation que s'il est explicitement remplacé par un meilleur candidat.
* **Dans la version "côté parcours"** : Les parcours doivent remplir des capacités d'accueil $C_i$ importantes [cite: 1, 457] (en moyenne $C \approx n/9$, soit plus de 220 places pour $n=2000$). À chaque fois qu'un seul de ces étudiants reçoit une meilleure offre ailleurs, le master perd une place, redevient "incomplet", et doit obligatoirement retourner dans la file d'attente (la pile `masters_actifs`) pour formuler de nouvelles propositions.

Ce phénomène de "va-et-vient" continu pour combler les places libérées génère un nombre de ré-itérations bien plus important, ce qui se traduit par une pente plus forte sur le graphique, tout en conservant une croissance globalement linéaire.