from classes import Tuile, Main, Pioche, Plateau, Joueur, Combinaison
import copy
class Jeu:
    def __init__(self, n_joueurs: int = 1):
        """Initialise une partie avec n_joueurs (par défaut 1).

        Chaque joueur reçoit 14 tuiles au départ.
        """
        self.pioche = Pioche()
        self.plateau = Plateau()
        # Crée la liste de joueurs
        self.joueurs = [Joueur(f"Joueur {i+1}") for i in range(max(1, int(n_joueurs)))]
        self.tour = 0
        self.partie_terminee = False

        # Distribution initiale : 14 tuiles par joueur
        for _ in range(14):
            for j in self.joueurs:
                j.piocher(self.pioche)

    def afficher_etat(self):
        print("\n===== ÉTAT DU JEU =====")
        print(f"Plateau :\n{self.plateau.afficher()}")
        for j in self.joueurs:
            print(f"\n{j.nom} : {j.rack.afficher()}")
        print("========================\n")

    def poser_combinaison(self, joueur):
        print("\n>>> Pose de combinaison (plateau et/ou rack)")
        print(f"Plateau :\n{self.plateau.afficher()}")
        print(f"Ton rack : {joueur.rack.afficher()}")
        print("Tu peux mélanger des tuiles du plateau et de ton rack.")
        try:
            positions = input("Positions plateau (ex: 0:1,2:0, vide si aucune). Pour une colonne: col:j : ").strip()
            rack_indices = input("Indices rack (ex: 0,1,2, vide si aucune) : ").strip()

            pos_list = []
            if positions:
                # support colonne: 'col:j' -> prend la j-ème tuile de chaque combinaison (si elle existe)
                if positions.startswith('col:'):
                    try:
                        col_idx = int(positions.split(':',1)[1])
                    except Exception:
                        raise IndexError("Format colonne invalide. Utilise col:j")
                    for i in range(len(self.plateau.mains)):
                        if col_idx >= 0 and col_idx < len(self.plateau.mains[i].tuiles):
                            pos_list.append((i, col_idx))
                else:
                    parts = [p.strip() for p in positions.split(",") if p.strip()]
                    for part in parts:
                        i,j = part.split(":")
                        i, j = int(i), int(j)
                        if i < 0 or i >= len(self.plateau.mains):
                            raise IndexError(f"Index de combinaison invalide: {i}")
                        if j < 0 or j >= len(self.plateau.mains[i].tuiles):
                            raise IndexError(f"Index de tuile invalide: {j} dans combinaison {i}")
                        pos_list.append((i, j))

            rack_list = []
            if rack_indices:
                rack_list = [int(idx.strip()) for idx in rack_indices.split(",") if idx.strip()]
                for idx in rack_list:
                    if idx < 0 or idx >= len(joueur.rack.tuiles):
                        raise IndexError(f"Index de rack invalide: {idx}")

            tuiles_plateau = [self.plateau.mains[i].tuiles[j] for (i,j) in pos_list]
            tuiles_rack = [joueur.rack.tuiles[idx] for idx in rack_list]
            tuiles = tuiles_plateau + tuiles_rack
            if not tuiles:
                print("Aucune tuile sélectionnée.")
                return
            comb = Combinaison(tuiles)
            if comb.est_valide():
                # Retirer d'abord les tuiles du plateau (attention à l'ordre)
                for i,j in sorted(pos_list, reverse=True):
                    self.plateau.retirer_tuile(i, j)
                # Retirer les tuiles du rack
                for idx in sorted(rack_list, reverse=True):
                    joueur.rack.retirer(joueur.rack.tuiles[idx])
                self.plateau.ajouter(comb)
                print(" Combinaison posée !")
            else:
                print(" Combinaison invalide (selon les tuiles sélectionnées).")
        except Exception as e:
            print("Erreur :", e)

    def tirer_tuile(self, joueur):
        t = joueur.tirer_tuile(self.pioche)
        if t:
            print(f"{joueur.nom} a tiré {t}")
        else:
            print("La pioche est vide.")

    def passer_tour(self):
        print("Tour passé.")

    def verifier_fin(self):
        for j in self.joueurs:
            if len(j.rack.tuiles) == 0:
                print(f" {j.nom} a gagné la partie !")
                self.partie_terminee = True

    def jouer(self):
        print("=== Début du jeu Rummikub ===")
        while not self.partie_terminee:
            joueur = self.joueurs[self.tour % len(self.joueurs)]
            print(f"\n----- Tour de {joueur.nom} -----")
            self.afficher_etat()

            choix = input("Choisis une action (p=poser, t=tirer, m=manipuler plateau, s=sauter, q=quitter) : ").lower()

            if choix == "p":
                self.poser_combinaison(joueur)
            elif choix == "t":
                self.tirer_tuile(joueur)
            elif choix == "m":
                sub = input("Action plateau (deplacer/fusionner/split) : ").lower().strip()

                backup = copy.deepcopy(self.plateau.mains)
                try:
                    if sub == 'deplacer':
                        src = input("Source (ex 0:1) : ")
                        i,j = [int(x) for x in src.split(":")]
                        dest = int(input("Index combinaison destination : "))
                        pos_dest_str = input("Position d'insertion destination (optionnel, vide pour fin) : ").strip()
                        pos_dest = int(pos_dest_str) if pos_dest_str != "" else None
                        ok = joueur.manipuler_plateau(self.plateau, 'deplacer', index_src=i, index_tuile=j, index_dest=dest, pos_dest=pos_dest)
                    elif sub == 'fusionner':
                        a = int(input("Index 1 : "))
                        b = int(input("Index 2 : "))
                        ok = joueur.manipuler_plateau(self.plateau, 'fusionner', index1=a, index2=b)
                    elif sub == 'split':
                        idx = int(input("Index combinaison à splitter : "))
                        pos = int(input("Position de split (index de tuile) : "))
                        ok = joueur.manipuler_plateau(self.plateau, 'split', index=idx, split_pos=pos)
                    elif sub == 'reutiliser':
                        indices_str = input("Indices des tuiles à réutiliser (ex: 0:1,1:2) : ")
                        parts = [p.strip() for p in indices_str.split(",") if p.strip()]
                        indices = [(int(i), int(j)) for i,j in (part.split(":") for part in parts)]
                        ok = joueur.manipuler_plateau(self.plateau, 'reutiliser', indices=indices)
                    else:
                        print("Action non reconnue.")
                        ok = False
                except Exception as e:
                    print("Erreur lors de la manipulation :", e)
                    ok = False
                if not self.plateau.est_valide_plateau():
                    print(" Manipulation annulée : le plateau serait invalide. Restauration de l'état précédent.")
                    self.plateau.mains = backup
                else:
                    if ok:
                        print(" Manipulation appliquée.")
                    else:
                        print("La manipulation a échoué.")
            elif choix == "s":
                self.passer_tour()
            elif choix == "q":
                print("Fin de la partie.")
                break
            else:
                print("Choix invalide.")

            self.verifier_fin()
            self.tour += 1
        print("=== Fin du jeu ===")
