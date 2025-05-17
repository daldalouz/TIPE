# PS : pour arreter le programme, il faut appuyer sur une touche sur l'interface de la console

import random
import threading
import time
import numpy as np
import msvcrt
import heapq
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import queue


class Noeud:
    def __init__(self, id, valeur, intervalle, voisins):
        self.id = id
        self.valeur = valeur
        self.intervalle = intervalle
        self.voisins = voisins  # voisins contient dans sa première variable l'instance noeud et dans sa seconde variable la distance entre le noeud et ce voisin

    def ajouter_voisin(self, voisin, distance):
        self.voisins.append((voisin, distance))

    def mettre_a_jour_noeud(self,graphe,etat_stable,update_queue):
        while not msvcrt.kbhit():
            distance_minimale = np.inf
            for voisin, distance in self.voisins:
                distance_minimale = min(distance_minimale, voisin.valeur + distance)
            if self.valeur != distance_minimale:
              update_queue.put(self)
            ancienneval = self.valeur
            self.valeur = distance_minimale
            print(f"Je m'appelle {self.id}, ma valeur est {self.valeur}, mon ancienne valeur est {ancienneval}, mon intervalle est {self.intervalle}")
            if est_etat_stable(graphe, etat_stable):
                print("\n✅ État stable atteint ! Tous les noeuds ont convergé.")
                break
            time.sleep(self.intervalle / 200)


class Graphe:
    def __init__(self, noeuds, taille):
        self.noeuds = noeuds  # Liste des nœuds dans le graphe
        self.k = taille  # K est le nombre total de nœuds


def mise_a_jour(noeud,graphe,etat_stable,update_queue):
    noeud.mettre_a_jour_noeud(graphe,etat_stable,update_queue)


def creer_graphe(taille,g):
    noeud0 = Noeud(0, 0, 0, [])
    g.add_node(0, data=noeud0)
    noeuds = [Noeud(i, random.randint(0, 9999), random.randrange(1000, 5000, 500), []) for i in range(1, taille)]
    noeuds.insert(0, noeud0)

    # Étape 1 : garantir la connexité en construisant un arbre couvrant aléatoire
    noeuds_connectes = [noeuds[0]]
    noeuds_non_connectes = noeuds[1:]

    while noeuds_non_connectes: 
        
        u = random.choice(noeuds_connectes)
        v = random.choice(noeuds_non_connectes)
        distance = random.randint(1, 20)
        u.ajouter_voisin(v, distance)
        v.ajouter_voisin(u, distance)
        noeuds_connectes.append(v)
        g.add_node(v.id, data=v)
        g.add_edge(u.id,v.id, weight=distance)
        noeuds_non_connectes.remove(v)

    # Étape 2 : ajouter des arêtes supplémentaires avec probabilité p
    for i in range(taille):
        for j in range(i + 1, taille):
            u = noeuds[i]
            v = noeuds[j]
            if not any(voisin.id == v.id for voisin, _ in u.voisins): 
                if random.random() < 0.2:
                    distance = random.randint(1, 20)
                    u.ajouter_voisin(v, distance)
                    g.add_edge(u.id,v.id,weight=distance)
                    v.ajouter_voisin(u, distance)

    return Graphe(noeuds, taille)


def afficher_noeuds(graphe):
    for noeud in graphe.noeuds:
        print(f"Je m'appelle {noeud.id}, ma valeur est {noeud.valeur}, mon intervalle est {noeud.intervalle}")
        

def noeud_plus_grd_intervalle(graphe):
    return max(graphe.noeuds, key=lambda n: n.intervalle)


def mise_a_jour_avec_rondes(noeud,graphe,etat_stable,update_queue):
    compteur_rondes = 0 
    while not msvcrt.kbhit(): # je mets cette condiition au cas ou j'ai un etat qui ne converge pas (provient du fait que le noeud 0 n'a pas une valeur 0... je trouve pas le soucis qui déclenche cela)
        distance_minimale = np.inf
        for voisin, distance in noeud.voisins:
            distance_minimale = min(distance_minimale, voisin.valeur + distance)
        if noeud.valeur != distance_minimale:
              update_queue.put(noeud)
        ancienneval = noeud.valeur
        noeud.valeur = distance_minimale
        compteur_rondes += 1
        print(f"[Ronde {compteur_rondes}] Je m'appelle {noeud.id}, ma valeur est {noeud.valeur}, mon ancienne valeur est {ancienneval} mon intervalle est {noeud.intervalle}")
        if est_etat_stable(graphe, etat_stable):
                print("\n✅ État stable atteint ! Tous les noeuds ont convergé.")
                break
        time.sleep(noeud.intervalle / 200)

