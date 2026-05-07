def lectureFichier(s): # Definition d'une fonction, avec un parametre (s). Ne pas oublier les ":"
    monFichier = open(s, "r") # Ouverture en lecture. Indentation par rapport a la ligne d'avant (<-> bloc).
    contenu = monFichier.readlines() # Contenu contient une liste de chainces de caracteres, chaque chaine correspond a une ligne       
    monFichier.close() #Fermeture du fichier
    contenu[0]=contenu[0].split()     # ligne.split() renvoie une liste de toutes les chaines contenues dans la chaine ligne (separateur=espace)
    contenu[1]=contenu[1].split()
    return contenu
    # Commandes utiles:
    # n=int(s) transforme la chaine s en entier.
    # s=str(n) l'inverse
    # Quelques methodes sur les listes:
    # l.append(t) ajoute t a la fin de la liste l
    # l.index(t) renvoie la position de t dans l (s'assurer que t est dans l)
    # for s in l: s vaut successivement chacun des elements de l (pas les indices, les elements)


def createFichierLP(nomFichier,nombreVariables):
    monFichier=open(nomFichier,"w") #Ouverture en ecriture. Le fichier est ecrase s'il existe, cree s'il n'existe pas
    monFichier.write("Maximize\n")
    for i in range(0,nombreVariables): #Boucle i variant de 0 a NombreVariables-1
        monFichier.write("x"+str(i)+" ") #write pour ecrire. Indentation
        if (i<nombreVariables-1): # Syntaxe d'un test. 'and' et 'or' dans les expressions logique
            monFichier.write("+ ")
        else:
            monFichier.write("\n")
    monFichier.write("st\n") # Fin de l'indentation -> fin de la boucle
    monFichier.write("Binary\n")
    for i in range(0,nombreVariables):
        monFichier.write("x"+str(i)+" ")
    monFichier.write("\n")
    monFichier.write("end")
    monFichier.close()




# QUESTION 2:
# 1- Une pile ou une file des étudiants qui sont libre, pour faciliter les opérations d'ajout et retrait soit du début soit du fin

# 2- Un taleau qui a pour taille le nombre des étudiant et chaque case correspondant à un étudiant contient son prochain choix
# à considérer lors des affectations

# 3- Une Matrice de (Parcours x Etudiants) dans lauqel au lieu d'avoir les étudiants classé tout au long de la ligne, la matrcice
# va avoir au niveau de la case [j][i] le claseement de l'étudiant i
# (--- À REVOIR CETTE SOLUTION ---)

# 4- Un tas, donc un arbre triée pour chaque parcours dans lequel l'étudiant avec le pire classement serait toujours au niveau de
# la racine de cette arbre

# 5- La même structure du tas il suffit de supprimer l'étudiant à la racine et le replacer par le nouveau et ensuite réorganiser