# BulleUp

**Gestionnaire de collections de bandes dessinées**

Application backend Django REST Framework permettant de gérer sa collection de BD, créer des listes de souhaits et suivre d'autres collectionneurs.

> 📚 **Projet d'apprentissage** de Django REST Framework et des bonnes pratiques de développement d'APIs RESTful.

---

## ✨ Fonctionnalités

- Authentification JWT avec rotation et blacklist des tokens
- Gestion de profil utilisateur (avatar, bio, informations)
- Changement et réinitialisation de mot de passe
- Suppression de compte sécurisée
- Gestion de collection de BD et wishlist
- Système d'avis et de notes
- Suivi d'autres utilisateurs (followers/following)
- Optimisation automatique des avatars (HEIC, EXIF, compression)
- Format d'erreur uniforme pour l'API

---

## 🛠 Technologies

**Backend**
- Python 3.12
- Django 3.2.5
- Django REST Framework
- djangorestframework-simplejwt
- Pillow (traitement d'images)
- SQLite (dev) / PostgreSQL (prod)

**Frontend** (application mobile séparée)
- React Native / Expo
- TypeScript
- React Query
- Axios

---

## 🚀 Installation

```bash
# Cloner le projet
git clone <url-du-repo>
cd bulleUp

# Créer un environnement virtuel
python -m venv env
source env/bin/activate  # macOS/Linux

# Installer les dépendances
pip install -r requirements.txt

# Configurer .env
cp .env.example .env
# Éditer .env avec vos valeurs

# Migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

---

## 🎯 Roadmap

### Phase 1 - Base (✅ Complétée)
- [x] Authentification JWT avec blacklist
- [x] Gestion utilisateurs et profils
- [x] Système de collection et wishlist
- [x] Avis et notes
- [x] Système de followers
- [x] Format d'erreur uniforme
- [x] Optimisation des avatars

### Phase 2 - Améliorations
- [ ] Pagination avancée
- [ ] Filtres et recherche
- [ ] Upload d'images de BD
- [ ] Statistiques de collection
- [ ] Notifications
- [ ] Cache Redis pour performances

### Phase 3 - Social
- [ ] Feed d'activité
- [ ] Recommandations personnalisées
- [ ] Partage de collections
- [ ] Messagerie entre utilisateurs

### Phase 4 - Production
- [ ] Tests unitaires et d'intégration
- [ ] CI/CD avec GitHub Actions
- [ ] Déploiement (Docker, AWS/Heroku)
- [ ] Monitoring et logs
- [ ] Documentation OpenAPI/Swagger

---

## 👤 Auteur

**Meka** - Projet d'apprentissage Django REST Framework

---

**Version** : 1.0.0
