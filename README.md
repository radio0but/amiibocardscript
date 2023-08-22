# Amiibo Card Generator Suite

Ce projet contient deux applications Python pour créer des cartes Animal Crossing prêtes à imprimer en PDF. Il comprend `AnimalCrossingCardsDownloader.py` pour télécharger et sélectionner des images et `AnimalCrossingCardsPrintPrep.py` pour générer le fichier PDF final. Ce projet utilise AmiiboAPI pour les donnees. Le AnimalCrossingCardsPrintPrep.py est specifiquement calibre pour les cartes nfc 5,44cm x 8,55cm teste sur une imprimante HP DeskJet 3630. 

## Installation

### Windows

1. Installez Python depuis [le site officiel](https://www.python.org/downloads/).
2. Installez GTK 3 depuis [ce lien](https://www.gtk.org/docs/installations/windows/).
3. Installez les dépendances Python avec la commande suivante:

```bash
pip install requests pillow PyGObject
```

### Ubuntu/Fedora

1. Installez Python et GTK 3 avec:

```bash
sudo apt-get install python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 # Ubuntu
sudo dnf install python3 gtk3 python3-gobject python-pillow # Fedora
```

2. Installez les dépendances Python:

```bash
pip3 install requests
```

### Arch

1. Installez Python et GTK 3 avec:

```bash
sudo pacman -S python-gobject python-pillow gtk3
```

2. Installez les dépendances Python:

```bash
pip install requests
```

### MacOS

1. Installez Homebrew si vous ne l'avez pas:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Installez Python et GTK:

```bash
brew install python gtk+3 pygobject3
```

3. Installez les dépendances Python:

```bash
pip install requests pillow
```

## Utilisation

1. **Téléchargement et Sélection des Images**: Exécutez `AnimalCrossingCardsDownloader.py` pour télécharger et sélectionner 9 images.

```bash
python AnimalCrossingCardsDownloader.py
```

Sélectionnez les images en cliquant dessus et cliquez sur le bouton de téléchargement lorsqu'elles sont prêtes.

2. **Création du PDF**: Exécutez `AnimalCrossingCardsPrintPrep.py` pour ouvrir l'interface de création de PDF.

```bash
python AnimalCrossingCardsPrintPrep.py
```

Sélectionnez le dossier contenant les images téléchargées, choisissez l'orientation, prévisualisez et générez le PDF.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
```
