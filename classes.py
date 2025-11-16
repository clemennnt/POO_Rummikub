import random

class Tuile:
    """
    Représente une tuile du jeu Rummikub.
    Attributs :
        couleur (str): Couleur de la tuile ('rouge', 'bleu', 'noir', 'jaune', ou 'joker').
        valeur (int): Valeur numérique de la tuile (1-13, ou 0 pour joker).
        is_joker (bool): Indique si la tuile est un joker.
    Méthodes :
        __init__, __repr__
    """
    def __init__(self, couleur:str, valeur:int, is_joker:bool=False):
        self.couleur = couleur
        self.valeur = valeur
        self.is_joker = is_joker

    def __repr__(self):
        # Affichage couleur terminal (ANSI)
        if self.is_joker:
            return "\033[35mJ\033[0m"  # Joker en magenta
        couleur_ansi = {
            "rouge": "\033[31m",
            "bleu": "\033[34m",
            "noir": "\033[30m",
            "jaune": "\033[33m"
        }.get(self.couleur, "")
        reset = "\033[0m"
        return f"{couleur_ansi}{self.valeur}{reset}"

class Main:
    """
    Représente une main de tuiles (utilisée pour les combinaisons et le rack).
    Attributs :
        tuiles (list[Tuile]) : Liste des tuiles dans la main.
    Méthodes :
        ajouter_tuile, retirer_tuile, est_valide, __repr__
    """
    def __init__(self):
        self.tuiles = []

    def ajouter_tuile(self, tuile:Tuile):
        self.tuiles.append(tuile)

    def retirer_tuile(self, tuile:Tuile):
        self.tuiles.remove(tuile)

    def est_valide(self):
        if len(self.tuiles) < 3:
            return False
        tuiles = self.tuiles[:]
        jokers = [t for t in tuiles if t.is_joker]
        non_jokers = [t for t in tuiles if not t.is_joker]
        valeurs = [t.valeur for t in non_jokers]
        couleurs = [t.couleur for t in non_jokers]
        # Groupe : même valeur, couleurs toutes différentes
        if len(valeurs) > 0 and len(set(valeurs)) == 1:
            # On doit avoir au plus un joker, et toutes les couleurs différentes
            total_couleurs = couleurs + [f"joker{n}" for n in range(len(jokers))]
            if len(set(total_couleurs)) == len(total_couleurs):
                return True
        # Suite : même couleur, valeurs consécutives
        if len(set(couleurs)) == 1 and len(couleurs) > 0:
            vals = sorted(valeurs)
            jokers_count = len(jokers)
            # On insère les jokers pour compléter la suite
            for _ in range(jokers_count):
                # Cherche où insérer le joker pour compléter la suite
                inserted = False
                for i in range(len(vals)-1):
                    if vals[i+1] - vals[i] > 1:
                        vals.insert(i+1, vals[i]+1)
                        inserted = True
                        break
                if not inserted:
                    # Joker en fin ou début
                    if vals:
                        vals.append(vals[-1]+1)
                    else:
                        vals.append(1)
            # Vérifie la suite
            if all(vals[i]+1 == vals[i+1] for i in range(len(vals)-1)):
                return True
        return False

    def __repr__(self):
        return f"Main(tuiles={self.tuiles})"



class Combinaison(Main):
    """
    Représente une combinaison de tuiles (suite ou groupe). Hérite de Main.
    Méthodes :
        contient_joker, remplacer_joker, points
    """
    def __init__(self, tuiles):
        super().__init__()
        self.tuiles = list(tuiles)
    def contient_joker(self):
        return any(t.is_joker for t in self.tuiles)
    def remplacer_joker(self, tuile_replacement:Tuile):
        for i, t in enumerate(self.tuiles):
            if t.is_joker:
                self.tuiles[i] = tuile_replacement
                return True
        return False
    def points(self, context: str = 'normal'):
        """Calcule les points de la combinaison.

        Paramètre implicite (comportement selon contexte) :
        - context='initial' : pour la première pose, les jokers prennent la valeur
          des tuiles qu'ils remplacent (inférée à partir de la combinaison).
        - context='final' : pour le décompte final, chaque joker vaut 25 points.

        """
        def _sum_final():
            total = 0
            for t in self.tuiles:
                if getattr(t, 'is_joker', False):
                    total += 25
                else:
                    total += getattr(t, 'valeur', 0)
            return total

        if context == 'final':
            return _sum_final()

        # contexte 'initial'  : essayer d'inférer jokers
        jokers = [i for i, t in enumerate(self.tuiles) if getattr(t, 'is_joker', False)]
        non_jokers = [t for t in self.tuiles if not getattr(t, 'is_joker', False)]
        valeurs = [t.valeur for t in non_jokers]
        couleurs = [t.couleur for t in non_jokers]
        n = len(self.tuiles)

        # Groupe : même valeur
        if len(valeurs) > 0 and len(set(valeurs)) == 1:
            v = valeurs[0]
            return v * n

        # Suite : même couleur, valeurs consécutives possibles
        if len(set(couleurs)) == 1 and len(valeurs) > 0:
            vals = sorted(valeurs)
            jokers_count = len(jokers)
            min_start = max(1, vals[0] - jokers_count)
            max_start = min(13 - n + 1, vals[-1])
            for start in range(min_start, max_start + 1):
                seq = list(range(start, start + n))
                if all(v in seq for v in vals):
                    return sum(seq)



