import random
import numpy as np

def generate_card(
    mean_health=60, std_dev_health=25, min_health=20, max_health=140,
    attack_scaling=0.6, attack_variance=0.1,
    ability_base_chance=0.2, extreme_health_ability_boost=0.63,
    high_health_dual_attack_threshold=90
):
    """Generates a card with randomized stats based on the given parameters."""
    # Health follows a normal distribution but is clipped within bounds
    health = int(np.clip(np.random.normal(mean_health, std_dev_health), min_health, max_health))
    
    # Attack scales with health but has some variance
    attack = int(health * (attack_scaling + random.uniform(-attack_variance, attack_variance)))
    
    # Probability of an ability slot increases at extreme health values
    health_proximity = abs(health - mean_health) / (max_health - min_health)
    ability_chance = ability_base_chance + health_proximity * extreme_health_ability_boost
    has_ability = random.random() < ability_chance
    
    # Cards with high health get a second attack value
    attack_values = [round(attack/10)*10]
    if health > high_health_dual_attack_threshold:
        attack_values.append(int(round((attack * random.uniform(0.2, 0.5))/10)*10))  # Weaker secondary attack
    
    return {
        "Health": round(health/10)*10,
        "Attack": attack_values,
        "Has Ability": has_ability
    }

# Generate sample cards for testing
if __name__ == "__main__":
    num_samples = 20
    for _ in range(num_samples):
        print(generate_card())
