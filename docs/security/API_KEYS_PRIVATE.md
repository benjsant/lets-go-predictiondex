# 🔐 API Keys - NE PAS COMMITER

## Clés générées le 26 janvier 2026

### Clé 1 - Client Admin
```
BgQJ2_Ur4uYKBsw6Jf4TI_yfA6u0BFwb4a1YbOSmMVQ
```

### Clé 2 - Client Streamlit
```
25b-IZRYPY4ZRHdSJtj7x566ekaSDZ-MoPtWHpS8NTo
```

### Clé 3 - Client Test
```
KnHmEUZhAY_PAZdJopdkuuTEV-PmqXIpRscmOZY1i2w
```

## Utilisation

### Avec curl
```bash
curl -H "X-API-Key: BgQJ2_Ur4uYKBsw6Jf4TI_yfA6u0BFwb4a1YbOSmMVQ" \
     http://localhost:8080/pokemon
```

### Avec Python requests
```python
import requests

headers = {"X-API-Key": "BgQJ2_Ur4uYKBsw6Jf4TI_yfA6u0BFwb4a1YbOSmMVQ"}
response = requests.get("http://localhost:8080/pokemon", headers=headers)
```

### Dans Streamlit
Ajoutez la clé dans l'environnement :
```bash
export API_KEY="25b-IZRYPY4ZRHdSJtj7x566ekaSDZ-MoPtWHpS8NTo"
```

## Régénération

Pour générer de nouvelles clés :
```bash
python api_pokemon/middleware/security.py
```

## ⚠️ IMPORTANT

- **NE JAMAIS** commiter ce fichier dans Git
- Distribuer via canal sécurisé (email chiffré, vault, etc.)
- Stocker dans un gestionnaire de mots de passe
- Révoquer immédiatement si compromises
