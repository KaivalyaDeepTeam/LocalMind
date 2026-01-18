# LocalMind
## Guide Technique

---

**Transformez l'Audio en Intelligence**

Transcription de qualité professionnelle avec analyse de qualité alimentée par l'IA.
100% hors ligne. Coût zéro. Confidentialité complète.

---

## Contenu

- [Démarrage Rapide](#démarrage-rapide)
- [Votre Première Transcription](#votre-première-transcription)
- [Comprendre la Notation de Qualité](#comprendre-la-notation-de-qualité)
- [Choisir le Bon Modèle](#choisir-le-bon-modèle)
- [Paramètres](#paramètres)
- [Exporter et Partager](#exporter-et-partager)
- [Dépannage](#dépannage)

---

## Démarrage Rapide

### Ce Dont Vous Avez Besoin

- **macOS** 10.15 ou ultérieur
- **4GB RAM** minimum (8GB recommandé)
- **Fichier audio** au format MP3, WAV, M4A, FLAC, OGG ou WEBM

### Premier Lancement

1. Téléchargez LocalMind
2. Déplacez vers le dossier Applications
3. Double-cliquez pour ouvrir
4. Accordez les autorisations si demandé

C'est tout. Pas de compte. Pas d'abonnement. Pas d'internet requis.

---

## Votre Première Transcription

### Étape 1: Ajoutez Votre Audio

Glissez-déposez votre fichier audio dans la fenêtre.

**Formats supportés:**
MP3 · WAV · M4A · FLAC · OGG · WEBM

**Taille du fichier:**
Jusqu'à 2GB par fichier

### Étape 2: Configurez le Traitement

Choisissez vos préférences:

**Mode de Traitement:**
- **Hors ligne** - Traite localement sur votre appareil
- **En ligne** - Utilise l'IA cloud (nécessite des clés API)

**Langue:**
Détection automatique ou sélectionnez parmi plus de 50 langues

**Modèle:**
Large V3 (Meilleure Qualité) - Recommandé pour la première utilisation

### Étape 3: Traiter

Cliquez sur **Traiter** et observez le pipeline:

1. **Transcription** - Conversion de la parole en texte
2. **Fusion des Canaux** - Combinaison des flux audio
3. **Audit de Qualité** - Analyse alimentée par l'IA
4. **Génération de Rapport** - Création de la sortie complète

**Temps de traitement:**
Audio de 10 minutes ≈ 5-7 minutes sur un laptop moyen

---

## Comprendre la Notation de Qualité

LocalMind ne transcrit pas seulement—il évalue vos conversations en utilisant un raisonnement IA avancé.

### Paramètres Par Défaut

**Conformité** (poids 1.0x)
- Salutation et Introduction
- Écoute Active
- Identification du Problème
- Solution Fournie
- Connaissance du Produit
- Clarté de Communication
- Empathie et Rapport
- Contrôle d'Appel
- Clôture d'Appel
- Conformité au Script

### Personnaliser les Scores

Ajustez les poids des paramètres de 0.1x à 3.0x:

- **Poids plus élevé** = Plus important pour le score global
- **Poids plus faible** = Moins d'impact sur la note finale

### Comment Fonctionne la Notation

LocalMind utilise le **raisonnement Chain-of-Thought (CoT)**:

1. Analyse le contexte complet de la transcription
2. Identifie les moments et motifs clés
3. Évalue contre chaque paramètre
4. Fournit des explications détaillées
5. Calcule le score final pondéré

---

## Choisir le Bon Modèle

### Modèles de Transcription

#### Qwen 2.5 (7B) - Meilleur pour l'audit (Recommandé)

- **Taille:** 4GB
- **Vitesse:** Rapide
- **Qualité:** Excellente sortie JSON
- **Idéal pour:** Analyse de qualité, usage professionnel

#### Whisper Large V3
- Précision maximale (97-99%)
- Idéal pour les transcriptions critiques

---

## Paramètres

Accédez aux paramètres via le menu **Paramètres** ou `⌘,` (Command-Virgule)

### Fournisseur LLM

Choisissez votre fournisseur d'IA:

**LLM Local (Gratuit, Hors ligne)**
- Pas d'internet requis
- Confidentialité complète
- Pas de coûts API
- Recommandé pour la plupart des utilisateurs

**OpenAI API / Anthropic API**
- Nécessite une clé API
- Traitement cloud

### Paramètres de Transcription

**Modèle:** Large V3 (Meilleure Qualité)
**Langue:** Détection automatique
**Accélération GPU:** Activer pour un traitement 3-5x plus rapide

### Paramètres de Sortie

**Répertoire de Sortie:** Choisissez où enregistrer les résultats

**Auto-export après traitement:**
- ✓ Auto-export JSON
- ✓ Auto-export PDF

### Apparence

**Langue de l'IU:**
English · Español · 日本語 · العربية · हिन्दी · Русский · Français · 中文

**Thème:** Sombre · Clair · Système

---

## Exporter et Partager

### Formats Disponibles

**JSON** - Données lisibles par machine
**PDF** - Rapport professionnel avec mise en forme
**TXT** - Transcription en texte brut uniquement

### Exportation

1. Terminez le traitement
2. Cliquez sur le bouton **Exporter**
3. Choisissez le(s) format(s)
4. Sélectionnez la destination
5. Cliquez sur **Enregistrer**

---

## Support Multilingue

LocalMind parle votre langue.

### Langues d'IU Supportées

- 🇬🇧 **English** (Anglais)
- 🇪🇸 **Español** (Espagnol)
- 🇯🇵 **日本語** (Japonais)
- 🇦🇪 **العربية** (Arabe) - avec disposition RTL
- 🇮🇳 **हिन्दी** (Hindi)
- 🇷🇺 **Русский** (Russe)
- 🇫🇷 **Français**
- 🇨🇳 **中文** (Chinois Simplifié)

### Changer de Langue

**Paramètres → Apparence → Langue de l'IU**

Les changements s'appliquent immédiatement. Aucun redémarrage requis.

### Langues de Transcription

LocalMind transcrit **plus de 50 langues** incluant:

Anglais · Espagnol · Français · Allemand · Italien · Portugais · Néerlandais · Russe · Arabe · Hindi · Japonais · Coréen · Chinois · et bien d'autres

---

## Dépannage

### Le Traitement Prend Trop de Temps

**Essayez ceci:**
- Utilisez un modèle Whisper plus petit (Medium au lieu de Large)
- Activez l'accélération GPU dans les Paramètres
- Fermez d'autres applications pour libérer la RAM

### Scores de Qualité Faibles

**Rappelez-vous:**
- La notation de qualité nécessite le téléchargement de LLM
- La première exécution télécharge les modèles (peut prendre du temps)
- Assurez-vous que "Activer la Notation de Qualité" est coché

---

## Confidentialité et Sécurité

### Ce Que LocalMind Collecte

**Rien.**

- Pas de télémétrie
- Pas d'analytique
- Pas de rapports de crash
- Pas de statistiques d'utilisation

Votre audio ne quitte jamais votre appareil en mode hors ligne.

### Stockage des Données

Toutes les données stockées localement:
- **Transcriptions:** Votre répertoire de sortie choisi
- **Modèles:** `~/.cache/localmind/`
- **Paramètres:** `~/Library/Application Support/localmind/`

### Open Source

LocalMind est open source (Licence MIT).

Auditez le code vous-même: [github.com/prepladder/localmind](https://github.com/prepladder/localmind)

---

## À Propos de LocalMind

LocalMind a été construit pour donner à tous l'accès à la transcription et à l'analyse de qualité professionnelle sans sacrifier la confidentialité ni payer d'abonnements mensuels.

**Notre Promesse:**

- ✓ Toujours gratuit
- ✓ Toujours capable de fonctionner hors ligne
- ✓ Toujours open source
- ✓ Toujours axé sur la confidentialité

**Version:** 1.0.0
**Dernière Mise à Jour:** Janvier 2026

---

**Fabriqué avec soin pour les chercheurs, podcasteurs, journalistes, centres d'appels, professionnels du droit et tous ceux qui valorisent leur confidentialité.**

---

© 2026 LocalMind. Publié sous Licence MIT.
