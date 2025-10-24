import random

class Tuile:
    def __init__(self, couleur:str, valeur:int, is_joker:bool=False):
        self.couleur = couleur
        self.valeur = valeur
        self.is_joker = is_joker

    def __repr__(self):
        if self.is_joker:
            return "Tuile(Joker)"
        return f"{self.couleur[:1].upper()}{self.valeur}"

class Main:
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
    def __init__(self, tuiles):
        super().__init__()
        # accepter une liste de tuiles
        self.tuiles = list(tuiles)

    def contient_joker(self):
        return any(t.is_joker for t in self.tuiles)

    def remplacer_joker(self, tuile_replacement:Tuile):
        for i, t in enumerate(self.tuiles):
            if t.is_joker:
                self.tuiles[i] = tuile_replacement
                return True
        return False



class Pioche:
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
    def __init__(self):
        self.tuiles = []

    def ajouter_tuile(self, tuile:Tuile):
        self.tuiles.append(tuile)

    def retirer_tuile(self, tuile:Tuile):
        self.tuiles.remove(tuile)

    # alias pour compatibilité avec d'autres noms utilisés
    def retirer(self, tuile:Tuile):
        return self.retirer_tuile(tuile)

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
        """Ajoute une combinaison si elle est valide. Retourne True/False."""
        if hasattr(combinaison, 'est_valide') and combinaison.est_valide():
            self.mains.append(combinaison)
            return True
        return False

    def retirer_tuile(self, index_combinaison:int, index_tuile:int):

        try:
            tuile = self.mains[index_combinaison].tuiles.pop(index_tuile)
            # Si la combinaison devient vide, on la retire du plateau
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

    def toutes_tuiles(self):
        
        result = []
        for i, comb in enumerate(self.mains):
            for j, t in enumerate(comb.tuiles):
                result.append((i, j, t))
        return result

    def deplacer_tuile(self, index_src:int, index_tuile:int, index_dest:int, pos_dest:int=None):
        
        try:
            tuile = self.mains[index_src].tuiles.pop(index_tuile)
            if pos_dest is None:
                self.mains[index_dest].tuiles.append(tuile)
            else:
                self.mains[index_dest].tuiles.insert(pos_dest, tuile)
            # Si la combinaison source devient vide, on la retire
            if not self.mains[index_src].tuiles:
                self.mains.pop(index_src)
            return True
        except Exception as e:
            print(f"Erreur lors du déplacement de tuile : {e}")
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
            out.append(f"{i}: {m.tuiles}")
        return "\n".join(out)
    
    
    
class Joueur:
    def __init__(self, nom:str):
        self.nom = nom
        # main représente une combinaison en cours, rack est la main du joueur
        self.main = Main()
        self.rack = Rack()

    def piocher(self, pioche:Pioche):
        tuile = pioche.tirer()
        if tuile:
            # piocher met une tuile dans le rack du joueur
            self.rack.ajouter_tuile(tuile)

    def tirer_tuile(self, pioche:Pioche):
      
        t = pioche.tirer()
        if t:
            self.rack.ajouter_tuile(t)
        return t

    def jouer_main(self, plateau:Plateau):
        if self.main.est_valide():
            plateau.ajouter_main(self.main)
            self.main = Main()  # Réinitialiser la main après le jeu

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