class Pioche:
    """
    Représente la pioche du jeu (ensemble des tuiles restantes).
    Attributs :
        tuiles (list[Tuile]) : Tuiles restantes à piocher.
    Méthodes :
        tirer, __repr__
    """
    def __init__(self):
        self.tuiles = []
        couleurs = ["rouge", "bleu", "noir", "jaune"]
        self.tuiles = [Tuile(c, v) for c in couleurs for v in range(1, 14)] * 2
        self.tuiles.append(Tuile("joker", 0, True))
        self.tuiles.append(Tuile("joker", 0, True))
        random.shuffle(self.tuiles)

    def tirer(self):
        return self.tuiles.pop() if self.tuiles else None

    def __repr__(self):
        return f"Pioche(tuiles_restantes={len(self.tuiles)})"
  
  
    
class Rack:
    """
    Représente le rack d'un joueur (tuiles en main).
    Attributs :
        tuiles (list[Tuile]) : Tuiles du rack.
    Méthodes :
        ajouter_tuile, retirer, afficher, __repr__
    """
    def __init__(self):
        self.tuiles = []

    def ajouter_tuile(self, tuile:Tuile):
        self.tuiles.append(tuile)

    def retirer(self, tuile:Tuile):
        self.tuiles.remove(tuile)

    def afficher(self):
        if not self.tuiles:
            return "(vide)"
        parts = []
        for i, t in enumerate(self.tuiles):
            parts.append(f"{i}:{t}")
        return "  ".join(parts)

    def __repr__(self):
        return f"Rack(tuiles={self.tuiles})"
    
    
    
class Plateau:
    """
    Représente le plateau de jeu, contenant toutes les combinaisons posées.
    Attributs :
        mains (list[Combinaison]) : Liste des combinaisons posées sur le plateau.
    Méthodes :
        reutiliser_tuiles, ajouter_main, ajouter, retirer_tuile, ajouter_tuile,
        deplacer_tuile, deplacer_tuiles, fusionner_combinaisons, split_combinaison,
        est_valide_plateau, afficher, __repr__
    """
    def reutiliser_tuiles(self, indices):
        tuiles = []
        for idx_comb, idx_tuile in sorted(indices, reverse=True):
            tuiles.append(self.retirer_tuile(idx_comb, idx_tuile))
        return tuiles
    def __init__(self):
        self.mains = []

    def ajouter_main(self, main:Main):
        self.mains.append(main)

    def ajouter(self, combinaison:Main):
        if hasattr(combinaison, 'est_valide') and combinaison.est_valide():
            self.mains.append(combinaison)
            return True
        return False

    def retirer_tuile(self, index_combinaison:int, index_tuile:int):
        try:
            tuile = self.mains[index_combinaison].tuiles.pop(index_tuile)
            if not self.mains[index_combinaison].tuiles:
                self.mains.pop(index_combinaison)
            return tuile
        except Exception as e:
            print(f"Erreur lors du retrait de tuile : {e}")
            return None

    def ajouter_tuile(self, index_combinaison:int, tuile, pos_dest: int = None):
        try:
            if pos_dest is None:
                self.mains[index_combinaison].tuiles.append(tuile)
            else:
                self.mains[index_combinaison].tuiles.insert(pos_dest, tuile)
            return True
        except Exception as e:
            print(f"Erreur lors de l'ajout de tuile : {e}")
            return False


    def deplacer_tuile(self, index_src:int, index_tuile:int, index_dest:int, pos_dest:int=None):
        try:
            tuile = self.mains[index_src].tuiles.pop(index_tuile)
            if pos_dest is None:
                self.mains[index_dest].tuiles.append(tuile)
            else:
                self.mains[index_dest].tuiles.insert(pos_dest, tuile)
            if not self.mains[index_src].tuiles:
                self.mains.pop(index_src)
            return True
        except Exception as e:
            print(f"Erreur lors du déplacement de tuile : {e}")
            return False

    def deplacer_tuiles(self, sources:list, index_dest:int, pos_dest:int=None):

        try:
            # Normaliser et trier les sources
            sources_norm = sorted(sources, key=lambda x: (x[0], x[1]))
            # Récupérer les tuiles dans l'ordre des sources
            tuiles = [self.mains[i].tuiles[j] for (i, j) in sources_norm]
            # Retirer en ordre inverse pour préserver indices
            for i, j in sorted(sources_norm, reverse=True):
                self.retirer_tuile(i, j)

            # Si destination est en fin (nouvelle combinaison)
            if index_dest >= len(self.mains):
                # créer nouvelle combinaison
                comb = Combinaison(tuiles)
                self.mains.append(comb)
                return True

            # Insertion : si pos_dest None => append in order
            if pos_dest is None:
                for t in tuiles:
                    self.mains[index_dest].tuiles.append(t)
            else:
                # insérer en respectant l'ordre des tuiles
                for offset, t in enumerate(tuiles):
                    self.mains[index_dest].tuiles.insert(pos_dest + offset, t)

            return True
        except Exception as e:
            print(f"Erreur lors du déplacement multiple : {e}")
            return False

    def fusionner_combinaisons(self, index1:int, index2:int):
        try:
            self.mains[index1].tuiles.extend(self.mains[index2].tuiles)
            self.mains.pop(index2)
            return True
        except Exception as e:
            print(f"Erreur lors de la fusion : {e}")
            return False

    def split_combinaison(self, index:int, split_pos:int):
        try:
            comb = self.mains[index]
            tuiles1 = comb.tuiles[:split_pos]
            tuiles2 = comb.tuiles[split_pos:]
            self.mains[index] = Combinaison(tuiles1)
            self.mains.insert(index+1, Combinaison(tuiles2))
            return True
        except Exception as e:
            print(f"Erreur lors du split : {e}")
            return False

    def est_valide_plateau(self):
        return all(m.est_valide() for m in self.mains)

    def __repr__(self):
        return f"Plateau(mains={self.mains})"

    def afficher(self):
        if not self.mains:
            return "(aucune combinaison sur le plateau)"
        out = []
        for i, m in enumerate(self.mains):
            # Affiche chaque tuile de la combinaison avec son index
            tuiles_str = "  ".join(f"{j}:{t}" for j, t in enumerate(m.tuiles))
            out.append(f"{i}: {tuiles_str}")
        return "\n".join(out)
    
    
    
