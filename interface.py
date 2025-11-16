import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, QGridLayout, QFrame)
from PyQt5.QtCore import Qt
from classes import Joueur
from game import Jeu
import copy

class RummikubInterface(QWidget):
    """
    Interface graphique principale du jeu Rummikub (PyQt5).

    Attributs :
        jeu (Jeu): Instance du jeu.
        joueur (Joueur): Joueur courant.
        tour (int): Index du tour.
        selected_plateau (set): Sélection de tuiles sur le plateau.
        selected_rack (set): Sélection de tuiles dans le rack.

    Méthodes principales :
        init_ui() : Construit l'UI.
        refresh() : Met à jour l'affichage.
        poser_combinaison() : Pose une combinaison sur le plateau.
        deplacer_selection() : Déplace des tuiles sélectionnées.
        retirer_selection() : Retire des tuiles du plateau vers le rack.
        passer_tour() : Passe au joueur suivant.
    """
    def __init__(self):
        """
        Initialise l'interface graphique du jeu Rummikub.
        Demande le nombre de joueurs et leurs noms, puis prépare l'UI.
        """
        super().__init__()
        self.setWindowTitle("Rummikub - Interface graphique ")
        # Demande le nombre de joueurs au démarrage puis leurs noms
        from PyQt5.QtWidgets import QInputDialog
        n, ok = QInputDialog.getInt(self, "Nombre de joueurs", "Combien de joueurs ?", value=1, min=1, max=8)
        if not ok:
            n = 1
        # Demander un nom pour chaque joueur (valeur par défaut : Joueur X)
        noms = []
        for i in range(n):
            nom, ok_nom = QInputDialog.getText(self, "Nom du joueur", f"Nom du joueur {i+1}:", text=f"Joueur {i+1}")
            if not ok_nom or not nom.strip():
                nom = f"Joueur {i+1}"
            noms.append(nom.strip())
        self.jeu = Jeu(n)
        # Appliquer les noms choisis aux joueurs créés dans Jeu
        for i, nom in enumerate(noms):
            if i < len(self.jeu.joueurs):
                self.jeu.joueurs[i].nom = nom
        self.tour = 0
        self.joueur = self.jeu.joueurs[self.tour]
        self.selected_plateau = set()  
        self.selected_rack = set()     
        self.init_ui()
        self.refresh()
        

    def init_ui(self):
        """
        Construit tous les widgets et layouts principaux de l'interface.
        """
        self.layout = QVBoxLayout()
        self.plateau_grid = QVBoxLayout()
        self.rack_layout = QHBoxLayout()

        # Buttons
        self.btn_poser = QPushButton("Poser la combinaison sélectionnée")
        self.btn_tirer = QPushButton("Tirer une tuile")
        self.btn_sauter = QPushButton("Passer son tour")
        self.btn_stop = QPushButton("Arrêter la partie")
        self.btn_refresh = QPushButton("Rafraîchir")
        self.msg = QLabel()
        self.msg.setStyleSheet("color: red;")

        # Layouts
        self.layout.addWidget(QLabel("Plateau :"))
        self.layout.addLayout(self.plateau_grid)
        self.layout.addWidget(QLabel("Ton rack :"))
        self.layout.addLayout(self.rack_layout)

        btns_hbox = QHBoxLayout()
        btns_hbox.addWidget(self.btn_poser)
        btns_hbox.addWidget(self.btn_tirer)
        btns_hbox.addWidget(self.btn_sauter)
        btns_hbox.addWidget(self.btn_stop)


        # bouton pour déplacer la sélection sur une autre combinaison
        self.btn_deplacer_selection = QPushButton("Déplacer sélection")
        btns_hbox.addWidget(self.btn_deplacer_selection)

        # bouton pour retirer la sélection du plateau vers le rack
        self.btn_retirer_selection = QPushButton("Retirer sélection")
        btns_hbox.addWidget(self.btn_retirer_selection)

        self.layout.addLayout(btns_hbox)

        self.layout.addWidget(self.btn_refresh)
        self.layout.addWidget(self.msg)
        self.setLayout(self.layout)

        # Connections
        self.btn_poser.clicked.connect(self.poser_combinaison)
        self.btn_tirer.clicked.connect(self.tirer_tuile)
        self.btn_sauter.clicked.connect(self.passer_tour)
        self.btn_stop.clicked.connect(self.arreter_jeu)
        self.btn_deplacer_selection.clicked.connect(self.deplacer_selection)
        self.btn_retirer_selection.clicked.connect(self.retirer_selection)
        self.btn_refresh.clicked.connect(self.refresh)
        
    def tirer_tuile(self):
        if getattr(self.joueur, 'has_drawn', False):
            self.msg.setStyleSheet("color: red;")
            self.msg.setText("Tu as déjà tiré ce tour.")
            return
        t = self.joueur.tirer_tuile(self.jeu.pioche)
        if t:
            self.joueur.has_drawn = True
            self.msg.setStyleSheet("color: green;")
            self.msg.setText(f"Tu as tiré : {t} — le tour se termine.")
        else:
            self.msg.setStyleSheet("color: red;")
            self.msg.setText("La pioche est vide.")
        self.refresh()
        # Après tirage, le tour est automatiquement passé
        self.passer_tour()

    def passer_tour(self):
        self.msg.setStyleSheet("color: blue;")
        self.msg.setText("Tour passé.")
        self.refresh()

    def arreter_jeu(self):
        reply = QMessageBox.question(self, 'Arrêter la partie', 'Es-tu sûr de vouloir arrêter la partie ?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            QApplication.quit() 

    def refresh(self):
        """
        Met à jour l'affichage du plateau, du rack et du joueur courant.
        """
        # Met à jour le joueur courant
        self.joueur = self.jeu.joueurs[self.tour % len(self.jeu.joueurs)]
        # Affiche le joueur courant en haut
        if hasattr(self, 'label_current'):
            self.label_current.setText(f"Joueur courant : {self.joueur.nom} (pts: {getattr(self.joueur, 'points', 0)})")
        else:
            self.label_current = QLabel(f"Joueur courant : {self.joueur.nom} (pts: {getattr(self.joueur, 'points', 0)})")
            self.layout.insertWidget(0, self.label_current)
        # reset msg color par défaut
        self.msg.setStyleSheet("color: red;")
        # Plateau
        for i in reversed(range(self.plateau_grid.count())):
            item = self.plateau_grid.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                self.plateau_grid.removeItem(item)
     
        for i, comb in enumerate(self.jeu.plateau.mains):
            # Affichage par défaut (ligne)
            hbox = QHBoxLayout()
            for j, tuile in enumerate(comb.tuiles):
                # Affichage chiffre ou J, couleur Qt
                if getattr(tuile, 'is_joker', False):
                    txt = 'J'
                    color = 'magenta'
                else:
                    txt = str(tuile.valeur)
                    color = {
                        'rouge': 'red',
                        'bleu': 'blue',
                        'noir': 'black',
                        'jaune': 'orange'
                    }.get(getattr(tuile, 'couleur', ''), 'grey')
                btn = QPushButton(txt)
                btn.setCheckable(True)
                btn.setChecked((i, j) in self.selected_plateau)
                btn.clicked.connect(self.make_plateau_toggle(i, j, btn))
                btn.setToolTip(f"Plateau {i}:{j}")
                btn.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 18px; margin:2px;")
                hbox.addWidget(btn)
            label = QLabel(f"(Combinaison {i})")
            hbox.addWidget(label)
            self.plateau_grid.addLayout(hbox)


        # Rack
        for i in reversed(range(self.rack_layout.count())):
            item = self.rack_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
       
        for idx, tuile in enumerate(self.joueur.rack.tuiles):
            if getattr(tuile, 'is_joker', False):
                txt = 'J'
                color = 'magenta'
            else:
                txt = str(tuile.valeur)
                color = {
                    'rouge': 'red',
                    'bleu': 'blue',
                    'noir': 'black',
                    'jaune': 'orange'
                }.get(getattr(tuile, 'couleur', ''), 'grey')
            btn = QPushButton(txt)
            btn.setCheckable(True)
            btn.setChecked(idx in self.selected_rack)
            btn.clicked.connect(self.make_rack_toggle(idx, btn))
            btn.setToolTip(f"Rack {idx}")
            btn.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 18px; margin:2px;")
            self.rack_layout.addWidget(btn)

        self.msg.clear()
    def make_plateau_toggle(self, i, j, btn):
        def toggle():
            if (i, j) in self.selected_plateau:
                self.selected_plateau.remove((i, j))
                btn.setChecked(False)
            else:
                self.selected_plateau.add((i, j))
                btn.setChecked(True)
        return toggle

    def make_rack_toggle(self, idx, btn):
        def toggle():
            if idx in self.selected_rack:
                self.selected_rack.remove(idx)
                btn.setChecked(False)
            else:
                self.selected_rack.add(idx)
                btn.setChecked(True)
        return toggle

    def poser_combinaison(self):
        """
        Pose une nouvelle combinaison sur le plateau à partir de la sélection.
        Gère la validation, le calcul des points et la fin de partie.
        """
        pos_list = list(self.selected_plateau)
        rack_list = list(self.selected_rack)
        try:
            tuiles_plateau = [self.jeu.plateau.mains[i].tuiles[j] for (i, j) in pos_list]
            tuiles_rack = [self.joueur.rack.tuiles[idx] for idx in rack_list]
            tuiles = tuiles_plateau + tuiles_rack
            if not tuiles:
                self.msg.setText("Aucune tuile sélectionnée.")
                return
            from classes import Combinaison
            comb = Combinaison(tuiles)
            if comb.est_valide():
                # Calculer les points apportés par les tuiles prises dans le rack
                from classes import Combinaison
                comb_rack = Combinaison(tuiles_rack) if tuiles_rack else None
                points_rack = comb_rack.points(context='initial') if comb_rack else 0

                # Si c'est la première modification liée au rack ce tour, on sauvegarde l'état
                if comb_rack and not getattr(self.joueur, 'has_melded', False) and not getattr(self.joueur, 'temp_meld_points', 0):
                    self.joueur._backup_plateau = copy.deepcopy(self.jeu.plateau.mains)
                    self.joueur._backup_rack = list(self.joueur.rack.tuiles)
                    self.joueur._placed_this_turn = True

                # Retirer d'abord les tuiles du plateau
                for i, j in sorted(pos_list, reverse=True):
                    self.jeu.plateau.retirer_tuile(i, j)
                # Retirer les tuiles du rack
                for idx in sorted(rack_list, reverse=True):
                    self.joueur.rack.retirer(self.joueur.rack.tuiles[idx])
                # Ajouter la combinaison sur le plateau
                self.jeu.plateau.ajouter(comb)

                # Accumuler les points temp pour la première pose, ou ajouter directement si already melded
                if points_rack > 0:
                    if getattr(self.joueur, 'has_melded', False):
                        self.joueur.points = getattr(self.joueur, 'points', 0) + points_rack
                    else:
                        self.joueur.temp_meld_points = getattr(self.joueur, 'temp_meld_points', 0) + points_rack

                self.msg.setStyleSheet("color: green;")
                self.msg.setText("Combinaison posée !")
                self.selected_plateau.clear()
                self.selected_rack.clear()
                self.refresh()
                # Vérifier fin de partie et afficher le classement si terminé
                self.jeu.verifier_fin()
                if getattr(self.jeu, 'partie_terminee', False):
                    # Préparer et afficher un message final
                    lines = [f"{p.nom} : {getattr(p, 'points', 0)} pts" for p in self.jeu.joueurs]
                    text = "\n".join(lines)
                    QMessageBox.information(self, "Fin de la partie - Scores", f"Partie terminée.\n\n{ text }")
                    # Désactiver les boutons pour éviter d'autres actions
                    for w in [self.btn_poser, self.btn_tirer, self.btn_sauter]:
                        w.setEnabled(False)
            else:
                self.msg.setStyleSheet("color: red;")
                self.msg.setText("Combinaison invalide.")
        except Exception as e:
            self.msg.setStyleSheet("color: red;")
            self.msg.setText(f"Erreur : {e}")


    def deplacer_selection(self):
        """
        Déplace les tuiles sélectionnées du plateau vers une autre combinaison ou en crée une nouvelle.
        """
        from PyQt5.QtWidgets import QInputDialog
        if not self.selected_plateau:
            self.msg.setStyleSheet("color: red;")
            self.msg.setText("Aucune tuile du plateau sélectionnée.")
            return
        # demander index de combinaison destination
        max_dest = max(len(self.jeu.plateau.mains), 0)
        dest, ok = QInputDialog.getInt(self, "Destination", "Index combinaison destination (0.. N, =N pour nouvelle) :", value=0, min=0, max=max_dest)
        if not ok:
            return
        pos_str, ok2 = QInputDialog.getText(self, "Position", "Position d'insertion (vide pour fin) :", text="")
        if not ok2:
            return
        pos = int(pos_str) if pos_str.strip() != "" else None

        # Préparer sources
        sources = sorted(list(self.selected_plateau), key=lambda x: (x[0], x[1]))

    # Backup
        backup = copy.deepcopy(self.jeu.plateau.mains)
        try:
            ok_move = self.jeu.plateau.deplacer_tuiles(sources, dest, pos)
            if not ok_move:
                raise Exception("Erreur interne lors du déplacement")
            if not self.jeu.plateau.est_valide_plateau():
                # rollback
                self.jeu.plateau.mains = backup
                self.msg.setStyleSheet("color: red;")
                self.msg.setText("Déplacement annulé : le plateau serait invalide.")
            else:
                self.msg.setStyleSheet("color: green;")
                self.msg.setText("Déplacement effectué.")
                # clear selection
                self.selected_plateau.clear()
                self.refresh()
        except Exception as e:
            self.jeu.plateau.mains = backup
            self.msg.setStyleSheet("color: red;")
            self.msg.setText(f"Erreur lors du déplacement : {e}")

    def retirer_selection(self):
        """
        Retire les tuiles sélectionnées du plateau et les remet dans le rack du joueur.
        """
        from copy import deepcopy
        if not self.selected_plateau:
            self.msg.setStyleSheet("color: red;")
            self.msg.setText("Aucune tuile du plateau sélectionnée.")
            return
        sources = sorted(list(self.selected_plateau), key=lambda x: (x[0], x[1]))
        backup_plateau = deepcopy(self.jeu.plateau.mains)
        backup_rack = list(self.joueur.rack.tuiles)
        try:
            removed = []
            # Retirer en ordre inverse
            for i, j in sorted(sources, reverse=True):
                t = self.jeu.plateau.retirer_tuile(i, j)
                if t is None:
                    raise Exception(f"Impossible de retirer la tuile {i}:{j}")
                removed.append(t)
            # Ajouter les tuiles retirées au rack du joueur (dans l'ordre original)
            for t in reversed(removed):
                self.joueur.rack.ajouter_tuile(t)

            if not self.jeu.plateau.est_valide_plateau():
                # rollback
                self.jeu.plateau.mains = backup_plateau
                self.joueur.rack.tuiles = backup_rack
                self.msg.setStyleSheet("color: red;")
                self.msg.setText("Retrait annulé : le plateau serait invalide.")
            else:
                self.msg.setStyleSheet("color: green;")
                self.msg.setText("Tuiles retirées vers ton rack.")
                self.selected_plateau.clear()
                self.refresh()
        except Exception as e:
            self.jeu.plateau.mains = backup_plateau
            self.joueur.rack.tuiles = backup_rack
            self.msg.setStyleSheet("color: red;")
            self.msg.setText(f"Erreur lors du retrait : {e}")

    def passer_tour(self):
        """
        Termine le tour du joueur courant, valide la première pose si besoin, passe au joueur suivant.
        """
        # Gérer la validation de la première pose (accumulation multi-combinaisons)
        current = self.jeu.joueurs[self.tour % len(self.jeu.joueurs)]
        # Si le joueur n'a pas encore validé son initial meld
        if not getattr(current, 'has_melded', False):
            temp = getattr(current, 'temp_meld_points', 0)
            if temp > 0 and temp < 30:
                # rollback des changements effectués ce tour
                if getattr(current, '_backup_plateau', None) is not None:
                    self.jeu.plateau.mains = current._backup_plateau
                if getattr(current, '_backup_rack', None) is not None:
                    current.rack.tuiles = current._backup_rack
                current.temp_meld_points = 0
                current._backup_plateau = None
                current._backup_rack = None
                current._placed_this_turn = False
                self.msg.setStyleSheet("color: red;")
                self.msg.setText("Première pose non atteinte (moins de 30 pts) : mouvements annulés.")
            elif temp >= 30:
                # on valide la première pose : on ajoute les points accumulés
                current.points = getattr(current, 'points', 0) + temp
                current.has_melded = True
                current.temp_meld_points = 0
                current._backup_plateau = None
                current._backup_rack = None
                current._placed_this_turn = False

        # Reset draw flag for the player (next time they will be able to draw on their new turn)
        current.has_drawn = False

        # Passe au joueur suivant
        self.tour = (self.tour + 1) % len(self.jeu.joueurs)
        self.msg.setStyleSheet("color: blue;")
        self.msg.setText(f"Tour passé. Joueur suivant : {self.jeu.joueurs[self.tour].nom}")
        # Clear selections when switching player
        self.selected_plateau.clear()
        self.selected_rack.clear()
        self.refresh()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RummikubInterface()
    window.show()
    sys.exit(app.exec_())

  



                        


                                



