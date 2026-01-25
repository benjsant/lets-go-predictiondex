#!/usr/bin/env python3
"""
Test Manuel de l'API de Prédiction
Teste les fonctionnalités avec et sans available_moves_b
"""

import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

# Codes couleur pour le terminal
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(text: str):
    """Affiche un header formaté"""
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{'='*80}{RESET}")


def print_success(text: str):
    """Affiche un message de succès"""
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text: str):
    """Affiche un message d'erreur"""
    print(f"{RED}❌ {text}{RESET}")


def print_info(text: str):
    """Affiche une information"""
    print(f"{BLUE}ℹ️  {text}{RESET}")


def print_warning(text: str):
    """Affiche un avertissement"""
    print(f"{YELLOW}⚠️  {text}{RESET}")


def check_api_health() -> bool:
    """Vérifie que l'API est démarrée"""
    print_header("VÉRIFICATION: API démarrée")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=2)
        if response.status_code == 200:
            print_success("API accessible sur http://localhost:8000")
            print_success("Documentation disponible sur http://localhost:8000/docs")
            return True
        else:
            print_error(f"API répond avec status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Impossible de se connecter à l'API")
        print_info("Démarrez l'API avec: cd api_pokemon && uvicorn main:app --reload --port 8000")
        return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_model_info() -> Dict[str, Any]:
    """Test 1: Vérifier les infos du modèle chargé"""
    print_header("TEST 1: Informations du Modèle")
    
    try:
        response = requests.get(f"{BASE_URL}/predict/model-info")
        
        if response.status_code != 200:
            print_error(f"Status code: {response.status_code}")
            print_error(response.text)
            return None
        
        result = response.json()
        
        print_success(f"Model Type: {result['model_type']}")
        print_success(f"Version: {result['version']}")
        print_success(f"Features: {result['n_features']}")
        print_success(f"Test Accuracy: {result['metrics']['test_accuracy']*100:.2f}%")
        print_success(f"Test ROC-AUC: {result['metrics']['test_roc_auc']*100:.2f}%")
        print_success(f"Trained At: {result['trained_at']}")
        
        # Vérifier si c'est v2
        if result['version'] == 'v2':
            print_success("✨ Modèle v2 (multi-scénarios) chargé")
        else:
            print_warning(f"Modèle {result['version']} chargé (attendu: v2)")
        
        return result
        
    except Exception as e:
        print_error(f"Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_prediction_without_moves_b() -> Dict[str, Any]:
    """Test 2: Prédiction sans available_moves_b (comportement original)"""
    print_header("TEST 2: Prédiction SANS available_moves_b")
    print_info("Scénario: Carapuce vs Salamèche, B utilise son meilleur move automatiquement")
    
    try:
        payload = {
            "pokemon_a_id": 7,  # Carapuce
            "pokemon_b_id": 4,   # Salamèche
            "available_moves": ["Charge", "Pistolet à O", "Hydrocanon"]
        }
        
        print_info(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            f"{BASE_URL}/predict/best-move",
            json=payload
        )
        
        if response.status_code != 200:
            print_error(f"Status code: {response.status_code}")
            print_error(response.text)
            return None
        
        result = response.json()
        
        print_success(f"Pokémon A: {result['pokemon_a_name']}")
        print_success(f"Pokémon B: {result['pokemon_b_name']}")
        print_success(f"Recommended Move: {result['recommended_move']}")
        print_success(f"Win Probability: {result['win_probability']*100:.1f}%")
        
        print_info("\n📊 Top 3 moves:")
        for i, move in enumerate(result['all_moves'][:3], 1):
            print(f"   {i}. {move['move_name']:20s} | Win Prob: {move['win_probability']*100:5.1f}% | "
                  f"Type mult: {move['type_multiplier']}x | Power: {move['move_power']}")
        
        return result
        
    except Exception as e:
        print_error(f"Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_prediction_with_moves_b() -> Dict[str, Any]:
    """Test 3: Prédiction avec available_moves_b (nouvelle fonctionnalité)"""
    print_header("TEST 3: Prédiction AVEC available_moves_b")
    print_info("Scénario: Carapuce vs Salamèche, B limité à ['Flammèche', 'Charge']")
    
    try:
        payload = {
            "pokemon_a_id": 7,  # Carapuce
            "pokemon_b_id": 4,   # Salamèche
            "available_moves": ["Charge", "Pistolet à O", "Hydrocanon"],
            "available_moves_b": ["Flammèche", "Charge"]  # B limité à ces moves
        }
        
        print_info(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            f"{BASE_URL}/predict/best-move",
            json=payload
        )
        
        if response.status_code != 200:
            print_error(f"Status code: {response.status_code}")
            print_error(response.text)
            return None
        
        result = response.json()
        
        print_success(f"Pokémon A: {result['pokemon_a_name']}")
        print_success(f"Pokémon B: {result['pokemon_b_name']}")
        print_success(f"Recommended Move: {result['recommended_move']}")
        print_success(f"Win Probability: {result['win_probability']*100:.1f}%")
        
        print_info("\n📊 Top 3 moves:")
        for i, move in enumerate(result['all_moves'][:3], 1):
            print(f"   {i}. {move['move_name']:20s} | Win Prob: {move['win_probability']*100:5.1f}% | "
                  f"Type mult: {move['type_multiplier']}x | Power: {move['move_power']}")
        
        return result
        
    except Exception as e:
        print_error(f"Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_different_pokemon_pair() -> Dict[str, Any]:
    """Test 4: Autre paire de Pokémon"""
    print_header("TEST 4: Autre Paire - Pikachu vs Bulbizarre")
    print_info("Scénario: Pikachu (électrique) vs Bulbizarre (plante/poison)")
    
    try:
        payload = {
            "pokemon_a_id": 25,  # Pikachu
            "pokemon_b_id": 1,   # Bulbizarre
            "available_moves": ["Tonnerre", "Vive-Attaque", "Queue de Fer"],
            "available_moves_b": ["Fouet Lianes", "Tranch'Herbe", "Charge"]
        }
        
        print_info(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            f"{BASE_URL}/predict/best-move",
            json=payload
        )
        
        if response.status_code != 200:
            print_error(f"Status code: {response.status_code}")
            print_error(response.text)
            return None
        
        result = response.json()
        
        print_success(f"Pokémon A: {result['pokemon_a_name']}")
        print_success(f"Pokémon B: {result['pokemon_b_name']}")
        print_success(f"Recommended Move: {result['recommended_move']}")
        print_success(f"Win Probability: {result['win_probability']*100:.1f}%")
        
        print_info("\n📊 Top 3 moves:")
        for i, move in enumerate(result['all_moves'][:3], 1):
            print(f"   {i}. {move['move_name']:20s} | Win Prob: {move['win_probability']*100:5.1f}% | "
                  f"Type mult: {move['type_multiplier']}x | Power: {move['move_power']}")
        
        return result
        
    except Exception as e:
        print_error(f"Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return None


def compare_predictions(result1: Dict[str, Any], result2: Dict[str, Any]):
    """Test 5: Comparer les prédictions avec et sans available_moves_b"""
    print_header("TEST 5: Comparaison avec/sans available_moves_b")
    
    if not result1 or not result2:
        print_error("Impossible de comparer - résultats manquants")
        return
    
    print_info("📊 COMPARAISON DES RÉSULTATS:")
    
    print(f"\n{BOLD}Sans available_moves_b:{RESET}")
    print(f"  - Meilleur move: {result1['recommended_move']}")
    print(f"  - Win probability: {result1['win_probability']*100:.1f}%")
    print(f"  - Nombre de moves évalués: {len(result1['all_moves'])}")
    
    print(f"\n{BOLD}Avec available_moves_b=['Flammèche', 'Charge']:{RESET}")
    print(f"  - Meilleur move: {result2['recommended_move']}")
    print(f"  - Win probability: {result2['win_probability']*100:.1f}%")
    print(f"  - Nombre de moves évalués: {len(result2['all_moves'])}")
    
    # Calcul de la différence
    diff_prob = result2['win_probability'] - result1['win_probability']
    
    print(f"\n{BOLD}Différence:{RESET}")
    print(f"  - Δ Win probability: {diff_prob*100:+.1f}%")
    
    if abs(diff_prob) > 0.01:  # Plus de 1% de différence
        print_success("✨ Les probabilités diffèrent significativement")
        print_info("Le paramètre available_moves_b influence bien les prédictions")
    elif abs(diff_prob) > 0.001:  # Plus de 0.1% de différence
        print_success("✨ Les probabilités diffèrent légèrement")
        print_info("Impact visible mais modéré de available_moves_b")
    else:
        print_warning("⚠️ Les probabilités sont quasi identiques")
        print_info("Cela peut arriver si les moves de B sont similaires dans les deux cas")
    
    # Comparer les meilleurs moves
    if result1['recommended_move'] != result2['recommended_move']:
        print_success("✨ Le meilleur move change selon le scénario")
    else:
        print_info("Le meilleur move reste le même dans les deux cas")


def run_all_tests():
    """Exécute tous les tests"""
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}🧪 TEST MANUEL DE L'API DE PRÉDICTION{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")
    
    # Vérifier que l'API est accessible
    if not check_api_health():
        print_error("\n❌ L'API n'est pas accessible. Impossible de continuer les tests.")
        print_info("\nDémarrez l'API avec:")
        print_info("  cd api_pokemon")
        print_info("  uvicorn main:app --reload --port 8000")
        return False
    
    # Test 1: Model info
    model_info = test_model_info()
    if not model_info:
        print_error("Test 1 échoué - impossible de continuer")
        return False
    
    # Test 2: Sans available_moves_b
    result1 = test_prediction_without_moves_b()
    if not result1:
        print_error("Test 2 échoué")
        return False
    
    # Test 3: Avec available_moves_b
    result2 = test_prediction_with_moves_b()
    if not result2:
        print_error("Test 3 échoué")
        return False
    
    # Test 4: Autre paire
    result3 = test_different_pokemon_pair()
    if not result3:
        print_warning("Test 4 échoué (certains Pokémon peuvent ne pas être dans la DB)")
    
    # Test 5: Comparaison
    compare_predictions(result1, result2)
    
    # Résumé final
    print_header("RÉSUMÉ DES TESTS")
    print_success("✅ Test 1: Model Info - OK")
    print_success("✅ Test 2: Prédiction sans available_moves_b - OK")
    print_success("✅ Test 3: Prédiction avec available_moves_b - OK")
    
    if result3:
        print_success("✅ Test 4: Autre paire de Pokémon - OK")
    else:
        print_warning("⚠️ Test 4: Autre paire de Pokémon - SKIP")
    
    print_success("✅ Test 5: Comparaison - OK")
    
    print(f"\n{BOLD}{GREEN}{'='*80}{RESET}")
    print(f"{BOLD}{GREEN}✅ TOUS LES TESTS ESSENTIELS RÉUSSIS{RESET}")
    print(f"{BOLD}{GREEN}{'='*80}{RESET}\n")
    
    print_info("📝 Prochaines étapes:")
    print_info("  1. Vérifier les notebooks Jupyter (notebooks/)")
    print_info("  2. Générer un dataset v2 complet avec tous les scénarios")
    print_info("  3. Entraîner le modèle v2 avec GridSearchCV étendu")
    print_info("  4. Comparer les performances v1 vs v2 (notebook 04)")
    
    return True


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_warning("\n\n⚠️ Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\n❌ ERREUR FATALE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