class Joueur:
    """
    Représente un joueur du Rummikub.
    Attributs :
        nom (str): Nom du joueur.
        main (Main): Main temporaire (utilisée pour manipuler avant pose).
        rack (Rack): Tuiles du joueur.
        points (int): Score du joueur.
        has_melded (bool): Indique si la première pose a été validée.
        has_drawn (bool): Indique si le joueur a déjà pioché ce tour.
        temp_meld_points (int): Points accumulés pour la première pose.
        _backup_plateau, _backup_rack: Sauvegardes pour rollback.
        _placed_this_turn (bool): Indique si une pose a été faite ce tour.
    Méthodes :
        piocher, tirer_tuile, jouer_main, manipuler_plateau, __repr__
    """
    def __init__(self, nom:str):
        self.nom = nom
        self.main = Main()
        self.rack = Rack()
        # Points accumulés et état de la première pose
        self.points = 0
        self.has_melded = False
        # État temporaire pendant un tour
        self.has_drawn = False
        self.temp_meld_points = 0
        self._backup_plateau = None
        self._backup_rack = None
        self._placed_this_turn = False

    def piocher(self, pioche:Pioche):
        tuile = pioche.tirer()
        if tuile:
            self.rack.ajouter_tuile(tuile)

    def tirer_tuile(self, pioche:Pioche):
      
        t = pioche.tirer()
        if t:
            self.rack.ajouter_tuile(t)
        return t

    def jouer_main(self, plateau:Plateau):
        if self.main.est_valide():
            plateau.ajouter_main(self.main)
            self.main = Main() 

    def manipuler_plateau(self, plateau:Plateau, action:str, **kwargs):
        
        if action == "deplacer":
            return plateau.deplacer_tuile(kwargs.get('index_src'), kwargs.get('index_tuile'), kwargs.get('index_dest'), kwargs.get('pos_dest'))
        elif action == "fusionner":
            return plateau.fusionner_combinaisons(kwargs.get('index1'), kwargs.get('index2'))
        elif action == "split":
            return plateau.split_combinaison(kwargs.get('index'), kwargs.get('split_pos'))
        elif action == "reutiliser":
            return plateau.reutiliser_tuiles(kwargs.get('indices'))
        return False

    def __repr__(self):
        return f"Joueur(nom={self.nom}, main={self.main}, rack={self.rack})" 


