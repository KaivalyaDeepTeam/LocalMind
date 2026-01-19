# Guide Technique LocalMind
## Version 1.2.0

---

**Transformez l'Audio en Intelligence**

Transcription de qualité professionnelle avec analyse qualité alimentée par IA.
100% hors ligne. Coût zéro. Confidentialité totale.

---

## Table des Matières

1. [Introduction](#introduction)
2. [Configuration Requise](#configuration-requise)
3. [Installation et Premier Lancement](#installation-et-premier-lancement)
4. [Section A: Transcription (Parole vers Texte)](#section-a-transcription-parole-vers-texte)
5. [Section B: Analyse Qualité LLM](#section-b-analyse-qualité-llm)
6. [Options d'Exportation](#options-dexportation)
7. [Référence des Paramètres](#référence-des-paramètres)
8. [Dépannage](#dépannage)
9. [Confidentialité et Sécurité](#confidentialité-et-sécurité)

---

## Introduction

LocalMind est une application de bureau qui effectue deux tâches IA distinctes:

| Tâche | Technologie | Objectif |
|-------|-------------|----------|
| **Transcription** | OpenAI Whisper | Convertir la parole en texte |
| **Analyse Qualité** | LLM Local/Cloud | Noter et analyser les conversations |

Ce sont des **systèmes séparés** qui fonctionnent ensemble mais peuvent être utilisés indépendamment.

---

## Configuration Requise

### Configuration Minimale

| Composant | Requis |
|-----------|--------|
| Système d'exploitation | macOS 12 (Monterey) ou ultérieur |
| RAM | 8 Go |
| Stockage | 10 Go d'espace libre |
| Processeur | Intel ou Apple Silicon |

### Configuration Recommandée

| Composant | Requis |
|-----------|--------|
| Système d'exploitation | macOS 14 (Sonoma) ou ultérieur |
| RAM | 16 Go ou plus |
| Stockage | 20 Go d'espace libre |
| Processeur | Puce Apple M1/M2/M3 |

### Téléchargements au Premier Lancement

| Type de Modèle | Taille | Moment du Téléchargement |
|----------------|--------|--------------------------|
| Whisper (transcription) | ~1.5 Go | Première transcription |
| LLM Local (analyse) | ~4 Go | Première analyse qualité |

**Internet requis uniquement pour les téléchargements initiaux des modèles.**

---

## Installation et Premier Lancement

### Étape 1: Télécharger

Téléchargez `LocalMind-1.2.0-macOS.dmg` depuis:
[github.com/KaivalyaDeepTeam/LocalMind/releases](https://github.com/KaivalyaDeepTeam/LocalMind/releases)

### Étape 2: Installer

1. Ouvrez le fichier DMG téléchargé
2. Glissez LocalMind dans votre dossier Applications
3. Éjectez le DMG

### Étape 3: Premier Lancement

**Important:** macOS peut bloquer l'application car elle ne provient pas de l'App Store.

**Pour ouvrir LocalMind:**

1. Faites un clic droit sur LocalMind.app
2. Sélectionnez "Ouvrir" dans le menu
3. Cliquez sur "Ouvrir" dans la boîte de dialogue de sécurité

---

# Section A: Transcription (Parole vers Texte)

Cette section couvre **la conversion audio en texte** utilisant la technologie Whisper d'OpenAI.

---

## Qu'est-ce que la Transcription?

La transcription convertit les mots parlés dans les fichiers audio en texte écrit. LocalMind utilise **OpenAI Whisper**, l'un des systèmes de reconnaissance vocale les plus précis disponibles.

### Comment Ça Fonctionne

```
Fichier Audio → Whisper AI → Transcription Écrite
    (MP3)         (Local)         (Texte)
```

### Caractéristiques Principales

- **Plus de 50 langues** supportées
- **Détection automatique de la langue**
- **Identification des locuteurs** (diarisation)
- **Horodatages** pour chaque segment
- **Fonctionne complètement hors ligne** après téléchargement du modèle

### Formats Audio Supportés

| Format | Extension | Description |
|--------|-----------|-------------|
| MP3 | .mp3 | Format le plus courant |
| WAV | .wav | Non compressé, haute qualité |
| M4A | .m4a | Format Apple/iTunes |
| FLAC | .flac | Compression sans perte |
| OGG | .ogg | Format open source |
| WebM | .webm | Format audio web |

**Taille maximale de fichier:** 2 Go par fichier

---

## Modèles Whisper Expliqués

| Modèle | Taille | Précision | Vitesse | Idéal Pour |
|--------|--------|-----------|---------|------------|
| **Large V3** | 1.5 Go | 97-99% | Lent | Usage professionnel |
| **Medium** | 750 Mo | 95-97% | Moyen | Usage quotidien |
| **Small** | 250 Mo | 92-95% | Rapide | Transcriptions rapides |
| **Base** | 150 Mo | 88-92% | Très Rapide | Tests |
| **Tiny** | 75 Mo | 80-88% | Le Plus Rapide | Temps réel |

---

# Section B: Analyse Qualité LLM

Cette section couvre **l'analyse de conversations alimentée par IA** utilisant les Grands Modèles de Langage.

---

## Qu'est-ce que l'Analyse LLM?

L'analyse LLM lit votre transcription et évalue la qualité de la conversation. Elle fournit:

- **Score global** (0-100%)
- **Scores par paramètre** (critères personnalisables)
- **Points forts** identifiés dans la conversation
- **Axes d'amélioration**
- **Retour détaillé** pour chaque paramètre

### Différence Clé avec la Transcription

| Aspect | Transcription | Analyse LLM |
|--------|---------------|-------------|
| **Entrée** | Fichier audio | Transcription texte |
| **Sortie** | Texte écrit | Scores et retours |
| **Technologie** | Whisper | LLM (Phi/Qwen/GPT) |
| **Objectif** | Convertir la parole | Évaluer la qualité |
| **Requis?** | Oui | Optionnel |

---

## Options de Fournisseurs LLM

### 1. LLM Local (Recommandé)

| Avantages | Inconvénients |
|-----------|---------------|
| 100% gratuit | Plus lent que le cloud |
| Confidentialité totale | Nécessite 8Go+ de RAM |
| Pas besoin d'internet | Téléchargement de modèle volumineux |

### 2. API OpenAI

| Avantages | Inconvénients |
|-----------|---------------|
| Très rapide | Coûte de l'argent |
| Haute qualité | Nécessite internet |

### 3. API Anthropic

| Avantages | Inconvénients |
|-----------|---------------|
| Excellent raisonnement | Coûte de l'argent |
| Idéal pour l'analyse | Nécessite internet |

---

## Modèles LLM Locaux

| Modèle | Taille | Vitesse | Qualité | Idéal Pour |
|--------|--------|---------|---------|------------|
| **Phi-3.5 Mini** | 2.4 Go | Rapide | Bonne | Par défaut |
| **Qwen 2.5 3B** | 2.0 Go | Très Rapide | Bonne | Analyse rapide |
| **Qwen 2.5 7B** | 4.4 Go | Moyen | Excellente | Usage professionnel |
| **Mistral 7B** | 4.1 Go | Moyen | Excellente | Retour détaillé |
| **Gemma 2 2B** | 1.6 Go | Le Plus Rapide | Modérée | Priorité vitesse |

---

## Paramètres de Notation Qualité

| Paramètre | Poids | Ce Qu'il Mesure |
|-----------|-------|-----------------|
| Greeting & Introduction | 1.0x | Ouverture professionnelle |
| Active Listening | 1.0x | Attention et engagement |
| Problem Identification | 1.0x | Compréhension du problème |
| Solution Provided | 1.0x | Résolution utile |
| Product Knowledge | 1.0x | Précision des informations |
| Communication Clarity | 1.0x | Explications claires |
| Empathy & Rapport | 1.0x | Connexion émotionnelle |
| Call Control | 1.0x | Gestion du flux |
| Call Closing | 1.0x | Conclusion professionnelle |
| Script Compliance | 1.0x | Respect des directives |

---

## Options d'Exportation

| Format | Raccourci | Idéal Pour |
|--------|-----------|------------|
| **PDF** | Cmd + Shift + P | Direction, clients |
| **Markdown** | Cmd + Shift + M | Partage rapide |
| **JSON** | Cmd + Shift + J | Intégration système |
| **Texte** | Cmd + Shift + T | Archivage simple |

---

## Confidentialité et Sécurité

### Gestion des Données

| Mode | Données Audio | Transcription |
|------|---------------|---------------|
| **Local LLM** | Reste sur l'appareil | Reste sur l'appareil |
| **OpenAI API** | Reste sur l'appareil | Envoyée à OpenAI |
| **Anthropic API** | Reste sur l'appareil | Envoyée à Anthropic |

**Vos fichiers audio ne sont JAMAIS téléchargés vers le cloud.**

### Ce que LocalMind Collecte

**Rien.**

- Pas de télémétrie
- Pas d'analytiques
- Pas de rapports de crash
- Pas de compte requis

---

## Raccourcis Clavier

| Action | Raccourci |
|--------|-----------|
| Ouvrir Fichier | Cmd + O |
| Démarrer Traitement | Cmd + Return |
| Arrêter | Escape |
| Exporter PDF | Cmd + Shift + P |
| Exporter Markdown | Cmd + Shift + M |
| Exporter JSON | Cmd + Shift + J |
| Exporter Transcription | Cmd + Shift + T |
| Paramètres de Notation | Cmd + Shift + S |
| Paramètres | Cmd + , |
| Quitter | Cmd + Q |

---

## Obtenir de l'Aide

- **Documentation:** [github.com/KaivalyaDeepTeam/LocalMind](https://github.com/KaivalyaDeepTeam/LocalMind)
- **Problèmes:** [github.com/KaivalyaDeepTeam/LocalMind/issues](https://github.com/KaivalyaDeepTeam/LocalMind/issues)

---

**Version:** 1.2.0
**Dernière Mise à Jour:** Janvier 2026
**Licence:** MIT

© 2026 Équipe LocalMind. Fait avec soin pour tous ceux qui valorisent leur vie privée.
