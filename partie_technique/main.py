from recup_notes import (
    lire_audio,
    decouper_signal,
    extraire_frequences,
    filtrer_amplitudes_globales,
    convertir_frequences_en_notes_avec_amplitude,
    enlever_doublons,
    coller_notes,
    temps_forts
    )

from reconstitution_partition import (
    transformer_en_bemols,
    TrouverAlterations,
    determiner_tonalite,
    decouper_en_mesures,
    regrouper_accord,
    transposer_partition,
    generer_lilypond,
    ecrire_lilypond,
    compiler_lilypond,
    )

from parametres import (
    nom_fichier_audio,
    temps_par_mesure,
    cle,
    ref_rythme
)


def main_recup_notes(chemin_audio, tonalite):
    
    freq_ech, donnees = lire_audio(chemin_audio)
    blocs = decouper_signal(donnees, freq_ech)

    print("Analyse des fréquences...")
    freqs_detectees = [extraire_frequences(bloc, freq_ech) for bloc in blocs]
    
    # matrice de couples (frequence, amplitude) avec l'amplitude qui vaut parfois 0 grace au filtre
    freqs_filtrees = filtrer_amplitudes_globales(freqs_detectees)
    
    notes_detectees = convertir_frequences_en_notes_avec_amplitude(freqs_filtrees)
    
    notes_sans_doublons = enlever_doublons(notes_detectees)
    
    info_notes_brutes = coller_notes(notes_sans_doublons)
    
    
    tf = temps_forts(info_notes_brutes) 
    print(f"\nTemps forts : \n{tf}")
    
    return main_reconstitution_partition(info_notes_brutes, tf, tonalite) #renvoie le chmin pdf


def main_reconstitution_partition(info_notes_brutes, temps_forts, tonalite):
    
    tonalite_input = tonalite.strip().lower()
    
    alterations = TrouverAlterations(info_notes_brutes)
    
    # print(f"\nAlteration : {alterations}")
    
    if alterations and alterations[0] == "ais": # cas ou on a des bemols
        notes_armure = transformer_en_bemols(info_notes_brutes)
        temps_forts = transformer_en_bemols(temps_forts)
    else:
        notes_armure = info_notes_brutes
        
        
    #---------Transposition
    tonalite_origine = determiner_tonalite(alterations)
    print(f"\nTonalité : {tonalite_origine}")
    
    notes_trans = transposer_partition(notes_armure, tonalite_origine or "c", tonalite_input)
    print(" Notes transposées (extraits) :", notes_trans[:12])
    
    alterations_t = TrouverAlterations(notes_trans)
    print(" Altérations détectées :", alterations_t)
    
    tonalite_pour_lilypond = tonalite_input
    print(" Tonalité transposée :", tonalite_pour_lilypond)
    
    notes_mesures, duree_mesure = decouper_en_mesures(notes_trans, temps_forts)  # La premiere mesure n'a pas forcement de temps fort
    notes_mesures_accords = regrouper_accord(notes_mesures)  # mesures contenant des accords (accord = (liste des notes, duree))
    
    #print(f"Mesures d'accords : \n{notes_mesures_accords}")
    
    # Finalement on prend pas en compte la premiere mesure, on commence par le premier temps fort
    code = generer_lilypond(notes_mesures_accords, duree_mesure, cle, tonalite_pour_lilypond, temps_par_mesure, ref_rythme)
    
    ecrire_lilypond(code) 

    return compiler_lilypond()


if __name__ == "__main__":
    chemin_pdf = main_recup_notes(nom_fichier_audio, "d") #audio, tonalite cible
    print(chemin_pdf)
