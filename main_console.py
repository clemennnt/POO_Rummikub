from game import Jeu
if __name__ == "__main__":
    n = int(input("Nombre de joueurs ? "))
    jeu = Jeu(n_joueurs=n)
    jeu.jouer()