def est_etat_stable(graphe, etat_stable):
    for noeud in graphe.noeuds:
        if noeud.valeur != etat_stable[noeud.id]:
            return False
    return True

    


def dijkstra_classique(graphe, source_id=0):
    distances = {noeud.id: np.inf for noeud in graphe.noeuds}
    distances[source_id] = 0
    visited = set() 
    queue = [(0, source_id)]

    while queue:
        dist_actuelle, noeud_id = heapq.heappop(queue)

        if noeud_id in visited:
            continue
        visited.add(noeud_id)

        noeud = graphe.noeuds[noeud_id]

        for voisin, distance in noeud.voisins:
            if voisin.id not in visited:
                nouvelle_dist = dist_actuelle + distance
                if nouvelle_dist < distances[voisin.id]:
                    distances[voisin.id] = nouvelle_dist
                    heapq.heappush(queue, (nouvelle_dist, voisin.id))

    return distances


def main():
    taille = 10
    G = nx.Graph()
    graphe = creer_graphe(taille,G)

    update_queue = queue.Queue()
    emptyLab = { graphe.noeuds[i].id:"" for i in range(1, graphe.k)}
    def update(frame):
        while not update_queue.empty():
            data = update_queue.get()
            """
            action, data = update_queue.get()
            if action == "add_node":
                G.add_node(data)
            elif action == "add_edge":
                G.add_edge(*data)
           """
            plt.cla()  # clear current axes
            pos = nx.shell_layout(G)
            colors = {0: 'black', 1: 'red'}
            labels = {node: f"{node}\n{attrs['data'].valeur}" for node,attrs in G.nodes(data=True)}
            edge_labels = nx.get_edge_attributes(G, 'weight')
            nx.draw_shell(G, with_labels=False, node_color='lightblue', edge_color='gray', font_weight='bold',node_size=2000)
            for node, label in labels.items():
                x, y = pos[node]
                if data.id==node:
                  plt.text(x, y, label, ha='center', va='center', fontsize=10, color=colors[1])
                else:
                  plt.text(x, y, label, ha='center', va='center', fontsize=10, color=colors[0])
            
            #nx.draw_networkx_labels(G, pos, emptyLab)
            #nx.draw_networkx_labels(G, pos, labels)
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)


    

# Matplotlib real-time animation


    
    
    afficher_noeuds(graphe)
    noeud_rondes = noeud_plus_grd_intervalle(graphe)
    etat_stable = dijkstra_classique(graphe)
    

    # Créer et démarrer les threads pour mettre à jour les noeuds, sauf le noeud 0
    threads = []
    thread_rondes = threading.Thread(target=mise_a_jour_avec_rondes, args=(noeud_rondes,graphe,etat_stable,update_queue))
    threads.append(thread_rondes)
    for noeud in graphe.noeuds[1:]:
        if noeud != noeud_rondes:
            thread = threading.Thread(target=mise_a_jour, args=(noeud,graphe,etat_stable,update_queue))
            threads.append(thread)

    # Démarrage aléatoire des threads
    liste_temp = threads.copy()
    while liste_temp:
        i = random.randint(0, len(liste_temp) - 1)
        liste_temp[i].start()
        liste_temp.pop(i)
        print("Thread démarré")

    
    
    fig = plt.figure()
    ani = animation.FuncAnimation(fig, update,emptyLab, interval=100)  # update every 100 ms
    plt.show()
    '''
    fig, ax = plt.subplots()
    pos = nx.shell_layout(G)
    nx.draw_shell(G, with_labels=True, node_color='lightblue', edge_color='gray', font_weight='bold',node_size=1000)
    labels = {node: f"\n{attrs['data'].valeur}" for node,attrs in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels, ax=ax)
    plt.show()
    '''
    # Attendre que tous les threads terminent
    '''
    for thread in threads:
        thread.join()
   '''
    # Afficher l'état final
    afficher_noeuds(graphe)
    dijkstra_resultat = dijkstra_classique(graphe, source_id=0)
    print("\n--- Résultat Dijkstra classique ---")
    for id_noeud, distance in sorted(dijkstra_resultat.items()):
        print(f"Noeud {id_noeud} -> distance depuis 0 : {distance}")

    # Mise à jour du noeud 0
    #graphe.noeuds[0].mettre_a_jour_noeud(graphe,etat_stable)


    



if __name__ == "__main__":
    main()