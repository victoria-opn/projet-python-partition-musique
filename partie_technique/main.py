from recup_notes import (
    lire_audio,
    decouper_signal,
    extraire_frequences,
    filtrer_amplitudes_globales,
    trouver_note,
    convertir_frequences_en_notes_avec_amplitude,
    enlever_doublons,
    enlever_amplitude,
    coller_notes,
    convertir_en_noms_reels,
    temps_forts
    )

from reconstitution_partition import (
    transformer_en_bemols,
    nombre_notes,
    TrouverAlterations,
    determiner_tonalite,
    decouper_en_mesures,
    regrouper_notes_accords,
    regrouper_accord,
    convertir_duree_en_valeur_rythmique,
    lilypond_accord,
    octave_to_lilypond,
    transposer_partition,
    generer_lilypond,
    ecrire_lilypond,
    compiler_lilypond,
    transformer_en_bemols
    )

from parametres import (
    duree_decoupe,
    nombre_max_notes,
    decalage_octave_lilypond,
    seuil_amplitude_relatif,
    seuil_amplitude_globale,
    duree_mesure_max,
    duree_mesure_min,
    coeff_collage,
    seuil_alteration,
    tempo,
    tolerance_accord,
    temps_par_mesure,
    nom_fichier_audio,
    nom_fichier,
    notes_lilypond,
    notes_nom_reel,
    frequences_notes,
    cle,
    ref_rythme
)

import json




def main_recup_notes():
    
    freq_ech, donnees = lire_audio(nom_fichier_audio)
    blocs = decouper_signal(donnees, freq_ech)

    print("Analyse des fréquences...")
    freqs_detectees = [extraire_frequences(bloc, freq_ech) for bloc in blocs]
    
    # matrice de couples (frequence, amplitude) avec l'amplitude qui vaut parfois 0 grace au filtre
    freqs_filtrees = filtrer_amplitudes_globales(freqs_detectees)
    
    notes_detectees = convertir_frequences_en_notes_avec_amplitude(freqs_filtrees)
    
    notes_sans_doublons = enlever_doublons(notes_detectees)
    
    info_notes_brutes = coller_notes(notes_sans_doublons)
    
    
    tf = temps_forts(info_notes_brutes) 
    
    # print(f"\nInfo_notes_brutes : \n{info_notes_brutes}")
    print(f"\nTemps forts : \n{tf}")
    
    with open("inb_cc_6_note", "w") as f:
        json.dump(info_notes_brutes, f)
        
    """with open("ma_liste.txt", "r") as f:
        info_notes_brutes = json.load(f)"""
    
    main_reconstitution_partition(info_notes_brutes, tf)


def main_reconstitution_partition(info_notes_brutes, temps_forts):
    
    tonalite_input = input("Entrez la tonalité cible (ex: c, g, d, fis, bes...): ").strip().lower()
    
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
    
    #---------Pas transposition
    # tonalite = determiner_tonalite(alterations)
    # print(f"\nTonalité : {tonalite}")
    
    # notes_mesures, duree_mesure = decouper_en_mesures(notes_armure, temps_forts)  # La premiere mesure n'a pas forcement de temps fort
    # notes_mesures_accords = regrouper_accord(notes_mesures)  # mesures contenant des accords (accord = (liste des notes, duree))
    
    # print(f"Mesures d'accords : \n{notes_mesures_accords}")
    
    # Finalement on prend pas en compte la premiere mesure, on commence par le premier temps fort
    code = generer_lilypond(notes_mesures_accords, duree_mesure, cle, tonalite_pour_lilypond, temps_par_mesure, ref_rythme)
    
    #code = generer_lilypond(notes_mesures_accords, duree_mesure, cle, tonalite, temps_par_mesure, ref_rythme)
    ecrire_lilypond(code) 
    
    compiler_lilypond()


main_recup_notes()

