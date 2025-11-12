import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, QGridLayout, QFrame)
from PyQt5.QtCore import Qt
from classes import Joueur
from game import Jeu


class RummikubInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rummikub - Interface graphique ")
        # Demande le nombre de joueurs au démarrage
        from PyQt5.QtWidgets import QInputDialog
        n, ok = QInputDialog.getInt(self, "Nombre de joueurs", "Combien de joueurs ?", value=1, min=1, max=8)
        if not ok:
            n = 1
        self.jeu = Jeu(n)
        self.tour = 0
        self.joueur = self.jeu.joueurs[self.tour]
        self.selected_plateau = set()  
        self.selected_rack = set()     
        self.init_ui()
        self.refresh()
        

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.plateau_grid = QVBoxLayout()
        self.rack_layout = QHBoxLayout()
        self.btn_poser = QPushButton("Poser la combinaison sélectionnée")
        self.btn_tirer = QPushButton("Tirer une tuile")
        self.btn_sauter = QPushButton("Passer son tour")
        self.btn_stop = QPushButton("Arrêter la partie")
        self.btn_refresh = QPushButton("Rafraîchir")
        self.msg = QLabel()
        self.msg.setStyleSheet("color: red;")

        self.layout.addWidget(QLabel("Plateau :"))
        self.layout.addLayout(self.plateau_grid)
        self.layout.addWidget(QLabel("Ton rack :"))
        self.layout.addLayout(self.rack_layout)

        btns_hbox = QHBoxLayout()
        btns_hbox.addWidget(self.btn_poser)
        btns_hbox.addWidget(self.btn_tirer)
        btns_hbox.addWidget(self.btn_sauter)
        btns_hbox.addWidget(self.btn_stop)
        # bouton pour sélectionner automatiquement une colonne entière
        self.btn_poser_colonne = QPushButton("Poser une colonne")
        btns_hbox.addWidget(self.btn_poser_colonne)
        self.layout.addLayout(btns_hbox)

        self.layout.addWidget(self.btn_refresh)
        self.layout.addWidget(self.msg)
        self.setLayout(self.layout)

        self.btn_poser.clicked.connect(self.poser_combinaison)
        self.btn_tirer.clicked.connect(self.tirer_tuile)
        self.btn_sauter.clicked.connect(self.passer_tour)
        self.btn_stop.clicked.connect(self.arreter_jeu)
        self.btn_poser_colonne.clicked.connect(self.poser_colonne)
        self.btn_refresh.clicked.connect(self.refresh)
        
    def tirer_tuile(self):
        t = self.joueur.tirer_tuile(self.jeu.pioche)
        if t:
            self.msg.setStyleSheet("color: green;")
            self.msg.setText(f"Tu as tiré : {t}")
        else:
            self.msg.setStyleSheet("color: red;")
            self.msg.setText("La pioche est vide.")
        self.refresh()

    def passer_tour(self):
        self.msg.setStyleSheet("color: blue;")
        self.msg.setText("Tour passé.")
        self.refresh()

    def arreter_jeu(self):
        reply = QMessageBox.question(self, 'Arrêter la partie', 'Es-tu sûr de vouloir arrêter la partie ?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            QApplication.quit()  # Quitte proprement toute l'application

    def refresh(self):
        # Met à jour le joueur courant
        self.joueur = self.jeu.joueurs[self.tour % len(self.jeu.joueurs)]
        # Affiche le joueur courant en haut
        if hasattr(self, 'label_current'):
            self.label_current.setText(f"Joueur courant : {self.joueur.nom}")
        else:
            self.label_current = QLabel(f"Joueur courant : {self.joueur.nom}")
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
            hbox = QHBoxLayout()
            for j, tuile in enumerate(comb.tuiles):
                btn = QPushButton(str(tuile))
                btn.setCheckable(True)
                btn.setStyleSheet("margin:2px;")
                btn.setChecked((i, j) in self.selected_plateau)
                btn.clicked.connect(self.make_plateau_toggle(i, j, btn))
                btn.setToolTip(f"Plateau {i}:{j}")
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
            btn = QPushButton(str(tuile))
            btn.setCheckable(True)
            btn.setChecked(idx in self.selected_rack)
            btn.clicked.connect(self.make_rack_toggle(idx, btn))
            btn.setToolTip(f"Rack {idx}")
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
                for i, j in sorted(pos_list, reverse=True):
                    self.jeu.plateau.retirer_tuile(i, j)
                for idx in sorted(rack_list, reverse=True):
                    # retirer de la main du joueur courant
                    self.joueur.rack.retirer(self.joueur.rack.tuiles[idx])
                self.jeu.plateau.ajouter(comb)
                self.msg.setStyleSheet("color: green;")
                self.msg.setText("Combinaison posée !")
                self.selected_plateau.clear()
                self.selected_rack.clear()
                self.refresh()
            else:
                self.msg.setStyleSheet("color: red;")
                self.msg.setText("Combinaison invalide.")
        except Exception as e:
            self.msg.setStyleSheet("color: red;")
            self.msg.setText(f"Erreur : {e}")

    def poser_colonne(self):
        from PyQt5.QtWidgets import QInputDialog
        j, ok = QInputDialog.getInt(self, "Poser colonne", "Indice de colonne (j):", min=0)
        if not ok:
            return
        # sélection automatique : prendre la j-ième tuile de chaque combinaison s'il y en a
        self.selected_plateau.clear()
        for i, comb in enumerate(self.jeu.plateau.mains):
            if j >= 0 and j < len(comb.tuiles):
                self.selected_plateau.add((i, j))
        self.refresh()

    def passer_tour(self):
        # Incrémente l'index de joueur courant et rafraîchit l'interface
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
